from wbcore.metadata.configs.endpoints import EndpointViewConfig


class AssetPositionPandasEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class AggregatedAssetPositionLiquidityEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None
