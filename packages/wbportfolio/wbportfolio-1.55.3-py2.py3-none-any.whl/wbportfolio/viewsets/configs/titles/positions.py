from wbcore.metadata.configs.titles import TitleViewConfig


class AssetPositionPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Invested Asset Positions"


class AggregatedAssetPositionLiquidityTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Aggregated Asset Position Liquidity Table"
