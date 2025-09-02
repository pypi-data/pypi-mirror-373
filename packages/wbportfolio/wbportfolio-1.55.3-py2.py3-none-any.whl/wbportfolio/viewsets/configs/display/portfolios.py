from typing import Optional

from django.utils.translation import gettext_lazy as _
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import Layout, Page, default
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_page_with_inline,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class PortfolioDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(
                    label="Information",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="name", label="Name", width=Unit.PIXEL(300)),
                        dp.Field(key="currency", label="CCY", width=Unit.PIXEL(75)),
                        dp.Field(key="hedged_currency", label="Hedged CCY", width=Unit.PIXEL(100), show="open"),
                        dp.Field(key="updated_at", label="Updated At", width=Unit.PIXEL(150)),
                        dp.Field(key="depends_on", label="Depends on", show="open", width=Unit.PIXEL(300)),
                        dp.Field(key="invested_timespan", label="Invested", show="open"),
                        dp.Field(key="instruments", label="Instruments", width=Unit.PIXEL(250)),
                    ],
                ),
                dp.Field(
                    label="Valuation & Position",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="initial_position_date", label="Issue Date", width=Unit.PIXEL(150)),
                        dp.Field(key="last_position_date", label="Last Position Date", width=Unit.PIXEL(150)),
                        dp.Field(
                            key="last_asset_under_management_usd", label="AUM ($)", width=Unit.PIXEL(100), show="open"
                        ),
                        dp.Field(key="last_positions", label="Position", width=Unit.PIXEL(100), show="open"),
                    ],
                ),
                dp.Field(
                    label="Rebalancing",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="automatic_rebalancer", label="Automatic Rebalancer"),
                        dp.Field(key="last_order_proposal_date", label="Last Rebalance", width=Unit.PIXEL(250)),
                        dp.Field(
                            key="next_expected_order_proposal_date",
                            label="Next Rebalancing",
                            width=Unit.PIXEL(250),
                            show="open",
                        ),
                    ],
                ),
                dp.Field(
                    label="Administration",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="is_manageable", label="Managed", width=Unit.PIXEL(100)),
                        dp.Field(key="is_tracked", label="Tracked", width=Unit.PIXEL(100), show="open"),
                        dp.Field(key="only_weighting", label="Only-Weight", width=Unit.PIXEL(100), show="open"),
                        dp.Field(key="is_lookthrough", label="Look through", width=Unit.PIXEL(100), show="open"),
                        dp.Field(key="is_composition", label="Composition", width=Unit.PIXEL(100), show="open"),
                    ],
                ),
            ]
        )

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    title="Main Information",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["name", "name", "currency", "is_manageable"],
                                ["invested_timespan", "invested_timespan", "create_index", "."]
                                if self.new_mode
                                else [
                                    "invested_timespan",
                                    "invested_timespan",
                                    "automatic_rebalancer",
                                    "automatic_rebalancer",
                                ],
                                ["is_tracked", "is_lookthrough", "only_weighting", "is_composition"],
                                [repeat_field(4, "instruments_section")],
                                [repeat_field(4, "dependencyportfolios_section")],
                                [repeat_field(4, "preferredclassification_section")],
                            ],
                            # grid_template_rows=["min-content"] * 3 + ["1fr", "446px"],
                            # grid_template_columns=[repeat(4, "183px"), "1fr", "1fr"],
                            sections=[
                                create_simple_section(
                                    "instruments_section",
                                    _("Linked Instruments"),
                                    [["instruments_list"]],
                                    "instruments_list",
                                    collapsed=True,
                                ),
                                create_simple_section(
                                    "dependencyportfolios_section",
                                    _("Dependency Portfolios"),
                                    [["dependencyportfolios"]],
                                    "dependencyportfolios",
                                    collapsed=True,
                                ),
                                create_simple_section(
                                    "preferredclassification_section",
                                    _("Preferred Classification"),
                                    [["preferredclassification"]],
                                    "preferredclassification",
                                    collapsed=True,
                                ),
                            ],
                        ),
                    },
                ),
                Page(
                    title="Order",
                    layouts={
                        default(): dp.Layout(
                            grid_template_areas=[
                                ["order_proposals"],
                            ],
                            grid_template_rows=["auto"],
                            inlines=[
                                dp.Inline(key="order_proposals", endpoint="order_proposals"),
                            ],
                        )
                    },
                ),
                Page(
                    title="Composition",
                    display=Display(
                        navigation_type=dp.NavigationType.PANEL,
                        pages=[
                            create_simple_page_with_inline("Assets", "assets"),
                            create_simple_page_with_inline("Top-Down Composition", "topdowncomposition"),
                            create_simple_page_with_inline("Contributor", "contributor"),
                            create_simple_page_with_inline("Distribution Table", "distribution_table"),
                            create_simple_page_with_inline("Distribution Chart", "distribution_chart"),
                            # Page(
                            #     title="Distribution",
                            #     layouts={
                            #         default(): Layout(
                            #             grid_template_areas=[["distribution_table", "distribution_chart"]],
                            #             grid_template_rows=["auto"],
                            #             grid_template_columns=["2fr", "1fr"],
                            #             inlines=[
                            #                 Inline(
                            #                     key="distribution_table", endpoint="distribution_table", title="Table"
                            #                 ),
                            #                 Inline(
                            #                     key="distribution_chart", endpoint="distribution_chart", title="Chart"
                            #                 ),
                            #             ],
                            #         ),
                            #     },
                            # ),
                            create_simple_page_with_inline(
                                "Portfolio Composition vs. Dependant Portfolios", "modelcomposition"
                            ),
                        ],
                    ),
                ),
            ]
        )


class PortfolioPortfolioThroughModelDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="dependency_portfolio", label="Dependency Portfolio"),
                dp.Field(key="portfolio", label="Dependant Portfolio"),
                dp.Field(key="type", label="Type"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["dependency_portfolio", "type"],
            ]
        )


class TopDownPortfolioCompositionPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        rebalancing_column_label = "Last Rebalancing"
        effective_column_label = "Actual"
        if self.view.last_rebalancing_date:
            rebalancing_column_label += f" ({self.view.last_rebalancing_date:%Y-%m-%d})"
        if self.view.last_effective_date:
            effective_column_label += f" ({self.view.last_effective_date:%Y-%m-%d})"
        return dp.ListDisplay(
            fields=[
                dp.Field(key="instrument", label="Instrument", pinned="left"),
                dp.Field(key="rebalancing_weights", label=rebalancing_column_label),
                dp.Field(key="effective_weights", label=effective_column_label),
            ],
            tree=True,
            tree_group_field="instrument",
            tree_group_parent_pointer="parent_row_id",
        )
