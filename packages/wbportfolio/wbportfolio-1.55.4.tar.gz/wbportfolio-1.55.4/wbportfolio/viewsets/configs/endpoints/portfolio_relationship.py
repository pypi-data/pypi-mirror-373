from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class PortfolioInstrumentPreferredClassificationThroughEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:portfolio-preferredclassification-list",
            args=[self.view.kwargs["portfolio_id"]],
            request=self.request,
        )


class InstrumentPortfolioThroughPortfolioModelEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None
