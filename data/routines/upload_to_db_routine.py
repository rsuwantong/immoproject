from routine.routine import Routine
from sqlalchemy import create_engine
import psycopg2
from data.data import Data


class EtlUploadDB(Routine):
    """
    Class to proceed to upload ETL to the database
    """

    @property
    def name(self):
        return "etl_to_db"

    def run_routine(self):
        data = Data(self._config, use_cache=True)
        engine = create_engine("postgresql://postgres:Bohr7411@localhost:5432/immoguru")
        agency_fees = data.get("for_filling_agency_fees")
        agency_fees = agency_fees[~agency_fees.price_min.isna()]
        # TODO: Proper log when duplicates
        agency_fees = agency_fees.drop_duplicates()
        agency_fees = agency_fees[
            [
                "agency_code",
                "agency_name",
                "agency_address",
                "postal_code",
                "city",
                "price_min",
                "agency_rate",
                "agency_fee_min_keuros",
            ]
        ]
        agency_fees.rename(columns={"price_min": "price_min_keuros"}, inplace=True)
        agency_fees["price_max_keuros"] = agency_fees.groupby(["agency_code"])[
            "price_min_keuros"
        ].transform(lambda x: x.shift(-1))
        agency_fees = agency_fees[
            [
                "agency_code",
                "agency_name",
                "agency_address",
                "postal_code",
                "city",
                "price_min_keuros",
                "price_max_keuros",
                "agency_rate",
                "agency_fee_min_keuros",
            ]
        ]
        # TODO: remove index
        agency_fees.to_sql("agency_fees", engine)
