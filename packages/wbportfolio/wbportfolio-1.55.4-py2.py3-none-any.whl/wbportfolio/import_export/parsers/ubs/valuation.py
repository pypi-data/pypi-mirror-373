import datetime
import re
from io import BytesIO

import numpy as np
import pandas as pd

from wbportfolio.import_export.utils import get_file_extension


def file_name_parse(file_name):
    isin = re.findall("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})", file_name)

    assert len(isin) == 1, "Not exactly 1 isin found in the filename"

    return {
        "isin": isin[0],
    }


def parse(import_source):
    if get_file_extension(import_source.file) == ".xlsx":
        df = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl", sheet_name="Summary").dropna(
            how="all"
        )
    elif get_file_extension(import_source.file) == ".xls":
        df = pd.read_excel(BytesIO(import_source.file.read()), sheet_name="Summary").dropna(how="all")
    else:
        raise Exception("File not supported")

    parts = file_name_parse(import_source.file.name)
    isin = parts["isin"]

    xx, yy = np.where(df == "Instrument")
    df = df.iloc[: xx[0], :].transpose().dropna(how="all", axis=0).reset_index(drop=True)

    df = df.rename(columns=df.iloc[0]).drop(df.index[0])

    date = df.loc[:, df.columns.str.contains("Statement as at Close of Business")].dropna(how="any").iloc[0, 0]
    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    value = df.loc[:, df.columns.str.contains("RPL")].dropna(how="any").iloc[0, 0]

    data = [
        {
            "instrument": {"instrument_type": "product", "isin": isin},
            "date": date.strftime("%Y-%m-%d"),
            "net_value": value,
            "calculated": False,
        }
    ]

    return {"data": data}
