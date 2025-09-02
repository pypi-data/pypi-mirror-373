from contextlib import suppress
from datetime import datetime

import pandas as pd

from wbportfolio.models import Portfolio


def parse(import_source):
    csv_file = import_source.file.open()

    df = pd.read_csv(csv_file)

    def get_portfolio_id(row) -> int | None:
        with suppress(Portfolio.DoesNotExist):
            return Portfolio.all_objects.get(instruments__children__isin__in=[row["Isin"]]).pk

    df = df[~df["Isin"].isnull()]
    df["Trade date"] = df["Trade date"].ffill()
    df["portfolio"] = df.apply(get_portfolio_id, axis=1)
    df = df[["Trade date", "portfolio", "Net Ref ccy"]]
    df = df.groupby(["Trade date", "portfolio"]).sum().to_dict()

    data = []
    for keys, cash_flow_forecast in df["Net Ref ccy"].items():
        data.append(
            {
                "value_date": datetime.strptime(keys[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                "portfolio": keys[1],
                "cash_flow_forecast": cash_flow_forecast,
                "pending": True,
            }
        )

    return {
        "data": data,
    }
