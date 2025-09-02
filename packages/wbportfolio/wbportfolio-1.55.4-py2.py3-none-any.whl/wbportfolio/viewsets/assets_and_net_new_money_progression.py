from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from wbcore import viewsets
from wbcrm.models.accounts import Account

from wbportfolio.analysis.claims import get_assets_and_net_new_money_progression
from wbportfolio.filters import AssetsAndNetNewMoneyProgressionFilterSet
from wbportfolio.models.products import Product
from wbportfolio.models.transactions.claim import Claim

from .configs import AssetAndNetNewMoneyProgressionChartTitleConfig


class AssetAndNetNewMoneyProgressionChartViewSet(viewsets.ChartViewSet):
    queryset = Claim.objects.all()

    filterset_class = AssetsAndNetNewMoneyProgressionFilterSet

    title_config_class = AssetAndNetNewMoneyProgressionChartTitleConfig

    def get_plotly(self, queryset) -> "go.Figure":
        if "period" not in self.request.GET:
            from_date = date(2023, 12, 31)
            to_date = date(2024, 6, 30)
        else:
            from_date, to_date = self.request.GET["period"].split(",")
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        account_id = self.request.GET.get("account", None)
        product_id = self.request.GET.get("product", None)

        name = f"Progression: {from_date:%d.%m.%Y}-{to_date:%d.%m.%Y}"

        account_tree_id = None
        el = list()
        if account_id:
            account = Account.objects.get(id=account_id)
            account_tree_id = account.tree_id  # type: ignore
            el.append(str(account))

        if product_id:
            el.append(str(Product.objects.get(id=product_id)))

        if len(el) > 0:
            name += f" ({", ".join(el)})"

        data = get_assets_and_net_new_money_progression(
            from_date=from_date, to_date=to_date, account_tree_id=account_tree_id, product_id=product_id
        )
        df = pd.DataFrame(data)

        # Compute performance of each month
        df["performance"] = df["total_assets"] - df["total_assets"].shift(1) - df["net_new_money"]

        # Compute the x label
        df["x"] = df[["year", "month"]].apply(lambda row: "-".join(row.values.astype(str)), axis=1)

        # Implode the pivoted table to have a list of values
        df = df.melt(id_vars=["x", "year", "month"], value_vars=["net_new_money", "performance", "total_assets"])

        # Sort by year, then month, then variable to have everything in the right order
        df = df.sort_values(["year", "month", "variable"])

        # Remove the first two rows, as they are the NNM and Performance of the previous month, which we do not want to display
        df = df.iloc[2:]

        # Create a pattern to have the measure for the waterfall chart
        df["measure"] = np.tile(["absolute", "relative", "relative"], len(df) // 3 + 1)[: len(df)]

        # We reset the index and drop all columns we don't need
        # IMPORTANT: Do not drop year and month, even though we
        # don't need it - we will loose the ordering
        df = df.reset_index()[["x", "year", "month", "variable", "value", "measure"]]

        # Rename things, to have it pretty in the chart
        df["variable"] = (
            df["variable"]
            .str.replace("net_new_money", "NNM")
            .replace("total_assets", "AuM")
            .replace("performance", "Performance")
        )
        df.iloc[0, 0] = ""
        df.iloc[0, 3] = "Initial AuM"
        df.iloc[-1, 3] = "Final AuM"

        # Create the figure and show it
        fig = go.Figure()
        fig.add_trace(
            go.Waterfall(
                name=name,
                orientation="v",
                measure=df["measure"],
                x=[df["x"], df["variable"]],
                y=df["value"],
                text=list(map(lambda x: f"{x/1_000_000:,.0f}" if x is not None else "0", df["value"])),
                decreasing={"marker": {"color": "#FF6961"}},
                increasing={"marker": {"color": "#77DD77"}},
                totals={"marker": {"color": "#D3D3D3"}},
            )
        )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=0, b=40),
            showlegend=True,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1,
                "xanchor": "center",
                "x": 0.5,
            },
        )

        return fig
