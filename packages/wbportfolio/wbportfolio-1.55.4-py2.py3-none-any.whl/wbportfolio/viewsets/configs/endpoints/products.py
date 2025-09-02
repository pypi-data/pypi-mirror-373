from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ProductCustomerEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class ProductPerformanceFeesEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        return reverse("wbportfolio:product-list", request=self.request)


class InstrumentPriceAUMDataEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:aumchart-list", request=self.request)


# Product Portfolio Viewsets
class NominalProductEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:product-nominalchart-list", [self.view.kwargs["product_id"]], request=self.request)


class AUMProductEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:product-aumchart-list", [self.view.kwargs["product_id"]], request=self.request)
