from datetime import date
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pandas.tseries.offsets import BDay
from plotly.subplots import make_subplots
from wbcore.contrib.currency.models import CurrencyFXRates
from wbfdm.enums import MarketData
from wbfdm.models import Instrument as InstrumentFDM
from wbfdm.models.instruments.instrument_prices import InstrumentPrice


class LiquidityStressMixin:
    def get_product_ids_from_group_product_or_product(self) -> [None, list]:
        """
        The function returns a list of id(s) if:
            - a simple product id if instrument_type == Product.
            - the list of the product ids if instrument_type == ProductGroup.
            - the list of the products ids if instrument_type == Product and if the product belongs to a group.
        Otherwise the function returns None.
        """

        if self.instrument_type not in ["Product", "ProductGroup"]:
            return None
        products_id = [self.pk]  # if self is a Product and has not a self.group, it keeps this value.
        casted_instrument = self.get_casted_instrument()
        if self.instrument_type.key == "product_group":
            products_id = casted_instrument.products.values_list("id", flat=True)
        elif self.instrument_type.key == "product" and casted_instrument.group:
            products_id = casted_instrument.group.products.values_list("id", flat=True)

        return products_id

    @staticmethod
    def waterfall_and_slicing_calculation(
        mean_volume_by_id: pd.Series, price_change: float, df_asset_positions: pd.DataFrame, liq_factor: float
    ) -> pd.DataFrame:
        df = pd.DataFrame(index=df_asset_positions.index, columns=["waterfall", "slicing"])
        df["waterfall"] = df_asset_positions.shares.div(mean_volume_by_id * liq_factor, level="instrument")
        df["waterfall"] = df["waterfall"].mask(df["waterfall"] > 360, 360)
        stock_index = df.loc[:, "waterfall"].dropna().index
        df.loc[stock_index, "slicing"] = 1 / ((1 + price_change) / df["waterfall"]).loc[("Equity", slice(None))].min()
        return df

    def get_volumes_from_scenario_stress_test(
        self, weights_date: date, df_volumes: pd.DataFrame, df_asset_positions: pd.DataFrame, liq_factor: float
    ) -> pd.DataFrame:
        # Depending on the scenario, we slice the volume DataFrame for the corresponding dates.
        scenarios = [
            "Baseline Scenario",
            "COVID-19",
            "Lehman",
            "Lehman Spring",
            "Debt Crisis",
            "China Crisis",
            "Dotcom",
            "Volume falls by 60 pct",
        ]

        def get_volume_period_scenario(scenario_name: str):
            import datetime as dt

            from pandas.tseries.offsets import BDay

            if scenario_name == "Baseline Scenario" or scenario_name == "Volume falls by 60 pct":
                start, end = (weights_date - BDay(50)).date(), weights_date

            elif scenario_name == "COVID-19":
                start, end = dt.date(2021, 2, 10), dt.date(2021, 3, 23)

            elif scenario_name == "Lehman":
                start, end = dt.date(2008, 10, 3), dt.date(2008, 10, 10)

            elif scenario_name == "Lehman Spring":
                start, end = dt.date(2009, 2, 16), dt.date(2009, 2, 23)

            elif scenario_name == "Debt Crisis":
                start, end = dt.date(2011, 8, 1), dt.date(2011, 8, 11)

            elif scenario_name == "China Crisis":
                start, end = dt.date(2015, 8, 15), dt.date(2015, 8, 24)

            elif scenario_name == "Dotcom":
                start, end = dt.date(2002, 7, 15), dt.date(2002, 7, 22)

            else:
                return pd.DataFrame()  # No existing scenario

            df_volume_scenario = df_volumes.loc[:, start:end]
            return df_volume_scenario

        # Depending to the method, the "days to liquidate"'s result is different.
        methods = ["waterfall", "slicing"]

        # ---- SCENARIOS CALCULATION ---- :
        price_change_factor = 0
        multi_columns = pd.MultiIndex.from_product([scenarios, methods], names=["scenario", "method"])
        days_to_liquidate = pd.DataFrame(index=df_asset_positions.index, columns=multi_columns)
        liquidity_equivalent_one_day = pd.DataFrame(index=df_asset_positions.index, columns=scenarios)

        for scenario in scenarios:
            volume_scenario = get_volume_period_scenario(scenario)
            if volume_scenario.empty:
                continue
            mean_volume = volume_scenario.mean(axis=1)
            if scenario == "Volume falls by 60 pct":
                mean_volume *= 0.4

            days_to_liquidate.loc[:, (scenario, methods)] = self.waterfall_and_slicing_calculation(
                mean_volume, price_change_factor, df_asset_positions, liq_factor
            ).values
            liquidity_equivalent_one_day[scenario] = (
                (1 + price_change_factor)
                * df_asset_positions.total_value_usd
                / days_to_liquidate.loc[(slice(None), mean_volume.index), (scenario, "waterfall")]
            )
        return days_to_liquidate

    @staticmethod
    def get_percentile_worst_dollar_volume(df_dollar_volume: pd.DataFrame, method: str = "mean_below_worst"):
        list_pct_worst_volume = range(0, 101)
        multi_index = pd.MultiIndex.from_product(
            [list_pct_worst_volume, df_dollar_volume.index.values], names=["x%_worst_volume", "instrument"]
        )
        average_worst_dollar_volume = pd.Series(index=multi_index, dtype=float)
        for pct_worst_volume in list_pct_worst_volume:
            if method == "mean_below_worst":
                average_worst_dollar_volume.loc[(pct_worst_volume, slice(None))] = (
                    df_dollar_volume.where(
                        df_dollar_volume.le(
                            df_dollar_volume.quantile(pct_worst_volume / 100, axis=1, interpolation="midpoint"), axis=0
                        )
                    )
                    .mean(axis=1)
                    .values
                )
            else:
                average_worst_dollar_volume.loc[(pct_worst_volume, slice(None))] = df_dollar_volume.quantile(
                    pct_worst_volume / 100, axis=1, interpolation="midpoint"
                ).values
        return average_worst_dollar_volume

    @staticmethod
    def reverse_stress_test(
        total_aum: float,
        df_asset_positions: pd.DataFrame,
        average_worst_dollar_volume: pd.Series,
        liq_factor: float,
        below_x_days: int = 5,
    ) -> pd.DataFrame:
        # Remove cash instruments from the instruments liquidity estimation
        cash_instruments = df_asset_positions.loc[("Cash", slice(None))].index.unique("instrument")
        instruments_id = average_worst_dollar_volume.index.unique("instrument")
        instruments_id = instruments_id.drop(cash_instruments)

        x_pct = average_worst_dollar_volume.index.unique(0)
        aum_multiplication = range(1, 51)
        multi_index = pd.MultiIndex.from_product(
            [instruments_id, x_pct, x_pct],
            names=["instrument", "x%_redemption", "x%_worst_volume"],
        )
        df = pd.DataFrame(index=multi_index)

        df = df.join(pd.DataFrame(average_worst_dollar_volume, columns=["average_worst_dollar_volume"]))
        df = df.join(df_asset_positions.weighting.droplevel("type"), on="instrument")
        for multiplication in aum_multiplication:
            amount_to_liquidate = (
                total_aum * multiplication * df.index.get_level_values("x%_redemption") / 100 * df["weighting"]
            )
            df[f"days_to_liquidate {multiplication}"] = amount_to_liquidate / (
                liq_factor * df["average_worst_dollar_volume"]
            )

        df_days_to_liquidate = df.filter(like="days_to_liquidate")
        df_weights_sold = (1 / df_days_to_liquidate).mul(df["weighting"], axis="index") * below_x_days

        # TODO: cannot use mask on series because it does not work with pandas 1.5.3.
        weights = df.weighting.to_frame(name=df_weights_sold.columns[0])
        weights = weights.reindex(df_weights_sold.columns, axis=1).ffill(axis=1)
        df_weights_sold = df_weights_sold.mask(df_weights_sold > weights, weights)
        df_weights_sold = df_weights_sold.groupby(["x%_redemption", "x%_worst_volume"]).sum()
        df = df_weights_sold.unstack(level=0)

        # Add cash weights
        cash = df_asset_positions.loc[("Cash", slice(None))].weighting.sum()
        df += cash
        return df

    def stress_volume_bid_ask_test(
        self,
        df_asset_positions: pd.DataFrame,
        df_dollar_volume: pd.DataFrame,
        df_volumes: pd.DataFrame,
        df_bid_ask_spread: pd.DataFrame,
        liq_factor: float,
        pct_worst_dollar_volume: float = 0.1,
        pct_worst_volume: float = 0.1,
        pct_higher_bid_ask_spread: float = 0.9,
        price_change_factor: float = 0,
        acceptable_loss: float = 0.3,
    ) -> pd.DataFrame:
        worst_dollar_volumes = df_dollar_volume.where(
            df_dollar_volume.le(df_dollar_volume.quantile(pct_worst_dollar_volume, axis=1), axis=0)
        )

        # volumes:
        worst_corresponding_volumes = df_volumes.where(worst_dollar_volumes.notnull())
        worst_volumes = worst_corresponding_volumes.where(
            worst_corresponding_volumes.le(worst_corresponding_volumes.quantile(pct_worst_volume, axis=1), axis=0)
        )
        mean_worst_volumes = worst_volumes.mean(axis=1)

        scenarios = ["S-T Worst Volume", "S-T Worst B-A"]
        methods = ["waterfall", "slicing"]
        multi_columns = pd.MultiIndex.from_product([scenarios, methods], names=["scenario", "method"])
        days_to_liquidate = pd.DataFrame(index=df_asset_positions.index, columns=multi_columns)

        days_to_liquidate.loc[:, ("S-T Worst Volume", methods)] = self.waterfall_and_slicing_calculation(
            mean_worst_volumes, price_change_factor, df_asset_positions, liq_factor
        ).values

        # bid-ask spread:
        worst_corresponding_bid_ask_spread = df_bid_ask_spread.where(worst_dollar_volumes.notnull())
        worst_bid_ask_spread = worst_corresponding_bid_ask_spread.where(
            worst_corresponding_bid_ask_spread.ge(
                worst_corresponding_bid_ask_spread.quantile(pct_higher_bid_ask_spread, axis=1), axis=0
            )
        )

        # we do not use the function to calculate waterfall here because formula is different.
        days_to_liquidate.loc[(slice(None), worst_bid_ask_spread.index), ("S-T Worst B-A", "waterfall")] = (
            worst_bid_ask_spread.mean(axis=1) / acceptable_loss
        ).values
        days_to_liquidate.loc[(slice(None), worst_bid_ask_spread.index), ("S-T Worst B-A", "slicing")] = (
            1 / ((1 + price_change_factor) / days_to_liquidate.loc[:, ("S-T Worst B-A", "waterfall")]).min()
        )

        return days_to_liquidate

    @staticmethod
    def aggregate_days_to_liquidate(days_to_liquidate: pd.DataFrame) -> pd.DataFrame:
        # Aggregation:
        instrument_types = days_to_liquidate.index.get_level_values("type").drop_duplicates()
        timeline = ["1 day or less", "2-7 days", "8-15 days", "16-30 days", "31-60 days", "61-180 days"]
        df_aggregate = pd.DataFrame(
            index=pd.MultiIndex.from_product([instrument_types, timeline], names=["type", "time"]),
            columns=days_to_liquidate.drop("instrument", axis=1, level=0).columns,
        )
        _dict = {
            "1 day or less": [0, 1],
            "2-7 days": [1, 7],
            "8-15 days": [7, 15],
            "16-30 days": [15, 30],
            "31-60 days": [30, 60],
            "61-180 days": [60, 180],
        }
        df_waterfall = days_to_liquidate.loc[:, (slice(None), "waterfall")]
        df_slicing = days_to_liquidate.loc[:, (slice(None), "slicing")]
        type_index = pd.Index(instrument_types)
        for period, value in _dict.items():
            tmp_waterfall = df_waterfall.where((df_waterfall >= value[0]) & (df_waterfall <= value[1]))
            for scenario in days_to_liquidate.drop(("instrument", "weighting"), axis=1).columns:
                all_index = days_to_liquidate.loc[:, scenario].dropna().index
                total_weight = days_to_liquidate.loc[all_index, ("instrument", "weighting")]
                if scenario[1] == "waterfall":
                    selection_idx = tmp_waterfall.loc[:, scenario].dropna().index
                    total_weight = total_weight.sum()
                    sliced_weight = (
                        days_to_liquidate.loc[selection_idx, ("instrument", "weighting")]
                        .groupby("type")
                        .sum()
                        .reindex(type_index)
                    )
                    df_aggregate.loc[(slice(None), period), scenario] = (sliced_weight / total_weight).values
                else:  # slicing
                    tmp_slicing = df_slicing.loc[:, scenario]
                    total_weight = total_weight.groupby("type").sum() / total_weight.sum()
                    total_weight.name = ("instrument", "agg_weights")
                    df_aggregate.loc[(slice(None), period), scenario] = (
                        total_weight / tmp_slicing.groupby("type").max() * value[1]
                    ).values
                    df_aggregate = df_aggregate.join(total_weight)
                    df_aggregate.loc[(slice(None), period), scenario] = df_aggregate.loc[
                        (slice(None), period), scenario
                    ].mask(
                        (
                            df_aggregate.loc[(slice(None), period), scenario]
                            > df_aggregate.loc[(slice(None), period), ("instrument", "agg_weights")]
                        )
                        | (df_aggregate.loc[(slice(None), period), scenario] == -np.inf),
                        df_aggregate.loc[(slice(None), period), ("instrument", "agg_weights")],
                    )
                    df_aggregate.drop(("instrument", "agg_weights"), axis=1, inplace=True)
        df_aggregate.loc[:, (slice(None), "waterfall")] = (
            df_aggregate.loc[:, (slice(None), "waterfall")].fillna(0).groupby("type").cumsum()
        )
        df_aggregate_portfolio = df_aggregate.stack("method").groupby(["time", "method"]).sum()
        df_aggregate_portfolio = pd.concat({"Portfolio": df_aggregate_portfolio}, names=["type"]).unstack("method")
        df_aggregate_portfolio = df_aggregate_portfolio.reindex(labels=timeline, level="time")
        df_aggregate = pd.concat([df_aggregate_portfolio, df_aggregate])
        return df_aggregate

    @staticmethod
    def series_of_colors(portfolio_value: pd.Series) -> pd.DataFrame:
        portfolio_value_colors = pd.DataFrame(columns=["colors", "message"])
        portfolio_value_colors.loc[:, "colors"] = portfolio_value.astype(float).round(4)
        for k, v in portfolio_value_colors.colors.items():
            v_adj = round(v * 100, 2)
            if k == "1 day or less":
                portfolio_value_colors.at[k, "colors"] = "#0FFBA6" if v >= 0.7 else "#FBE426"
                portfolio_value_colors.at[k, "message"] = (
                    pd.NA if v >= 0.7 else f"to liquidate {v_adj}%, more than 1 day is needed"
                )
            elif k == "2-7 days":
                portfolio_value_colors.at[k, "colors"] = "#0FFBA6" if v >= 0.8 else "#FBE426"
                portfolio_value_colors.at[k, "message"] = (
                    pd.NA if v >= 0.8 else f"to liquidate {v_adj}%, more than 7 days are needed"
                )
            elif k == "8-15 days":
                portfolio_value_colors.at[k, "colors"] = (
                    "#0FFBA6" if v >= 0.9 else "#FBE426" if v >= 0.7 else "#FC6955"
                )
                portfolio_value_colors.at[k, "message"] = (
                    pd.NA if v >= 0.9 else f"to liquidate {v_adj}%, more than 15 days are needed"
                )
            elif k == "16-30 days":
                portfolio_value_colors.at[k, "colors"] = "#0FFBA6" if v >= 1 else "#FBE426" if v >= 0.9 else "#FC6955"
                portfolio_value_colors.at[k, "message"] = (
                    pd.NA if v >= 1 else f"to liquidate {v_adj}%, more than 30 days are needed"
                )
            elif k == "31-60 days":
                portfolio_value_colors.at[k, "colors"] = "#0FFBA6" if v >= 1 else "#FBE426" if v >= 0.95 else "#FC6955"
                portfolio_value_colors.at[k, "message"] = (
                    pd.NA if v >= 1 else f"to liquidate {v_adj}%, more than 60 days are needed"
                )
            else:
                portfolio_value_colors.at[k, "colors"] = "#0FFBA6" if v >= 1 else "#FBE426" if v >= 0.99 else "#FC6955"
                portfolio_value_colors.at[k, "message"] = (
                    pd.NA if v >= 1 else f"to liquidate {v_adj}%, more than 180 days are needed"
                )
        return portfolio_value_colors

    def liquidity_monitor_graph(self, portfolio_value: pd.Series, expectation_net_redemption_df: pd.DataFrame):
        index = portfolio_value.index
        # portfolio_value = df_aggregate.loc[("Portfolio", slice(None)), (scenario, method)].droplevel(0, axis=0)
        portfolio_value_colors = self.series_of_colors(portfolio_value)

        portfolio_value_list = portfolio_value.mul(100).values.tolist()
        expectation = expectation_net_redemption_df.mul(100).values.tolist()
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Liquidity Balance Overview", "Redemption Coverage Ratio"))
        fig.add_bar(
            x=index,
            y=portfolio_value_list,
            row=1,
            col=1,
            marker=dict(color=portfolio_value_colors.colors),
            name=portfolio_value.name[1],
        )
        fig.add_bar(
            x=index,
            y=expectation,
            row=1,
            col=1,
            marker=dict(color="rgb(179, 179, 179)"),
            name="Expected Net Redemption",
        )
        fig.update_yaxes(ticksuffix="%", row=1, col=1, range=[0, 108])
        fig.update_traces(texttemplate="%{value}", row=1, col=1)

        rcr = pd.Series(portfolio_value_list, index=index) / pd.Series(expectation, index=index) * 100
        rcr = rcr.mask(rcr > 200, 200.00001)
        rcr_colors = rcr.map(lambda x: "#0FFBA6" if x > 200 else "#FC6955" if x < 120 else "#FBE426")
        fig.add_bar(
            x=rcr,
            y=index,
            row=1,
            col=2,
            marker_color=rcr_colors,
            orientation="h",
            text=[f"{val: .0f}%" if val < 200 else f">{val: .0f}%" for val in rcr],
        )
        fig["data"][2].width = 0.6
        fig["data"][2]["showlegend"] = False
        fig.update_xaxes(ticksuffix="%", range=[0, 225], row=1, col=2)

        fig.update_traces(textposition="outside")
        fig.update_layout(
            barmode="group",
            font_size=12,
            uniformtext_mode="hide",
            title_font_size=20,
            yaxis_title="Percent (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="left"),
        )
        return fig

    @staticmethod
    def asset_liquidity_graph(df_aggregate, scenario, method):
        pd.options.plotting.backend = "plotly"
        df = (df_aggregate.loc[:, (scenario, method)] * 100).astype(float).round(2)
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "bar"}, {"type": "table"}]],
            subplot_titles=("Liquidity profile - Breakdown per asset type", "Available Resources (% NAV)"),
        )
        index_bar = df.index.drop("Portfolio", level=0)  # for bar plot, we do not need portfolio (total) value
        for instrument_type in index_bar.get_level_values(0).drop_duplicates()[::-1]:
            series = df.loc[(instrument_type, slice(None))]
            fig.add_bar(name=instrument_type, x=series.index, y=series.values, row=1, col=1)
        fig.update_yaxes(ticksuffix="%", title="Percent (%)", row=1, col=1)

        df_table = df.unstack()  # Asset Type in index ; Time bucket in columns
        df_table = df_table.reindex(df.index.get_level_values(1).drop_duplicates(), axis=1)  # preserve columns order
        df_table = df_table.reindex(df.index.get_level_values(0).drop_duplicates(), axis=0)  # preserve index order
        df_values = df_table.T.values.tolist()
        df_values.insert(0, df_table.index.to_list())  # Index in values for the table.
        fig.add_table(
            header=dict(
                values=df_table.columns.insert(0, "Asset Type").to_list(),
                line_color="darkslategray",
                fill_color="royalblue",
                align=["left", "center"],
                font=dict(color="white", size=12),
                height=50,
            ),
            cells=dict(
                values=df_values,
                line_color="darkslategray",
                align=["left", "center"],
                font=dict(color="black", size=11),
                suffix=[None] + ["%"] * 5,
                fill=dict(color=["paleturquoise", ["lightgrey", "white"]]),
                height=40,
            ),
            row=1,
            col=2,
        )

        fig.update_layout(barmode="stack", legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="left"))

        return fig

    @staticmethod
    def liquidity_bucketing_graph(df_aggregate, scenario):
        pd.options.plotting.backend = "plotly"
        df = (
            (df_aggregate.loc[("Portfolio", slice(None)), (scenario, slice(None))] * 100)
            .astype(float)
            .round(2)
            .droplevel(0)
            .droplevel(0, axis=1)
        )
        df = df.reindex(["waterfall", "slicing"], axis="columns")
        df.rename(
            index={
                "1 day or less": "Very High Liquidity",
                "2-7 days": "High Liquidity",
                "8-15 days": "Medium Liquidity",
                "16-30 days": "Low Liquidity",
                "31-60 days": "Very Low Liquidity",
                "61-180 days": "Almost No Liquidity",
            },
            inplace=True,
        )

        colors = ["green", "lightgreen", "lightblue", "#FC6955", "orange", "red"]
        fig = make_subplots(rows=1, cols=2, subplot_titles=(None, "Delta"))
        fig.add_traces(df.diff().fillna(df).abs().T.plot.bar()["data"], rows=1, cols=1)

        fig.update_layout(
            barmode="group", legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="left"), font_size=10
        )

        for i in range(len(fig["data"])):
            fig["data"][i]["marker"]["color"] = colors[i]

        df = df["waterfall"] - df["slicing"]
        fig2 = df.plot.bar()["data"][0]
        fig2["marker_color"] = colors
        fig2["showlegend"] = False
        fig.add_trace(fig2, row=1, col=2)
        fig.update_yaxes(ticksuffix="%", title="Percent (%)", range=[0, 105])

        return fig

    @staticmethod
    def liability_liquidity_profile_expectations_graph(df_redemption):
        new_index = ["1 day or less", "2-7 days", "8-15 days", "16-30 days", "31-60 days", "61-180 days"]

        def get_expected_values(net=True):
            col_filter = "net_perc_net_red" if net else "net_perc_gross_red"
            expected_redemptions = pd.Series(
                df_redemption.filter(like=col_filter).mean().sort_values().round(4).values, index=new_index
            )
            return expected_redemptions * 100

        expected_net_redemption = get_expected_values(net=True)
        expected_gross_redemption = get_expected_values(net=False)

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Expected Net Redemptions", "Expected Gross Redemptions"))
        fig.add_trace(expected_net_redemption.plot.bar()["data"][0], row=1, col=1)
        fig.add_trace(expected_gross_redemption.plot.bar()["data"][0], row=1, col=2)
        fig.update_yaxes(ticksuffix="%", range=[0, 108])
        fig.update_traces(textposition="outside", texttemplate="%{value}")
        fig.update_layout(
            font_size=12,
            uniformtext_mode="hide",
            title_font_size=20,
            yaxis_title="Percent (%)",
            showlegend=False,
            legend_title="",
        )

        return fig

    @staticmethod
    def liability_liquidity_profile_metrics_graph(df_redemption):
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "table"}, {"type": "table"}]],
            subplot_titles=("Net Redemptions", "Gross Redemptions"),
        )
        df = (df_redemption.filter(like="net_perc").max() * 100).round(1)
        gross = df.filter(like="net_perc_gross").sort_values()
        net = df.filter(like="net_perc_net").sort_values()
        gross_cells = [
            ["Max Daily", "Max Weekly", "Max 2 Weeks", "Max 1 Month", "Max 2 Months", "Max 6 Months"],
            gross.values,
        ]
        net_cells = [
            ["Max Daily", "Max Weekly", "Max 2 Weeks", "Max 1 Month", "Max 2 Months", "Max 6 Months"],
            net.values,
        ]
        fig.add_table(
            columnorder=[1, 2],
            columnwidth=[100, 400],
            header=dict(
                values=["Liquidity Metrics", "Aggregate"],
                line_color="darkslategray",
                fill_color="royalblue",
                align="center",
                font=dict(color="white", size=12),
                height=30,
            ),
            cells=dict(
                values=net_cells,
                line_color="darkslategray",
                align="center",
                font=dict(color="black", size=11),
                suffix=[None] + ["%"],
                fill=dict(color=["paleturquoise", "white"]),
                height=30,
            ),
            row=1,
            col=1,
        )

        fig.add_table(
            columnorder=[1, 2],
            columnwidth=[100, 400],
            header=dict(
                values=["Liquidity Metrics", "Aggregate"],
                line_color="darkslategray",
                fill_color="royalblue",
                align="center",
                font=dict(color="white", size=12),
                height=30,
            ),
            cells=dict(
                values=gross_cells,
                line_color="darkslategray",
                align="center",
                font=dict(color="black", size=11),
                suffix=[None] + ["%"],
                fill=dict(color=["paleturquoise", "white"]),
                height=30,
            ),
            row=1,
            col=2,
        )

        return fig

    @staticmethod
    def liquidity_monitor_stress_testing_tables(df_aggregate, df_redemption, method):
        tmp = df_aggregate.loc[("Portfolio", slice(None)), (slice(None), method)].droplevel(0, axis=0)
        tmp = tmp.mask(tmp < 0, df_aggregate.loc[("Equity", slice(None)), (slice(None), method)].droplevel(0, axis=0))
        df_aggregate = tmp.droplevel(1, axis=1)
        df_redemption = df_redemption.filter(like="net_perc").mean()
        gross = (
            df_redemption.filter(like="net_perc_gross")
            .sort_values()
            .rename(
                index={
                    "net_perc_gross_red": "1 day or less",
                    "net_perc_gross_red 5D": "2-7 days",
                    "net_perc_gross_red 12D": "8-15 days",
                    "net_perc_gross_red 23D": "16-30 days",
                    "net_perc_gross_red 45D": "31-60 days",
                    "net_perc_gross_red 120D": "61-180 days",
                }
            )
        )
        net = (
            df_redemption.filter(like="net_perc_net")
            .sort_values()
            .rename(
                index={
                    "net_perc_net_red": "1 day or less",
                    "net_perc_net_red 5D": "2-7 days",
                    "net_perc_net_red 12D": "8-15 days",
                    "net_perc_net_red 23D": "16-30 days",
                    "net_perc_net_red 45D": "31-60 days",
                    "net_perc_net_red 120D": "61-180 days",
                }
            )
        )
        lcr_vs_net = df_aggregate.div(net, axis=0) * 100
        lcr_vs_net = lcr_vs_net.reindex(df_aggregate.index, axis=0)  # preserve index order
        lcr_vs_net_colors = lcr_vs_net.applymap(
            lambda x: "#0FFBA6" if x > 200 else "#FC6955" if x < 120 else "#FBE426"
        )
        lcr_vs_net = lcr_vs_net.applymap(lambda x: f"{x: .0f}%" if x <= 200 else ">200%")
        lcr_vs_gross = df_aggregate.div(gross, axis=0) * 100
        lcr_vs_gross = lcr_vs_gross.reindex(df_aggregate.index, axis=0)  # preserve index order
        lcr_vs_gross_colors = lcr_vs_gross.applymap(
            lambda x: "#0FFBA6" if x > 200 else "#FC6955" if x < 120 else "#FBE426"
        )
        lcr_vs_gross = lcr_vs_gross.applymap(lambda x: f"{x: .0f}%" if x <= 200 else ">200%")

        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "table"}, {"type": "table"}]],
            subplot_titles=(
                "Liquidity Coverage Ratio (vs net redemptions)",
                "Liquidity Coverage Ratio (vs gross redemptions)",
            ),
        )
        headers = df_aggregate.index.to_list()
        headers.insert(0, "Scenarios")
        net_cells = lcr_vs_net.values.tolist()
        net_cells.insert(0, lcr_vs_net.columns.to_list())
        gross_cells = lcr_vs_gross.values.tolist()
        gross_cells.insert(0, lcr_vs_gross.columns.to_list())

        fig.add_table(
            columnwidth=[50, 40],
            header=dict(
                values=headers,
                line_color="darkslategray",
                fill_color="royalblue",
                align="center",
                font=dict(color="white", size=12),
                height=40,
            ),
            cells=dict(
                values=net_cells,
                line_color="darkslategray",
                align="center",
                font=dict(color="black", size=11),
                fill=dict(color=["paleturquoise"] + lcr_vs_net_colors.values.tolist()),
                height=30,
            ),
            row=1,
            col=1,
        )
        fig.add_table(
            columnwidth=[50, 40],
            header=dict(
                values=headers,
                line_color="darkslategray",
                fill_color="royalblue",
                align="center",
                font=dict(color="white", size=12),
                height=40,
            ),
            cells=dict(
                values=gross_cells,
                line_color="darkslategray",
                align="center",
                font=dict(color="black", size=11),
                fill=dict(color=["paleturquoise"] + lcr_vs_gross_colors.values.tolist()),
                height=30,
            ),
            row=1,
            col=2,
        )

        return fig

    @staticmethod
    def asset_liquidity_profile_stress_testing_bar_char(df_aggregate, method):
        pd.options.plotting.backend = "plotly"
        df = (
            (df_aggregate.loc[("Portfolio", slice(None)), (slice(None), method)] * 100)
            .astype(float)
            .round(2)
            .droplevel(0)
            .droplevel(1, axis=1)
        )
        df = df.drop("Baseline Scenario", axis=1)

        colors = ["green", "lightgreen", "lightblue", "lightsalmon", "orange", "red"]

        fig = df.diff().fillna(df).T.plot.bar()
        fig.update_yaxes(ticksuffix="%", title="Percent (%)", range=[0, 105])
        fig.update_traces(texttemplate="%{value}", textposition="outside")
        fig.update_layout(
            barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", font=dict(size=15), title=""),
        )

        for i in range(len(fig["data"])):
            fig["data"][i]["marker"]["color"] = colors[i]

        return fig

    @staticmethod
    def asset_liquidity_profile_stress_testing_table(df_aggregate, scenario1, scenario2, method):
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "table"}, {"type": "table"}]],
            subplot_titles=(f"{scenario1}", f"{scenario2}"),
        )

        def add_table_to_fig(scenario, col):
            df = (df_aggregate.loc[:, (scenario, method)] * 100).astype(float).round(2)
            df_table = df.unstack().reindex(df.index.get_level_values(0).drop_duplicates())
            df_table = df_table.reindex(df.index.get_level_values(1).drop_duplicates(), axis=1)
            headers = df_table.columns.insert(0, "Asset Type")
            cells_values = df_table.T.values.tolist()
            cells_values.insert(0, df_table.index.to_list())  # Index in values for the table.
            fig.add_table(
                header=dict(
                    values=headers,
                    line_color="darkslategray",
                    fill_color="royalblue",
                    font=dict(color="white", size=12),
                    align="center",
                    height=30,
                ),
                cells=dict(
                    values=cells_values,  # 2nd column
                    line_color="darkslategray",
                    fill_color=["paleturquoise", "white"],
                    font=dict(color="black", size=11),
                    suffix=[None] + ["%"],
                    align="center",
                    height=30,
                ),
                row=1,
                col=col,
            )

        if scenario1:
            add_table_to_fig(scenario1, 1)
        if scenario2:
            add_table_to_fig(scenario2, 2)
        fig.update_layout(height=350)
        return fig

    @staticmethod
    def asset_liquidity_profile_color_table():
        df = pd.DataFrame(
            index=["1 day is needed"] + list(map(lambda x: x + " days are needed", ["2-7", "8-15", "16-30", ">30"])),
            columns=list(map(lambda x: "To liquidate " + str(x) + "% of AUM", [100, 90, 80, 70])),
        )
        df_colors = df.copy()
        df.fillna("", inplace=True)
        df_colors.iloc[0, :] = "#0FFBA6"
        df_colors.loc["2-7 days are needed"] = ["#0FFBA6"] * 3 + ["#FBE426"]
        df_colors.loc["8-15 days are needed"] = ["#0FFBA6"] + ["#FBE426"] * 2 + ["#FC6955"]
        df_colors.loc["16-30 days are needed"] = ["#FBE426"] * 3 + ["#FC6955"]
        df_colors.loc[">30 days are needed"] = ["#FBE426"] + ["#FC6955"] * 3

        fig = go.Figure(
            data=go.Table(
                columnwidth=[3, 2],
                header=dict(
                    values=["Colors"] + df.columns.tolist(),
                    line_color="darkslategray",
                    fill_color="white",
                    align="center",
                    font=dict(color="black", size=12),
                    height=30,
                ),
                cells=dict(
                    values=[df.index.tolist()] + df.T.values.tolist(),
                    line_color="black",
                    fill_color=["white"] + df_colors.T.values.tolist(),
                    align="center",
                    font=dict(color="black", size=11),
                    height=30,
                ),
            )
        )
        return fig

    @staticmethod
    def summary_ratings(series):
        pass

    @staticmethod
    def liability_liquidity_profile_color_table():
        s = pd.Series(
            index=list(map(lambda x: "Redemption Coverage Ratio " + x, [">200%", "120%-200%", "<120%"])), dtype=float
        )
        s_colors = s.copy()
        s.fillna("", inplace=True)
        s_colors.iat[0] = "#0FFBA6"
        s_colors.iat[1] = "#FBE426"
        s_colors.iat[2] = "#FC6955"

        fig = go.Figure(
            data=go.Table(
                header=dict(height=0),
                cells=dict(
                    values=[s.index.tolist()] + [s.values.tolist()],
                    line_color="black",
                    fill_color=["white"] + [s_colors.values.tolist()],
                    align="center",
                    font=dict(color="black", size=11),
                    height=30,
                ),
            )
        )
        return fig

    """ The main function for the liquidity stress tests """

    def liquidity_stress_test(
        self,
        report_date: Optional[date] = None,
        weights_date: Optional[date] = None,
        liq_factor: float = 1 / 3,
        below_x_days: int = 5,
    ) -> dict:
        if not (product_ids := self.get_product_ids_from_group_product_or_product()):
            # In the case the model is not a Product or ProductGroup, we return an empty DataFrame
            return dict()

        # We test if a date is None, if yes, we stop the code to avoid errors.
        # Weights date cannot being after report date.
        # if report_date is None or weights_date > report_date:
        if weights_date > report_date:
            return dict()

        assets = self.portfolio.assets.filter(date=weights_date)
        qs_assets = assets.order_by("underlying_instrument")
        if not qs_assets.exists():
            return dict()

        assets_fields = [
            "date",
            "underlying_instrument__id",
            "underlying_instrument__instrument_type",
            "total_value_fx_usd",
            "weighting",
            "shares",
        ]
        df_assets = (
            pd.DataFrame(list(qs_assets.values_list(*assets_fields)), columns=assets_fields)
            .rename(
                {
                    "underlying_instrument__instrument_type": "type",
                    "underlying_instrument__id": "instrument",
                    "total_value_fx_usd": "total_value_usd",
                },
                axis=1,
            )
            .set_index("instrument")
            .astype(dtype={"shares": "float", "total_value_usd": "float", "weighting": "float"})
        )
        instrument_ids = df_assets.index.unique("instrument")
        start_date = date(2000, 1, 1)
        qs_prices = (
            InstrumentPrice.objects.filter(
                calculated=False,
                date__gte=start_date,
                date__lte=weights_date,
                instrument__in=instrument_ids,
            )
            .annotate_base_data()
            .order_by("date", "instrument")
            .select_related("currency_fx_rate_to_usd")
        )
        if not qs_prices.exists():
            return {}

        price_fields = ["date", "instrument", "net_value_usd", "volume_usd", "volume"]
        df_prices = pd.DataFrame(list(qs_prices.values_list(*price_fields)), columns=price_fields)
        df_prices.set_index(["date", "instrument"], inplace=True)
        df_prices = df_prices.astype(float)

        qs_fdm = InstrumentFDM.objects.filter(pms_instrument__in=instrument_ids)
        if not qs_fdm.exists():
            return {}

        df_instrument_eq = pd.DataFrame(
            list(qs_fdm.values_list("id", "pms_instrument")), columns=["id", "pms_instrument"]
        )
        df_instrument_eq.rename(columns={"id": "instrument_id"}, inplace=True)
        df_ask_bid = pd.DataFrame(qs_fdm.dl.market_data(values=[MarketData.ASK, MarketData.BID], from_date=start_date))
        if df_ask_bid.empty:
            return {}
        df_ask_bid = df_ask_bid.join(df_instrument_eq.set_index("instrument_id"), on="instrument_id")
        df_ask_bid = df_ask_bid[["ask", "bid", "pms_instrument", "valuation_date", "currency"]]
        df_ask_bid.rename(columns={"valuation_date": "date", "pms_instrument": "instrument"}, inplace=True)
        qs_fx_rate = CurrencyFXRates.objects.filter(
            currency__key__in=df_ask_bid.currency.unique(),
            date__gte=date(2000, 1, 1),
            date__lte=weights_date,
        )
        if not qs_fx_rate.exists():
            return {}
        currency_fields = ["date", "currency__key", "value"]
        df_fx_rates = pd.DataFrame(list(qs_fx_rate.values_list(*currency_fields)), columns=currency_fields)
        df_fx_rates.rename(columns={"currency__key": "currency", "value": "fx_rate"}, inplace=True)
        df_fx_rates.set_index(["date", "currency"], inplace=True)
        df_ask_bid = df_ask_bid.join(df_fx_rates, on=["date", "currency"]).dropna()
        if df_ask_bid.empty:
            return {}

        df_ask_bid = df_ask_bid.set_index(["date", "instrument"]).drop("currency", axis=1).astype(float)
        df_ask_bid.loc[:, ["bid", "ask"]] = df_ask_bid.loc[:, ["bid", "ask"]].div(df_ask_bid.fx_rate, axis=0)
        df_ask_bid.drop(columns="fx_rate", inplace=True)

        if not qs_prices.exists() or df_ask_bid.empty:
            return dict()

        df_prices = pd.concat([df_prices, df_ask_bid], axis=1).sort_index()
        df_prices.rename(columns={"volume_usd": "dollar_volume"}, inplace=True)

        df_assets.type = df_assets.type.replace("Index", "Cash")
        df_assets = df_assets.set_index("type", append=True).swaplevel().sort_index()

        # cleaning volumes
        df_prices.dollar_volume = df_prices.dollar_volume.where(df_prices.dollar_volume > 10000)
        df_prices.volume = df_prices.where(df_prices.dollar_volume.notnull()).volume

        df_prices["bid_ask_spread"] = (df_prices.ask - df_prices.bid) / df_prices.ask

        qs_product_price = InstrumentPrice.objects.filter(
            calculated=True, date__lte=report_date, instrument__in=product_ids
        ).order_by("date", "instrument")
        if not qs_product_price.exists():
            return dict()

        product_fields = ["date", "instrument", "net_value_usd", "outstanding_shares"]
        df_products_price = (
            pd.DataFrame(list(qs_product_price.values(*product_fields)), columns=product_fields)
            .set_index(["date", "instrument"])
            .astype(float)
            .groupby(level=["date", "instrument"])
            .ffill()
        )
        df_products_price["aum"] = df_products_price.outstanding_shares * df_products_price.net_value_usd
        df_aum = df_products_price.groupby(level="date").aum.sum().replace(0, method="ffill").to_frame()
        from wbportfolio.models.transactions.trades import Trade

        qs_trades = Trade.objects.filter(
            underlying_instrument__in=product_ids,
            type__in=["SUBSCRIPTION", "REDEMPTION"],
            transaction_date__lte=report_date,
        ).order_by("transaction_date")
        if not qs_trades.exists():
            return {}

        trades_fields = [
            "transaction_date",
            "type",
            "underlying_instrument",
            "underlying_instrument__currency",
            "total_value",
        ]
        df_trades = (
            pd.DataFrame(list(qs_trades.values_list(*trades_fields)), columns=trades_fields)
            .rename({"underlying_instrument__currency": "currency", "transaction_date": "date"}, axis=1)
            .set_index(["date", "currency", "underlying_instrument"])
            .astype(dtype={"total_value": "float"})
        )
        qs_fx_rate = CurrencyFXRates.objects.filter(
            currency__in=df_trades.index.unique("currency"),
            date__in=df_trades.index.unique("date"),
        ).order_by("date", "currency")
        fx_rates_fields = ["date", "currency", "value"]
        df_fx_rates = pd.DataFrame(list(qs_fx_rate.values_list(*fx_rates_fields)), columns=fx_rates_fields)
        df_fx_rates.rename(columns={"value": "fx_rate"}, inplace=True)
        df_trades = df_trades.join(df_fx_rates.set_index(["date", "currency"]).astype(float))
        df_trades["total_value_usd"] = df_trades.total_value / df_trades.fx_rate
        df_trades = df_trades.droplevel(level="currency")
        accumulated_days_list = [5, 12, 23, 45, 120]

        # df_trades.transaction_date = pd.to_datetime(df_trades["transaction_date"])  # to use df.rolling
        # Gross Redemption
        df_gross_redemption = df_trades.where(df_trades.type == "REDEMPTION")
        df_gross_redemption = df_gross_redemption.groupby("date").total_value_usd.sum()
        df_gross_redemption.name = "gross_redemption"
        df_gross_redemption = df_aum.join(df_gross_redemption)
        df_gross_redemption.gross_redemption = df_gross_redemption.gross_redemption.fillna(0)
        df_gross_redemption["net_perc_gross_red"] = abs(df_gross_redemption.gross_redemption) / df_gross_redemption.aum
        for acc_days in accumulated_days_list:
            df_gross_redemption[f"net_perc_gross_red {acc_days}D"] = df_gross_redemption.net_perc_gross_red.rolling(
                acc_days
            ).sum()

        # Net Redemption
        df_trades_by_day = df_trades.groupby("date").total_value_usd.sum()
        df_net_redemption = df_trades_by_day.where(df_trades_by_day < 0)
        df_net_redemption.name = "net_redemption"
        df_net_redemption = df_aum.join(df_net_redemption)
        df_net_redemption.net_redemption = df_net_redemption.net_redemption.fillna(0)
        df_net_redemption.loc[:, "net_perc_net_red"] = abs(df_net_redemption.net_redemption) / df_net_redemption.aum

        # Accumulated net percent redemption for both - gross and net.
        for acc_days in accumulated_days_list:
            df_net_redemption[f"net_perc_net_red {acc_days}D"] = df_net_redemption.net_perc_net_red.rolling(
                acc_days
            ).sum()
        cols_to_use = df_net_redemption.columns.difference(df_gross_redemption.columns)[::-1]
        df_redemptions = pd.concat([df_gross_redemption, df_net_redemption[cols_to_use]], axis=1)

        expected_net_redemption = df_redemptions.filter(like="net_perc_net_red").mean().sort_values().round(4)
        gross_total_portfolio_value_usd = df_assets.total_value_usd.sum()
        net_total_portfolio_value_usd = df_redemptions.aum.values[-1]  # which is for the report date
        df_assets.loc[:, "weighting"] = df_assets.loc[:, "total_value_usd"] / df_assets.loc[:, "total_value_usd"].sum()
        df_volumes = df_prices.volume.unstack("date")
        df_dollar_volume = df_prices.dollar_volume.unstack("date")
        df_bid_ask_spread = df_prices.bid_ask_spread.unstack("date")
        days_to_liquidate = self.get_volumes_from_scenario_stress_test(weights_date, df_volumes, df_assets, liq_factor)
        average_worst_dollar_volume = self.get_percentile_worst_dollar_volume(df_dollar_volume, method="other")
        rst_analysis = self.reverse_stress_test(
            gross_total_portfolio_value_usd, df_assets, average_worst_dollar_volume, liq_factor, below_x_days
        )
        stress_tests_analysis = self.stress_volume_bid_ask_test(
            df_assets, df_dollar_volume, df_volumes, df_bid_ask_spread, liq_factor
        )
        days_to_liquidate = days_to_liquidate.join(stress_tests_analysis)
        days_to_liquidate.loc[("Cash", slice(None))] = 0  # cash is instantaneous

        tmp = df_assets.loc[:, "weighting"].to_frame(name=("instrument", "weighting")).copy()
        days_to_liquidate = days_to_liquidate.join(tmp)
        df_aggregate = self.aggregate_days_to_liquidate(days_to_liquidate)

        portfolio_waterfall_baseline = df_aggregate.loc[
            ("Portfolio", slice(None)), ("Baseline Scenario", "waterfall")
        ].droplevel(0, axis=0)
        portfolio_slicing_baseline = df_aggregate.loc[
            ("Portfolio", slice(None)), ("Baseline Scenario", "slicing")
        ].droplevel(0, axis=0)
        portfolio_risk_waterfall = self.series_of_colors(portfolio_waterfall_baseline)
        portfolio_risk_slicing = self.series_of_colors(portfolio_slicing_baseline)

        asset_liquidity_message = ""
        asset_liquidity_color = "#0FFBA6"
        if not portfolio_risk_waterfall.message.dropna().empty:
            asset_liquidity_message = portfolio_risk_waterfall.message.dropna().iat[0]
            asset_liquidity_color = portfolio_risk_waterfall.dropna().colors.iat[0]
        elif not portfolio_risk_slicing.message.dropna().empty:
            asset_liquidity_message = portfolio_risk_slicing.message.dropna().iat[0]
            asset_liquidity_color = portfolio_risk_slicing.dropna().colors.iat[0]

        liability_slicing = pd.DataFrame(portfolio_slicing_baseline.values / expected_net_redemption.values)
        color_slicing = "#0FFBA6"
        if not liability_slicing.where((liability_slicing < 2) & (liability_slicing >= 1.2)).dropna().empty:
            color_slicing = "#FBE426"
        elif not liability_slicing.where(liability_slicing < 1.2).dropna().empty:
            color_slicing = "#FC6955"
        # ------------- PLOTLY GRAPHS ------------------ #
        # BASELINE SCENARIO WATERFALL FIGURE
        fig1 = self.liquidity_monitor_graph(portfolio_waterfall_baseline, expected_net_redemption)

        fig2 = self.liquidity_monitor_graph(portfolio_slicing_baseline, expected_net_redemption)

        fig4 = self.asset_liquidity_graph(df_aggregate, "Baseline Scenario", "waterfall")

        fig5 = self.asset_liquidity_graph(df_aggregate, "Baseline Scenario", "slicing")

        fig6 = self.liquidity_bucketing_graph(df_aggregate, "Baseline Scenario")

        fig7 = self.liability_liquidity_profile_expectations_graph(df_redemptions)

        fig8 = self.liability_liquidity_profile_metrics_graph(df_redemptions)

        fig9 = self.liquidity_monitor_stress_testing_tables(df_aggregate, df_redemptions, "waterfall")

        fig10 = self.liquidity_monitor_stress_testing_tables(df_aggregate, df_redemptions, "slicing")

        fig11 = self.asset_liquidity_profile_stress_testing_bar_char(df_aggregate, "waterfall")

        fig12 = self.asset_liquidity_profile_stress_testing_table(df_aggregate, "COVID-19", "Lehman", "waterfall")
        fig13 = self.asset_liquidity_profile_stress_testing_table(
            df_aggregate, "Lehman Spring", "Debt Crisis", "waterfall"
        )
        fig14 = self.asset_liquidity_profile_stress_testing_table(df_aggregate, "China Crisis", "Dotcom", "waterfall")
        fig15 = self.asset_liquidity_profile_stress_testing_table(
            df_aggregate, "Volume falls by 60 pct", "S-T Worst Volume", "waterfall"
        )
        fig16 = self.asset_liquidity_profile_stress_testing_table(df_aggregate, "S-T Worst B-A", None, "waterfall")

        fig17 = self.asset_liquidity_profile_stress_testing_bar_char(df_aggregate, "slicing")

        fig18 = self.asset_liquidity_profile_stress_testing_table(df_aggregate, "COVID-19", "Lehman", "slicing")
        fig19 = self.asset_liquidity_profile_stress_testing_table(
            df_aggregate, "Lehman Spring", "Debt Crisis", "slicing"
        )
        fig20 = self.asset_liquidity_profile_stress_testing_table(df_aggregate, "China Crisis", "Dotcom", "slicing")
        fig21 = self.asset_liquidity_profile_stress_testing_table(
            df_aggregate, "Volume falls by 60 pct", "S-T Worst Volume", "slicing"
        )
        fig22 = self.asset_liquidity_profile_stress_testing_table(df_aggregate, "S-T Worst B-A", None, "slicing")

        # ------------- RST FIGURE -------------------------- #

        # Create figure
        fig3 = go.Figure()
        # Add traces, one for each slider step
        for col_i, col in enumerate(rst_analysis.columns.unique(0), start=1):
            fig3.add_trace(
                go.Surface(
                    visible=False,
                    colorscale=[
                        (0, "rgb(166,206,227)"),
                        (0.1, "rgb(227,26,28)"),
                        (0.6999, "rgb(251,154,153)"),
                        (0.70, "rgb(247,224,45)"),
                        (0.80, "rgb(247,224,45)"),
                        (0.80001, "rgb(178,223,138)"),
                        (1, "rgb(51,160,44)"),
                    ],
                    name="Aum x" + str(col_i),
                    z=(rst_analysis.loc[:, (col, slice(None))] * 100).round(2).values,
                    hovertemplate=(
                        "<br><b>% Weights sold:: %{z}%</b><br>"
                        + "<br>% Redemption: %{x}%<br>"
                        + "<br>% Worst Dollar Volume: %{y}%<br>"
                    ),
                )
            )

        # Make 10th trace visible
        fig3.data[0].visible = True

        # Create and add slider
        steps = []
        for i in range(len(fig3.data)):
            step = dict(
                method="update",
                args=[
                    {"visible": [False] * len(fig3.data)},
                    {
                        "title": "Slider switched to AUM x "
                        + str(i + 1)
                        + " = $"
                        + str(round((i + 1) * net_total_portfolio_value_usd / 10**6))
                        + "M"
                    },
                ],  # layout attribute
            )
            step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
            steps.append(step)

        sliders = [dict(active=0, currentvalue={"prefix": "AUM: "}, pad={"t": 50}, steps=steps)]

        fig3.update_layout(
            sliders=sliders,
            scene=dict(xaxis_title="% Redemption", yaxis_title="% Worst Dollar Volume", zaxis_title="% Weights sold"),
        )

        # Edit slider labels
        fig3["layout"]["sliders"][0]["currentvalue"]["prefix"] = "AUM x "
        for i in range(len(rst_analysis.columns.get_level_values(0).drop_duplicates())):
            fig3["layout"]["sliders"][0]["steps"][i]["label"] = i + 1
        nb_of_holdings = len(df_assets.loc[(df_assets.index.get_level_values("type") != "Cash", slice(None))])
        _dict = {
            "report_date": report_date,
            "weights_date": weights_date,
            "name": self.portfolio.name,
            "currency": self.portfolio.currency.key,
            "nb_of_holdings": nb_of_holdings,
            "total": f"{round(net_total_portfolio_value_usd):,}".replace(",", "'"),
            "asset_liquidity_message": asset_liquidity_message,
            "asset_liquidity_color": asset_liquidity_color,
            "liability_liquidity_color": color_slicing,
            "fig1": fig1,
            "fig2": fig2,
            "fig3": fig3,
            "fig4": fig4,
            "fig5": fig5,
            "fig6": fig6,
            "fig7": fig7,
            "fig8": fig8,
            "fig9": fig9,
            "fig10": fig10,
            "fig11": fig11,
            "fig12": fig12,
            "fig13": fig13,
            "fig14": fig14,
            "fig15": fig15,
            "fig16": fig16,
            "fig17": fig17,
            "fig18": fig18,
            "fig19": fig19,
            "fig20": fig20,
            "fig21": fig21,
            "fig22": fig22,
            "fig23": self.asset_liquidity_profile_color_table(),
            "fig24": self.liability_liquidity_profile_color_table(),
        }
        return _dict

    def pct_liquidated_below_n_days(
        self,
        evaluation_date: date,
        below_n_days: int = 5,
        liq_factor: float = 1 / 3,
        pct_worst_volume: int = 100,
        pct_redemption: int = 100,
        last_x_trading_dates: int = 60,
        is_slicing: bool = True,
    ) -> [float, None]:
        # Allows to get ids from all share classes if product is a group of product,
        # otherwise it just returns the product id.
        if not (product_ids := self.get_product_ids_from_group_product_or_product()):
            return None

        aum = float(self.get_redemption_analysis_df(product_ids=product_ids, report_date=evaluation_date).AUM.iat[-1])

        qs_assets = self.portfolio.assets.filter(date=evaluation_date)

        if not qs_assets:
            return None

        qs_assets = (
            self.portfolio.assets.filter(date=evaluation_date)
            .order_by("underlying_instrument")
            .values("underlying_instrument", "underlying_instrument__instrument_type", "weighting")
        )

        df_assets = (
            pd.DataFrame(qs_assets)
            .rename(columns={"underlying_instrument__instrument_type": "instrument_type"})
            .set_index("underlying_instrument")
            .astype({"weighting": "float"})
        )

        first_trading_date = (evaluation_date - BDay(last_x_trading_dates)).date()

        qs_price = (
            InstrumentPrice.objects.filter(
                instrument__in=df_assets.index, date__gte=first_trading_date, date__lte=evaluation_date
            )
            .order_by("date", "instrument")
            .values("date", "instrument__currency", "instrument", "net_value", "volume")
        )

        df_prices = (
            pd.DataFrame(qs_price)
            .rename(columns={"instrument__currency": "currency"})
            .set_index(["date", "currency", "instrument"])
        )

        qs_currencies = (
            CurrencyFXRates.objects.filter(
                currency__in=df_prices.index.get_level_values("currency"),
                date__gte=first_trading_date,
                date__lte=evaluation_date,
            )
            .order_by("date", "currency__id")
            .values("date", "currency", "value")
        )
        df_currencies = pd.DataFrame(qs_currencies).set_index(["date", "currency"])
        df_prices = df_prices.join(df_currencies)
        df_prices["net_value_usd"] = df_prices.net_value / df_prices.value
        df_prices["dollar_volume"] = df_prices.net_value_usd * df_prices.volume

        dollar_volume = (
            df_prices.dollar_volume.where(df_prices.dollar_volume > 10000).dropna().droplevel("currency").unstack()
        )

        average_worst_dollar_volume = dollar_volume.where(
            dollar_volume.le(dollar_volume.astype(float).quantile(pct_worst_volume / 100))
        ).mean()

        days_to_liquidate = below_n_days / (
            aum * pct_redemption / 100 * df_assets.weighting / (liq_factor * average_worst_dollar_volume)
        )

        if is_slicing:  # if False, computations are done for Waterfall already.
            days_to_liquidate.loc[
                df_assets[(df_assets.instrument_type != "Cash") & (df_assets.instrument_type != "Index")].index
            ] = days_to_liquidate.min()

        weights_sold = days_to_liquidate.mask(days_to_liquidate > 1, 1).mul(df_assets.weighting).sum()
        weights_sold += df_assets.loc[
            df_assets[(df_assets.instrument_type.key == "cash") | (df_assets.instrument_type.key == "index")].index,
            "weighting",
        ].sum()

        # readable_result = f"{round(weights_sold * 100, 2)}%"
        return weights_sold
