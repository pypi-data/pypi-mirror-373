from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class DailyPortfolioCashFlowDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> dp.Display:
        return dp.create_simple_display(
            grid_template_areas=[
                ["portfolio", "value_date", "cash_flow_forecast", "total_assets"],
                ["estimated_total_assets", "cash", "cash_flow_asset_ratio", "true_cash"],
                ["cash_pct", "true_cash_pct", "target_cash", "excess_cash"],
                ["proposed_rebalancing", "proposed_rebalancing", "rebalancing", "rebalancing"],
                [dp.repeat_field(4, "comment")],
            ]
        )

    def get_list_display(self) -> dp.ListDisplay:
        negative_formatting = dp.FormattingRule(condition=("<", 0), style={"color": WBColor.RED_DARK.value})
        positive_formatting = dp.FormattingRule(condition=(">", 0), style={"color": WBColor.GREEN_DARK.value})
        bold_formatting = dp.FormattingRule(condition=("!=", 0), style={"fontWeight": "bold"})
        pending_formatting = dp.FormattingRule(
            style={"backgroundColor": WBColor.GREY.value, "fontStyle": "italic"},
            condition=[("==", True, "pending")],
        )
        swing_formatting_positive = dp.FormattingRule(
            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
            condition=[("==", "pos", "swing_pricing_indicator")],
        )
        swing_formatting_negative = dp.FormattingRule(
            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
            condition=[("==", "neg", "swing_pricing_indicator")],
        )
        fields = []

        if "portfolio_id" not in self.view.kwargs:
            fields.append(dp.Field(key="portfolio", label="Portfolio", pinned="left"))

        fields.extend(
            [
                dp.Field(key="value_date", label="Value Date", width=100, pinned="left"),
                dp.Field(
                    key="cash_flow_forecast", label="CF Forecast", width=100, formatting_rules=[negative_formatting]
                ),
                dp.Field(
                    key="total_assets",
                    label="Total AuM",
                    width=100,
                    formatting_rules=[negative_formatting, pending_formatting],
                ),
                dp.Field(
                    key="estimated_total_assets",
                    label="Estimated AuM",
                    width=100,
                    formatting_rules=[negative_formatting],
                ),
                dp.Field(
                    key="cash",
                    label="Cash & E.",
                    width=100,
                    formatting_rules=[negative_formatting, pending_formatting],
                ),
                dp.Field(
                    key="cash_flow_asset_ratio",
                    label="Cash Flow Forecast / E. AuM",
                    width=125,
                    formatting_rules=[negative_formatting, swing_formatting_positive, swing_formatting_negative],
                ),
                dp.Field(key="true_cash", label="True Cash", width=100, formatting_rules=[negative_formatting]),
                dp.Field(key="cash_pct", label="Cash & E. %", width=100, formatting_rules=[negative_formatting]),
                dp.Field(key="true_cash_pct", label="True Cash %", width=100, formatting_rules=[negative_formatting]),
                dp.Field(
                    key="target_cash_pct", label="Target Cash %", width=100, formatting_rules=[negative_formatting]
                ),
                dp.Field(key="target_cash", label="Target Cash", width=100, formatting_rules=[negative_formatting]),
                dp.Field(key="excess_cash", label="Δ Target Cash", width=100, formatting_rules=[negative_formatting]),
                dp.Field(
                    key="proposed_rebalancing",
                    label="Proposed Rbl.",
                    width=100,
                    formatting_rules=[negative_formatting, positive_formatting, bold_formatting],
                ),
                dp.Field(
                    key="rebalancing",
                    label="Rbl.",
                    width=100,
                    formatting_rules=[negative_formatting, positive_formatting, bold_formatting],
                ),
                dp.Field(key="comment", label="Comment", width=300),
            ]
        )
        return dp.ListDisplay(
            fields=fields,
            legends=[
                dp.Legend(items=[dp.LegendItem(label="Pending data", icon=WBColor.GREY.value)]),
                dp.Legend(
                    items=[
                        dp.LegendItem(label="Swing Pricing: Subscription", icon=WBColor.YELLOW_LIGHT.value),
                        dp.LegendItem(label="Swing Pricing: Redemption", icon=WBColor.BLUE_LIGHT.value),
                    ]
                ),
            ],
        )
