from contextlib import suppress
from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import Section
from wbcore.metadata.configs.display.instance_display import Inline, Layout, Page
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.instance_display.shortcuts import Display
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbportfolio.models import OrderProposal


class OrderProposalDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="portfolio", label="Portfolio") if "portfolio_id" not in self.view.kwargs else None,
                dp.Field(key="trade_date", label="Order Date"),
                dp.Field(key="rebalancing_model", label="Rebalancing Model"),
                dp.Field(key="comment", label="Comment"),
                dp.Field(key="creator", label="Creator"),
                dp.Field(key="approver", label="Approver"),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=OrderProposal.Status.DRAFT.label,
                            value=OrderProposal.Status.DRAFT.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=OrderProposal.Status.PENDING.label,
                            value=OrderProposal.Status.PENDING.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=OrderProposal.Status.APPROVED.label,
                            value=OrderProposal.Status.APPROVED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=OrderProposal.Status.DENIED.label,
                            value=OrderProposal.Status.DENIED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN.value,
                            label=OrderProposal.Status.APPLIED.label,
                            value=OrderProposal.Status.APPLIED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREY.value,
                            label=OrderProposal.Status.EXECUTION.label,
                            value=OrderProposal.Status.EXECUTION.value,
                        ),
                    ],
                ),
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=("==", OrderProposal.Status.DRAFT.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", OrderProposal.Status.PENDING.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", OrderProposal.Status.APPROVED.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN.value},
                            condition=("==", OrderProposal.Status.APPLIED.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREY.value},
                            condition=("==", OrderProposal.Status.EXECUTION.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", OrderProposal.Status.DENIED.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_DARK.value},
                            condition=("==", OrderProposal.Status.FAILED.value),
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        orders_grid_template_areas = [["orders"]]
        orders_grid_template_rows = ["1fr"]
        sections = []
        with suppress(AttributeError, AssertionError):
            op = self.view.get_object()
            if op.execution_status:
                orders_grid_template_areas = [["execution"], ["orders"]]
                orders_grid_template_rows = ["100px", "1fr"]
                sections.append(
                    Section(
                        key="execution",
                        title="Execution",
                        collapsed=False,
                        display=Display(
                            pages=[
                                Page(
                                    layouts={
                                        default(): Layout(
                                            grid_template_areas=[["execution_status_repr", "execution_comment"]],
                                            grid_template_columns=["0.3fr", "0.7fr"],
                                        )
                                    }
                                )
                            ]
                        ),
                    )
                )
        return Display(
            pages=[
                Page(
                    title="Main Information",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["status", "status", "status"],
                                ["trade_date", "total_cash_weight", "min_order_value"],
                                ["rebalancing_model", "target_portfolio", "target_portfolio"]
                                if self.view.new_mode
                                else ["rebalancing_model", "creator", "approver"],
                                ["comment", "comment", "comment"],
                            ],
                        ),
                    },
                ),
                Page(
                    title="Orders",
                    layouts={
                        default(): Layout(
                            grid_template_areas=orders_grid_template_areas,
                            grid_template_rows=orders_grid_template_rows,
                            inlines=[Inline(key="orders", endpoint="orders")],
                            sections=sections,
                        ),
                    },
                ),
            ]
        )
