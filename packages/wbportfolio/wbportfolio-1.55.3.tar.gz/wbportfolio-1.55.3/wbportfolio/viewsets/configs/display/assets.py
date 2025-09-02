from typing import TYPE_CHECKING, Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.icons import WBIcon
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig
from wbfdm.contrib.metric.viewsets.configs.display import (
    InstrumentMetricPivotedListDisplayConfig,
)

if TYPE_CHECKING:
    from wbportfolio.viewsets.assets import CompositionModelPortfolioPandasView


class AssetPositionDisplayConfig(InstrumentMetricPivotedListDisplayConfig):
    LEGENDS = [
        dp.Legend(
            items=[
                dp.LegendItem(icon=WBColor.YELLOW.value, label="Estimated"),
                dp.LegendItem(icon=WBColor.GREEN_LIGHT.value, label="Real"),
            ],
        ),
    ]
    FORMATTING = [
        dp.Formatting(
            column="is_estimated",
            formatting_rules=[
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.YELLOW.value},
                    condition=("==", True),
                ),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                    condition=("==", False),
                ),
            ],
        ),
    ]

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                # dp.Field(key="date", label="Date"),
                # dp.Field(key="is_estimated", label="Temporary", width=Unit.PIXEL(100)),
                dp.Field(key="underlying_instrument", label="Name"),
                dp.Field(key="underlying_instrument_isin", label="ISIN"),
                dp.Field(key="underlying_instrument_ticker", label="Ticker"),
                dp.Field(key="portfolio", label="Portfolio"),
                dp.Field(key="exchange", label="Exchange"),
                dp.Field(key="date", label="Date"),
                dp.Field(key="price", label="Price"),
                dp.Field(key="shares", label="Shares"),
                dp.Field(key="total_value", label="Total Value"),
                dp.Field(key="currency_fx_rate", label="Currency Rate"),
                dp.Field(key="total_value_fx_portfolio", label="Total Value Portfolio"),
                dp.Field(key="weighting", label="Weighting"),
                dp.Field(key="portfolio_created", label="Portfolio Created"),
                dp.Field(key="market_share", label="Market Share"),
                dp.Field(key="liquidity", label="Liquidity"),
            ],
            legends=self.LEGENDS,
            formatting=self.FORMATTING,
        )


class AssetPositionPortfolioDisplayConfig(AssetPositionDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(
                    label="Instrument",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="underlying_quote_name", label="Name"),
                        dp.Field(key="underlying_quote_isin", label="ISIN"),
                        dp.Field(key="underlying_quote_ticker", label="Ticker"),
                        dp.Field(key="exchange", label="Exchange", width=Unit.PIXEL(250)),
                    ],
                ),
                dp.Field(
                    label="Valuation",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="weighting", label="Weighting"),
                        dp.Field(key="price", label="Price"),
                        dp.Field(key="shares", label="Shares"),
                        dp.Field(key="currency_fx_rate", label="Currency Rate", show="open"),
                        dp.Field(
                            key="total_value_fx_portfolio",
                            label="Total Value Portfolio",
                            width=Unit.PIXEL(150),
                        ),
                        dp.Field(key="total_value", label="Total Value", show="open"),
                        dp.Field(
                            key="total_value_fx_usd", label="Total Value ($)", width=Unit.PIXEL(150), show="open"
                        ),
                    ],
                ),
                dp.Field(
                    label="Portfolio",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="asset_valuation_date", label="Value Date", width=Unit.PIXEL(100)),
                        dp.Field(
                            key="portfolio_created", label="Portfolio Created", width=Unit.PIXEL(150), show="open"
                        ),
                        dp.Field(key="market_share", label="Market Share", show="open"),
                        dp.Field(key="liquidity", label="Liquidity", show="open"),
                    ],
                ),
            ],
            legends=self.LEGENDS,
            formatting=self.FORMATTING,
        )


class AssetPositionInstrumentDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        base_display = AssetPositionPortfolioDisplayConfig(
            view=self.view, request=self.request, instance=self.instance
        )
        return dp.ListDisplay(
            fields=[
                base_display.get_list_display().fields[0],
                base_display.get_list_display().fields[1],
                dp.Field(
                    label="Portfolio",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="asset_valuation_date", label="Value Date", width=Unit.PIXEL(100)),
                        dp.Field(key="portfolio", label="Portfolio", width=Unit.PIXEL(150)),
                        dp.Field(
                            key="portfolio_created", label="Portfolio Created", width=Unit.PIXEL(150), show="open"
                        ),
                        dp.Field(key="market_share", label="Market Share", show="open"),
                        dp.Field(key="liquidity", label="Liquidity", show="open"),
                    ],
                ),
            ],
            legends=[
                dp.Legend(
                    key="is_invested",
                    items=[dp.LegendItem(icon=WBIcon.UNFILTER.icon, label="Not Invested", value=True)],
                )
            ],
        )


class CashPositionPortfolioDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="portfolio_name", label="Portfolio"),
                dp.Field(
                    key="total_value_fx_usd",
                    label="Total Value ($)",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "fontWeight": "bold",
                            },
                        ),
                        dp.FormattingRule(
                            style={"color": WBColor.RED_DARK.value},
                            condition=("<", 0),
                        ),
                    ],
                ),
                dp.Field(key="portfolio_weight", label="Portfolio Weight"),
            ]
        )


class CompositionModelPortfolioPandasDisplayConfig(DisplayViewConfig):
    view: "CompositionModelPortfolioPandasView"

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="underlying_instrument_repr", label="Instrument", width=450),
            dp.Field(
                key=f"group_{self.view.portfolio.id}",
                label=str(self.view.portfolio),
                children=[
                    dp.Field(
                        key=f"shares_{self.view.portfolio.id}",
                        label="Shares",
                        width=150,
                    ),
                    dp.Field(
                        key=f"weighting_{self.view.portfolio.id}",
                        label="Weighting",
                        width=150,
                    ),
                ],
            ),
        ]
        for portfolio in self.view.dependant_portfolios:
            fields.append(
                dp.Field(
                    key=f"group_{portfolio.id}",
                    label=str(portfolio),
                    children=[
                        dp.Field(
                            key=f"shares_{portfolio.id}",
                            label="Shares",
                            width=150,
                        ),
                        dp.Field(
                            key=f"weighting_{portfolio.id}",
                            label="Weighting",
                            width=150,
                        ),
                        dp.Field(
                            key=f"difference_{portfolio.id}",
                            label="Δ",
                            width=75,
                            formatting_rules=[
                                dp.FormattingRule(
                                    condition=("<", 0), style={"fontWeight": "bold", "color": "#FF6961"}
                                ),
                                dp.FormattingRule(condition=(">", 0), style={"fontWeight": "bold", "color": "green"}),
                            ],
                        ),
                    ],
                ),
            )
        return dp.ListDisplay(fields=fields)


class DistributionTableDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="weighting", label="Weighting"),
        ]
        for k, v in reversed(self.view.columns_map.items()):
            fields.append(dp.Field(key=k, label=v))
        return dp.ListDisplay(fields=fields)
