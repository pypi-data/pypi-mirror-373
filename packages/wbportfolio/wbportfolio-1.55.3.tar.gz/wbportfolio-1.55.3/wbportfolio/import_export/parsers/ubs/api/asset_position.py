import json

import numpy as np
import pandas as pd
from wbcore.contrib.currency.models import CurrencyFXRates

from wbportfolio.import_export.utils import extract_exchange_ticker

BASE_MAPPING = {
    "instrument": "underlying_quote__name",
    "ric": "underlying_quote__refinitiv_identifier_code",
    "bbTicker": "underlying_quote__ticker",
    "isin": "underlying_quote__isin",
    "sedol": "underlying_quote__sedol",
    "valoren": "underlying_quote__valoren",
    "assetClass": "underlying_quote__instrument_type",
    "percentageWeight": "weighting",
    "shares": "initial_shares",
    "localClose": "initial_price",
    "currency": "currency__key",
    "fxMultiplier": "initial_currency_fx_rate",
}

INSTRUMENT_MAPPING = {
    "EQUITY": {},
    "INDEX": {},
    "ETF": {},
    "UBS_SECURITY": {},
    "FUTURE": {"contracts": "contracts"},
    "CASH": {"currencyAmount": "initial_shares"},
    "CASH_COMP": {
        "currencyAmount": "initial_shares",
    },
    "BOND": {"creditRating": "credit_rating", "maturityDate": "maturity_date"},
    "OPTION": {
        "description": "description",
        "strike": "strike",
        "sizeOfContract": "size_of_contract",
        "exerciseStyle": "exercise_style",
        "optionType": "option_type",
        "expiryDate": "expiry_date",
        "underlying__description": "underlying__description",
        "underlying__ric": "underlying__refinitiv_identifier_code",
        "underlying__bbTicker": "underlying__ticker",
        "underlying__assetClass": "underlying__instrument_type",
    },
}

INSTRUMENT_TYPE_MAP = {
    "EQUITY": "equity",
    "INDEX": "index",
    "ETF": "etf",
    "UBS_SECURITY": "equity",
    "FUTURE": "future",
    "CASH": "cash",
    "CASH_COMP": "cash",
    "BOND": "bond",
    "OPTION": "option",
}


def parse(import_source):
    content = json.load(import_source.file)
    data = list()
    if (
        (constituents := content.get("constituents", None))
        and (val_date := content.get("asOfDate", None))
        and (amc := content.get("amc", None))
    ):
        for asset_class, asset_data in constituents.items():
            if asset_class in INSTRUMENT_MAPPING.keys():
                asset_class_map = INSTRUMENT_MAPPING[asset_class]
                _map = {**asset_class_map, **BASE_MAPPING}
                df = pd.json_normalize(asset_data, sep="__")
                df = df.replace([np.inf, -np.inf, np.nan], None)
                df = df.rename(columns=_map).dropna(how="all", axis=1)
                df["weighting"] = df["weighting"] / 100.0
                df["date"] = val_date
                df["portfolio__instrument_type"] = "product"
                df["portfolio__isin"] = amc["isin"]
                df["underlying_quote__currency__key"] = df["currency__key"]
                df["underlying_quote__instrument_type"] = df.underlying_quote__instrument_type.apply(
                    lambda x: INSTRUMENT_TYPE_MAP[x]
                )
                if asset_class == "CASH":
                    df["initial_price"] = 1.0
                    df["initial_currency_fx_rate"] = (
                        df["currency__key"]
                        .apply(
                            lambda x: CurrencyFXRates.objects.filter(currency__key=x, date__lte=val_date)
                            .latest("date")
                            .value
                        )
                        .astype(float)
                    )
                df["is_estimated"] = False
                if "underlying_quote__ticker" in df.columns:
                    df["underlying_quote__exchange"] = df["underlying_quote__ticker"].apply(
                        lambda x: {"bbg_exchange_codes": extract_exchange_ticker(x)[1]}
                    )
                    df["underlying_quote__ticker"] = df["underlying_quote__ticker"].apply(
                        lambda x: extract_exchange_ticker(x)[0]
                    )
                if "underlying_quote__exchange" in df.columns:
                    df["exchange"] = df["underlying_quote__exchange"]
                data.extend(df.to_dict("records"))
    return {"data": data}
