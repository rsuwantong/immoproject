import pandas as pd
import datetime as dt

from data.etl.etl import Etl


class EtlAgencyMaster(Etl):
    """
    ETL to load agency master
    """

    @property
    def name(self):
        return "agency_master"

    @property
    def layer_id(self):
        return 0

    def _process_raw_data(self, raw_df: pd.DataFrame = None):
        df = raw_df

        return df
