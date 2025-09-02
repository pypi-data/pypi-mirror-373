from io import BytesIO

import pandas as pd

from wbportfolio.models import Product, Trade


def parse(import_source):
    df_dict = pd.read_excel(BytesIO(import_source.file.read()), engine="openpyxl")
    df_dict = df_dict.rename(
        columns={
            "Trade Date": "transaction_date",
            "ISIN": "underlying_instrument__isin",
            "Client Side": "client_side",
            "Net Quantity": "shares",
            "Price": "price",
            "Custodian": "custodian",
        }
    )
    df_dict = df_dict.where(pd.notnull(df_dict), None)
    df_dict["transaction_date"] = pd.to_datetime(df_dict["transaction_date"])
    product_isins = set()

    data = list()
    for obj in df_dict.to_dict("records"):
        shares = -1 * obj["shares"]
        isin = obj["underlying_instrument__isin"]
        data.append(
            {
                "underlying_instrument": {"isin": isin, "instrument_type": "product"},
                "portfolio": {"isin": isin, "instrument_type": "product"},
                "transaction_date": obj["transaction_date"].strftime("%Y-%m-%d"),
                "shares": shares,
                "bank": obj["custodian"] if obj["custodian"] else "NA",
                "transaction_subtype": Trade.Type.REDEMPTION if shares < 0 else Trade.Type.SUBSCRIPTION,
                "price": round(obj["price"], 6),
            }
        )
        product_isins.add(isin)

    underlying_instruments = Product.objects.filter(isin__in=product_isins).values_list("id", flat=True)

    return {
        "data": data,
        "history": {
            "underlying_instruments": list(underlying_instruments),
            "transaction_date": df_dict.transaction_date.max().strftime("%Y-%m-%d"),
        },
    }
