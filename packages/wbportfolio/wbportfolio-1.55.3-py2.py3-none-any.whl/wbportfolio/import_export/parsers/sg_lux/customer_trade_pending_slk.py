import csv
import math
from io import StringIO

import numpy as np
import pandas as pd
from wbfdm.models import InstrumentPrice
from xlrd import xldate_as_datetime

from wbportfolio.models import Product, Register, Trade

from .sylk import SYLK
from .utils import assemble_transaction_reference, get_portfolio_id


def convert_string_to_number(string):
    try:
        return float(string.replace(" ", "").replace(",", ""))
    except ValueError:
        return 0.0


def remove_not_needed_columns(df: pd.DataFrame):
    del df["NORDER"]
    del df["NORDER_EXTERN"]
    del df["REGISTER_ID1"]
    del df["ISIN1"]
    del df["AMOUNT"]
    del df["QUANTITY"]
    del df["AMOUNT_EST_EUR"]
    del df["CODE_OPERATION"]
    del df["TRADE_DATE"]
    del df["VALUE_DATE"]
    del df["REGISTER_DEAL_NAME"]
    del df["REGISTER_ID2"]


def convert_dates(df: pd.DataFrame):
    df["trade_date"] = df["TRADE_DATE"].apply(lambda x: xldate_as_datetime(x, datemode=0).date())
    df["trade_date"] = df["trade_date"].apply(lambda x: x.strftime("%Y-%m-%d"))
    df["value_date"] = df["VALUE_DATE"].apply(lambda x: xldate_as_datetime(x, datemode=0).date())
    df["value_date"] = df["value_date"].apply(lambda x: x.strftime("%Y-%m-%d"))


def map_products_by_isin(df: pd.DataFrame):
    product_mapping = {
        product["isin"]: product["id"]
        for product in Product.objects.filter(isin__in=df["ISIN1"].unique()).values("id", "isin")
    }
    df["underlying_instrument"] = df["ISIN1"].apply(lambda x: product_mapping[x])
    df["portfolio"] = df["underlying_instrument"].apply(lambda x: get_portfolio_id(x))


def map_registers_by_references(df: pd.DataFrame):
    register_mapping = {
        register["register_reference"]: register["id"]
        for register in Register.objects.filter(register_reference__in=df["REGISTER_ID1"].unique()).values(
            "id", "register_reference"
        )
    }
    df["register"] = df["REGISTER_ID1"].apply(lambda x: register_mapping[str(x)])


def get_price(x):
    try:
        estimated_price = float(
            InstrumentPrice.objects.filter(
                instrument=x["underlying_instrument"], calculated=False, date__lte=x["trade_date"]
            )
            .latest("date")
            .net_value
        )
    except InstrumentPrice.DoesNotExist:
        try:
            estimated_price = Product.objects.get(id=x["underlying_instrument"]).issue_price
        except Product.DoesNotExist:
            estimated_price = 100
    return estimated_price


def get_shares(x):
    multiplier = 1 if x["CODE_OPERATION"] == 1 else -1
    if x["QUANTITY"] and not math.isnan(x["QUANTITY"]):
        return round(x["QUANTITY"] * multiplier, 4)

    return round((x["AMOUNT"] * multiplier) / x["price"], 4)


def parse(import_source):
    data = list()

    sylk_handler = SYLK()
    for line in [_line.decode("cp1252") for _line in import_source.file.open("rb").readlines()]:
        sylk_handler.parseline(line)

    buffer = StringIO()
    csvwriter = csv.writer(buffer, quotechar="'", delimiter=";", lineterminator="\n", quoting=csv.QUOTE_ALL)
    for line in sylk_handler.stream_rows():
        csvwriter.writerow(line)

    buffer.seek(0)
    content = buffer.read().replace('""', "")
    df = pd.read_csv(StringIO(content), sep=";", quotechar="'", usecols=[0, 4, 5, 6, 7, 12, 13, 15, 16, 17, 18, 22])
    if not df.empty:
        df["pending"] = True

        df.loc[df["CODE_OPERATION"] == 6, "pending"] = False
        transfers = df.loc[df["CODE_OPERATION"] == 6, :].copy()
        transfers["CODE_OPERATION"] = 2
        transfers["QUANTITY"] = -transfers["QUANTITY"]
        transfers["TRANSFER_REGISTER"] = transfers["REGISTER_ID1"].astype("int").astype("str")
        transfers["REGISTER_ID1"] = transfers["REGISTER_ID2"].astype("int").astype("str")
        transfers["REGISTER_DEAL_NAME"] = transfers["REGISTER_ID1"].apply(
            lambda x: Register.objects.get(register_reference=x).register_name_1
        )

        df = pd.concat([df, transfers], axis=0)

        if "TRANSFER_REGISTER" in df:
            df["TRANSFER_REGISTER"] = df["TRANSFER_REGISTER"].replace(np.nan, "", regex=True)

        convert_dates(df)
        df["NORDER_EXTERN"] = df["NORDER_EXTERN"].replace(np.nan, "", regex=True)
        map_products_by_isin(df)
        df["price"] = df.apply(get_price, axis=1)
        df["shares"] = df.apply(get_shares, axis=1)
        df["transaction_subtype"] = df.shares.apply(
            lambda x: Trade.Type.REDEMPTION.value if x < 0 else Trade.Type.SUBSCRIPTION.value
        )

        df["bank"] = df["REGISTER_DEAL_NAME"]
        df["external_id_alternative"] = df["NORDER"]
        df["register__register_reference"] = df["REGISTER_ID1"]
        df["external_id"] = df.apply(assemble_transaction_reference, axis=1)

        if "TRANSFER_REGISTER" in df:
            del df["TRANSFER_REGISTER"]
        remove_not_needed_columns(df)
        # Convert df to list of dicts
        data = df.rename(columns={"trade_date": "transaction_date"}).to_dict("records")
    return {"data": data}
