import numpy as np
import pandas as pd

from .utils import _get_exchange_from_ticker, _get_ticker, file_name_parse_isin

COLUMN_MAP = {
    "Ticker": "underlying_instrument__ticker",
    "Underlying": "underlying_instrument__name",
    "Underlying ISIN": "underlying_instrument__isin",
    "Div Crncy": "currency__key",
    "Quantity": "shares",
    "Fx Rate": "currency_fx_rate",
    "Retro in%": "retrocession",
    "Gross Div": "price_gross",
    "Ex Div Date": "ex_date",
    "Value Date": "value_date",
}


def parse(import_source):
    parts = file_name_parse_isin(import_source.file.name)
    product_data = parts["product"]

    df = pd.read_csv(import_source.file, sep=";", skipinitialspace=True)
    df = df.rename(columns=COLUMN_MAP).astype("str")

    df["underlying_instrument__exchange"] = df["underlying_instrument__ticker"].apply(
        lambda x: _get_exchange_from_ticker(x)
    )
    df["underlying_instrument__ticker"] = df["underlying_instrument__ticker"].apply(lambda x: _get_ticker(x))
    df["ex_date"] = pd.to_datetime(df["ex_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
    df["value_date"] = pd.to_datetime(df["value_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
    df = df[df["underlying_instrument__isin"].str.contains("([A-Z]{2})([A-Z0-9]{9})([0-9]{1})", regex=True)]
    float_columns = ["shares", "price_gross", "currency_fx_rate", "retrocession"]
    for float_column in float_columns:
        df[float_column] = df[float_column].str.replace(" ", "").astype("float")
    df = df.drop(columns=df.columns.difference(COLUMN_MAP.values()))

    df["retrocession"] = df["retrocession"] / 100.0
    df["portfolio"] = [{"instrument_type": "product", **product_data}] * df.shape[0]
    df = df.replace([np.inf, -np.inf, np.nan], None)
    return {
        "data": df.to_dict("records"),
        "history": {
            "value_date": parts["valuation_date"].strftime("%Y-%m-%d"),
            "product": product_data,
        },
    }
