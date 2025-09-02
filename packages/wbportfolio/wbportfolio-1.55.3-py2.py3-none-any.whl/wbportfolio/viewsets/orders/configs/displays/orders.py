from typing import Optional

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbportfolio.models import Order, OrderProposal

ORDER_STATUS_LEGENDS = dp.Legend(
    key="has_warnings",
    items=[
        dp.LegendItem(icon=WBColor.YELLOW_DARK.value, label=_("Warning"), value=True),
    ],
)

ORDER_STATUS_FORMATTING = dp.Formatting(
    column="has_warnings",
    formatting_rules=[
        dp.FormattingRule(
            style={"backgroundColor": WBColor.YELLOW_DARK.value},
            condition=("==", True),
        )
    ],
)
ORDER_TYPE_FORMATTING_RULES = [
    dp.FormattingRule(
        style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
        condition=("==", Order.Type.SELL.name),
    ),
    dp.FormattingRule(
        style={"color": WBColor.RED.value, "fontWeight": "bold"},
        condition=("==", Order.Type.DECREASE.name),
    ),
    dp.FormattingRule(
        style={"color": WBColor.GREEN.value, "fontWeight": "bold"},
        condition=("==", Order.Type.INCREASE.name),
    ),
    dp.FormattingRule(
        style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
        condition=("==", Order.Type.BUY.name),
    ),
    dp.FormattingRule(
        style={"color": WBColor.GREY.value, "fontWeight": "bold"},
        condition=("==", Order.Type.NO_CHANGE.name),
    ),
]

VALUE_FORMATTING_RULES = [
    dp.FormattingRule(
        style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
        condition=("<", 0),
    ),
    dp.FormattingRule(
        style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
        condition=(">", 0),
    ),
]


class OrderOrderProposalDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        order_proposal = get_object_or_404(OrderProposal, pk=self.view.kwargs.get("order_proposal_id", None))
        fields = [
            dp.Field(
                label="Instrument",
                open_by_default=True,
                key=None,
                children=[
                    dp.Field(key="underlying_instrument", label="Name", width=Unit.PIXEL(250)),
                    dp.Field(key="underlying_instrument_isin", label="ISIN", width=Unit.PIXEL(125)),
                    dp.Field(key="underlying_instrument_ticker", label="Ticker", width=Unit.PIXEL(100)),
                    dp.Field(
                        key="underlying_instrument_refinitiv_identifier_code", label="RIC", width=Unit.PIXEL(100)
                    ),
                    dp.Field(key="underlying_instrument_instrument_type", label="Asset Class", width=Unit.PIXEL(125)),
                    dp.Field(key="underlying_instrument_exchange", label="Exchange", width=Unit.PIXEL(125)),
                ],
            ),
            dp.Field(
                label="Weight",
                open_by_default=False,
                key=None,
                children=[
                    dp.Field(key="effective_weight", label="Effective Weight", show="open", width=Unit.PIXEL(150)),
                    dp.Field(key="target_weight", label="Target Weight", show="open", width=Unit.PIXEL(150)),
                    dp.Field(
                        key="weighting",
                        label="Delta Weight",
                        formatting_rules=VALUE_FORMATTING_RULES,
                        width=Unit.PIXEL(150),
                    ),
                ],
            ),
        ]
        if not order_proposal.portfolio.only_weighting:
            fields.append(
                dp.Field(
                    label="Shares",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="effective_shares", label="Effective Shares", show="open", width=Unit.PIXEL(150)),
                        dp.Field(key="target_shares", label="Target Shares", show="open", width=Unit.PIXEL(150)),
                        dp.Field(
                            key="shares",
                            label="Shares",
                            formatting_rules=VALUE_FORMATTING_RULES,
                            width=Unit.PIXEL(150),
                        ),
                    ],
                )
            )
            fields.append(
                dp.Field(
                    label="Total Value",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(
                            key="effective_total_value_fx_portfolio",
                            label="Effective Total Value",
                            show="open",
                            width=Unit.PIXEL(150),
                        ),
                        dp.Field(
                            key="target_total_value_fx_portfolio",
                            label="Target Total Value",
                            show="open",
                            width=Unit.PIXEL(150),
                        ),
                        dp.Field(
                            key="total_value_fx_portfolio",
                            label="Total Value",
                            formatting_rules=VALUE_FORMATTING_RULES,
                            width=Unit.PIXEL(150),
                        ),
                    ],
                )
            )
        fields.append(
            dp.Field(
                label="Information",
                open_by_default=False,
                key=None,
                children=[
                    dp.Field(
                        key="order_type",
                        label="Direction",
                        formatting_rules=ORDER_TYPE_FORMATTING_RULES,
                        width=Unit.PIXEL(125),
                    ),
                    dp.Field(key="comment", label="Comment", width=Unit.PIXEL(250)),
                    dp.Field(key="order", label="Order", show="open", width=Unit.PIXEL(100)),
                ],
            )
        )
        if order_proposal.execution_status:
            fields.append(
                dp.Field(
                    label="Execution",
                    open_by_default=True,
                    key=None,
                    children=[
                        dp.Field(key="execution_confirmed", label="Confirmed", width=Unit.PIXEL(50)),
                        dp.Field(key="execution_comment", label="Comment", width=Unit.PIXEL(100)),
                    ],
                )
            )
        return dp.ListDisplay(
            fields=fields,
            legends=[ORDER_STATUS_LEGENDS],
            formatting=[ORDER_STATUS_FORMATTING],
        )

    def get_instance_display(self) -> Display:
        order_proposal = get_object_or_404(OrderProposal, pk=self.view.kwargs.get("order_proposal_id", None))

        fields = [
            ["company", "security", "underlying_instrument"],
            ["effective_weight", "target_weight", "weighting"],
        ]
        if not order_proposal.portfolio.only_weighting:
            fields.append(["effective_shares", "target_shares", "shares"])
        fields.append([repeat_field(3, "comment")])
        return create_simple_display(fields)
