import numpy as np
import pandas as pd

FIELD_MAP = {
    "#AssetIdentifier": "identifier",
    "AssetCurrency": "currency__key",
    "AssetValor": "valoren",
    "ISIN": "isin",
    "SymbolTK": "ticker",
    "OperatingMic": "exchange",
    "AssetType": "instrument_type",
    "AssetText": "name",
}

ASSET_TYPE_MAP = {
    "EQUADR": "equity",
    "EQUBEA": "equity",
    "EQUREG": "equity",
    "FNDETF": "etf",
    "OTHOTH": None,
    "STROTH": "etf",
    "STRPRT": "etf",
}


def parse(import_source):
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=";")
    df = df.rename(columns=FIELD_MAP)
    df = df.replace([np.inf, -np.inf, np.nan], None)
    df["instrument_type"] = df["instrument_type"].apply(lambda x: ASSET_TYPE_MAP[x])
    df = df.drop(columns=df.columns.difference(FIELD_MAP.values())).astype(str)
    df["exchange"] = df["exchange"].apply(lambda x: {"operating_mic_code": x})
    df = df.dropna(subset="instrument_type")
    return {"data": df.to_dict("records")}
