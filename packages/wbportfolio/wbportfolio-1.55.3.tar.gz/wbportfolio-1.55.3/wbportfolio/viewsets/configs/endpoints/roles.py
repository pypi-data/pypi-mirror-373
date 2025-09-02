from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class PortfolioRoleInstrumentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:instrument-portfoliorole-list", args=[self.view.kwargs["instrument_id"]], request=self.request
        )
