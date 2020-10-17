import abc
import logging
import os
import pandas as pd
from pathlib import Path


from config.immo_config import ImmoConfig
from helper.cache import Cache
from helper.utils import get_latest_in_directory


class Etl(metaclass=abc.ABCMeta):
    """
    Class to proceee to ETL for a particular dataset
    """

    def __init__(
        self,
        config: ImmoConfig,
        etls: dict,
        use_cache: bool = True,
        cache: Cache = None,
    ):
        self._log = logging.getLogger(__name__)
        self._config = config
        self._use_cache = use_cache
        self._cache_to_prod = self._config.cache["cache_to_prod"]
        self._cache_from_prod = self._config.cache["cache_from_prod"]
        self._etls = etls
        self._processed_data = None
        self._cache = Cache(self._config) if cache is None else cache

        if type(self.layer_id) != int or self.layer_id < 0:
            raise AttributeError("'layer_id' must be a positive integer")

    # ---------------------------------- API methods ----------------------------------------------------------------- #
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Name of the ETL. Must match entry in config.etl
        """
        pass

    @property
    @abc.abstractmethod
    def layer_id(self) -> int:
        """
        What's the layer_id of this ETL ? Must be a positive integer.
        Higher layer_id ETLs should comprise greater complexity, typically:
            0 = Raw data import and basic cleaning (column type, column renaming, etc.)
            1 = Generic data processing, basic merging, etc.
            2 = Business logic, complex source assembling, etc.
        An ETL can only depend on ETLs with a layer_id strictly inferior, eg. a ETL with layer 1 can only
        rely on layer 0 ETLs

        Returns
        -------
        layer: int
            Layer to which the ETL belongs

        """
        pass

    @property
    def df(self) -> pd.DataFrame:
        if self._processed_data is not None:
            return self._processed_data.copy()
        else:
            # Try to get cache
            if self._use_cache:
                self._processed_data = self._cache.get_from_cache(
                    "etl", self.name, "csv"
                )
            # If cache not used or not retrieved
            if self._processed_data is None:
                self._load_process_cache_raw_data()
        return self._processed_data.copy()

    def get(self, etl_name):
        if etl_name not in self._etls:
            raise KeyError(f"Unknown ETL {etl_name}!")
        elif self._etls[etl_name].layer_id >= self.layer_id:
            raise AttributeError(
                f"ETL {self.name} can only depend on ETLs with a layer_id strictly smaller than {self.layer_id}"
            )
        else:
            return self._etls[etl_name].df.copy()

    # ---------------------------------- Private methods ------------------------------------------------------------- #

    @property
    def _data_root(self):
        return self._config.general["data_root"]

    def _load_process_cache_raw_data(self):
        if self.layer_id == 0:
            raw_df = self._load_raw_data()
        else:
            raw_df = None
        self._processed_data = self._process_raw_data(raw_df)

        self._cache.save_to_cache(
            df=self._processed_data, module="etl", name=self.name, extension="csv"
        )

    def _process_raw_data(self, raw_df: pd.DataFrame = None):
        if self.layer_id == 0:
            return raw_df
        else:
            raise NotImplementedError(
                "Method '_process_raw_data' should be implemented for non-raw data ETLs"
            )

    def _load_raw_data(self):
        read_params = self._config.raw_data[self.name]
        self._log.info(
            f"Loading raw data for '{self.name}' from {read_params['location']}"
        )
        if read_params["format"] == "csv":
            return pd.read_csv(
                os.path.join(
                    self._data_root, read_params["location"], read_params["filename"]
                ),
                **read_params["read_kwargs"],
            )
        elif read_params["format"] in ["xls", "xlsx"]:
            return pd.read_excel(
                os.path.join(
                    self._data_root, read_params["location"], read_params["filename"]
                ),
                **read_params["read_kwargs"],
            )
        elif read_params["format"] == "parquet":
            return pd.read_parquet(
                os.path.join(
                    self._data_root, read_params["location"], read_params["filename"]
                ),
                **read_params["read_kwargs"],
            )
        else:
            raise NotImplementedError

    def update_cache_after_manual_overlay(self):
        df = self.df.copy()
        df_overlaid = self._apply_manual_overlay(df)
        self._processed_data = df_overlaid
        self._cache.save_to_cache(
            df=self._processed_data, module="etl", name=self.name, extension="csv"
        )

    def _apply_manual_overlay(self, df: pd.DataFrame):
        """
        Method to overload to define how manual input should be overlaid on base df

        Parameters
        ----------
        df: pd.DataFrame
            Base df

        Returns
        -------
        pd.DataFrame
            Df overlaid with manual input
        """
        raise NotImplementedError(f"No overlay strategy defined for ETL {self.name}")

    def _get_manual_overlay_file(self):
        manual_df_dir = os.path.join(
            self._data_root, self._config.manual_overlay["location"], self.name
        )
        manual_df_filename = get_latest_in_directory(
            manual_df_dir, "manual_" + self.name
        )

        manual_df = pd.read_csv(
            os.path.join(manual_df_dir, manual_df_filename),
            **self._config.manual_overlay["read_kwargs"],
        )

        return manual_df
