import numpy as np
import pandas as pd
from wbfdm.import_export.parsers.refinitiv.utils import _clean_and_return_dict

DEFAULT_MAPPING = {
    "AX": "factor",
    "Dates": "date",
    "Instrument": "instrument",
}


def parse(import_source):
    df = pd.read_json(import_source.file, orient="records")
    df = df.replace([np.inf, -np.inf, np.nan], None)
    df = df.rename(columns=DEFAULT_MAPPING).dropna(how="all", axis=1)
    df = df.dropna(how="all", subset=df.columns.difference(["instrument"]))
    df["date"] = pd.to_datetime(df["date"], utc=True, unit="ms")
    df.date = df.date.dt.strftime("%Y-%m-%d")
    df = df.dropna(how="any")
    data = list()
    if not df.empty:
        df = df.groupby(["instrument", "date"]).first().reset_index()
        data = _clean_and_return_dict(df)
    return {"data": data}
