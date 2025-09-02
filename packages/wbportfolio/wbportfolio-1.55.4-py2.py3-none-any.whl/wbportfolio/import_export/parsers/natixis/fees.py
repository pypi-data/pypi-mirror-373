import pandas as pd
from pandas.tseries.offsets import BDay

from .utils import file_name_parse_isin

FIELD_MAP = {
    "Date": "fee_date",
    "Manag. Fees Natixis": "ISSUER",
    "Manag. Fees Client": "MANAGEMENT",
    "Perf fees amount": "PERFORMANCE",
    # "Currency": "currency"
}


def parse(import_source):
    # Parse the Parts of the filename into the different parts
    parts = file_name_parse_isin(import_source.file.name)
    # Get the valuation date and investment from the parts list
    product = parts["product"]

    df = pd.read_csv(import_source.file, encoding="utf-8", delimiter=";")
    df = df.rename(columns=FIELD_MAP)
    df = df.drop(columns=df.columns.difference(FIELD_MAP.values()))
    df["fee_date"] = pd.to_datetime(df["fee_date"], dayfirst=True)

    # Switch the weeekend day fees to the next monday
    df["fee_date"] = df["fee_date"].apply(lambda x: x + BDay(1) if x.weekday() in [5, 6] else x)

    # Ensure float columns are number
    for col in ["MANAGEMENT", "ISSUER", "PERFORMANCE"]:
        df[col] = df[col].astype("str").str.replace(" ", "").astype("float")

    # Groupby and sum similar fees (e.g. Monday)
    df = df.groupby("fee_date").sum().reset_index()
    df = pd.melt(
        df,
        id_vars=["fee_date"],
        value_vars=["MANAGEMENT", "ISSUER", "PERFORMANCE"],
        var_name="transaction_subtype",
        value_name="total_value",
    )
    df = df[df["total_value"] != 0]

    df["product"] = [product] * df.shape[0]
    df["fee_date"] = df["fee_date"].dt.strftime("%Y-%m-%d")
    df["calculated"] = False
    df["total_value_gross"] = df["total_value"]
    return {"data": df.to_dict("records")}
