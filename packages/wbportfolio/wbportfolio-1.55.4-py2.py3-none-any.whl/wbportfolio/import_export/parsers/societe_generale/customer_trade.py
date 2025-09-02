import datetime
import re
from io import BytesIO

import pandas as pd

from wbportfolio.models import Product, Trade


def parse(import_source):
    df_dict = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl", sheet_name=None)

    data = list()
    product_isins = set()
    max_date = datetime.date(1900, 1, 1)

    for sheet_name, df in df_dict.items():
        if "prices" not in sheet_name:
            isin = re.findall("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})", sheet_name)
            isin = isin[0]
            product_isins.add(isin)
            df = df.rename(
                columns={
                    "Trade Date": "transaction_date",
                    "Price": "price",
                    "Nominal": "nominal",
                    "Market CP": "bank",
                    "Way": "way",
                }
            )
            df["transaction_date"] = pd.to_datetime(
                df["transaction_date"],
            )
            for trade in df.to_dict("records"):
                max_date = max(trade["transaction_date"].date(), max_date)

                nominal = trade["nominal"] if trade["way"] == "S" else trade["nominal"] * -1
                data.append(
                    {
                        "underlying_instrument": {"isin": isin, "instrument_type": "product"},
                        "portfolio": {"isin": isin, "instrument_type": "product"},
                        "transaction_date": trade["transaction_date"].strftime("%Y-%m-%d"),
                        "nominal": nominal,
                        "transaction_subtype": Trade.Type.REDEMPTION if nominal < 0 else Trade.Type.SUBSCRIPTION,
                        "bank": trade["bank"],
                        "price": round(trade["price"] / 10, 6),
                    }
                )
    underlying_instruments = Product.objects.filter(isin__in=product_isins).values_list("id", flat=True)
    return {
        "data": data,
        "history": {
            "underlying_instruments": list(underlying_instruments),
            "transaction_date": max_date.strftime("%Y-%m-%d"),
        },
    }
