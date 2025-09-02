from typing import Optional

from django.utils.translation import gettext_lazy as _
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.formatting import Condition, Operator
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig
from wbfdm.contrib.metric.viewsets.configs.utils import (
    PERFORMANCE_FORMATTING,
    get_performance_fields,
)


class ProductDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(
                    key="information",
                    label=_("Information"),
                    open_by_default=False,
                    children=[
                        dp.Field(key="name_repr", label="Name", width=250),
                        dp.Field(key="parent", label="Parent"),
                        dp.Field(key="isin", label="ISIN"),
                        dp.Field(key="ticker", label="Ticker", show="open"),
                        dp.Field(key="bank", label="Bank"),
                        dp.Field(key="description", label="Description", show="open"),
                        dp.Field(key="currency", label="Currency", width=100, show="open"),
                        dp.Field(key="classifications", label="Classifications", show="open"),
                        dp.Field(key="white_label_customers", label="Customers", width=100, show="open"),
                    ],
                ),
                dp.Field(
                    label="Fees",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="current_bank_fees", label="Bank Fees", width=100, show="open"),
                        dp.Field(key="current_management_fees", label="Management Fees", width=100, show="open"),
                        dp.Field(key="current_total_issuer_fees", label="Total Issuer Fees", width=100),
                        dp.Field(key="current_performance_fees", label="Performance Fees", width=100, show="open"),
                    ],
                ),
                dp.Field(
                    label="Last Valuation",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="last_valuation_date", show="open", label="Date", width=150),
                        dp.Field(key="net_value", label="Valuation", width=150, tooltip=dp.Tooltip(key="market_data")),
                    ],
                ),
                dp.Field(
                    key=None,
                    label=_("Performance"),
                    open_by_default=False,
                    children=[
                        dp.Field(key="performance_is_estimated", label="Estimated", width=50, show="open"),
                        dp.Field(key="performance_date", label="Date", width=85),
                        *get_performance_fields(with_comparison_performances=True),
                        dp.Field(key="assets_under_management", label="AUM", width=100, show="open"),
                        dp.Field(key="assets_under_management_usd", label="AUM ($)", width=100),
                    ],
                ),
                dp.Field(
                    label="NNM",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(
                            key="nnm_weekly",
                            label="Weekly",
                            width=150,
                            show="open",
                            formatting_rules=PERFORMANCE_FORMATTING,
                        ),
                        dp.Field(
                            key="nnm_monthly",
                            label="Monthly",
                            width=150,
                            show="open",
                            formatting_rules=PERFORMANCE_FORMATTING,
                        ),
                        dp.Field(
                            key="nnm_year_to_date", label="YTD", width=150, formatting_rules=PERFORMANCE_FORMATTING
                        ),
                        dp.Field(
                            key="nnm_yearly",
                            label="Yearly",
                            width=150,
                            show="open",
                            formatting_rules=PERFORMANCE_FORMATTING,
                        ),
                    ],
                ),
            ],
            formatting=[
                dp.Formatting(
                    column="is_invested",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": "#ADD8E6"},
                            condition=Condition(Operator("=="), False),
                        ),
                    ],
                )
            ],
            legends=[
                dp.Legend(
                    key="is_invested",
                    items=[dp.LegendItem(icon="#ADD8E6", label="Internal (Double Accounting)", value=False)],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "name"), repeat_field(2, "name_repr")],
                ["inception_date", "delisted_date", "isin", "id_repr"],
                ["share_price", "issue_price", "initial_high_water_mark", "currency"],
                [repeat_field(2, "bank"), repeat_field(2, "parent")],
                [repeat_field(4, "tags")],
                [repeat_field(4, "description")],
                [repeat_field(4, "classifications_section")],
                [repeat_field(4, "fees_section")],
                [repeat_field(4, "information_section")],
                [repeat_field(4, "white_label_customers_section")],
                [repeat_field(4, "portfolios_section")],
                [repeat_field(4, "related_instruments_section")],
                [repeat_field(4, "baseindexpositions_section")],
                [repeat_field(4, "portfoliorole_section")],
                [repeat_field(4, "preferredclassification_section")],
            ],
            [
                create_simple_section(
                    "classifications_section", _("Classifications"), [["classifications"]], "classifications"
                ),
                create_simple_section(
                    "fees_section",
                    _("Fees"),
                    [
                        ["current_bank_fees", "current_management_fees", "current_performance_fees", "."],
                    ],
                    "fees",
                ),
                create_simple_section(
                    "information_section",
                    _("Information"),
                    [
                        [repeat_field(2, "asset_class"), "type_of_return", "legal_structure"],
                        ["jurisdiction", "investment_index", repeat_field(2, "risk_scale")],
                        [repeat_field(2, "external_webpage"), repeat_field(2, "liquidity")],
                    ],
                    "information",
                ),
                create_simple_section(
                    "white_label_customers_section",
                    _("White Label Customers"),
                    [["white_label_customers"]],
                    "white_label_customers",
                ),
                create_simple_section("portfolios_section", _("Portfolios"), [["portfolios"]], "portfolios"),
                create_simple_section(
                    "related_instruments_section",
                    _("Related Instruments"),
                    [["related_instruments"]],
                    "related_instruments",
                ),
                create_simple_section(
                    "baseindexpositions_section", _("Index"), [["baseindexpositions"]], "baseindexpositions"
                ),
                create_simple_section("portfoliorole_section", _("Roles"), [["portfoliorole"]], "portfoliorole"),
                create_simple_section(
                    "preferredclassification_section",
                    _("Preferred Classification per Instrument"),
                    [["preferredclassification"]],
                    "preferredclassification",
                ),
            ],
        )


class ProductCustomerDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label="Name"),
                dp.Field(key="isin", label="ISIN"),
                dp.Field(key="ticker", label="Ticker"),
                dp.Field(key="net_value", label="Net Value"),
                dp.Field(key="bank_repr", label="Bank"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(3, "name")],
                ["isin", "ticker", "bank"],
                ["share_price", "issue_price", "currency"],
                [repeat_field(3, "description")],
            ]
        )


class ProductPerformanceFeesDisplayConfig(ProductDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="computed_str", label="Title", width=Unit.PIXEL(400)),
                dp.Field(key="isin", label="ISIN", width=Unit.PIXEL(150)),
                dp.Field(key="sum_management_fees", label="Mgmt", width=Unit.PIXEL(150)),
                dp.Field(key="sum_management_fees_usd", label="Mgmt ($)", width=Unit.PIXEL(150)),
                dp.Field(key="sum_performance_fees_net", label="Perf", width=Unit.PIXEL(150)),
                dp.Field(key="sum_performance_fees_net_usd", label="Perf ($)", width=Unit.PIXEL(150)),
                dp.Field(key="sum_total", label="Total", width=Unit.PIXEL(150)),
                dp.Field(
                    key="sum_total_usd",
                    label="$ Total",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"fontWeight": "bold"},
                        ),
                    ],
                    width=Unit.PIXEL(150),
                ),
            ]
        )
