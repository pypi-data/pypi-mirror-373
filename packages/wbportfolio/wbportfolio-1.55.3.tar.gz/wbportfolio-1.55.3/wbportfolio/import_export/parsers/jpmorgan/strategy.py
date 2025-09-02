import datetime
import logging
import re

import numpy as np
import pandas as pd

from wbportfolio.import_export.utils import convert_string_to_number

logger = logging.getLogger("importers.parsers.jp_morgan.strategy")


def file_name_parse(file_name):
    dates = re.findall("([0-9]{8})", file_name)

    assert len(dates) == 1, "Not exactly 1 date found in the filename"

    return {"valuation_date": datetime.datetime.strptime(dates[0], "%Y%m%d").date()}


def manually_create_100_position(parent_strategies, valuation_date):
    data = []
    from wbportfolio.models import Index, Product

    for strategy_ticker in parent_strategies:
        if index := Index.objects.filter(ticker=strategy_ticker).first():
            for product in Product.objects.filter(ticker=strategy_ticker):
                valuations = product.valuations.filter(date__lte=valuation_date)
                last_price = 0
                if valuations.exists():
                    last_price = float(valuations.latest("date").net_value)
                data.append(
                    {
                        "underlying_quote": index.id,
                        "portfolio": {"instrument_type": "product", "id": product.id},
                        "currency__key": index.currency.key,
                        "initial_currency_fx_rate": 1.0,
                        "weighting": 1.0,
                        "is_estimated": True,  # this position is not a real position, it is created by the importer.
                        "initial_price": last_price,
                        "date": valuation_date.strftime("%Y-%m-%d"),
                    }
                )
    return data


def parse(import_source):
    # Load file into a CSV DictReader

    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=",")
    df = df.replace([np.inf, -np.inf, np.nan], None)

    # Parse the Parts of the filename into the different parts
    parts = file_name_parse(import_source.file.name)

    # Get the valuation date from the parts list
    valuation_date = parts["valuation_date"]

    # Iterate through the CSV File and parse the data into a list
    data = list()
    parents_strategies = set()
    for strategy_data in df.to_dict("records"):
        bbg_tickers = strategy_data["BBG Ticker"].split(" ")
        exchange = None
        if len(bbg_tickers) == 2:
            ticker = bbg_tickers[0]
            instrument_type = bbg_tickers[1]
        elif len(bbg_tickers) == 3:
            ticker = bbg_tickers[0]
            exchange = bbg_tickers[1]
            instrument_type = bbg_tickers[2]

        strategy = strategy_data["Strategy Ticker"].replace("Index", "").strip()
        strategy_currency_key = strategy_data["Strategy CCY"]

        position_currency_key = strategy_data["Position CCY"]

        isin = strategy_data["Position ISIN"]
        name = strategy_data["Position Description"]
        initial_price = convert_string_to_number(strategy_data["Prices"])
        initial_currency_fx_rate = convert_string_to_number(strategy_data["Fx Rates"])
        if exchange:
            exchange = {"bbg_exchange_codes": exchange}
        try:
            weighting = convert_string_to_number(strategy_data["Weight In Percent"].replace("%", "")) / 100
        except Exception:
            weighting = 0.0
        underlying_quote = {
            "ticker": ticker,
            "exchange": exchange,
            "isin": isin,
            "name": name,
            "currency__key": position_currency_key,
            "instrument_type": instrument_type.lower(),
        }
        if isin:
            underlying_quote["isin"] = isin
        data.append(
            {
                "underlying_quote": underlying_quote,
                "portfolio": {
                    "instrument_type": "index",
                    "ticker": strategy,
                    "currency__key": strategy_currency_key,
                },
                "exchange": exchange,
                "is_estimated": False,
                "currency__key": position_currency_key,
                "initial_currency_fx_rate": initial_currency_fx_rate,
                "weighting": weighting,
                "initial_price": initial_price,
                "date": valuation_date.strftime("%Y-%m-%d"),
            }
        )
        parents_strategies.add(strategy)
    manual_data = manually_create_100_position(parents_strategies, valuation_date)
    return {"data": data + manual_data}
