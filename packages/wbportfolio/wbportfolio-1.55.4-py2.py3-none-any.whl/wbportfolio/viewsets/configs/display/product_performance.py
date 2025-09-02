from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbportfolio.filters.performances import PerformancePandasFilter


class PerformancePandasDisplayConfig(DisplayViewConfig):
    LEGENDS = [
        dp.Legend(
            items=[
                dp.LegendItem(icon=WBColor.GREEN_DARK.value, label="Strong Growth"),
                dp.LegendItem(icon=WBColor.GREEN.value, label="Medium Growth"),
                dp.LegendItem(icon=WBColor.GREEN_LIGHT.value, label="Slight Growth"),
                dp.LegendItem(icon=WBColor.RED_LIGHT.value, label="Slight Loss"),
                dp.LegendItem(icon=WBColor.RED.value, label="Medium Loss"),
                dp.LegendItem(icon=WBColor.RED_DARK.value, label="Strong Loss"),
            ]
        )
    ]
    FORMATTING = [
        dp.Formatting(
            column="perf_usd",
            formatting_rules=[
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                    condition=(">", 0),
                ),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.GREEN.value},
                    condition=(">", 0.01),
                ),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.GREEN_DARK.value},
                    condition=(">", 0.03),
                ),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.RED_LIGHT.value},
                    condition=("<", 0),
                ),
                dp.FormattingRule(style={"backgroundColor": WBColor.RED.value}, condition=("<", -0.01)),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.RED_DARK.value},
                    condition=("<", -0.03),
                ),
            ],
        ),
    ]

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        n1_label = "N1"
        n2_label = "N2"
        if (
            self.request
            and (dates_str := self.request.GET.get("dates"))
            and (performance_by := self.request.GET.get("performance_by"))
        ):
            dates = dates_str.split(",")
            n1_label = f"{dates[0]} {PerformancePandasFilter.PerformanceBy[performance_by].label}"
            n2_label = f"{dates[1]} {PerformancePandasFilter.PerformanceBy[performance_by].label}"

        return dp.ListDisplay(
            fields=[
                dp.Field(key="computed_str", label="Title", width=Unit.PIXEL(300)),
                # dp.Field(key="isin", label="ISIN", width=Unit.PIXEL(150)),
                dp.Field(key="n1", label=n1_label),
                dp.Field(key="n2", label=n2_label),
                dp.Field(key="diff", label="Δ"),
                dp.Field(key="perf", label="Performance"),
                dp.Field(key="n1_usd", label=f"{n1_label} ($)"),
                dp.Field(key="n2_usd", label=f"{n2_label} ($)"),
                dp.Field(key="diff_usd", label="Δ ($)"),
                dp.Field(
                    key="perf_usd",
                    label="Performance ($)",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "fontWeight": "bold",
                            },
                        )
                    ],
                ),
            ],
            legends=self.LEGENDS,
            formatting=self.FORMATTING,
        )


class ProductPerformanceNetNewMoneyDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="computed_str", label="Title", width=Unit.PIXEL(300)),
                dp.Field(key="net_negative_money", label="Outflows", width=Unit.PIXEL(200)),
                dp.Field(key="net_negative_money_usd", label="Outflows ($)", width=Unit.PIXEL(200)),
                dp.Field(key="net_positive_money", label="Inflows", width=Unit.PIXEL(200)),
                dp.Field(key="net_positive_money_usd", label="Inflows ($)", width=Unit.PIXEL(200)),
                dp.Field(key="net_money", label="Net New Money", width=Unit.PIXEL(200)),
                dp.Field(key="net_money_usd", label="Net New Money ($)", width=Unit.PIXEL(200)),
            ],
            formatting=[
                dp.Formatting(
                    column="net_money",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=(">=", 0),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("<", 0),
                        ),
                    ],
                ),
            ],
        )


class PerformanceComparisonDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="computed_str", label="Title", width=Unit.PIXEL(300)),
                dp.Field(key="benchmark_computed_str", label="Comparison benchmark", width=Unit.PIXEL(250))
                if self.view.benchmark_label
                else {},
                dp.Field(key="inception_date", label="Launch Date"),
                dp.Field(key="instrument_last_valuation_price", label="Last NAV (Price)"),
                dp.Field(key="last_valuation_date", label="Last NAV (Date)"),
                dp.Field(
                    key="perf_last_day",
                    label="Last Daily Perf.",
                    width=Unit.PIXEL(200),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "color": WBColor.RED.value,
                                "fontWeight": "bold",
                            },
                            condition=("<", 0),
                        ),
                        dp.FormattingRule(
                            style={
                                "color": WBColor.GREEN_DARK.value,
                                "fontWeight": "bold",
                            },
                            condition=(">=", 0),
                        ),
                    ],
                ),
                dp.Field(
                    key="perf_month_to_date",
                    label="Month to Date",
                    width=Unit.PIXEL(200),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "color": WBColor.RED.value,
                                "fontWeight": "bold",
                            },
                            condition=("<", 0),
                        ),
                        dp.FormattingRule(
                            style={
                                "color": WBColor.GREEN_DARK.value,
                                "fontWeight": "bold",
                            },
                            condition=(">=", 0),
                        ),
                    ],
                ),
                dp.Field(
                    key="perf_year_to_date",
                    label="Year to Date",
                    width=Unit.PIXEL(200),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "color": WBColor.RED.value,
                                "fontWeight": "bold",
                            },
                            condition=("<", 0),
                        ),
                        dp.FormattingRule(
                            style={
                                "color": WBColor.GREEN_DARK.value,
                                "fontWeight": "bold",
                            },
                            condition=(">=", 0),
                        ),
                    ],
                ),
                dp.Field(
                    key="perf_inception",
                    label="Since Inception",
                    width=Unit.PIXEL(200),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "color": WBColor.RED.value,
                                "fontWeight": "bold",
                            },
                            condition=("<", 0),
                        ),
                        dp.FormattingRule(
                            style={
                                "color": WBColor.GREEN_DARK.value,
                                "fontWeight": "bold",
                            },
                            condition=(">=", 0),
                        ),
                    ],
                ),
                dp.Field(
                    key="perf_between_dates",
                    label="Between Dates",
                    width=Unit.PIXEL(200),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "color": WBColor.RED.value,
                                "fontWeight": "bold",
                            },
                            condition=("<", 0),
                        ),
                        dp.FormattingRule(
                            style={
                                "color": WBColor.GREEN_DARK.value,
                                "fontWeight": "bold",
                            },
                            condition=(">=", 0),
                        ),
                    ],
                )
                if self.view.dates
                else {},
            ]
        )
