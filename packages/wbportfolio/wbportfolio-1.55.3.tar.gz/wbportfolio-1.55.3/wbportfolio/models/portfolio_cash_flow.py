from contextlib import suppress
from decimal import Decimal

from django.db import models
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.models import WBModel

from wbportfolio.import_export.handlers.portfolio_cash_flow import (
    DailyPortfolioCashFlowImportHandler,
)
from wbportfolio.models.portfolio_cash_targets import PortfolioCashTarget
from wbportfolio.models.portfolio_swing_pricings import PortfolioSwingPricing


class DailyPortfolioCashFlow(ImportMixin, WBModel):
    import_export_handler_class = DailyPortfolioCashFlowImportHandler
    pending = models.BooleanField(default=False)

    portfolio = models.ForeignKey(
        to="wbportfolio.Portfolio",
        related_name="daily_cashflows",
        on_delete=models.CASCADE,
    )
    value_date = models.DateField()

    cash = models.DecimalField(max_digits=19, decimal_places=4, blank=True)
    cash_flow_forecast = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal(0), blank=True)
    total_assets = models.DecimalField(max_digits=19, decimal_places=4, blank=True)

    min_target_cash_pct = models.DecimalField(max_digits=4, decimal_places=4, default=Decimal(0), blank=True)
    target_cash_pct = models.DecimalField(max_digits=4, decimal_places=4, default=Decimal(0), blank=True)
    max_target_cash_pct = models.DecimalField(max_digits=4, decimal_places=4, default=Decimal(0), blank=True)

    swing_pricing = models.ForeignKey(
        to="wbportfolio.PortfolioSwingPricing",
        related_name="cash_flow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    estimated_total_assets = models.DecimalField(max_digits=19, decimal_places=4, blank=True)
    cash_flow_asset_ratio = models.DecimalField(max_digits=5, decimal_places=4, blank=True)
    true_cash = models.DecimalField(max_digits=19, decimal_places=4, blank=True)
    cash_pct = models.DecimalField(max_digits=5, decimal_places=4, blank=True)
    true_cash_pct = models.DecimalField(max_digits=5, decimal_places=4, blank=True)
    target_cash = models.DecimalField(max_digits=19, decimal_places=4, blank=True)
    excess_cash = models.DecimalField(max_digits=19, decimal_places=4, blank=True)
    proposed_rebalancing = models.DecimalField(max_digits=19, decimal_places=4, blank=True, default=Decimal(0))
    rebalancing = models.DecimalField(max_digits=19, decimal_places=4, blank=True, default=Decimal(0))

    comment = models.TextField(default="", blank=True)

    def save(self, *args, **kwargs):
        # convert to decimal in case we get floats
        if isinstance(self.cash_flow_forecast, float):
            self.cash_flow_forecast = Decimal(self.cash_flow_forecast)

        if isinstance(self.total_assets, float):
            self.total_assets = Decimal(self.total_assets)

        if isinstance(self.rebalancing, float):
            self.rebalancing = Decimal(self.rebalancing)

        with suppress(PortfolioCashTarget.DoesNotExist):
            cash_target = self.portfolio.cash_targets.filter(valid_date__lte=self.value_date).latest("valid_date")
            self.min_target_cash_pct = cash_target.min_target
            self.target_cash_pct = cash_target.target
            self.max_target_cash_pct = cash_target.max_target

        with suppress(PortfolioSwingPricing.DoesNotExist):
            self.swing_pricing = self.portfolio.swing_pricings.filter(valid_date__lte=self.value_date).latest(
                "valid_date"
            )

        with suppress(self.DoesNotExist):
            if self.total_assets is None or self.pending:
                prev = self.portfolio.daily_cashflows.filter(value_date__lt=self.value_date).latest("value_date")
                if prev.pending:
                    self.total_assets = prev.estimated_total_assets
                else:
                    self.total_assets = prev.total_assets

        if self.total_assets is None:
            self.total_assets = 0

        with suppress(self.DoesNotExist):
            if self.cash is None or self.pending:
                earlier = self.portfolio.daily_cashflows.filter(value_date__lt=self.value_date).latest("value_date")
                self.cash = earlier.true_cash

        if self.cash is None:
            self.cash = 0

        if self.pending and self.rebalancing:
            self.cash -= self.rebalancing

        if self.pending:
            self.estimated_total_assets = self.total_assets + self.cash_flow_forecast
        elif self.estimated_total_assets is None:
            self.estimated_total_assets = self.total_assets

        self.cash_flow_asset_ratio = (
            self.cash_flow_forecast / self.estimated_total_assets
            if self.estimated_total_assets != Decimal(0)
            else Decimal(0)
        )
        self.true_cash = self.cash + self.cash_flow_forecast
        self.cash_pct = (
            self.cash / self.estimated_total_assets if self.estimated_total_assets != Decimal(0) else Decimal(0)
        )
        self.true_cash_pct = (
            self.true_cash / self.estimated_total_assets if self.estimated_total_assets != Decimal(0) else Decimal(0)
        )
        self.target_cash = self.estimated_total_assets * self.target_cash_pct
        self.excess_cash = self.true_cash - self.target_cash

        if self.true_cash_pct < self.min_target_cash_pct or self.true_cash_pct > self.max_target_cash_pct:
            self.proposed_rebalancing = self.excess_cash
        elif self.pending:
            self.proposed_rebalancing = 0

        super().save(*args, **kwargs)

        if self.portfolio.daily_cashflows.filter(value_date__gt=self.value_date).exists():
            self.portfolio.daily_cashflows.filter(value_date__gt=self.value_date).earliest("value_date").save()

    class Meta:
        verbose_name = "Daily Portfolio CashFlow"
        verbose_name_plural = "Daily Portfolio CashFlow"
        constraints = [
            models.UniqueConstraint(fields=["portfolio", "value_date"], name="unique_portfolio_value_date"),
        ]
        permissions = [("administrate_dailyportfoliocashflow", "Can administrate Daily Portfolio CashFlow")]
        notification_types = [
            create_notification_type(
                "wbportfolio.dailyportfoliocashflow.notify_rebalance",
                "Rebalancing suggested",
                "Sends a notification, when the system suggests to rebalance a portfolio due to being outside of the cash target parameters",
                True,
                True,
                False,
            ),
            create_notification_type(
                "wbportfolio.dailyportfoliocashflow.notify_swingpricing",
                "Swing Pricing Notification",
                "Sends a notification, when the system detects a future swing pricing event",
                False,
                False,
                False,
            ),
        ]

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:portfoliocashflow"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:portfoliocashflow-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{portfolio}}: {{cash}}"
