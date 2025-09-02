import csv
from io import StringIO

import numpy as np
import pandas as pd
from xlrd import xldate_as_datetime

from wbportfolio.models import Product, Trade

from .sylk import SYLK
from .utils import get_portfolio_id

MAP = {
    "register_id": "register__register_reference",
    "register_name": "bank",
    "isin": "underlying_instrument",
    "trans_date": "transaction_date",
    "settl_date": "value_date",
    "trans_ref": "external_id",
    "trans_price": "price",
    "quantity": "shares",
    "note": "comment",
}


def parse(import_source):
    data = list()
    sylk_handler = SYLK()
    merger_isin_map = import_source.source.import_parameters.get("custom_merged_isin_map", {"XX": "LU"})
    merger_export_parts_trans_desc = import_source.source.import_parameters.get(
        "merger_export_parts_trans_desc", "Export Parts"
    )

    for line in [_line.decode("cp1252") for _line in import_source.file.open("rb").readlines()]:
        sylk_handler.parseline(line)

    buffer = StringIO()
    csvwriter = csv.writer(buffer, quotechar="'", delimiter=";", lineterminator="\n", quoting=csv.QUOTE_ALL)
    for line in sylk_handler.stream_rows():
        csvwriter.writerow(line)

    buffer.seek(0)
    content = buffer.read().replace('""', "")
    df = pd.read_csv(StringIO(content), sep=";", quotechar="'")
    if not df.empty:
        # Filter out all non transaction rows and remove record_desc col
        df = df[df["record_desc"].str.strip() == "TRANSACTION"]

        # Convert timestamps to json conform date strings
        df["trans_date"] = df["trans_date"].apply(lambda x: xldate_as_datetime(x, datemode=0).date())
        df["trans_date"] = df["trans_date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        df["settl_date"] = df["settl_date"].apply(lambda x: xldate_as_datetime(x, datemode=0).date())
        df["settl_date"] = df["settl_date"].apply(lambda x: x.strftime("%Y-%m-%d"))

        # Replace all nan values with empty str
        df[["register_firstname", "cust_ref"]] = df[["register_firstname", "cust_ref"]].replace(np.nan, "", regex=True)

        # Merge register_firstname and cust_ref
        df["note"] = df["register_firstname"] + df["cust_ref"]
        # the trade marked with "Export Parts" and where isin is marked for merge need to be filter out as they are introduced by the merger
        df = df[
            ~(
                (df["trans_desc"] == merger_export_parts_trans_desc)
                & (df["isin"].str.contains("|".join(merger_isin_map.keys())))
            )
        ]
        for pat, repl in merger_isin_map.items():
            df["isin"] = df["isin"].str.replace(pat, repl)

        # Create Product Mapping and apply to df
        product_mapping = {
            product["isin"]: product["id"]
            for product in Product.objects.filter(isin__in=df["isin"].unique()).values("id", "isin")
        }
        df["isin"] = df["isin"].apply(lambda x: product_mapping[x])

        # Rename Columns
        df = df.rename(columns=MAP)
        df = df[df.columns.intersection(MAP.values())]

        df["transaction_subtype"] = df.shares.apply(
            lambda x: Trade.Type.REDEMPTION.value if x < 0 else Trade.Type.SUBSCRIPTION.value
        )
        df["portfolio"] = df["underlying_instrument"].apply(lambda x: get_portfolio_id(x))
        df["underlying_instrument"] = df["underlying_instrument"].apply(
            lambda x: {"id": x, "instrument_type": "product"}
        )
        df["pending"] = False
        # Convert df to list of dicts

        data = df.to_dict("records")

    return {
        "data": data,
    }
