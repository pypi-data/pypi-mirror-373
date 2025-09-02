import datetime
import logging
import re
from io import BytesIO

import numpy as np
import pandas as pd

from wbportfolio.import_export.utils import extract_exchange_ticker

logger = logging.getLogger("importers.parsers.jp_morgan.strategy")


def file_name_parse(file_name):
    dates = re.findall("([0-9]{8})", file_name)

    assert len(dates) == 1, "Not exactly 1 date found in the filename"

    return {"valuation_date": datetime.datetime.strptime(dates[0], "%Y%m%d").date()}


def parse(import_source):
    data = list()
    prices = list()
    df_dict = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl", sheet_name=None)
    for sheet_name, df in df_dict.items():
        xx, yy = np.where(df == "Ticker")
        if len(xx) == 1 and len(yy) == 1:
            df_info = df.iloc[: xx[0] - 1, :].transpose()
            df_info = df_info.rename(columns=df_info.iloc[0]).drop(df_info.index[0]).dropna(how="all")

            strategy_ticker = df_info.loc[:, df_info.columns.str.contains("Ticker")].iloc[0, 0]
            strategy_currency = df_info.loc[:, df_info.columns.str.contains("CCY")].iloc[0, 0]
            valuation_date = df_info.loc[:, df_info.columns.str.contains("Date")].iloc[0, 0]
            valuation_date = datetime.datetime.strptime(valuation_date, "%Y-%m-%d")
            strategy_close = df_info.loc[:, df_info.columns.str.contains("Level")].iloc[0, 0]

            df_positions = df.iloc[xx[0] :, yy[0] :]
            df_positions = (
                df_positions.rename(columns=df_positions.iloc[0]).drop(df_positions.index[0]).dropna(how="all")
            )
            df_positions = df_positions.rename(
                columns={
                    df_positions.columns[df_positions.columns.str.contains("Forex")][0]: "initial_currency_fx_rate",
                    df_positions.columns[df_positions.columns.str.contains("Currency")][0]: "currency__key",
                    df_positions.columns[df_positions.columns.str.contains("Weight")][0]: "weighting",
                    df_positions.columns[df_positions.columns.str.contains("Level")][0]: "initial_price",
                    df_positions.columns[df_positions.columns.str.contains("Ticker")][0]: "underlying_quote__ticker",
                    df_positions.columns[df_positions.columns.str.contains("ISIN")][0]: "underlying_quote__isin",
                    df_positions.columns[df_positions.columns.str.contains("Name")][0]: "underlying_quote__name",
                }
            )
            for position in df_positions.to_dict("records"):
                ticker, exchange = extract_exchange_ticker(position["underlying_quote__ticker"])
                if exchange:
                    exchange = {"bbg_exchange_codes": exchange}
                data.append(
                    {
                        "underlying_quote": {
                            "instrument_type": "equity",
                            "ticker": ticker,
                            "isin": position["underlying_quote__isin"],
                            "name": position["underlying_quote__name"],
                            "currency__key": position["currency__key"],
                            "exchange": exchange,
                        },
                        "portfolio": {
                            "instrument_type": "index",
                            "ticker": strategy_ticker,
                            "currency__key": strategy_currency,
                        },
                        "is_estimated": False,
                        "exchange": exchange,
                        "asset_type": "equity",
                        "currency__key": position["currency__key"],
                        "initial_currency_fx_rate": round(position["initial_currency_fx_rate"], 14),
                        "weighting": round(position["weighting"], 8),
                        "initial_price": round(position["initial_price"], 6),
                        "date": valuation_date.strftime("%Y-%m-%d"),
                    }
                )
            prices.append(
                {
                    "instrument": {
                        "instrument_type": "index",
                        "ticker": strategy_ticker,
                        "currency__key": strategy_currency,
                    },
                    "date": valuation_date.strftime("%Y-%m-%d"),
                    "net_value": strategy_close,
                }
            )
    return {"data": data, "prices": prices}
