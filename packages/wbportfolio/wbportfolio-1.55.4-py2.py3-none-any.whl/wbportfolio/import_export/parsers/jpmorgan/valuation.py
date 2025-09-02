import datetime
import logging
import re

import numpy as np
import pandas as pd

from wbportfolio.import_export.utils import convert_string_to_number

logger = logging.getLogger("importers.parsers.jpmorgan.index")


def file_name_parse(file_name):
    dates = re.findall("([0-9]{8})", file_name)

    assert len(dates) == 1, "Not exactly 1 date found in the filename"

    return {"valuation_date": datetime.datetime.strptime(dates[0], "%Y%m%d").date()}


def parse(import_source):
    # Load files into a CSV DictReader
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=",")
    df = df.replace([np.inf, -np.inf, np.nan], None)

    # Iterate through the CSV File and parse the data into a list
    data = list()
    for price_data in df.to_dict("records"):
        date = datetime.datetime.strptime(price_data["Date"], "%d-%b-%y")

        data.append(
            {
                "instrument": {"instrument_type": "product", "isin": price_data["ISIN"]},
                "date": date.strftime("%Y-%m-%d"),
                "net_value": round(convert_string_to_number(price_data["Indicative_MID"]), 4),
                "calculated": False,
            }
        )

    return {"data": data}
