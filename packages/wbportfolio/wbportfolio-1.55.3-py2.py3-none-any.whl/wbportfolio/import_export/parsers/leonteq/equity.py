import re
from datetime import datetime
from io import BytesIO

import numpy as np
import pandas as pd

FIELD_MAP = {
    "CCY": "currency__key",
    "CURRENT PRICE": "initial_price",
    "FX": "initial_currency_fx_rate",
    "TOTAL UNITS": "initial_shares",
    "TYPE": "underlying_quote__instrument_type",
    "NAME": "underlying_quote__name",
    "ISIN": "underlying_quote__isin",
    "WEIGHT (%)": "weighting",
}


def parse(import_source):
    data = list()

    isin_regex = "([A-Z]{2}[A-Z0-9]{9}[0-9]{1})"

    dict_df = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl", sheet_name=None)

    for sheet_name, df in dict_df.items():
        if len(re.findall(isin_regex, sheet_name)) > 0:
            valuation_date = datetime.strptime(df.iloc[0, 1].split("AMC OVERVIEW REPORT AS OF ")[-1], "%d.%m.%Y")
            if valuation_date.weekday() not in [5, 6]:
                xx, yy = np.where(df == "COMPOSITION DATA")
                df = df.iloc[xx[0] + 1 :, yy[0] :]
                df = df.rename(columns=df.iloc[0]).drop(df.index[0]).dropna(how="all").rename(columns=FIELD_MAP)

                df = df[
                    (df["underlying_quote__instrument_type"].isin(["CASH", "SHARE"]))
                    & (df["N"].astype("str").str.isnumeric())
                ]

                equities_index = df["underlying_quote__instrument_type"] == "SHARE"
                df.loc[~equities_index, "initial_shares"] = df.loc[~equities_index, "TOTAL VALUE"]
                df.loc[~equities_index, "initial_price"] = 1.0
                df.initial_currency_fx_rate = df.initial_currency_fx_rate.fillna(1.0)
                # df["weighting"] = df.initial_currency_fx_rate * df.initial_price * df.initial_shares
                # df["weighting"] = df.weighting / df.weighting.sum()
                for position in df.to_dict("records"):
                    if position["underlying_quote__instrument_type"] == "CASH":
                        ticker = exchange = "CASH"
                    else:
                        ticker, exchange, _ = str(position["BBG TICKER / IDENTIFIER"]).split(" ")

                    if position["underlying_quote__instrument_type"] == "SHARE":
                        underlying_quote = {
                            "ticker": ticker,
                            "exchange": {"bbg_exchange_codes": exchange},
                            "name": position["underlying_quote__name"],
                            "currency__key": position["currency__key"],
                            "instrument_type": "equity",
                            "isin": position["underlying_quote__isin"],
                        }
                    else:
                        underlying_quote = {"currency__key": position["currency__key"], "instrument_type": "cash"}
                    data.append(
                        {
                            "underlying_quote": underlying_quote,
                            "currency__key": position["currency__key"],
                            "is_estimated": False,
                            "date": valuation_date.strftime("%Y-%m-%d"),
                            "asset_valuation_date": valuation_date.strftime("%Y-%m-%d"),
                            "initial_price": position["initial_price"],
                            "initial_currency_fx_rate": position["initial_currency_fx_rate"],
                            "initial_shares": position["initial_shares"],
                            "weighting": position["weighting"],
                            "exchange": {"bbg_exchange_codes": exchange},
                            "portfolio": {"instrument_type": "product", "isin": sheet_name},
                        }
                    )

    return {"data": data}
