import pandas as pd

from wbportfolio.models import Trade

FIELD_MAP = {
    "Transaction_Date": "transaction_date",
    "Trade_Date": "book_date",
    "Value_Date": "value_date",
    "Price": "price",
    "Quantity": "shares",
    "Currency": "currency__key",
    "Isin": "underlying_instrument__isin",
    "Asset_Text": "underlying_instrument__name",
    "Portfolio_Identifier": "portfolio",
    "Booking_comment": "comment",
}


def parse(import_source):
    df = pd.read_csv(import_source.file, encoding="utf-16", delimiter=";")
    df = df.loc[(df["Order_Type"] == "stex_buy_secondary") & (df["Bookkind"] == "trade_asset"), :]
    data = []
    if not df.empty:
        df = df.rename(columns=FIELD_MAP)
        df = df.drop(columns=df.columns.difference(FIELD_MAP.values()))
        df.shares = -df.shares
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df["book_date"] = pd.to_datetime(df["book_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df["value_date"] = pd.to_datetime(df["value_date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df["transaction_subtype"] = df.shares.apply(lambda x: Trade.Type.SELL if x < 0 else Trade.Type.BUY)
        df["portfolio"] = df["portfolio"].apply(lambda x: {"instrument_type": "product", "identifier": str(x)})
        df = df.dropna(subset=["underlying_instrument__isin"])

        df["underlying_instrument__currency__key"] = df["currency__key"]
        df["bank"] = "N/A"
        data = df.to_dict("records")
    return {"data": data}
