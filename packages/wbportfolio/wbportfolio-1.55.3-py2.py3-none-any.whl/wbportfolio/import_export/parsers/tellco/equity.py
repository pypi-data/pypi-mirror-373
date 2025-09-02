import codecs
import csv
import datetime

import pandas as pd
from wbcore.contrib.currency.models import Currency

from wbportfolio.import_export.utils import convert_string_to_number


def parse(import_source):
    # Load file into a CSV DictReader and convert the encoding to latin1 due to hyphonation
    csv_file = import_source.file.open()
    csv_file = codecs.iterdecode(csv_file, "latin1")

    # Read file into a CSV Dict Reader
    csv_reader = csv.DictReader(csv_file, delimiter=";")

    # Iterate through the CSV File and parse the data into a list
    data = list()
    for basket in csv_reader:
        if basket["Assetart"] == "CPON" or (
            basket["Assetart"] == "TRES" and "Sichtguthaben" not in basket["Assetbezeichnung"]
        ):
            continue
        identifier = basket["Fonds-Nr."].strip()
        valuation_date = datetime.datetime.strptime(basket["Datum"], "%Y%m%d")

        currency_key = basket["Währung"]
        currency = Currency.objects.get(key=currency_key)
        group_currency = Currency.objects.get(key=basket["Assetwährung"])

        if basket["Assetart"] == "TRES":
            initial_currency_fx_rate = convert_string_to_number(basket["Wertpapierkurs"])

            ticker = "CASH"
            title = currency.title
            initial_price = 1
            underlying_quote = {
                "instrument_type": "cash",
                "ticker": ticker,
                "name": title,
                "currency__key": currency.key,
            }
        elif basket["Assetart"] == "VMOB":
            instrument_type = "equity"
            if "STRUKT" in basket.get("TL2", ""):
                instrument_type = "product"
            initial_currency_fx_rate = float(currency.convert(valuation_date, group_currency))
            initial_price = basket["Wertpapierkurs"]

            exchange = f'X{basket["Bloomberg Code"]}' if basket["Bloomberg Code"] else None
            underlying_quote = {
                "instrument_type": instrument_type,
                "isin": basket["ISIN"],
                "exchange": {"mic_code": exchange},
                "name": basket["Assetbezeichnung"],
                "currency__key": currency.key,
            }

        initial_shares = basket["Stk / Nominal"]

        data.append(
            {
                "underlying_quote": underlying_quote,
                "exchange": underlying_quote.get("exchange", None),
                "portfolio": {
                    "instrument_type": "product_group",
                    "identifier": identifier,
                },
                "is_estimated": False,
                "currency__key": currency_key,
                "date": valuation_date.strftime("%Y-%m-%d"),
                "asset_valuation_date": valuation_date.strftime("%Y-%m-%d"),
                "initial_price": round(convert_string_to_number(initial_price), 4),
                "initial_currency_fx_rate": initial_currency_fx_rate,
                "initial_shares": round(convert_string_to_number(initial_shares), 4),
            }
        )
    csv_file.close()

    df = pd.DataFrame(data)  # quick Hack to compute weighting on import
    df["weighting"] = df.initial_currency_fx_rate * df.initial_price * df.initial_shares
    df["weighting"] = df.weighting / df.weighting.sum()

    return {"data": df.to_dict("records")}
