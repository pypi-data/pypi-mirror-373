import numpy as np
import pandas as pd

from .utils import _get_underlying_instrument, file_name_parse_isin

FIELD_MAP = {
    "Close": "initial_price",
    "Nb of shares": "initial_shares",
    "Fx Rate": "initial_currency_fx_rate",
    "Valuation Date": "asset_valuation_date",
    "Quoted Crncy": "currency__key",
    "exchange": "exchange",
    "underlying_quote": "underlying_quote",
}


def _apply_adjusting_factor(row):
    """
    If the position is a product position, then the adjusting factor adjusts the shares otherwise, it adjusts the price.

    No idea why though
    """
    if row["underlying_quote"]["instrument_type"] == "product":
        return pd.Series([row["initial_price"], row["initial_shares"] * row["Quotity/Adj. factor"]])
    else:
        return pd.Series([row["initial_price"] * row["Quotity/Adj. factor"], row["initial_shares"]])


def parse(import_source):
    # Parse the Parts of the filename into the different parts
    parts = file_name_parse_isin(import_source.file.name)

    # Get the valuation date and investment from the parts list
    valuation_date = parts["valuation_date"]
    product_data = parts["product"]

    # Load file into a CSV DictReader
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=";")
    df = df.rename(columns=FIELD_MAP)
    df = df.dropna(subset=["initial_price"])
    df["initial_price"] = df["initial_price"].astype("str").str.replace(" ", "").astype("float")
    df["underlying_quote"] = df[["Ticker", "Name", "currency__key"]].apply(
        lambda x: _get_underlying_instrument(*x), axis=1
    )
    df["initial_price"] = df["initial_price"].replace(0, np.nan).fillna(1.0)
    df[["initial_price", "initial_shares"]] = df[
        ["initial_price", "initial_shares", "Quotity/Adj. factor", "underlying_quote"]
    ].apply(lambda x: _apply_adjusting_factor(x), axis=1)
    df["exchange"] = df.underlying_quote.apply(lambda x: x.get("exchange", None))
    df = df.drop(columns=df.columns.difference(FIELD_MAP.values()))

    df["portfolio__instrument_type"] = "product"
    df["portfolio__isin"] = product_data["isin"]
    df["is_estimated"] = False
    df["date"] = valuation_date.strftime("%Y-%m-%d")
    df["asset_valuation_date"] = pd.to_datetime(df["asset_valuation_date"], dayfirst=True).dt.strftime("%Y-%m-%d")

    df["weighting"] = df.initial_currency_fx_rate * df.initial_price * df.initial_shares
    df["weighting"] = df.weighting / df.weighting.sum()
    return {"data": df.to_dict("records")}
