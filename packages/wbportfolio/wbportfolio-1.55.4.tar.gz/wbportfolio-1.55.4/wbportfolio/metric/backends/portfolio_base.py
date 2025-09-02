from contextlib import suppress
from datetime import date
from typing import Generator

import pandas as pd
from django.db.models import Q
from django.utils.functional import cached_property
from wbfdm.contrib.metric.backends.base import Metric
from wbfdm.contrib.metric.decorators import register
from wbfdm.enums import Financial, MarketData
from wbfdm.models import Instrument

from wbportfolio.models import Portfolio

from .base import PortfolioMetricBaseBackend
from .constants import (
    PORTFOLIO_CAPITAL_EMPLOYED,
    PORTFOLIO_EBIT,
    PORTFOLIO_LIABILITIES,
    PORTFOLIO_ROCE,
    PORTFOLIO_TOTAL_ASSETS,
)


class DataLoader:
    def __init__(
        self, portfolio: Portfolio, val_date: date, past_offset: int = 4, forecast_offset: int = 4, freq: str = "YE"
    ):
        self.portfolio = portfolio
        self.val_date = val_date
        self.instruments = Instrument.objects.filter(id__in=self.base_df.index)
        self.past_offset = past_offset
        self.forecast_offset = forecast_offset
        self.pivot_dates = list(
            pd.date_range(end=self.val_date, periods=self.past_offset, freq=freq, inclusive="left")
        ) + list(pd.date_range(start=self.val_date, periods=self.past_offset, freq=freq, inclusive="right"))
        self.columns_map = {
            self.val_date.year + offset: f"fy{offset + 1}".replace("-", "_")
            for offset in range(-1 * self.past_offset, self.forecast_offset)
        }
        self.from_year = self.val_date.year - self.past_offset
        self.to_year = self.val_date.year + self.forecast_offset - 1

        self.empty_series = pd.Series(dtype="float64")

    def _get_financial_df(self, financial: Financial, target_currency: str = "USD", **kwargs) -> pd.DataFrame:
        """
        Private helper method to gather necessary financial data from the finanical dataloader and pivot it into Instrument*Years format

        Args:
            financial: Financial Metric
            target_currency: Target currency
            **kwargs: fdm datalaoder keyword argument

        Returns:
            A dataframe whose index is the instrument ids and columns are the years offsets
        """

        df = pd.DataFrame(
            self.instruments.dl.financials(
                values=[financial],
                from_year=self.from_year,
                to_year=self.to_year,
                target_currency=target_currency,
                **kwargs,
            )
        )
        if df.empty:
            raise ValueError(f"No financial data for {financial.value}")
        return df.pivot_table(index="instrument_id", values="value", columns="year", aggfunc="first")

    # Data Input
    @cached_property
    def market_capitalization_df(self) -> pd.DataFrame:
        df_list = []
        for pivot_date in self.pivot_dates:
            try:
                mkt_caps = pd.DataFrame(
                    self.instruments.dl.market_data(
                        values=[MarketData.MARKET_CAPITALIZATION],
                        from_date=(pivot_date - pd.tseries.offsets.BDay(3)).date(),
                        to_date=pivot_date,
                        target_currency="USD",
                    )
                )
                res = (
                    mkt_caps[["instrument_id", "market_capitalization"]]
                    .groupby("instrument_id")
                    .last()["market_capitalization"]
                ).astype(float)
            except KeyError:
                res = self.empty_series
            res = res.rename(pivot_date.year)
            df_list.append(res)
        return pd.concat(df_list, axis=1).ffill(axis=1)

    @cached_property
    def ebit_usd_df(self) -> pd.DataFrame:
        return self._get_financial_df(Financial.EBIT)

    @cached_property
    def total_assets_usd_df(self) -> pd.DataFrame:
        return self._get_financial_df(Financial.TOTAL_ASSETS)

    @cached_property
    def liabilities_usd_df(self) -> pd.DataFrame:
        return self._get_financial_df(Financial.CURRENT_LIABILITIES)

    # Generate basic portfolio data as a dataframe
    @cached_property
    def base_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            self.portfolio.assets.filter(date=self.val_date)
            .exclude(Q(underlying_instrument__is_cash=True) | Q(underlying_instrument__is_cash_equivalent=True))
            .values("underlying_instrument", "shares", "price_fx_usd", "total_value_fx_usd", "weighting"),
            columns=["underlying_instrument", "shares", "price_fx_usd", "total_value_fx_usd", "weighting"],
        )
        df = (
            df.groupby("underlying_instrument")
            .agg(
                {
                    "shares": "sum",
                    "price_fx_usd": "first",
                    "total_value_fx_usd": "sum",
                    "weighting": "sum",
                }
            )
            .astype(float)
        )
        df["weighting"] = df["weighting"] / df["weighting"].sum()
        df.index = df.index.rename("instrument_id")
        return df

    # Portfolio Metrics

    @cached_property
    def portfolio_ownership_df(self) -> pd.DataFrame:
        return (1.0 / self.market_capitalization_df).multiply(self.base_df.total_value_fx_usd, axis=0)

    @cached_property
    def portfolio_ebit_usd_df(self) -> pd.DataFrame:
        df = self.portfolio_ownership_df * self.ebit_usd_df
        df.aggregate = df.sum(axis=0)
        return df

    @cached_property
    def portfolio_total_assets_usd_df(self) -> pd.DataFrame:
        df = self.portfolio_ownership_df * self.total_assets_usd_df
        df.aggregate = df.sum(axis=0)
        return df

    @cached_property
    def portfolio_liabilities_usd_df(self) -> pd.DataFrame:
        df = self.portfolio_ownership_df * self.liabilities_usd_df
        df.aggregate = df.sum(axis=0)
        return df

    @cached_property
    def portfolio_aggregation_capital_employed(self) -> pd.Series:
        return self.portfolio_total_assets_usd_df.aggregate - self.portfolio_liabilities_usd_df.aggregate

    @cached_property
    def portfolio_aggregation_roce(self) -> pd.Series:
        return self.portfolio_ebit_usd_df.aggregate / self.portfolio_aggregation_capital_employed.rolling(2).mean()


@register()
class PortfolioBaseMetricBackend(PortfolioMetricBaseBackend):
    portfolio_ebit = PORTFOLIO_EBIT
    portfolio_total_assets = PORTFOLIO_TOTAL_ASSETS
    portfolio_liabilities = PORTFOLIO_LIABILITIES
    portfolio_capital_employed = PORTFOLIO_CAPITAL_EMPLOYED
    portfolio_roce = PORTFOLIO_ROCE

    keys = [
        PORTFOLIO_EBIT,
        PORTFOLIO_TOTAL_ASSETS,
        PORTFOLIO_LIABILITIES,
        PORTFOLIO_CAPITAL_EMPLOYED,
        PORTFOLIO_ROCE,
    ]

    def compute_metrics(self, basket: Portfolio) -> Generator[Metric, None, None]:
        val_date = self._get_valid_date(basket)
        dataloader = DataLoader(basket, val_date)

        # Load all necessary metrics into a Metric DTO from the dataloader
        with suppress(ValueError):
            portfolio_ebit_metrics = self.convert_df_into_metrics(
                dataloader.portfolio_ebit_usd_df,
                "portfolio_ebit",
                dataloader.portfolio.id,
                val_date,
                columns_map=dataloader.columns_map,
            )
            portfolio_aggregation_ebit_metrics = self.convert_df_into_metrics(
                dataloader.portfolio_ebit_usd_df.aggregate,
                "portfolio_ebit",
                dataloader.portfolio.id,
                val_date,
                columns_map=dataloader.columns_map,
                dependency_metrics=portfolio_ebit_metrics,
            )

            portfolio_total_assets_metrics = self.convert_df_into_metrics(
                dataloader.portfolio_total_assets_usd_df,
                "portfolio_total_assets",
                dataloader.portfolio.id,
                val_date,
                columns_map=dataloader.columns_map,
            )
            portfolio_aggregation_total_assets_metrics = self.convert_df_into_metrics(
                dataloader.portfolio_total_assets_usd_df.aggregate,
                "portfolio_total_assets",
                dataloader.portfolio.id,
                val_date,
                columns_map=dataloader.columns_map,
                dependency_metrics=portfolio_total_assets_metrics,
            )

            portfolio_liabilities_metrics = self.convert_df_into_metrics(
                dataloader.portfolio_liabilities_usd_df,
                "portfolio_liabilities",
                dataloader.portfolio.id,
                val_date,
                columns_map=dataloader.columns_map,
            )
            portfolio_aggregation_liabilities_metrics = self.convert_df_into_metrics(
                dataloader.portfolio_liabilities_usd_df.aggregate,
                "portfolio_liabilities",
                dataloader.portfolio.id,
                val_date,
                columns_map=dataloader.columns_map,
                dependency_metrics=portfolio_liabilities_metrics,
            )

            portfolio_aggregation_capital_metrics = self.convert_df_into_metrics(
                dataloader.portfolio_aggregation_capital_employed,
                "portfolio_capital_employed",
                dataloader.portfolio.id,
                val_date,
                columns_map=dataloader.columns_map,
                dependency_metrics=portfolio_aggregation_total_assets_metrics
                + portfolio_aggregation_liabilities_metrics,
            )

            portfolio_aggregation_roce_metrics = self.convert_df_into_metrics(
                dataloader.portfolio_aggregation_roce,
                "portfolio_roce",
                dataloader.portfolio.id,
                val_date,
                columns_map=dataloader.columns_map,
                dependency_metrics=portfolio_aggregation_ebit_metrics + portfolio_aggregation_capital_metrics,
            )

            yield from portfolio_aggregation_roce_metrics
