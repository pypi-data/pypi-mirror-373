import numpy as np
import pandas as pd

from wbportfolio.models import Product, Trade


def get_portfolio(x):
    product = Product.objects.get(id=x)
    portfolio = product.primary_portfolio
    return portfolio.id


def parse(import_source):
    data = list()

    df = pd.read_excel(import_source.file.open(), usecols=[3, 4, 7, 10, 15, 16, 17, 18, 20, 21], engine="openpyxl")

    # Filter out all non transaction rows and remove RECORD_DESC col
    df = df[df["RECORD_DESC"].str.strip() == "TRANSACTION"]
    del df["RECORD_DESC"]

    # Convert timestamps to json conform date strings
    df["TRANS_DATE"] = df["TRANS_DATE"].apply(lambda x: x.date().strftime("%Y-%m-%d"))
    df["SETTL_DATE"] = df["SETTL_DATE"].apply(lambda x: x.date().strftime("%Y-%m-%d"))

    # Replace all nan values with empty str
    df[["REGISTER_FIRSTNAME", "CUST_REF"]] = df[["REGISTER_FIRSTNAME", "CUST_REF"]].replace(np.nan, "", regex=True)

    # Merge REGISTER_FIRSTNAME and CUST_REF and then remove both cols
    df["note"] = df["REGISTER_FIRSTNAME"] + df["CUST_REF"]
    del df["REGISTER_FIRSTNAME"]
    del df["CUST_REF"]

    # Create Product Mapping and apply to df
    product_mapping = {
        product["isin"]: product["id"]
        for product in Product.objects.filter(isin__in=df["ISIN"].unique()).values("id", "isin")
    }
    df["ISIN"] = df["ISIN"].apply(lambda x: product_mapping[x])

    # Rename Columns
    df.columns = [
        "bank",
        "underlying_instrument",
        "transaction_date",
        "value_date",
        "external_id",
        "price",
        "shares",
        "comment",
    ]
    df["transaction_subtype"] = df.shares.apply(lambda x: Trade.Type.REDEMPTION if x < 0 else Trade.Type.SUBSCRIPTION)
    df["portfolio"] = df["underlying_instrument"].apply(lambda x: get_portfolio(x))
    df["underlying_instrument"] = df["underlying_instrument"].apply(lambda x: {"id": x, "instrument_type": "product"})
    # Convert df to list of dicts
    data = list(df.T.to_dict().values())

    return {"data": data}
