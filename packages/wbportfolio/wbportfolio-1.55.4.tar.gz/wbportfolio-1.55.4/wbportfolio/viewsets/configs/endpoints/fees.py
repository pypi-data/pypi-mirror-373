from wbcore.metadata.configs.endpoints import EndpointViewConfig


class FeeEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class FeesProductEndpointConfig(FeeEndpointConfig):
    pass


class FeesAggregatedProductPandasEndpointConfig(EndpointViewConfig):
    pass
