from wbcore import serializers

from wbportfolio.models.portfolio_swing_pricings import PortfolioSwingPricing
from wbportfolio.serializers.portfolios import PortfolioRepresentationSerializer


class PortfolioSwingPricingModelSerializer(serializers.ModelSerializer):
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")

    class Meta:
        model = PortfolioSwingPricing
        fields = (
            "id",
            "portfolio",
            "_portfolio",
            "valid_date",
            "negative_threshold",
            "negative_swing_factor",
            "positive_threshold",
            "positive_threshold",
        )
