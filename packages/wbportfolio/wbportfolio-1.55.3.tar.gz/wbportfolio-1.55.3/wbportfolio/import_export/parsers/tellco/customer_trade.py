import codecs
import csv
import datetime
import re

from wbportfolio.import_export.utils import convert_string_to_number
from wbportfolio.models import Trade

product_mapping = {
    "2304": {
        "A": "CH0442615701",
        "B": "CH0442770316",
    },
    "2316": {
        "A": "CH0583763534",
        "B": "CH0583763542",
    },
}


def file_name_parse(file_name):
    identifier = re.findall("([0-9]{4}).*", file_name)
    assert len(identifier) == 1, "Not exactly one identifier was found."
    return identifier[0]


def parse(import_source):
    # Get the identifier from the file name to know which product group it is
    identifier = file_name_parse(import_source.file.name)

    # Load file into a CSV DictReader
    csv_file = import_source.file.open()
    csv_file_type = type(csv_file.read())

    # If the file is a byte string, then we need to convert it.
    if csv_file_type is bytes:
        csv_file = codecs.iterdecode(csv_file, "latin1")

    # Read file into a CSV Dict Reader
    csv_reader = csv.DictReader(csv_file, delimiter=";")

    # Iterate through the CSV File and parse the data into a list
    data = list()
    for customer_trade in csv_reader:
        isin = product_mapping[identifier][customer_trade["Anteilklasse"].strip()]

        transaction_date = datetime.datetime.strptime(customer_trade["Datum"], "%Y%m%d").date()
        shares = round(convert_string_to_number(customer_trade["Saldo - Anzahl"]), 4)
        data.append(
            {
                "underlying_instrument": {"isin": isin, "instrument_type": "product"},
                "portfolio": {"isin": isin, "instrument_type": "product"},
                "transaction_date": transaction_date.strftime("%Y-%m-%d"),
                "value_date": transaction_date.strftime("%Y-%m-%d"),
                "shares": shares,
                "bank": "Tellco Trade",
                "transaction_subtype": Trade.Type.REDEMPTION if shares < 0 else Trade.Type.SUBSCRIPTION,
                "price": round(convert_string_to_number(customer_trade["NIW"]), 4),
            }
        )
    csv_file.close()
    return {"data": data}
