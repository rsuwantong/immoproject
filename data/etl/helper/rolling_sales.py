import pandas as pd


def func_mean(x, num_weeks):
    return x.rolling(num_weeks, min_periods=1).mean()


def compute_rolling_sales(
    df,
    cols_to_groupby=["sku_id", "mrkt_id"],
    col_date=["start_promo_week"],
    choice_num_weeks_rolling_sales={
        "16_weeks": 16,
        "20_weeks": 20,
        "24_weeks": 24,
        "28_weeks": 28,
    },
    agg_col_name="",
):

    sales = df[cols_to_groupby + ["sales", "units"] + col_date]

    # Add date information for weeks we do not have sales - for rolling sales computation
    key_cols = sales[cols_to_groupby].drop_duplicates()

    date_cols = pd.DataFrame()
    for i, m in enumerate(sales.mrkt_id.unique()):
        date_cols_m = sales[col_date].drop_duplicates()
        date_cols_m["mrkt_id"] = m
        date_cols = date_cols.append(date_cols_m)

    key_cols = key_cols.merge(date_cols, on=["mrkt_id"], how="outer")
    sales = key_cols.merge(sales, on=cols_to_groupby + col_date, how="outer")
    sales[["units", "sales"]] = sales[["units", "sales"]].fillna(0)

    rolling_sales = pd.DataFrame()

    for i, w in enumerate(list(choice_num_weeks_rolling_sales.keys())):

        sales_by_groupby_key = (
            sales.groupby(cols_to_groupby + col_date)["sales", "units"]
            .sum()
            .reset_index()
        )

        sales_by_groupby_key["av_sales" + agg_col_name + "_" + w] = (
            sales_by_groupby_key.sort_values(cols_to_groupby + col_date)
            .groupby(cols_to_groupby)["sales"]
            .transform(func_mean, choice_num_weeks_rolling_sales[w])
        )
        sales_by_groupby_key["av_units" + agg_col_name + "_" + w] = (
            sales_by_groupby_key.sort_values(cols_to_groupby + col_date)
            .groupby(cols_to_groupby)["units"]
            .transform(func_mean, choice_num_weeks_rolling_sales[w])
        )

        rolling_sales_by_term = sales_by_groupby_key[
            cols_to_groupby
            + col_date
            + ["av_units" + agg_col_name + "_" + w, "av_sales" + agg_col_name + "_" + w]
        ]

        if i == 0:
            rolling_sales = rolling_sales_by_term
        else:
            rolling_sales = rolling_sales.merge(
                rolling_sales_by_term, on=cols_to_groupby + col_date
            )

    return rolling_sales
