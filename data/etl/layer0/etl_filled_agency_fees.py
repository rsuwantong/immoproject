import pandas as pd

from data.etl.etl import Etl


class EtlFilledAgencyFees(Etl):
    """
    ETL to load filled agency fees
    """

    @property
    def name(self):
        return "filled_agency_fees"

    @property
    def layer_id(self):
        return 0

    def _process_raw_data(self, raw_df: pd.DataFrame = None):
        df = raw_df

        return df
