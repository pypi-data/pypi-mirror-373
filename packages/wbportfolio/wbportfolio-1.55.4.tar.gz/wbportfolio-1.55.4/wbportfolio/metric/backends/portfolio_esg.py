from typing import Generator

import pandas as pd
from wbfdm.analysis.esg.enums import ESGAggregation
from wbfdm.analysis.esg.esg_analysis import DataLoader, get_esg_df
from wbfdm.contrib.metric.decorators import register
from wbfdm.contrib.metric.dto import Metric, MetricField, MetricKey

from wbportfolio.models import Portfolio

from .base import PortfolioMetricBaseBackend
from .portfolio_base import DataLoader as PortfolioDataLoader


def _generate_metric_key_from_enum():
    metric_keys = []
    for key, label in ESGAggregation.choices():
        metric_keys.append(
            MetricKey(
                key=f"portfolio_esg_{key.lower()}",
                label=label,
                subfields=[
                    MetricField(key="score", label="Score"),
                ],
            )
        )
    return metric_keys


PORTFOLIO_ESG_KEYS = _generate_metric_key_from_enum()


@register()
class PortfolioESGMetricBackend(PortfolioMetricBaseBackend):
    keys = PORTFOLIO_ESG_KEYS

    def _get_metrics_for_esg_aggregation(
        self, instruments, weights: pd.Series, total_value_fx_usd: pd.Series, esg_aggregation: ESGAggregation
    ) -> pd.Series:
        dl = DataLoader(
            weights, get_esg_df(instruments, esg_aggregation.get_esg_code()), self.val_date, total_value_fx_usd
        )
        df = dl.compute(esg_aggregation)

        return df.rename("score").to_frame()

    def compute_metrics(self, basket: Portfolio) -> Generator[Metric, None, None]:
        val_date = self._get_valid_date(basket)
        portfolio_dataloader = PortfolioDataLoader(basket, val_date)
        base_df = portfolio_dataloader.base_df

        if not base_df.empty:
            for esg in ESGAggregation:
                df = self._get_metrics_for_esg_aggregation(
                    portfolio_dataloader.instruments, base_df["weighting"], base_df["total_value_fx_usd"], esg
                )
                df_aggregated = df.sum(axis=0)
                metrics = self.convert_df_into_metrics(df, f"portfolio_esg_{esg.name.lower()}", basket.id, val_date)
                aggregated_metrics = self.convert_df_into_metrics(
                    df_aggregated,
                    f"portfolio_esg_{esg.name.lower()}",
                    basket.id,
                    val_date,
                    dependency_metrics=metrics,
                )
                yield from metrics
                yield from aggregated_metrics
