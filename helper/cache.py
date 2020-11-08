import logging
from pathlib import Path
import os
import pandas as pd
import warnings
from collections import defaultdict

from config.immo_config import ImmoConfig
from helper.utils import get_latest_in_directory
from helper.file_io import save_pickle, load_pickle

warnings.simplefilter(action="ignore", category=Warning)


class Cache(object):
    """
    Object to manipulate cache
    """

    # There is only one cache instance
    __instance = None
    __initialized = False

    # Always return the same instance
    def __new__(cls, *args, **kwargs):
        if Cache.__instance is None:
            Cache.__instance = object.__new__(cls)
        return Cache.__instance

    def __init__(self, config: ImmoConfig):
        # Initialize it only once
        if not Cache.__initialized:
            Cache.__initialized = True
            self._config = config
            self._log = logging.getLogger(__name__)
            self._to_prod = self._config.cache["cache_to_prod"]
            self._from_prod = self._config.cache["cache_from_prod"]
            self._read_kwargs = self._config.cache["read_kwargs"]
            self._write_kwargs = self._config.cache["write_kwargs"]
            self._cache_dict = defaultdict(dict)

    @property
    def prod_cache_root(self):
        return os.path.join(
            self._config.general["data_root"],
            self._config.cache["root_prod_relative_to_data_root"],
        )

    @property
    def local_cache_root(self):
        return os.path.join(
            Path.home(), self._config.cache["root_local_relative_to_home"]
        )

    def get_from_cache(self, module: str, name: str, extension: str):
        df = self.get_from_cache_dict(module, name)
        if df is not None:
            return df
        else:
            if self.has_cache(module, name, "local") and not self._from_prod:
                self._log.info(f"Retrieving local cache for {module} {name}")
                path = self.make_cache_path(module, name, "local")
                df = self.get_cache_from_path(path, name, extension)
                self._cache_dict[module][name] = df
                return df
            elif self.has_cache(module, name, "prod"):
                self._log.info(f"Retrieving prod cache for {module} {name}")
                path = self.make_cache_path(module, name, "prod")
                df = self.get_cache_from_path(path, name, extension)
                self._cache_dict[module][name] = df
                return df
            else:
                return None

    def get_from_cache_dict(self, module, name):
        if module in self._cache_dict:
            if name in self._cache_dict[module]:
                return self._cache_dict[module][name]
        return None

    def save_to_cache(
        self, module: str, name: str, extension: str, df=pd.DataFrame(), predictor=None
    ):
        if self._to_prod:
            cache_dir = self.make_cache_path(module, name, "prod")
        else:
            cache_dir = self.make_cache_path(module, name, "local")

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        filename = "_".join([name, self._config.general["timestamp"]]) + "." + extension

        full_path = os.path.join(cache_dir, filename)

        if extension == "csv":
            df.to_csv(full_path, **self._write_kwargs.get("csv", {}))
        elif extension in ["xls", "xlsx"]:
            df.to_excel(full_path, **self._write_kwargs.get("xlsx", {}))
        elif extension == "parquet":
            df.to_parquet(full_path, **self._write_kwargs.get("parquet", {}))
        elif extension == "dill":
            save_pickle(predictor, full_path)
        else:
            raise NotImplementedError

        self._log.info(
            f"Cached {name} to {'prod' if self._to_prod else 'local'} under {full_path} "
        )

    def make_cache_path(self, module, name, mode):
        assert mode in ["local", "prod"], f"Invalid cache mode '{mode}'"
        root = self.local_cache_root if mode == "local" else self.prod_cache_root

        return os.path.join(root, module, name)

    def has_cache(self, module: str, name: str, mode: str):

        path = self.make_cache_path(module, name, mode)
        if os.path.exists(path) and len(os.listdir(path)) > 0:
            return True
        return False

    def get_cache_from_path(self, cache_dir, name, extension):
        filename = get_latest_in_directory(path=cache_dir, file_start=name)
        full_path = os.path.join(cache_dir, filename)

        self._log.info(f"Using latest cached {filename}")

        read_kwargs = self._read_kwargs.get(extension, {}).copy()
        if "parse_dates" in read_kwargs:
            date_cols = read_kwargs.pop("parse_dates")
        else:
            date_cols = []

        if extension == "csv":
            df = pd.read_csv(full_path, **read_kwargs)
        elif extension == "xlsx":
            df = pd.read_excel(full_path, **read_kwargs)
        elif extension == "parquet":
            df = pd.read_parquet(full_path, **read_kwargs)
        elif extension == "dill":
            predictor = load_pickle(full_path)
        else:
            raise NotImplementedError

        if extension != "dill":
            for col in set(date_cols).intersection(set(df.columns)):
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    self._log.warning(
                        f"Could not convert column to {col} when reading from cache"
                    )

        if extension == "dill":
            out = predictor
        else:
            out = df

        return out
