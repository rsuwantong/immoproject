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
        df = df.rename(columns={"adresse": "agency_address",
                        "Code Postal": "postal_code",
                        "Ville": "city",
                                "agence_name": "agency_name",
                        "agence_url_0": "agency_url",
                                "tel_1": "telephone",
                        "nb_avis": "num_reviews",
                        "note": "score",
                        "prestations": "services",
                        "reseaux": "network",
                        "teaser-avis": "review_example",
                        "url_pj": "agency_url_pj",
                        "agence_id": "image_code"
                        })

        return df
