import pandas as pd
import os
from data.etl.etl import Etl
import numpy as np


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
        num_agencies_duplicated = (
            agencies.shape[0]
            - agencies[["agency_name", "agency_address"]].drop_duplicates().shape[0]
        )
        if num_agencies_duplicated != 0:
            self._log.warning(
                f"There are {num_agencies_duplicated} duplicated agencies in agency master."
            )
            agencies.loc[
                (agencies.agency_url == "")
                | (agencies.agency_url == "Rejoignez nous sur Facebook"),
                "agency_url",
            ] = np.nan
            agencies = (
                agencies.sort_values(
                    ["agency_name", "agency_address", "agency_url", "agency_url_pj"],
                    ascending=False,
                )
                .groupby(["agency_name", "agency_address"])
                .head(1)
            )

        self._log.info(f"There are {agencies.shape[0]} agencies in agency master.")

        fees = self.get("filled_agency_fees")
        self._log.info(
            f"There are {fees[['agency_name', 'agency_address']].drop_duplicates().shape[0]} agencies in filled fees."
        )
        # Get information from agency master for fees
        fees = fees.merge(
            agencies,
            on=[
                "agency_name",
                "agency_address",
                "postal_code",
                "city",
                "agency_url_pj",
            ],
            how="left",
        )
        ## Identify new agencies not in fees
        list_agencies_in_fees = fees[
            ["agency_name", "agency_address"]
        ].drop_duplicates()
        list_agencies_in_agency_master = agencies[["agency_name", "agency_address"]]
        list_new_agencies = list_agencies_in_agency_master.merge(
            list_agencies_in_fees, how="outer", indicator=True
        ).query('_merge=="left_only"')
        list_new_agencies.drop(columns="_merge", inplace=True)
        new_agencies_info = agencies.merge(
            list_new_agencies, on=["agency_name", "agency_address"]
        )
        self._log.info(f"There are {list_new_agencies.shape[0]} new agencies.")

        new_agencies_info = pd.concat([new_agencies_info] * 10)

        df = fees.merge(new_agencies_info, how="outer")
        num_agencies_final = (
            df[["agency_name", "agency_address"]].drop_duplicates().shape[0]
        )

        self._log.info(
            f"There are {num_agencies_final} agencies in for-filling agency fees."
        )

        # Compute agency_code
        df_for_agency_code = df[
            ["agency_name", "agency_address", "postal_code"]
        ].drop_duplicates()
        df_for_agency_code["pre_agency_code"] = [
            str(x).zfill(4)
            for x in df_for_agency_code.groupby(["postal_code"]).cumcount() + 1
        ]
        df_for_agency_code["agency_code"] = (
            df_for_agency_code["postal_code"].astype(str)
            + df_for_agency_code["pre_agency_code"]
        )
        df_for_agency_code.drop(
            columns=["pre_agency_code", "postal_code"], inplace=True
        )

        # Merge agency_code to main dataframe
        df = df.merge(df_for_agency_code, on=["agency_name", "agency_address"])

        df.loc[
            (df.agency_url == "") | (df.agency_url == "Rejoignez nous sur Facebook"),
            "agency_url",
        ] = np.nan
        df["agency_url"].fillna(df["agency_url_pj"], inplace=True)

        df["count"] = 0.1
        df["hyperlink_url"] = ""

        df = df[
            [
                "count",
                "comment",
                "is_non-standard",
                "is_agency",
                "tarif_dispo-web",
                "agency_code",
                "agency_name",
                "agency_address",
                "postal_code",
                "city",
                "price_min",
                "agency_rate",
                "agency_fee_min_keuros",
                "hyperlink_url",
                "agency_url",
                "agency_url_pj",
                "telephone",
                "image_url",
                "num_reviews",
                "score",
                "services",
                "network",
                "review_example",
                "image_code",
            ]
        ]

        # df.to_excel(
        #     os.path.join(
        #         "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
        #         "02_agency_fees",
        #         "for_filling",
        #         self._config.general["timestamp"]+"_"
        #         "for_filling_agencie_fees"
        #         + ".xlsx",
        #     ),
        #     index=False,
        # )

        list_postal_code = df.postal_code.unique()
        for c in list_postal_code:
            # Make folder to save outputs if not existed
            if not os.path.exists(
                os.path.join(
                    "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                    "02_agency_fees",
                    "for_filling",
                    str(c),
                )
            ):
                os.makedirs(
                    os.path.join(
                        "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                        "02_agency_fees",
                        "for_filling",
                        str(c),
                    )
                )

            df_postal_code = df[df.postal_code == c]
            df_postal_code.to_excel(
                os.path.join(
                    "/Users/jacquemart rata/Documents/04_PERSO/Immo/00_data",
                    "02_agency_fees",
                    "for_filling",
                    str(c),
                    self._config.general["timestamp"] + "_"
                    "for_filling_agencie_fees_" + str(c) + ".xlsx",
                ),
                index=False,
            )

        return df
