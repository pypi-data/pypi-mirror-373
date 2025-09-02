from django.db import models
from django.db.models import Q
from wbcore.models import WBModel


class PortfolioSwingPricing(WBModel):
    valid_date = models.DateField()

    portfolio = models.ForeignKey(
        to="wbportfolio.Portfolio",
        related_name="swing_pricings",
        on_delete=models.CASCADE,
    )

    negative_threshold = models.DecimalField(max_digits=4, decimal_places=4)
    negative_swing_factor = models.DecimalField(max_digits=4, decimal_places=4)
    positive_threshold = models.DecimalField(max_digits=4, decimal_places=4)
    positive_swing_factor = models.DecimalField(max_digits=4, decimal_places=4)

    def __str__(self) -> str:
        return f"{self.portfolio}: {self.negative_swing_factor:.2%}/{self.positive_swing_factor:.2%} ({self.valid_date:%d.%m.%Y})"

    class Meta:
        verbose_name = "Portfolio Swing Pricing"
        verbose_name_plural = "Portfolio Swing Pricings"
        constraints = [
            models.CheckConstraint(
                check=Q(negative_threshold__lt=0)
                & Q(negative_swing_factor__lt=0)
                & Q(positive_threshold__gt=0)
                & Q(positive_swing_factor__gt=0),
                name="value_polarity",
            ),
            models.UniqueConstraint(fields=["valid_date", "portfolio"], name="unique_valid_date_portfolio"),
        ]

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:portfolioswingpricing"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:portfolioswingpricing-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{portfolio}}: {{swing_factor}} ({{valid_date}})"
