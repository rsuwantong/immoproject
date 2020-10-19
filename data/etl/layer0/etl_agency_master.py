import pandas as pd
import os

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

        list_postal_code = df.postal_code.unique()
        for c in list_postal_code:
            # Make folder to save outputs if not existed
            if not os.path.exists(
                    os.path.join(
                        "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                        "02_agency_fees",
                        "agency_master",
                        str(c),
                    )
            ):
                os.makedirs(
                    os.path.join(
                        "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                        "02_agency_fees",
                        "agency_master",
                        str(c),
                    )
                )

            df_postal_code = df[df.postal_code == c]
            df_postal_code.to_csv(
                os.path.join(
                    "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                    "02_agency_fees",
                    "agency_master",
                    str(c),
                    self._config.general["timestamp"] + "_"
                                                        "agency_master_" + str(c) + ".csv",
                ),
                index=False,
            )

        return df
