from decimal import Decimal

from django.db import models
from wbcore.models import WBModel


class PortfolioCashTarget(WBModel):
    """This model stores cash targets for a given portfolio"""

    portfolio = models.ForeignKey(
        to="wbportfolio.Portfolio",
        related_name="cash_targets",
        on_delete=models.CASCADE,
    )

    valid_date = models.DateField()
    min_target = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    target = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal(0))
    max_target = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    comment = models.TextField(default="", blank=True)

    def __str__(self) -> str:
        return f"{self.portfolio}: {self.target:.2%} ({self.valid_date:%d.%m.%Y})"

    class Meta:
        verbose_name = "Portfolio Cash Target"
        verbose_name_plural = "Portfolio Cash Targets"
        constraints = [
            models.UniqueConstraint(fields=["portfolio", "valid_date"], name="unique_portfolio_valid_date"),
        ]

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:portfoliocashtarget"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:portfoliocashtarget-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{portfolio}}: {{target}} ({{valid_date}})"
