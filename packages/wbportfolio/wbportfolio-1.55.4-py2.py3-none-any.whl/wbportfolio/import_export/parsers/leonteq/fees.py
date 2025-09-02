from io import BytesIO

import pandas as pd

from wbportfolio.models import Fees


def parse(import_source):
    data = list()
    df = pd.DataFrame()
    try:
        df = pd.read_excel(
            BytesIO(import_source.file.read()),
            engine="openpyxl",
            sheet_name="FEE_CONSOLIDATION",
            header=[0, 2],
            skiprows=1,
        ).dropna(axis=1)
    except (ValueError, IndexError):
        pass

    if not df.empty:
        for isin in df.columns.unique(level=0):
            product_fees_df = df.loc[:, isin]

            product_fees_df = product_fees_df.rename(
                columns={
                    "TRADE DATE": "fee_date",
                    "INDEX SPONSOR FEE": "total_value",
                    "BUSINESS EVENT": "transaction_subtype",
                }
            )

            product_fees_df.loc[:, "fee_date"] = pd.to_datetime(product_fees_df.loc[:, "fee_date"], dayfirst=True)

            management_fees_eur = product_fees_df[
                product_fees_df.loc[:, "transaction_subtype"] == "Management Fee EUR"
            ]
            performance_fees_eur = product_fees_df[
                product_fees_df.loc[:, "transaction_subtype"] == "Performance Fee EUR"
            ]
            management_fees_eur["transaction_subtype"] = Fees.Type.MANAGEMENT
            performance_fees_eur["transaction_subtype"] = Fees.Type.PERFORMANCE

            concat_list = []
            if not management_fees_eur.empty:
                concat_list.append(management_fees_eur)
            if not performance_fees_eur.empty:
                concat_list.append(performance_fees_eur)
            product_fees_df = pd.concat(
                concat_list,
                axis=0,
            )
            product_fees_df = product_fees_df.where(pd.notnull(product_fees_df), None)
            for fees in product_fees_df.to_dict("records"):
                base_data = {
                    "product": {"isin": isin},
                    "fee_date": fees["fee_date"].strftime("%Y-%m-%d"),
                    "calculated": False,
                }

                total_value_gross = fees.get("total_value_gross", fees["total_value"])
                if total_value_gross != 0 or fees["total_value"] != 0:
                    data.append(
                        {
                            "transaction_subtype": fees["transaction_subtype"],
                            "total_value": fees["total_value"],
                            "total_value_gross": total_value_gross,
                            **base_data,
                        }
                    )

    return {"data": data}
