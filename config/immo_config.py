#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import pathlib
import subprocess
import copy
import yaml
import logging
from pathlib import Path

from helper.utils import CONST, get_timestamp


class ImmoConfig(object):
    """
    Configuration module
    """

    def __init__(self, job_config):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self.static_streams = []
        self.testing = False

        # -----------  2/ set the params dict -----------

        self._params = dict()

        # 1st, load general static params
        static_streams = self._read_yaml_files(CONST.CONF_PATH)
        self._params = self._dict_merge(
            self._params,
            self._static_inputs(static_streams, mode="overwrite"),
            mode="overwrite",
            check_keys=False,
        )

        # 2nd, overwrite with command line params
        self._params = self._dict_merge(
            self._params, job_config, mode="overwrite", check_keys=True
        )

        # 3rd, fill-in some missing fields with automatic values
        self._automated_config()

    def __getattr__(self, att):
        if "_params" not in self.__dict__:
            raise AttributeError
        if att in self._params:
            return self._params[att]
        else:
            raise AttributeError(f"{att} not in config keys!")

    def check_config_path(self, path):
        if path is None:
            return

        if type(path) is not str and not isinstance(path, os.PathLike):
            raise TypeError("`config_folder_path`must be a string or PathLike")

        config_folder_path = pathlib.Path(path)

        if not config_folder_path.exists():
            raise Exception(
                "Path '{}' to configuration file folder doesn't exist.".format(
                    config_folder_path
                )
            )

        return

    def _read_yaml_files(self, path):
        """
        Sets the YAML _streams for all static conf files found in path
        """
        # Check that 'path' is ok
        if path is None:
            return []

        if type(path) is not str and not isinstance(path, os.PathLike):
            raise TypeError("`config_folder_path`must be a string or PathLike")

        if not pathlib.Path(path).exists():
            raise Exception(
                "Path '{}' to configuration file folder doesn't exist.".format(path)
            )

        # Read yml fils in 'path'
        ymlfiles = [
            os.path.join(root, name)
            for root, dirs, files in os.walk(path)
            for name in files
            if name.endswith((".yml"))
        ]

        if len(ymlfiles) == 0:
            self._logger.warning(
                "No yaml files found in config folder {}.".format(path)
            )

        return ymlfiles

    @property
    def params(self):
        return self._params

    @classmethod
    def _static_inputs(cls, streams, mode):
        """
        Static inputs loaded from different yml files merged together. We use safe merge so that inconsistencies
        between different configs are detected.

        Returns
        -------
        dict
            The dictionnary of static parameters
        """

        inputs = dict()
        for stream in streams:
            f = io.open(stream, "r")
            f = yaml.load(f)
            inputs = cls._dict_merge(inputs, f, mode=mode, check_keys=False)
        return inputs

    @property
    def possible_input_keys(self):
        """
        The keys that we expect in the final dict of parameters
        """
        return {cat: set(self._params[cat]) for cat in self.possible_input_categories}

    @property
    def possible_input_categories(self):
        return self._params.keys()

    def validate(self):
        """
        Perform a dict_check on the underlying parameters at depth 1 (classic depth for main params)
        """
        missings = self._dict_check(self.params, max_level=1)
        if len(missings) > 0:
            raise Exception(
                "Missing arguments: '{}' in config object.".format(", ".join(missings))
            )

    def _automated_config(self):
        """
        Automated config fields to be performed after loading all args.
        """
        # executing git commit
        if is_git_directory():
            self.general["git_commit"] = (
                subprocess.check_output(["git", "rev-parse", "HEAD"])
                .decode("utf-8")
                .strip()
            )
        else:
            self.general["git_commit"] = "unknown"

        if self.general["timestamp"] is None:
            self.general["timestamp"] = get_timestamp()

        # Define data root
        if self.general["mode"] == "local":
            self.general["data_root"] = os.path.join(
                Path.home(), self.general["local_data_root_from_home"]
            )
        elif self.general["mode"] == "server":
            self.general["data_root"] = os.path.join(
                Path.home(), self.general["server_data_root_from_home"]
            )
        else:
            raise AttributeError(
                f"Invalid mode '{self.general['mode']}'. Must be either 'local' or 'server'"
            )

    @classmethod
    def _dict_merge(cls, dct_left, merge_dct, mode, check_keys=True, copy_data=True):
        """
        Recursive dict merge. Dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.

        Parameters
        ----------
        dct: dict
            Dictionary onto which the merge is executed

        merge_dct:dict
            Dictionary merged into dct

        mode:str, optional, default='safe'
            2 modes are allowed: "safe" or "overwrite". "safe" will raise error if the 2 dicts have the same key
            and different values while "overwrite" will overwrite ``dct`` with the value of ``merge_dct``

        check_keys: bool
            Should the method check if keys from ``merge_dct`` are present in ``dct_left`` and throw an error in case
            they are not

        Returns
        -------
        dict
            Merged dict

        """
        if not merge_dct:
            return dct_left

        if copy_data:
            dct = copy.deepcopy(dct_left)
        else:
            dct = dct_left

        if mode not in ["safe", "overwrite"]:
            raise ValueError("dict_merge mode '{}' not supported".format(mode))

        for k, v in merge_dct.items():

            if k not in dct.keys() and check_keys:
                raise Exception(f"Cannot overlay non existing config item '{k}'")

            if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict):
                dct[k] = cls._dict_merge(
                    dct[k], merge_dct[k], mode, copy_data=False, check_keys=check_keys
                )
            else:
                if mode == "safe":

                    if k in dct and dct[k] is not None and dct[k] != merge_dct[k]:
                        raise Exception(
                            "Trying to overwrite parameter '{}' of value '{}' with value '{}'. \
                                        Operation not allowed in 'safe' mode".format(
                                k, dct[k], merge_dct[k]
                            )
                        )
                    else:
                        dct[k] = merge_dct[k]

                if mode == "overwrite":
                    dct[k] = merge_dct[k]

        return dct

    @classmethod
    def _dict_check(cls, dct, current_level=0, max_level=1, detected_missings=set()):
        """
        Checks that no input key is missing.

        Parameters
        ----------
        dct: dict
            The dictionnary to be checked

        level: int, optional, default=1
            The depth to which we go searching in the nested dictionnaries of parameters.
            Default value is 1 as most of the main parameters are accessed at that depth.

        Returns
        -------
        """
        for k, v in dct.items():
            if k in dct and isinstance(dct[k], dict) and current_level < max_level:
                cls._dict_check(
                    dct[k],
                    current_level=current_level + 1,
                    max_level=max_level,
                    detected_missings=detected_missings,
                )
            elif k in dct and dct[k] is None:
                detected_missings |= {k}

        return detected_missings

    @classmethod
    def _dict_count(cls, dct, non_none_count=0, none_count=0):
        """
        Counts the number of parameters (bottom leaves of the config tree)

        Parameters
        ----------
        dct: dict
            The dictionnary to be checked

        non_none_count: int
            Current counter of non "none" parameters (for recursion)

        none_count: int
            Current counter of "none" parameters (for recursion)

        Returns
        -------
        non_none_count: int

        none_count: int
        """
        for k, v in dct.items():

            if isinstance(dct[k], dict):
                non_none_count, none_count = cls._dict_count(
                    dct[k], non_none_count=non_none_count, none_count=none_count
                )

            elif v is None:
                none_count += 1

            elif v is not None:
                non_none_count += 1

        return non_none_count, none_count

    def __repr__(self):
        n, n_none = self._dict_count(self.params)
        return "general Configuration {} categories, {} non null parameters, {} null.".format(
            len(self.possible_input_categories), n, n_none
        )

    def save(self, save_path=None):
        """
        Saves the merged configuration to a yaml file

        Parameters
        ----------
        save_path: str, optional, default=None
            The path where to save the file. If not provided, it will try saving in path provided in
            params.general["current_working_dir"]
        """
        if save_path is None:
            if "current_working_dir" not in self.general:
                raise Exception(
                    "No save path provided and default save path cannot be found."
                )
            else:
                save_path = self.general["current_working_dir"]

        try:
            save_path = pathlib.Path(save_path)
        except:
            raise Exception("Cannot cast the path to a regular Path object.")

        if not save_path.exists():
            raise Exception("The save_path {} doesn't exist.".format(save_path))

        with open("config.yml", "w") as outfile:
            yaml.dump(self.params, outfile, default_flow_style=False)


def is_git_directory(path="."):
    return (
        subprocess.call(
            ["git", "-C", path, "status"],
            stderr=subprocess.STDOUT,
            stdout=open(os.devnull, "w"),
            shell=True,
        )
        == 0
    )
