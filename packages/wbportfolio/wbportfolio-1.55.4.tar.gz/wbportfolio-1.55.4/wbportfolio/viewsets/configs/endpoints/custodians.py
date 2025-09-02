from wbcore.metadata.configs.endpoints import EndpointViewConfig


class CustodianEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return super().get_endpoint()
