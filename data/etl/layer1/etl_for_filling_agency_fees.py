import pandas as pd
import os
from routine.routine import Routine
from data.etl.etl import Etl


class EtlForFillingAgencyFees(Etl):
    """
    ETL to load agency master
    """

    @property
    def name(self):
        return "for_filling_agency_fees"

    @property
    def layer_id(self):
        return 1

    def _process_raw_data(self, raw_df: pd.DataFrame = None):
        agencies = self.get("agency_master")
        num_agencies_duplicated = agencies.shape[0]-agencies[["agency_name", "agency_address"]].drop_duplicates().shape[0]
        if num_agencies_duplicated != 0:
            self._log.warning(
                f"There are {num_agencies_duplicated} duplicated agencies in agency master."
            )
            agencies = agencies.drop_duplicates()

        self._log.info(f"There are {agencies.shape[0]} agencies in agency master.")


        fees = self.get("filled_agency_fees")
        self._log.info(f"There are {fees[['agency_name', 'agency_address']].drop_duplicates().shape[0]} agencies in filled fees.")

        list_agencies_in_fees = fees[["agency_name", "agency_address"]].drop_duplicates()
        list_agencies_in_agency_master = agencies[["agency_name", "agency_address"]]
        list_new_agencies = list_agencies_in_agency_master.merge(list_agencies_in_fees,  how="outer", indicator=True).query('_merge=="left_only"')
        list_new_agencies.drop(columns="_merge", inplace=True)
        new_agencies_info = agencies.merge(list_new_agencies, on=["agency_name", "agency_address"])
        self._log.info(
            f"There are {list_new_agencies.shape[0]} new agencies.")

        new_agencies_info = pd.concat([new_agencies_info]*10)

        df = fees.merge(new_agencies_info, on=["agency_name", "agency_address"], how="outer")
        num_agencies_final = df[['agency_name', 'agency_address']].drop_duplicates().shape[0]

        self._log.info(
            f"There are {num_agencies_final} agencies in for-filling agency fees.")

        df.to_excel(
                os.path.join(
                    "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                    "02_agency_fees",
                    "for_filling",
                    "for_filling_agencie_fees_"+self._config.general["timestamp"]+".xlsx",
                ),
                index=False,
            )

        list_postal_code = df.postal_code.unique()
        for c in range(0, len(list_postal_code)):

            # Make folder to save outputs if not existed
            if not os.path.exists(os.path.join(self._cwd, "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                    "02_agency_fees",
                    "for_filling",c)):
                os.makedirs(os.path.join(self._cwd, "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                    "02_agency_fees",
                    "for_filling",c))

            df_postal_code = df[df.postal_code==c]
            df_postal_code.to_excel(
                os.path.join(
                    "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                    "02_agency_fees",
                    "for_filling",c,
                    "for_filling_agencie_fees_" +c +"_"+ self._config.general["timestamp"] + ".xlsx",
                ),
                index=False,
            )

        return df
