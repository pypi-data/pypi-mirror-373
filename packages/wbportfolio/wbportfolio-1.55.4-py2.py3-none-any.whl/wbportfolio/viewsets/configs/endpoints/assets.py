from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class AssetPositionEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class AssetPositionPortfolioEndpointConfig(AssetPositionEndpointConfig):
    pass


class AssetPositionEquityEndpointConfig(AssetPositionEndpointConfig):
    pass


class AssetPositionInstrumentEndpointConfig(AssetPositionEndpointConfig):
    pass


class AssetPositionIndexEndpointConfig(AssetPositionEndpointConfig):
    pass


class AssetPositionProductGroupEndpointConfig(AssetPositionEndpointConfig):
    pass


class CashPositionPortfolioEndpointConfig(AssetPositionEndpointConfig):
    PK_FIELD = "portfolio"

    def get_instance_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:portfolio-list",
            args=[],
            request=self.request,
        )

    def get_update_endpoint(self, **kwargs):
        return None


class ContributorPortfolioChartEndpointConfig(AssetPositionEndpointConfig):
    pass


class AssetPositionUnderlyingInstrumentChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:instrument-assetpositionchart-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class DistributionChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:portfolio-distributionchart-list",
            args=[self.view.kwargs["portfolio_id"]],
            request=self.request,
        )


class DistributionTableEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class CompositionModelPortfolioPandasEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None
