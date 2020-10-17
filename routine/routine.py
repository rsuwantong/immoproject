import abc
import logging
import os
import json

from helper.logging import configure_logging
from helper.utils import get_timestamp, json_serial, get_versioned_log_path
from config.immo_config import ImmoConfig


class Routine(metaclass=abc.ABCMeta):
    def __init__(
        self,
        cwd_root: str,
        job_config: dict,
        timestamp: str = None,
        logger: logging.Logger = None,
    ):
        self._log = logger
        self._timestamp = timestamp
        self._initialize(cwd_root, job_config)

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @abc.abstractmethod
    def run_routine(self):
        pass

    def _initialize(self, cwd_root: str, job_config: dict):
        # Make working directory
        cwd = os.path.join(cwd_root, "_".join([self.timestamp, self.name]))
        os.makedirs(cwd, exist_ok=True)

        self._cwd = cwd

        # Save config
        if "general" not in job_config:
            job_config["general"] = dict()
        job_config["general"]["timestamp"] = self.timestamp

        config = ImmoConfig(job_config)

        config_dir = os.path.join(cwd, "config")
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)

        config_fn = os.path.join(
            config_dir, "{}.json".format("_".join(["config", self.timestamp]))
        )
        json.dump(config.params, open(config_fn, "w"), default=json_serial, indent=2)

        self._config = config

        # Configure logger
        if self._log is None:
            log_path, _ = get_versioned_log_path(cwd, "immo", self.timestamp)
            configure_logging(
                logging_level=config.logging["level"],
                filepath=log_path,
                model=self.name,
                timestamp=self.timestamp,
                use_color=False,
            )
            self._log = logging.getLogger(__name__)
        self._log.info("Run intialized!")

    @property
    def timestamp(self):
        if self._timestamp is None:
            self._timestamp = get_timestamp()
        return self._timestamp
