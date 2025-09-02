from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ProductGroupEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:product_group-list",
            args=[],
            request=self.request,
        )
