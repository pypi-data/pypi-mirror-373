from wbcore import serializers

from wbportfolio.models.portfolio_cash_targets import PortfolioCashTarget
from wbportfolio.serializers.portfolios import PortfolioRepresentationSerializer


class PortfolioCashTargetModelSerializer(serializers.ModelSerializer):
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")

    class Meta:
        model = PortfolioCashTarget
        fields = (
            "id",
            "portfolio",
            "_portfolio",
            "valid_date",
            "min_target",
            "target",
            "max_target",
            "comment",
        )
