import re
from datetime import datetime

import pandas as pd

from wbportfolio.models import FeeProductPercentage, Fees, Product

FIELD_MAP = {
    "Transaction_Date": "fee_date",
    "Quantity": "total_value",
    "Currency": "currency__key",
    "Portfolio_Identifier": "product",
    "Booking_Comment": "comment",
}


def parse(import_source):
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=";")
    df = df.loc[(df["Order_Type"] == "xfermon_client") & (df["Bookkind"] == "forex_impl_macc"), :]
    date_range_regex = import_source.source.import_parameters.get(
        "date_range_regex", r"\((\b\d{2}\.\d{2}\.\d{4}\b) to (\b\d{2}\.\d{2}\.\d{4}\b)\)"
    )
    data = []
    if not df.empty:
        df = df.rename(columns=FIELD_MAP)
        df["product"] = df["product"].apply(lambda x: Product.objects.filter(identifier=x).first())
        df["fee_date"] = pd.to_datetime(df["fee_date"], dayfirst=True)
        df["base_management_fees"] = df.apply(
            lambda row: float(row["product"].get_fees_percent(row["fee_date"], FeeProductPercentage.Type.MANAGEMENT)),
            axis=1,
        )
        df["base_bank_fees"] = df.apply(
            lambda row: float(row["product"].get_fees_percent(row["fee_date"], FeeProductPercentage.Type.BANK)),
            axis=1,
        )
        df.total_value = -df.total_value

        df_management = df.copy()
        df_management["transaction_subtype"] = Fees.Type.MANAGEMENT
        df_management["total_value"] = (
            df_management["total_value"]
            * df_management["base_management_fees"]
            / (df_management["base_management_fees"] + df_management["base_bank_fees"])
        )

        df_bank = df.copy()
        df_bank["transaction_subtype"] = Fees.Type.ISSUER
        df_bank["total_value"] = (
            df_bank["total_value"]
            * df_bank["base_bank_fees"]
            / (df_bank["base_management_fees"] + df_bank["base_bank_fees"])
        )

        df = pd.concat([df_management, df_bank], axis=0)
        df = df.drop(columns=df.columns.difference(["transaction_subtype", *FIELD_MAP.values()]))

        df["product"] = df["product"].apply(lambda x: x.id)
        df = df.dropna(subset=["product"])

        for row in df.to_dict("records"):
            # The fee are sometime aggregated. The aggregate date range information is given in the comment. We therefore try to extract it and duplicate the averaged fees
            if match := re.search(date_range_regex, row["comment"]):
                from_date = datetime.strptime(match.group(1), "%d.%m.%Y").date()
                to_date = datetime.strptime(match.group(2), "%d.%m.%Y").date()
            else:
                from_date = (row["fee_date"] - pd.tseries.offsets.BDay(1)).date()
                to_date = row["fee_date"]

            dates = pd.date_range(from_date, to_date, freq="B", inclusive="right")
            for ts in pd.date_range(from_date, to_date, freq="B", inclusive="right"):
                row_copy = row.copy()
                row_copy["fee_date"] = ts.strftime("%Y-%m-%d")
                row_copy["total_value"] = row["total_value"] / len(dates)
                del row_copy["comment"]
                data.append(row_copy)

    return {"data": data}
