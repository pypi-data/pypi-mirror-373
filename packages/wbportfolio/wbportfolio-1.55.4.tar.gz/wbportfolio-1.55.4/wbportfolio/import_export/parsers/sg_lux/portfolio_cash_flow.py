from datetime import datetime

import pandas as pd

from wbportfolio.models import ProductGroup


def parse(import_source):
    csv_file = import_source.file.open()

    df = pd.read_csv(csv_file, encoding="latin1", usecols=[0, 2, 4, 18])

    value_date = df["NAV Date"].iloc[0]
    total_assets = df.groupby("Code").sum("Market Value FCY")
    cash = df[df["Asset type code"] == "TRES"].groupby("Code").sum("Market Value FCY")

    data = []

    for code in df["Code"].unique():
        data.append(
            {
                "portfolio": ProductGroup.objects.get(identifier=code).portfolio.id,
                "value_date": datetime.strptime(value_date, "%Y/%m/%d").strftime("%Y-%m-%d"),
                "total_assets": total_assets.T[code].iloc[0],
                "cash": cash.T[code].iloc[0],
                "pending": False,
            }
        )

    return {"data": data}
