from io import BytesIO

import numpy as np
import pandas as pd


def parse(import_source):
    data = list()
    df = pd.DataFrame()
    try:
        df = pd.read_excel(
            BytesIO(import_source.file.read()), engine="openpyxl", sheet_name="VALUATION_CONSOLIDATION"
        ).dropna(how="all")
    except (ValueError, IndexError):
        pass

    if not df.empty:
        xx, yy = np.where(df == "HISTORICAL VALUATION")
        df = df.iloc[xx[0] :, yy[0] :]
        df = df.rename(columns=df.iloc[0]).drop(df.index[0]).dropna(how="all")
        df = df.drop(df.index[0]).set_index("HISTORICAL VALUATION")
        df.index = pd.to_datetime(df.index, dayfirst=True)

        for date, valuations in df.to_dict("index").items():
            date = date.to_pydatetime()
            for isin, value in valuations.items():
                if date.weekday() not in [5, 6]:
                    data.append(
                        {
                            "instrument": {"instrument_type": "product", "isin": isin},
                            "date": date.strftime("%Y-%m-%d"),
                            "net_value": value,
                            "calculated": False,
                        }
                    )

    return {"data": data}
