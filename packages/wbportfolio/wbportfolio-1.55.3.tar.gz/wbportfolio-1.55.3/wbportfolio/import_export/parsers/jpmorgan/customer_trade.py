import datetime
import re

import numpy as np
import pandas as pd

from wbportfolio.import_export.utils import convert_string_to_number
from wbportfolio.models import Product, Trade


def file_name_parse(file_name):
    dates = re.findall("([0-9]{8})", file_name)

    assert len(dates) > 0

    parts_dict = {"valuation_date": datetime.datetime.strptime(dates[0], "%Y%m%d").date()}

    isin = re.findall("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})", file_name)

    if len(isin) > 0:
        parts_dict["isin"] = isin[0]

    return parts_dict


def parse(import_source):
    bank_exclusion_list = [
        excluded_bank.strip().lower()
        for excluded_bank in import_source.source.import_parameters.get("bank_exclusion_list", [])
    ]
    # Load files into a CSV DictReader
    df = pd.read_csv(import_source.file, encoding="latin1", delimiter=",")
    df = df.replace([np.inf, -np.inf, np.nan], None)
    # Parse the Parts of the filename into the different parts
    parts = file_name_parse(import_source.file.name)
    df["Trade Date"] = pd.to_datetime(df["Trade Date"], format="%Y%m%d")
    # Get the valuation date from the parts list
    valuation_date = parts["valuation_date"]

    # Iterate through the CSV File and parse the data into a list
    data = list()
    for nominal_data in df.to_dict("records"):
        isin = nominal_data["ISIN"]
        shares = convert_string_to_number(nominal_data["Quantity"])

        # Check whether it is a buy or a sell and convert the value correspondely
        shares = shares if nominal_data["Side"] == "S" else shares * -1
        bank = nominal_data["CounterParty Name"]
        if (
            len(bank_exclusion_list) == 0 or bank.strip().lower() not in bank_exclusion_list
        ):  # we do basic string comparison to exclude appropriate banks. We might want to include regex if bank data is inconsistent
            data.append(
                {
                    "underlying_instrument": {"isin": isin, "instrument_type": "product"},
                    "transaction_date": nominal_data["Trade Date"].strftime("%Y-%m-%d"),
                    "shares": shares,
                    "portfolio": {"isin": isin, "instrument_type": "product"},
                    # 'currency': product.currency.key,
                    "transaction_subtype": Trade.Type.REDEMPTION if shares < 0 else Trade.Type.SUBSCRIPTION,
                    "bank": bank,
                    "price": convert_string_to_number(nominal_data["Price"]),
                }
            )
    import_data = {"data": data}
    if "isin" in parts:
        product = Product.objects.get(isin=parts["isin"])
        import_data["history"] = {
            "underlying_instrument": product.id,
            "transaction_date": valuation_date.strftime("%Y-%m-%d"),
        }
    return import_data
