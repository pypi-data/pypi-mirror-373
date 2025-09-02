import operator
from functools import reduce

import numpy as np
import pandas as pd

from wbportfolio.models import Trade

FIELD_MAP = {
    "Transaction_Date": "transaction_date",
    "Trade_Date": "book_date",
    "Value_Date": "value_date",
    "Price": "price",
    "Currency": "currency__key",
    "Portfolio_Identifier": "underlying_instrument__identifier",
    "External_Reference": "external_id_alternative",
    "Booking_Comment": "comment",
}

CUSTOMER_TRADE_ORDER_TYPES = [
    "stex_issue_primary_cnt",
    "stex_buy_secondary_cnt",
    "stex_sell_secondary",
    "sectrx2_rdmpt",
    "stex_sell_secondary_cnt",
]


def parse(import_source):
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=";")
    df = df.loc[
        df["Order_Type"].isin(CUSTOMER_TRADE_ORDER_TYPES),
        :,
    ]
    data = []
    if not df.empty:
        df = df.rename(columns=FIELD_MAP)
        df["shares"] = df["Quantity"] / df["price"]
        df = df.drop(columns=df.columns.difference(FIELD_MAP.values()))
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df["book_date"] = pd.to_datetime(df["book_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df["value_date"] = pd.to_datetime(df["value_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df["transaction_subtype"] = df.shares.apply(
            lambda x: Trade.Type.REDEMPTION if x < 0 else Trade.Type.SUBSCRIPTION
        )
        certificate_keys = import_source.source.import_parameters.get(
            "certificate_keys", ["Index", "Strategic Certificate"]
        )
        df = df.dropna(subset=["underlying_instrument__identifier"])
        df = df[reduce(operator.or_, [df["comment"].str.contains(key, case=False) for key in certificate_keys])]
        df = df.replace([np.inf, -np.inf, np.nan], None)
        df["bank"] = "N/A"
        data = df.to_dict("records")
    return {"data": data}
