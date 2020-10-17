import logging

from config.immo_config import ImmoConfig
from helper.cache import Cache

# Layer 0 (raw data import)
from data.etl.layer0.etl_agency_master import EtlAgencyMaster
from data.etl.layer0.etl_filled_agency_fees import EtlFilledAgencyFees

class Data(object):
    """
    Class to provide a unified interface to retrieve data
    """

    # Lists the ETLs
    etls_classes = {
        # Layer 0
        "agency_master": EtlAgencyMaster,
        "filled_agency_fees": EtlFilledAgencyFees
        # Layer 1
    }

    def __init__(self, config: ImmoConfig, use_cache: bool = True):
        self._log = logging.getLogger(__name__)
        self._config = config
        self._etls = {}
        self._cache = Cache(config=config)
        for etl_name, etl_class in self.etls_classes.items():
            self._etls[etl_name] = self.etls_classes[etl_name](
                config=self._config,
                use_cache=use_cache,
                etls=self._etls,
                cache=self._cache,
            )

    def get(self, etl_name: str):
        self.check_etl(etl_name)
        return self._etls[etl_name].df

    def check_etl(self, etl_name: str):
        assert etl_name in self._etls, f"No ETL named {etl_name}"

    def update_etls(self):
        for etl_name in set(self._etls.keys()).difference(
            set(self._config.no_update_etls)
        ):
            self.update_etl(etl_name)

    def update_etl(self, etl_name: str):
        self.check_etl(etl_name)
        self._etls[etl_name]._load_process_cache_raw_data()
