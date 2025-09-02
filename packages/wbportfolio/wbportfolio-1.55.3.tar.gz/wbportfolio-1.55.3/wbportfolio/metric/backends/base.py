from datetime import date

import numpy as np
import pandas as pd
from django.db.models import QuerySet
from wbfdm.contrib.metric.backends.base import AbstractBackend, Metric
from wbfdm.contrib.metric.exceptions import MetricInvalidParameterException

from wbportfolio.models import AssetPosition, Portfolio


class PortfolioMetricBaseBackend(AbstractBackend[Portfolio]):
    BASKET_MODEL_CLASS = Portfolio

    def convert_df_into_metrics(
        self,
        df: pd.DataFrame | pd.Series,
        key: str,
        portfolio_id: int,
        metric_date: date,
        columns_map: dict[int | str, str] | None = None,
        dependency_metrics: list["Metric"] | None = None,
    ) -> list[Metric]:
        if not dependency_metrics:
            dependency_metrics = []
        metrics = []
        df = df.replace([np.inf, -np.inf, np.nan], None)
        if isinstance(df, pd.DataFrame):
            if columns_map:
                df = df.rename(columns=columns_map)
            for instrument_id, metric in df.to_dict("index").items():
                metrics.append(
                    Metric(
                        basket_id=portfolio_id,
                        basket_content_type_id=self.content_type.id,
                        key=key,
                        metrics=metric,
                        date=metric_date,
                        instrument_id=instrument_id,
                        dependency_metrics=dependency_metrics,
                    )
                )
        else:
            if columns_map:
                df = df.rename(index=columns_map)
            metrics.append(
                Metric(
                    basket_id=portfolio_id,
                    basket_content_type_id=self.content_type.id,
                    key=key,
                    metrics=df.to_dict(),
                    date=metric_date,
                    dependency_metrics=dependency_metrics,
                )
            )
        return metrics

    def _get_valid_date(self, portfolio):
        qs = portfolio.assets.filter(is_estimated=False)
        if self.val_date is not None:
            qs = qs.filter(date__lte=self.val_date)
        try:
            return qs.latest("date").date
        except AssetPosition.DoesNotExist:
            raise MetricInvalidParameterException()

    def get_queryset(self) -> QuerySet[Portfolio]:
        product_portfolios = super().get_queryset().filter_active_and_tracked()
        try:
            last_position_date = (
                AssetPosition.objects.filter(portfolio__in=product_portfolios, is_estimated=False).latest("date").date
            )
        except AssetPosition.DoesNotExist:
            last_position_date = date.today()
        return product_portfolios.filter_invested_at_date(last_position_date)
