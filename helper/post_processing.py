import logging
import pandas as pd


log = logging.getLogger(__name__)


def calendar_post_processing(config, calendar: pd.DataFrame):
    outputs = dict()
    if not config.calendar_generation["include_competition"]:
        chessboard = _calendar_to_chessboard(config, calendar, sku_level=False)
        outputs["raw_results"] = _format_according_to_template(
            calendar, config.templates.get("raw_results", None)
        )
        outputs["chessboard_ppgs"] = _format_according_to_template(
            chessboard, config.templates.get("chessboard", None)
        )

    else:
        reverse_map = dict(
            zip(
                config.competitors["manufacturer_map"].values(),
                config.competitors["manufacturer_map"].keys(),
            )
        )
        pd_dict = dict(zip(range(6), [pd.DataFrame()] * 6))
        for manufac_id in set(config.competitors["manufacturer_map"].values()):
            log.info(f"Now getting calendar for {reverse_map[manufac_id]}")
            calendar_per_manuf = calendar.query(
                f"{config.c_manufacturer} == @manufac_id"
            )
            chessboard_per_manuf = _calendar_to_chessboard(
                config, calendar_per_manuf, sku_level=False
            )

            for i, df, template in zip(
                range(2),
                [calendar_per_manuf, chessboard_per_manuf],
                ["raw_results", "chessboard"],
            ):
                manufac_df = _format_according_to_template(
                    df, config.templates.get(template, None)
                )
                manufac_df[config.c_manufacturer] = reverse_map[manufac_id]
                pd_dict[i] = pd_dict[i].append(manufac_df).reset_index(drop=True)

        for idx, filename in zip(pd_dict.keys(), ["raw_results", "chessboard_ppgs"]):
            outputs[filename] = pd_dict[idx]

    return outputs


def _format_according_to_template(df: pd.DataFrame, template_cols: list = None):
    """
    Parameters
    ----------
    df: pd.DataFrame
        DF to be formatted according to template
    template_cols: list
        List of columns representing column template

    Returns
    -------
    pd.DataFrame:
        DF formatted according to template
    """
    if template_cols is None:
        return df

    initial_cols = df.columns

    absent_cols = set(template_cols) - set(initial_cols)
    if absent_cols:
        log.warning(
            f"Cols {absent_cols} are absent from template. They will be ignored"
        )

    diff_cols = set(initial_cols) - set(template_cols)
    final_cols = [c for c in template_cols if c in initial_cols] + sorted(
        list(diff_cols)
    )

    return df[final_cols]


def _calendar_to_chessboard(config, sku_weeks, sku_level=False):
    """
    Turns a raw calendar into a chessboard

    Parameters
    ----------
    config: ImmoConfig
        Config object
    sku_weeks: pd.DataFrame
        DF to converto to chessboard
    sku_level: bool, optional
        Should chessboard be prodced at SKU level

    Returns
    -------
    pd.DataFrame
        Chessboard DF
    """

    sku_identifiers = ["promo_group", config.c_uon]
    if sku_level:
        sku_identifiers.append(config.c_sku_id)

    sku_weeks = sku_weeks[
        sku_identifiers
        + [
            config.c_time,
            "m6_must_buy_qty",
            "m6_nominal_depth",
            "promo_key",
            "m6_promo_duration",
            "edv_mb",
            "edv_mb_price",
        ]
    ].drop_duplicates()

    sku_weeks["promo_description"] = (
        "id: "
        + sku_weeks["promo_key"].map(str)
        + " MB: "
        + sku_weeks["m6_must_buy_qty"].map(str)
        + " D: "
        + sku_weeks["m6_nominal_depth"].map(str)
        + " EDV_MB: "
        + sku_weeks["edv_mb"].astype(str)
        + " EDV_Price: "
        + sku_weeks["edv_mb_price"].astype(str)
    )

    # Erase promo description for non promo weeks
    sku_weeks.loc[(sku_weeks["promo_key"] < 0), "promo_description"] = ""
    results_wide = sku_weeks.pivot_table(
        values="promo_description",
        index=sku_identifiers,
        columns="predict_dt",
        aggfunc=lambda x: " ".join(x),
    ).fillna("")

    return results_wide.reset_index()
