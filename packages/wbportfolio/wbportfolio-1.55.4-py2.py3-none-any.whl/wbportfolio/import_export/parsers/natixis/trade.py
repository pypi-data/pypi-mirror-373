import pandas as pd

from wbportfolio.models import Trade

from .utils import _get_underlying_instrument, file_name_parse_isin


def _parse_trade_type(type):
    choices = {
        "Decrease": Trade.Type.DECREASE,
        "Increase": Trade.Type.INCREASE,
        "Rebalancing": Trade.Type.REBALANCE,
        "Buy": Trade.Type.BUY,
        "Sell": Trade.Type.SELL,
    }

    return choices[type]


def parse(import_source):
    data = list()
    df = pd.read_csv(import_source.file, sep=";")
    if not df.empty:
        # Parse the Parts of the filename into the different parts
        parts = file_name_parse_isin(import_source.file.name)

        # Get the valuation date and investment from the parts list
        product_data = parts["product"]

        # Iterate through the CSV File and parse the data into a list
        df["underlying_instrument"] = df[["BLOOMBERG CODE", "NAME", "QUOTED_CRNCY"]].apply(
            lambda x: _get_underlying_instrument(*x), axis=1
        )
        df["exchange"] = df.underlying_instrument.apply(lambda x: x.get("exchange", None))
        columns_map = {
            "underlying_instrument": "underlying_instrument",
            "TRADE DATE": "transaction_date",
            "EXECUTED QTY": "shares",
            "EXECUTED PRICE": "price",
            "FX RATE": "currency_fx_rate",
            "NET PRICE(Stock crncy)": "price",
            "PRICE(USD)": "price_gross",
            "TRADE TYPE": "transaction_subtype",
            "QUOTED_CRNCY": "currency__key",
        }
        df = df.rename(columns=columns_map)
        float_fields = ["shares", "price", "currency_fx_rate", "price", "price_gross"]
        for field in float_fields:
            if field in df:
                df[field] = df[field].apply(
                    lambda x: float(x.replace("-", "").replace(" ", "") if isinstance(x, str) else x)
                )

        df["price"] = df.apply(
            lambda x: x["price"] * x["QUOTITY/ADJ. FACTOR"] if "QUOTITY/ADJ. FACTOR" in x else x["price"], axis=1
        )
        df.transaction_date = pd.to_datetime(df.transaction_date, dayfirst=True)
        df.transaction_date = df.transaction_date.apply(lambda x: x.strftime("%Y-%m-%d"))
        df["transaction_subtype"] = df["transaction_subtype"].apply(lambda x: _parse_trade_type(x))
        df = df.drop(columns=df.columns.difference(columns_map.values()))
        df["portfolio"] = [{"instrument_type": "product", **product_data}] * df.shape[0]
        df["bank"] = "Natixis Cash Transfer"
        data = df.to_dict("records")
    return {"data": data}
