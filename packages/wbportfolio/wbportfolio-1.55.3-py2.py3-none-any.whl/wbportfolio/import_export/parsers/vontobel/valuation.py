import numpy as np
import pandas as pd

FIELD_MAP = {"Date": "date", "Quantity": "outstanding_shares", "NAV": "net_value"}


def parse(import_source):
    base_filename = import_source.source.import_parameters.get("valuation_base_filename", "StrategicCertificate")
    data = []
    if base_filename in import_source.file.name:
        df = pd.read_excel(import_source.file, engine="openpyxl", sheet_name=0)
        xx, yy = np.where(df == "Date")
        product_ticker = list(filter(lambda x: "Unnamed" not in x, df.columns))
        df = df.iloc[xx[0] :, yy[0] :]

        df = df.rename(columns=df.iloc[0]).drop(df.index[0]).dropna(how="all")
        df = df.rename(columns=FIELD_MAP)
        df = df.drop(columns=df.columns.difference(FIELD_MAP.values()))
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df["outstanding_shares"] = -df["outstanding_shares"]

        if len(product_ticker) == 0:
            for k, v in import_source.source.import_parameter.items():
                df[k] = v
        else:
            df["instrument__ticker"] = product_ticker[0]
        df = df.replace([np.inf, -np.inf, np.nan], None)
        data = df.to_dict("records")
    return {"data": data}
