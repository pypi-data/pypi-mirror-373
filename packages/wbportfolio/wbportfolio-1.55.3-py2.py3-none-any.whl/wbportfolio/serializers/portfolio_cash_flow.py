from datetime import date, timedelta

from rest_framework.exceptions import ValidationError
from wbcore import serializers

from wbportfolio.models.portfolio_cash_flow import DailyPortfolioCashFlow
from wbportfolio.serializers.portfolios import PortfolioRepresentationSerializer


class DailyPortfolioCashFlowModelSerializer(serializers.ModelSerializer):
    swing_pricing_indicator = serializers.CharField(read_only=True)
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")

    def validate(self, data):
        # We explictly forbit changing any data that is older than 1 week
        if value_date := data.get("value_date", getattr(self.instance, "value_date", None)):
            if value_date < (date.today() - timedelta(days=7)) and not self.context["request"].user.has_perm(
                "administrate_dailyportfoliocashflow"
            ):
                raise ValidationError({"non_field_errors": ["Changing entries older than 1 week is prohibited."]})

        return data

    class Meta:
        model = DailyPortfolioCashFlow
        percent_fields = ["true_cash_pct", "cash_pct", "target_cash_pct", "cash_flow_asset_ratio"]
        override_decimal_places = 0
        fields = (
            "id",
            "value_date",
            "portfolio",
            "_portfolio",
            "cash",
            "cash_pct",
            "cash_flow_forecast",
            "total_assets",
            "estimated_total_assets",
            "cash_flow_asset_ratio",
            "swing_pricing_indicator",
            "true_cash",
            "true_cash_pct",
            "target_cash",
            "target_cash_pct",
            "excess_cash",
            "proposed_rebalancing",
            "rebalancing",
            "pending",
            "comment",
        )
