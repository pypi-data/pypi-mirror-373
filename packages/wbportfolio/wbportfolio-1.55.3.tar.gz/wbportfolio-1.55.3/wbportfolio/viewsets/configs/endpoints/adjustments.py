from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class AdjustmentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:adjustment-list", args=[], request=self.request)

    def get_delete_endpoint(self, **kwargs):
        return None


class AdjustmentEquityEndpointConfig(AdjustmentEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:instrument-adjustment-list", args=[self.view.kwargs["instrument_id"]], request=self.request
        )
