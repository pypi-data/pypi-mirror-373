import datetime
import re
from contextlib import suppress

import numpy as np
import pandas as pd

from wbportfolio.models import ProductGroup


def file_name_parse(file_name):
    dates = re.findall(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", file_name)
    isin = re.findall(r"\.([a-zA-Z0-9]*)_", file_name)

    assert len(dates) == 2, "Not 2 dates found in the filename"
    assert len(isin) == 1, "Not exactly 1 isin found in the filename"

    return {
        "isin": isin[0],
        "valuation_date": datetime.datetime.strptime(dates[0], "%Y-%m-%d").date(),
        "generation_date": datetime.datetime.strptime(dates[1], "%Y-%m-%d").date(),
    }


def get_exchange(row):
    if str(row["Asset type code"]) == "VMOB" and row["Bloom Ticker"]:
        with suppress(ValueError):
            [_, exchange] = str(row["Bloom Ticker"]).replace(" Equity", "").replace(" EQUITY", "").split(" ")
            return {"bbg_exchange_codes": exchange}
    return None


def get_underlying_quote(row):
    if str(row["Asset type code"]) == "VMOB":
        data = {
            "instrument_type": "equity",
            "currency__key": row["currency__key"],
            "isin": row["Asset Code"] or row["Security code"],
            "name": row["Asset description"],
        }
        if bloomberg_ticker := row.get("Bloom Ticker", None):
            tickers = str(bloomberg_ticker).replace(" Equity", "").replace(" EQUITY", "").split(" ")
            if len(tickers) > 0:
                data["ticker"] = tickers[0]
            if len(tickers) > 1:
                data["exchange"] = {"bbg_exchange_codes": tickers[1]}
        return data
    return None


def parse(import_source):
    # Load file into a CSV DictReader and convert the encoding to latin1 due to hyphonation
    csv_file = import_source.file.open()
    # csv_file = codecs.iterdecode(csv_file, "latin1")

    cols = [0, 2, 4, 6, 7, 8, 10, 13, 27, 28, 64, 67]

    df = pd.read_csv(csv_file, encoding="latin1", usecols=cols)
    df = df.replace([np.inf, -np.inf, np.nan], None)
    columns_map = {
        "Code": "portfolio",
        "underlying_quote": "underlying_quote",
        "exchange__bbg_exchange_codes": "exchange__bbg_exchange_codes",
        "NAV Date": "date",
        "Quantity / Amount": "initial_shares",
        "Price": "initial_price",
        "Ccy": "currency__key",
        "FX Rate": "initial_currency_fx_rate",
        "asset_valuation_date": "asset_valuation_date",
    }
    df = df.rename(columns=columns_map)
    # Substitute the Code for the ProductGroup ID
    product_group_mapping = {
        product_group.identifier: product_group.id
        for product_group in ProductGroup.objects.filter(identifier__in=df["portfolio"].unique())
    }

    df["date"] = df["date"].apply(lambda x: x.replace("/", "-"))
    df["initial_currency_fx_rate"] = df["initial_currency_fx_rate"].apply(lambda x: 1 / x if x else 1).round(14)

    cash_mask = df["Accounting category"].isin(["T111"])
    cash = (
        df.loc[
            cash_mask,
            ["currency__key", "initial_currency_fx_rate", "portfolio", "date", "initial_price", "initial_shares"],
        ]
        .groupby(
            [
                "currency__key",
                "portfolio",
                "date",
            ]
        )
        .agg(
            {
                "initial_currency_fx_rate": "mean",
                "initial_price": "mean",
                "initial_shares": "sum",
            }
        )
        .reset_index()
    ).copy()
    cash["underlying_quote"] = cash["currency__key"].apply(lambda x: {"currency__key": x, "instrument_type": "cash"})

    # cash_equivalents_mask, all asset type code that match TRES and which don't have accounting category T111
    cash_equivalents_mask = df["Asset type code"].str.match("TRES") & ~df["Accounting category"].str.match("T111")

    cash_equivalents = (
        df.loc[
            cash_equivalents_mask,
            ["currency__key", "initial_currency_fx_rate", "portfolio", "date", "initial_price", "initial_shares"],
        ]
        .groupby(
            [
                "currency__key",
                "portfolio",
                "date",
            ]
        )
        .agg(
            {
                "initial_currency_fx_rate": "mean",
                "initial_price": "mean",
                "initial_shares": "sum",
            }
        )
        .reset_index()
    ).copy()
    cash_equivalents["underlying_quote"] = cash_equivalents["currency__key"].apply(
        lambda x: {"currency__key": x, "instrument_type": "cash_equivalent"}
    )

    # equities = df.loc[df["Accounting category"].str.match("010"), :].copy() # Historically, we filter out equity base on the "accounting category" that matches "010", we had issue with equity having the code "020". We decided to use the column "Asset type code" and filter out with the code "VCOM"
    equities = df.loc[df["Asset type code"].str.match("VMOB"), :].copy()
    if not equities.empty:
        equities["underlying_quote"] = equities.apply(lambda x: get_underlying_quote(x), axis=1)
        equities["exchange"] = equities.apply(lambda x: get_exchange(x), axis=1)
        del equities["Accounting category"]
        del equities["Asset type code"]
        del equities["Bloom Ticker"]
        del equities["Asset description"]
    df = pd.concat([cash, equities, cash_equivalents])

    df["asset_valuation_date"] = df["date"]
    # Rename the columns

    df = df.drop(df.columns.difference(columns_map.values()), axis=1)

    df["is_estimated"] = False
    df = df.replace([np.inf, -np.inf, np.nan], None)
    df = df[df["underlying_quote"].notnull()]

    df["weighting"] = df.initial_currency_fx_rate * df.initial_price * df.initial_shares
    portfolio_weights = df.groupby("portfolio")["weighting"].sum()
    df["weighting"] = df.apply(lambda x: x["weighting"] / portfolio_weights.loc[x["portfolio"]], axis=1)
    df["portfolio"] = df["portfolio"].apply(
        lambda x: {"id": product_group_mapping[str(x)], "instrument_type": "product_group"}
    )
    csv_file.close()
    return {"data": df.to_dict("records")}
