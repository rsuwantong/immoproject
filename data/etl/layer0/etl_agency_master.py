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

    def _process_raw_data(self, df: pd.DataFrame = None):
        df = df.rename({"adresse": "agency_address",
                        "Code Postal": "postal_code",
                        "Ville": "city",
                        "agence_url": "agency_url",
                        "nb_avis": "num_reviews",
                        "note": "score",
                        "Prestations": "services",
                        "Reseaux": "network",
                        "teaser-avis": "review_example",
                        "agences_urls": "agency_url_pj"
                        }, inplace=True)

        return df
