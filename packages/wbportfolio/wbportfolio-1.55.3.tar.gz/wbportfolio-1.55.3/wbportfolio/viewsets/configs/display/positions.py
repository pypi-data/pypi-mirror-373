from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

perf_formatting_rules = [
    dp.FormattingRule(
        style={
            "color": WBColor.YELLOW_DARK.value,
        },
        condition=(">", 3),
    ),
    dp.FormattingRule(
        style={
            "color": WBColor.RED_DARK.value,
        },
        condition=(">", 5),
    ),
]


class AssetPositionPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                # dp.Field(key="price_start", label="Price Start"),
                # dp.Field(key="price_end", label="Price End"),
                dp.Field(key="total_value_start", label="Value Start ($)"),
                dp.Field(key="total_value_end", label="Value End ($)"),
                dp.Field(key="allocation_start", label="Weighting Start"),
                dp.Field(key="allocation_end", label="Weighting End"),
                dp.Field(key="performance_total", label="Total Performance"),
                dp.Field(key="performance_forex", label="Forex Performance"),
                dp.Field(key="contribution_total", label="Total Contribution"),
                dp.Field(key="contribution_forex", label="Forex Contribution"),
                dp.Field(key="market_share", label="Market Shares (end)"),
            ]
        )


class AggregatedAssetPositionLiquidityDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        historic_date = self.request.GET.get("historic_date", None)
        compared_date = self.request.GET.get("compared_date", None)
        return dp.ListDisplay(
            fields=[
                dp.Field(
                    key="name",
                    label="Name",
                    formatting_rules=[dp.FormattingRule(style={"fontWeight": "bold"})],
                ),
                dp.Field(
                    key="shares_first_date", label=f"Total Shares - {historic_date}" if historic_date else "None"
                ),
                dp.Field(
                    key="volume_50d_first_date", label=f"Mean Volume - {historic_date}" if historic_date else "None"
                ),
                dp.Field(
                    key="liquidity_first_date",
                    label=f"Days To Liquidate - {historic_date}" if historic_date else "None",
                ),
                dp.Field(
                    key="pct_aum_first_date", label=f"Percent AUM - {historic_date}" if historic_date else "None"
                ),
                dp.Field(
                    key="liquidity_second_date",
                    label=f"Days To Liquidate - {compared_date}" if compared_date else "None",
                ),
                dp.Field(
                    key="pct_aum_second_date", label=f"Percent AUM - {compared_date}" if compared_date else "None"
                ),
            ],
        )
