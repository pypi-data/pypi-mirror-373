from contextlib import suppress
from io import BytesIO

import pandas as pd

from wbportfolio.models import Product, Trade


def parse(import_source):
    data = list()
    df = pd.DataFrame()
    try:
        df = pd.read_excel(
            BytesIO(import_source.file.read()),
            engine="openpyxl",
            index_col=1,
            sheet_name="TRANSACTION CONSOLIDATION",
            skiprows=3,
        ).dropna(axis=1)
        df["DATE"] = pd.to_datetime(df["DATE"], dayfirst=True)
        df = df[df["EVENT"] == "AMC Cash"]
    except (ValueError, IndexError):
        pass
    if not df.empty:
        for external_id, trade in df.to_dict("index").items():
            with suppress(Product.DoesNotExist):
                product = Product.objects.get(isin=trade["AMC ISIN"])
                shares = (-1 * trade["TOTAL QUANTITY"]) / product.share_price
                price = trade["NET PRICE"] * product.share_price
                price_gross = trade["GROSS PRICE"] * product.share_price
                portfolio = product.primary_portfolio
                data.append(
                    {
                        "underlying_instrument": {"id": product.id, "instrument_type": "product"},
                        "portfolio": portfolio.id,
                        "transaction_date": trade["DATE"].strftime("%Y-%m-%d"),
                        "shares": shares,
                        "external_id": external_id,
                        "transaction_subtype": Trade.Type.REDEMPTION if shares < 0 else Trade.Type.SUBSCRIPTION,
                        "bank": "Leonteq Cash Transfer",
                        "currency__key": product.currency.key,
                        "price": price,
                        "price_gross": price_gross,
                        "currency_fx_rate": trade["BOOKING FX"],
                    }
                )

    return {"data": data}
