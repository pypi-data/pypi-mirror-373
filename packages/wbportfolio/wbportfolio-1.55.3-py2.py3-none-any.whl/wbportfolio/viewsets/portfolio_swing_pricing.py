from wbcore import viewsets

from wbportfolio.models.portfolio_swing_pricings import PortfolioSwingPricing
from wbportfolio.serializers import PortfolioSwingPricingModelSerializer


class PortfolioSwingPricingModelViewSet(viewsets.ModelViewSet):
    queryset = PortfolioSwingPricing.objects.all()
    serializer_class = PortfolioSwingPricingModelSerializer
