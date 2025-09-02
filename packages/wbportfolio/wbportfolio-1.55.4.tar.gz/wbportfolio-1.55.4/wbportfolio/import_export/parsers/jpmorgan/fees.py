import datetime
import logging
import re

import numpy as np
import pandas as pd

from wbportfolio.import_export.utils import convert_string_to_number
from wbportfolio.models import Fees

logger = logging.getLogger("importers.parsers.jpmorgan.fee")


def file_name_parse(file_name):
    dates = re.findall("([0-9]{8})", file_name)

    assert len(dates) == 1, "Not exactly 1 date found in the filename"

    return {"valuation_date": datetime.datetime.strptime(dates[0], "%Y%m%d").date()}


def parse(import_source):
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=",")
    df["Date"] = pd.to_datetime(df["Date"])

    columns_fees = df.columns.difference(["ISIN", "CCY"])
    df[columns_fees] = df[columns_fees].where(pd.notnull(df[columns_fees]), 0)
    df = df.replace([np.inf, -np.inf, np.nan], None)

    # Iterate through the CSV File and parse the data into a list
    data = list()

    for fee_data in df.to_dict("records"):
        isin = fee_data["ISIN"]
        fee_date = fee_data["Date"]
        base_data = {
            "product": {"isin": isin},
            "fee_date": fee_date.strftime("%Y-%m-%d"),
            "calculated": False,
        }
        data.append(
            {
                "transaction_subtype": Fees.Type.PERFORMANCE,
                "total_value": round(convert_string_to_number(fee_data.get("Perf_Fee * Units", 0)), 4),
                "total_value_gross": round(convert_string_to_number(fee_data.get("Perf_Fee * Units", 0)), 4),
                **base_data,
            }
        )
        data.append(
            {
                "transaction_subtype": Fees.Type.MANAGEMENT,
                "total_value": round(convert_string_to_number(fee_data.get("Mgmt_Fee * Units", 0)), 4),
                **base_data,
            }
        )
        data.append(
            {
                "transaction_subtype": Fees.Type.ISSUER,
                "total_value": round(convert_string_to_number(fee_data.get("JPM_Fee * Units", 0)), 4),
                **base_data,
            }
        )

    return {"data": data}
