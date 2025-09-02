from typing import Optional

from wbcore.contrib.authentication.models import User
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.directory.models import Person
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import Display
from wbcore.metadata.configs.display.instance_display.styles import Style
from wbcore.metadata.configs.display.instance_display.utils import repeat
from wbcore.metadata.configs.display.view_config import DisplayViewConfig
from wbcore.metadata.configs.display.windows import Window

from wbportfolio.models.transactions.claim import Claim


class ClaimDisplayConfig(DisplayViewConfig):
    LEGENDS = [
        dp.Legend(
            key="status",
            items=[
                dp.LegendItem(
                    icon=WBColor.YELLOW_LIGHT.value,
                    label=Claim.Status.DRAFT.label,
                    value=Claim.Status.DRAFT.name,
                ),
                dp.LegendItem(
                    icon=WBColor.YELLOW.value,
                    label=Claim.Status.AUTO_MATCHED.label,
                    value=Claim.Status.AUTO_MATCHED.name,
                ),
                dp.LegendItem(
                    icon=WBColor.BLUE_LIGHT.value,
                    label=Claim.Status.PENDING.label,
                    value=Claim.Status.PENDING.name,
                ),
                dp.LegendItem(
                    icon=WBColor.GREEN_LIGHT.value,
                    label=Claim.Status.APPROVED.label,
                    value=Claim.Status.APPROVED.name,
                ),
                dp.LegendItem(
                    icon=WBColor.GREY.value,
                    label=Claim.Status.WITHDRAWN.label,
                    value=Claim.Status.WITHDRAWN.name,
                ),
            ],
        )
    ]
    LIST_FORMATTING = [
        dp.Formatting(
            column="status",
            formatting_rules=[
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                    condition=("==", Claim.Status.APPROVED.name),
                ),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.YELLOW.value},
                    condition=("==", Claim.Status.AUTO_MATCHED.name),
                ),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                    condition=("==", Claim.Status.PENDING.name),
                ),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.GREY.value},
                    condition=("==", Claim.Status.WITHDRAWN.name),
                ),
                dp.FormattingRule(
                    style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                    condition=("==", Claim.Status.DRAFT.name),
                ),
            ],
        )
    ]

    def get_list_display(self):
        user: User = self.request.user
        profile: Person = user.profile
        fields = [
            dp.Field(key="date", label="Date", width=Unit.PIXEL(100)),
            (
                dp.Field(key="product", label="Product", width=Unit.PIXEL(300))
                if "product_id" not in self.view.kwargs
                else ()
            ),
            dp.Field(key="claimant", label="Claimant", width=Unit.PIXEL(250)),
            (
                dp.Field(key="account", label="Account", width=Unit.PIXEL(150))
                if "account_id" not in self.view.kwargs
                else ()
            ),
            dp.Field(key="trade_comment", label="Comment", width=Unit.PIXEL(250)),
            dp.Field(
                key="shares",
                label="Shares",
                formatting_rules=[
                    dp.FormattingRule(
                        style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
                        condition=("<", 0),
                    )
                ],
                width=Unit.PIXEL(100),
            ),
            dp.Field(key="last_nav", label="NAV", width=Unit.PIXEL(100)),
            dp.Field(key="total_value", label="Value", width=Unit.PIXEL(100)),
            dp.Field(key="total_value_usd", label="Value (USD)", width=Unit.PIXEL(100)),
            dp.Field(key="bank", label="Bank", width=Unit.PIXEL(100)),
        ]
        if profile.is_internal or user.is_superuser:
            fields.extend(
                [
                    dp.Field(key="creator", label="Creator", width=Unit.PIXEL(150)),
                    (
                        dp.Field(key="trade", label="Trade", width=Unit.PIXEL(250))
                        if "trade_id" not in self.view.kwargs
                        else ()
                    ),
                ]
            )
        fields.append(dp.Field(key="reference", label="Reference", width=Unit.PIXEL(150)))
        return dp.ListDisplay(
            fields=fields,
            formatting=ClaimDisplayConfig.LIST_FORMATTING,
            legends=ClaimDisplayConfig.LEGENDS,
        )

    def get_window(self) -> Window | None:
        if self.instance or self.new_mode:
            if self.profile.is_internal or self.user.is_superuser:
                return Window(max_width=500, min_width=500, max_height=900, min_height=900)
            return Window(max_width=500, min_width=500, max_height=750, min_height=750)
        return None

    def get_instance_display(self) -> Display:
        fields = [
            ["trade_type", "trade_type"],
            ["product", "product"],
            ["as_shares", "quantity"],
            ["bank", "bank"],
            ["date", "date"],
            ["account", "account"],
            ["reference", "reference"],
        ]
        if "entry_id" not in self.view.kwargs:
            fields.append(["claimant", "claimant"])
        # For client we hide the status and trade as it does not concern them
        if self.profile.is_internal or self.user.is_superuser:
            fields.insert(0, ["status", "status"])
            if "trade_id" not in self.view.kwargs:
                fields.insert(6, ["trade", "trade"])

        return dp.Display(
            pages=[
                dp.Page(
                    layouts={
                        "default": dp.Layout(
                            grid_template_areas=fields,
                            grid_template_columns=[repeat(2, Style.minmax(Style.px(200), Style.px(250)))],
                        )
                    }
                )
            ]
        )


class ConsolidatedTradeSummaryDisplayConfig(DisplayViewConfig):
    DEFAULT_COL_WIDTH = 100

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="title", label="Title", pinned="left", width=250),
            dp.Field(
                key="initial_investment_date", label="Initial Investment", pinned="left", width=self.DEFAULT_COL_WIDTH
            ),
            dp.Field(key="aum_sparkline", label="NNM Chart", pinned="left"),
            dp.Field(
                key="shares",
                label="Outstanding Shares",
                open_by_default=False,
                children=[
                    dp.Field(key="sum_shares_start", label="Start", width=self.DEFAULT_COL_WIDTH, show="open"),
                    dp.Field(key="sum_shares_end", label="End", width=self.DEFAULT_COL_WIDTH),
                    dp.Field(key="sum_shares_diff", label="Δ", width=self.DEFAULT_COL_WIDTH, show="open"),
                    dp.Field(key="sum_shares_perf", label="%", width=self.DEFAULT_COL_WIDTH),
                ],
                marry_children=True,
            ),
            dp.Field(
                key="aum_stat",
                label="AUM",
                open_by_default=False,
                children=[
                    dp.Field(key="sum_aum_start", label="Start", width=self.DEFAULT_COL_WIDTH, show="open"),
                    dp.Field(key="sum_aum_end", label="End", width=self.DEFAULT_COL_WIDTH),
                    dp.Field(key="sum_aum_diff", label="Δ", width=self.DEFAULT_COL_WIDTH, show="open"),
                    dp.Field(key="sum_aum_perf", label="%", width=self.DEFAULT_COL_WIDTH),
                ],
                marry_children=True,
            ),
            dp.Field(
                key="nnm_stat",
                label="NNM",
                open_by_default=False,
                children=[
                    *map(
                        lambda monthly_nnm_column: dp.Field(
                            key=monthly_nnm_column[0],
                            label=monthly_nnm_column[1],
                            show="open",
                            width=self.DEFAULT_COL_WIDTH,
                        ),
                        self.view.nnm_monthly_columns,
                    ),
                    dp.Field(
                        key="sum_nnm_total",
                        label="Total",
                        width=self.DEFAULT_COL_WIDTH,
                    ),
                    dp.Field(
                        key="sum_nnm_perf",
                        label="%",
                        width=self.DEFAULT_COL_WIDTH,
                    ),
                ],
                marry_children=True,
            ),
            dp.Field(
                key="performance_stat",
                label="Performance",
                open_by_default=False,
                children=[
                    dp.Field(
                        key="total_performance",
                        label="Total",
                        width=self.DEFAULT_COL_WIDTH,
                    ),
                    dp.Field(
                        key="total_performance_perf",
                        label="%",
                        width=self.DEFAULT_COL_WIDTH,
                    ),
                ],
                marry_children=True,
            ),
        ]

        if self.view.commission_type_columns:
            fields.append(
                dp.Field(
                    key="rebate_stat",
                    label="Rebate",
                    open_by_default=False,
                    children=[
                        *map(
                            lambda commission_type_column: dp.Field(
                                key=commission_type_column[0],
                                label=commission_type_column[1],
                                show="open",
                                width=self.DEFAULT_COL_WIDTH,
                            ),
                            self.view.commission_type_columns,
                        ),
                        dp.Field(
                            key="rebate_total",
                            label="Total",
                            width=self.DEFAULT_COL_WIDTH,
                        ),
                    ],
                    marry_children=True,
                )
            )

        return dp.ListDisplay(fields=fields)


class ProfitAndLossPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="unrealized_pnl", label="Realized P&L"),
                dp.Field(key="realized_pnl", label="Unrealized P&L"),
                dp.Field(key="total_pnl", label="Total P&L"),
                dp.Field(key="total_invested", label="Total Invested"),
                dp.Field(key="performance", label="Performance"),
            ]
        )


class NegativeTermimalAccountPerProductDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="account_repr", label="Account"),
                dp.Field(key="product_repr", label="Product"),
                dp.Field(key="sum_shares", label="Total Shares"),
            ]
        )
