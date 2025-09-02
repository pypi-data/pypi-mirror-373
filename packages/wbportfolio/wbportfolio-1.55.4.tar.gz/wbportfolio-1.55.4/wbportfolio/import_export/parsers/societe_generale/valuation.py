from io import BytesIO

import numpy as np
import pandas as pd

from wbportfolio.import_export.utils import get_file_extension


def parse(import_source):
    if get_file_extension(import_source.file) == ".xlsx":
        df = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl", sheet_name="Position").dropna(
            how="all"
        )
    elif get_file_extension(import_source.file) == ".xls":
        df = pd.read_excel(BytesIO(import_source.file.read()), sheet_name="Position").dropna(how="all")
    else:
        raise Exception("File not supported")

    xx, yy = np.where(df == "ISIN Code")
    df = df.iloc[xx[0] :, yy[0] :]
    df = df.rename(columns=df.iloc[0]).drop(df.index[0]).dropna(how="all")

    df["Valuation Date"] = pd.to_datetime(df["Valuation Date"])

    data = list()
    for valuation in df.to_dict("records"):
        isin = valuation["ISIN Code"]
        data.append(
            {
                "instrument": {"instrument_type": "product", "isin": isin},
                "date": valuation["Valuation Date"].strftime("%Y-%m-%d"),
                "net_value": round(valuation["Bid"], 6),
                "calculated": False,
            }
        )

    return {"data": data}
