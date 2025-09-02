import re
from io import BytesIO

import pandas as pd
from wbfdm.models import Instrument

from wbportfolio.models import Trade

FIELD_MAP = {
    "Trade Date": "book_date",
    "Price": "price",
    "Qty": "shares",
    "Custodian": "bank",
}


def parse(import_source):
    # for extra safety we ensure that passed file satisfy some regex.
    filename_regex = import_source.source.import_parameters.get(
        "customer_trade_filename_regex",
        ".*([A-Z]{2}[A-Z0-9]{9}[0-9]{1})_TransactionList_([0-9]{4}-[0-9]{2}-[0-9]{2})_[0-9]{2}_[0-9]{2}.*.xlsx",
    )
    if match := re.match(filename_regex, import_source.file.name):
        isin = match.group(1)
        max_date = match.group(2)
        df = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl")
        product = Instrument.objects.get(isin=isin)
        if not df.empty:
            df = df.rename(columns=FIELD_MAP)
            df = df.drop(columns=df.columns.difference(FIELD_MAP.values()))
            df["transaction_subtype"] = df.shares.apply(
                lambda x: Trade.Type.REDEMPTION if x < 0 else Trade.Type.SUBSCRIPTION
            )
            df["underlying_instrument"] = product.id
            df["book_date"] = pd.to_datetime(df["book_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
            df["portfolio"] = product.primary_portfolio.id
            df = df.dropna()
            data = df.to_dict("records")
            return {"data": data, "history": {"underlying_instrument": product.id, "book_date": max_date}}
        return {"data": {}}
