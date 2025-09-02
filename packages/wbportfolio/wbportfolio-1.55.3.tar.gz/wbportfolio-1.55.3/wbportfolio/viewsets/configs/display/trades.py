from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.icons import WBIcon
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

NEGATIVE_RED_FORMATTING = [
    dp.FormattingRule(
        style={
            "color": WBColor.RED_DARK.value,
            "fontWeight": "bold",
        },
        condition=("<", 0),
    )
]

SHARE_FORMATTING = dp.Formatting(
    column="shares",
    formatting_rules=[
        dp.FormattingRule(
            style={
                "color": WBColor.RED_DARK.value,
                # "fontWeight": "bold",
            },
            condition=("<", 0),
        )
    ],
)


class TradeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="transaction_subtype", label="Type", width=Unit.PIXEL(100)),
                dp.Field(key="transaction_date", label="Trade Date", width=Unit.PIXEL(150)),
                dp.Field(key="underlying_instrument", label="Instrument", width=Unit.PIXEL(250)),
                dp.Field(
                    label="Value",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="shares", label="Shares", width=Unit.PIXEL(100)),
                        dp.Field(key="price", label="Price", width=Unit.PIXEL(100)),
                        dp.Field(key="total_value", label="Value", width=Unit.PIXEL(125)),
                        dp.Field(key="total_value_usd", label="Value ($)", width=Unit.PIXEL(125), show="open"),
                    ],
                ),
                dp.Field(
                    label="Bank",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="bank", label="Counterparty", width=Unit.PIXEL(150)),
                        dp.Field(key="custodian", label="Custodian", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="register", label="Register", width=Unit.PIXEL(200), show="open"),
                    ],
                ),
                dp.Field(
                    label="Information",
                    open_by_default=False,
                    key=None,
                    children=list(
                        filter(
                            lambda x: not (x.key == "portfolio" and "portfolio_id" in self.view.kwargs),
                            [
                                dp.Field(key="currency", label="Currency", width=Unit.PIXEL(100)),
                                dp.Field(key="portfolio", label="Portfolio", width=Unit.PIXEL(250), show="open"),
                                dp.Field(
                                    key="marked_for_deletion",
                                    label="Marked for Deletion",
                                    width=Unit.PIXEL(150),
                                    show="open",
                                ),
                                dp.Field(key="pending", label="Pending", width=Unit.PIXEL(150), show="open"),
                            ],
                        )
                    ),
                ),
            ],
            formatting=[SHARE_FORMATTING],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["transaction_date", "value_date", "."],
                [repeat_field(3, "underlying_instrument")],
                ["shares", "price", "bank"],
                ["external_id", "marked_for_deletion", "register"],
                [repeat_field(3, "comment")],
            ]
        )


class SubscriptionRedemptionDisplayConfig(TradeDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="transaction_subtype", label="Type", width=Unit.PIXEL(100)),
                dp.Field(key="transaction_date", label="Trade Date", width=Unit.PIXEL(150)),
                dp.Field(key="underlying_instrument", label="Product", width=Unit.PIXEL(250)),
                dp.Field(
                    label="Value",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="shares", label="Shares", width=Unit.PIXEL(100)),
                        dp.Field(key="price", label="Price", width=Unit.PIXEL(100)),
                        dp.Field(key="total_value", label="Value", width=Unit.PIXEL(125)),
                        dp.Field(key="total_value_usd", label="Value ($)", width=Unit.PIXEL(125), show="open"),
                    ],
                ),
                dp.Field(
                    label="Customer",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="claimed_shares", label="Claimed Shares", width=Unit.PIXEL(150)),
                        dp.Field(key="claims", label="Claims", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="comment", label="Comment", width=Unit.PIXEL(200)),
                    ],
                ),
                dp.Field(
                    label="Bank",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="bank", label="Bank", width=Unit.PIXEL(150)),
                        dp.Field(key="custodian", label="Custodian", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="register", label="Register", width=Unit.PIXEL(200), show="open"),
                    ],
                ),
                dp.Field(
                    label="Information",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="currency", label="Currency", width=Unit.PIXEL(100), show="open"),
                        dp.Field(key="portfolio", label="Portfolio", width=Unit.PIXEL(250), show="open"),
                        dp.Field(key="marked_for_deletion", label="Marked for Deletion", width=Unit.PIXEL(150)),
                        dp.Field(key="pending", label="Pending", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="marked_as_internal", label="Internal", width=Unit.PIXEL(150), show="open"),
                        dp.Field(key="internal_trade", label="Internal Trade", width=Unit.PIXEL(150), show="open"),
                    ],
                ),
            ],
            legends=[
                dp.Legend(
                    key="completely_claimed",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label="Completely Claimed",
                            value=True,
                        )
                    ],
                ),
                dp.Legend(
                    key="completely_claimed_if_approved",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label="Completely Claimed if approved",
                            value=True,
                        )
                    ],
                ),
                dp.Legend(
                    key="pending",
                    items=[
                        dp.LegendItem(icon=WBIcon.FOLDERS_ADD.icon, label="Pending", value=True),
                    ],
                ),
                dp.Legend(
                    key="marked_for_deletion",
                    items=[
                        dp.LegendItem(icon=WBIcon.DELETE.icon, label="To Be Deleted", value=True),
                    ],
                ),
            ],
            formatting=[
                SHARE_FORMATTING,
                dp.Formatting(
                    column="completely_claimed",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", True),
                        )
                    ],
                ),
                dp.Formatting(
                    column="completely_claimed_if_approved",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", True),
                        )
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["transaction_date", "value_date", "."],
                [repeat_field(3, "underlying_instrument")],
                ["shares", "price", "bank"],
                ["external_id", "marked_for_deletion", "register"],
                [repeat_field(3, "comment")],
                ["marked_as_internal", repeat_field(2, "internal_trade")],
            ]
        )


class TradePortfolioDisplayConfig(TradeDisplayConfig):
    pass
