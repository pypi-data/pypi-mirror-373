import json

import pandas as pd

from wbportfolio.models import Fees

BASE_MAPPING = {"managementFee": "total_value", "performanceFee": "total_value", "date": "fee_date"}


def parse(import_source):
    def _process_df(df, product_isin):
        df = df.rename(columns=BASE_MAPPING).dropna(how="all", axis=1)
        df = df.drop(columns=df.columns.difference(BASE_MAPPING.values()))
        df["product"] = [{"isin": product_isin}] * df.shape[0]
        return df

    content = json.load(import_source.file)
    data = []
    if isin := content.get("isin", None):
        if mngt_data := content.get("management_fees", None):
            df = _process_df(pd.DataFrame(mngt_data), isin)
            df["transaction_subtype"] = Fees.Type.MANAGEMENT.value
            data.extend(df.to_dict("records"))
        if perf_data := content.get("performance_fees", None):
            df = _process_df(pd.DataFrame(perf_data), isin)
            df["transaction_subtype"] = Fees.Type.PERFORMANCE.value
            data.extend(df.to_dict("records"))

    return {"data": data}
