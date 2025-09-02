import re
from io import BytesIO

import numpy as np
import pandas as pd

from wbportfolio.models import Product


def file_name_parse(file_name):
    isin = re.findall("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})", file_name)

    assert len(isin) == 1, "Not exactly 1 isin found in the filename"

    return {"isin": isin[0]}


# TODO: finish it
_fields_map = {
    "underlying_instrument": "underlying_instrument",
    "transaction_subtype": "transaction_subtype",
    "DATE": "transaction_date",
    "INSTRUMENT CCY": "currency__key",
    "TOTAL QUANTITY": "shares",
    "GROSS PRICE": "price_gross",
    "NET PRICE": "price",
    "currency_fx_rate": "currency_fx_rate",
    "NET AMOUNT": "total_value",
    "N°": "external_id",
}


def parse(import_source):
    data = list()
    parts = file_name_parse(import_source.file.name)
    product = Product.objects.get(isin=parts["isin"])

    df = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl", sheet_name="Transactions")

    def _get_exchange(identifier):
        ticker, exchange, _ = identifier.split(" ")
        if exchange:
            return {"bbg_exchange_codes": exchange}

    def _get_underlying_instrument(row):
        if row["EVENT"] == "AMC CASH":
            return product.id
        else:
            ticker, exchange, _ = row["IDENTIFIER"].split(" ")
            return {
                "ticker": ticker,
                "exchange": {"bbg_exchange_codes": exchange},
                "name": row["NAME"],
                "currency__key": row["currency__key"],
                "instrument_type": "equity",
            }

    xx, yy = np.where(df == "N°")
    df = df.iloc[xx[0] :, yy[0] :]
    df = df.rename(columns=df.iloc[0]).drop(df.index[0]).dropna(how="all")
    df["transaction_subtype"] = None
    df = df.rename(columns={"INSTRUMENT CCY  ": "INSTRUMENT CCY"})
    df = df.rename(columns=_fields_map)

    df["transaction_date"] = pd.to_datetime(df["transaction_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
    df["shares"] = -1 * df["shares"]

    df.loc[(df["EVENT"] == "BUY") & (df["ASSET CLASS"] == "SHARE"), "transaction_subtype"] = "BUY"
    df.loc[(df["EVENT"] == "SELL") & (df["ASSET CLASS"] == "SHARE"), "transaction_subtype"] = "SELL"
    df.loc[(df["EVENT"] == "AMC CASH") & (df["shares"] < 0), "transaction_subtype"] = "REDEMPTION"
    df.loc[(df["EVENT"] == "AMC CASH") & (df["shares"] > 0), "transaction_subtype"] = "SUBSCRIPTION"

    df = df[df["transaction_subtype"].notnull()]
    df["underlying_instrument"] = df.apply(lambda x: _get_underlying_instrument(x), axis=1)
    df["exchange"] = df["IDENTIFIER"].apply(lambda x: _get_exchange(x))
    df["currency_fx_rate"] = df["BOOKING FX"] * df["BASE CCY FX"]

    df = df.drop(df.columns.difference(_fields_map.values()), axis=1)
    df["portfolio"] = product.primary_portfolio.id

    customer_trade_index_mask = (df["transaction_subtype"] == "REDEMPTION") | (
        df["transaction_subtype"] == "SUBSCRIPTION"
    )
    df.loc[customer_trade_index_mask, "shares"] = df.loc[customer_trade_index_mask, "shares"] / product.share_price
    for field in ["price", "price_gross"]:
        df.loc[customer_trade_index_mask, field] = df.loc[customer_trade_index_mask, field] * product.share_price
    df["bank"] = "Leonteq Cash Transfer"
    data = df.to_dict("records")

    return {"data": data}
