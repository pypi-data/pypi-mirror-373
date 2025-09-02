import numpy as np
import pandas as pd

from .utils import get_perf_fee_isin

FIELD_MAP = {
    "EndOfDay": "date",
    "LastPriceDate": "asset_valuation_date",
    "LastPrice": "initial_price",
    "Quantity": "initial_shares",
    "TradingCurrency": "currency__key",
    "FxRate": "initial_currency_fx_rate",
    "ISIN": "underlying_quote__isin",
    "InstrumentName": "underlying_quote__name",
    "BuCurrency": "portfolio__currency__key",
    "Ticker": "underlying_quote__ticker",
    # "TradingPlace": "exchange",
    "Booking_comment": "comment",
    "AssetGroup": "underlying_quote__instrument_type",
    "InstrumentIdentifier": "underlying_quote__identifier",
    "#ClientName": "portfolio__identifier",
}

ASSET_GROUP_MAP = {
    "bond": "bond",
    "cash": "cash",
    "comdty": "commodity",
    "credit": "credit",
    "fund": "exchange_trade_product",
    "fut": "future",
    "fwd": "forward",
    "idx": "index",
    "insurpol": "insurpol",
    "interrateopt": "interest_rate_derivative",
    "limit": "limit",
    "opt": "option",
    "struct": "product",
    "swap": "swap",
    "cash_equivalent": "cash_equivalent",
}


def parse(import_source):
    perf_fee_isin = get_perf_fee_isin(import_source.source)
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=";")
    df = df.rename(columns=FIELD_MAP).replace([np.inf, -np.inf, np.nan], None)
    df = df.drop(columns=df.columns.difference(FIELD_MAP.values()))
    if import_source.source.import_parameters.get("import_perf_fees_as_cash", False):
        fees_idx = df["underlying_quote__isin"] == perf_fee_isin
        df.loc[fees_idx, "underlying_quote__isin"] = None
        df.loc[fees_idx, "underlying_quote__instrument_type"] = "cash_equivalent"
        df.loc[fees_idx, "initial_shares"] = df.loc[fees_idx, "initial_price"]  # inverse price and share
    else:
        df = df.loc[df["underlying_quote__isin"] != perf_fee_isin, :]

    df["underlying_quote__instrument_type"] = df["underlying_quote__instrument_type"].apply(
        lambda x: ASSET_GROUP_MAP[x] if x else None
    )
    # we remove instrument without isin or not of type cash because we don't support these (e.g, Dividend)
    df = df[
        ~df["underlying_quote__isin"].isnull()
        | df["underlying_quote__instrument_type"].isin(["cash", "cash_equivalent"])
    ]

    # we group by instrument identifier to be sure we don't introduce duplicated position
    df = (
        df.groupby("underlying_quote__identifier", dropna=False)
        .agg(
            {
                "initial_currency_fx_rate": "first",
                "initial_price": "first",
                "initial_shares": "sum",
                "date": "first",
                "asset_valuation_date": "first",
                "currency__key": "first",
                "underlying_quote__isin": "first",
                "underlying_quote__name": "first",
                "portfolio__currency__key": "first",
                "underlying_quote__ticker": "first",
                "underlying_quote__instrument_type": "first",
                "portfolio__identifier": "first",
            }
        )
        .reset_index(drop=True)
    )
    df.loc[df["underlying_quote__instrument_type"].isin(["cash", "cash_equivalent"]), "initial_price"] = 1.0
    df["date"] = pd.to_datetime(df["date"], dayfirst=True).dt.strftime("%Y-%m-%d")
    df["asset_valuation_date"] = pd.to_datetime(df["asset_valuation_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
    df["is_estimated"] = False
    df["underlying_quote__currency__key"] = df["currency__key"]
    df["weighting"] = df.initial_currency_fx_rate * df.initial_price * df.initial_shares
    df["weighting"] = df.weighting / df.weighting.sum()
    df["portfolio__currency__key"] = (
        df["portfolio__currency__key"].ffill().bfill()
    )  # We do that because we expect all cell value to be the same but we expect also emtpy cell (mistake from the provider)
    df = df.replace([np.inf, -np.inf, np.nan], None)
    return {"data": df.to_dict("records")}
