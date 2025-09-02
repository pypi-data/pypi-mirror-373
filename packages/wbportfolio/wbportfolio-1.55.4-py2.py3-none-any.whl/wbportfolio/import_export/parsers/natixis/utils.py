import datetime
import re

from wbportfolio.models import Product

INSTRUMENT_MAP_NAME = {"EDA23_AtonRa Z class": "LU2170995018"}


def _get_exchange_from_ticker(ticker):
    try:
        ticker, exchange = ticker.split(" ")
    except Exception:
        ticker, exchange = ticker, None
    return exchange


def _get_ticker(ticker):
    return ticker.split(" ")[0]


def _get_underlying_instrument(bbg_code, name, currency, instrument_type="equity", isin=None, cash_position=False):
    if isin := INSTRUMENT_MAP_NAME.get(bbg_code, None):
        return {"isin": isin}

    exchange = _get_exchange_from_ticker(bbg_code)
    ticker = _get_ticker(bbg_code)

    cash_position = cash_position or "CASH" == bbg_code or len(re.findall("(CASH [A-Z]{3})", bbg_code)) > 0
    if cash_position:
        underlying_quote = {"instrument_type": "cash", "currency__key": currency}
    else:
        underlying_quote = {
            "exchange": {"bbg_exchange_codes": exchange},
            "currency__key": currency,
            "name": name.split(" @")[0].split("/")[
                0
            ],  # we remove anything after @ and also any trailing symbol (which represents some country information at natixis)
            "ticker": ticker,
            "instrument_type": instrument_type,
        }
        if not isin:
            isin_re = re.findall("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})", ticker)
            if len(isin_re) > 0:
                isin = isin_re[0]
                # Natixis gives us ISIN as ticker for product. in that case, we registered the isin but we remove the ticker
                underlying_quote["instrument_type"] = "product"
                del underlying_quote["ticker"]
            elif Product.objects.filter(ticker=ticker).exists():
                underlying_quote["instrument_type"] = "product"
        if isin:
            underlying_quote["isin"] = isin
    return underlying_quote


def file_name_parse_isin(file_name):
    dates = re.findall(r"_([0-9]{4}-?[0-9]{2}-?[0-9]{2})", file_name)
    identifier = re.findall(r"([A-Z]{2}(?![A-Z]{10}\b)[A-Z0-9]{10})_", file_name)
    assert len(dates) == 2, "Not 2 dates found in the filename"
    assert len(identifier) == 1, "Not exactly 1 identifier found in the filename"
    try:
        valuation_date = datetime.datetime.strptime(dates[0], "%Y-%m-%d").date()
    except ValueError:
        valuation_date = datetime.datetime.strptime(dates[0], "%Y%m%d").date()
    try:
        generation_date = datetime.datetime.strptime(dates[1], "%Y-%m-%d").date()
    except ValueError:
        generation_date = datetime.datetime.strptime(dates[1], "%Y%m%d").date()

    return {
        "product": {"isin": identifier[0]},
        "valuation_date": valuation_date,
        "generation_date": generation_date,
    }
