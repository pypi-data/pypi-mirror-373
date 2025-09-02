from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.directory.viewsets.display.entries import CompanyModelDisplay as CMD
from wbcore.contrib.directory.viewsets.display.entries import PersonModelDisplay as PMD
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import (
    Inline,
    Layout,
    Page,
    Section,
    Style,
)
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

AUM_TABLE = Section(
    key="aum_table_section",
    collapsible=False,
    title=_("AUM By Product"),
    display=Display(
        pages=[
            Page(
                title=_("AUM By Product"),
                layouts={
                    default(): Layout(
                        grid_template_areas=[["aum_table"]],
                        inlines=[Inline(key="aum_table", endpoint="wbportfolio_aum")],
                    )
                },
            ),
        ]
    ),
)

AUM_FIELDS = Section(
    key="aum_fields_section",
    collapsible=False,
    title=_("AUM"),
    display=Display(
        pages=[
            Page(
                title=_("AUM"),
                layouts={
                    default(): Layout(
                        grid_template_areas=[
                            ["asset_under_management", "assets_under_management_currency", "investment_discretion"],
                            ["invested_assets_under_management_usd", "potential", "."],
                        ],
                        grid_auto_columns="minmax(min-content, 1fr)",
                        grid_auto_rows=Style.MIN_CONTENT,
                    )
                },
            ),
        ]
    ),
)


class CompanyModelDisplay(CMD):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        list_display = super().get_list_display()
        list_display.fields = (
            *list_display.fields[:5],
            dp.Field(key="invested_assets_under_management_usd", label="AUM Invested"),
            dp.Field(key="asset_under_management", label="AUM"),
            dp.Field(key="potential", label="Potential"),
            *list_display.fields[5:],
        )
        return list_display

    AUM_TABLE = AUM_TABLE
    PORTFOLIO_FIELDS = AUM_FIELDS

    def get_instance_display(self) -> Display:
        asset_allocation_section = Section(
            key="asset_allocation_section",
            collapsible=False,
            title=_("Asset Allocation"),
            display=Display(
                pages=[
                    Page(
                        title=_("Asset Allocation"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["asset_allocation"]],
                                inlines=[Inline(key="asset_allocation", endpoint="asset_allocation_table")],
                            )
                        },
                    ),
                ]
            ),
        )

        geographic_focus_section = Section(
            key="geographic_focus_section",
            collapsible=False,
            title=_("Geographic Focus"),
            display=Display(
                pages=[
                    Page(
                        title=_("Geographic Focus"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["geographic_focus"]],
                                inlines=[Inline(key="geographic_focus", endpoint="geographic_focus_table")],
                            )
                        },
                    ),
                ]
            ),
        )

        instance_display = super().get_instance_display()
        if "pk" in self.view.kwargs:
            instance_display.pages.insert(
                1,
                Page(
                    title=_("Customer Information"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["asset_allocation_section", "geographic_focus_section"]],
                            sections=[asset_allocation_section, geographic_focus_section],
                        )
                    },
                ),
            )

        return instance_display


class PersonModelDisplay(PMD):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        list_display = super().get_list_display()

        list_display.fields = (
            *list_display.fields[:7],
            dp.Field(key="invested_assets_under_management_usd", label="AUM Invested"),
            dp.Field(key="asset_under_management", label="AUM"),
            dp.Field(key="potential", label="Potential"),
            *list_display.fields[7:],
        )
        return list_display

    AUM_TABLE = AUM_TABLE
    PORTFOLIO_FIELDS = AUM_FIELDS


class AssetAllocationDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="percent", label="Percent"),
                dp.Field(key="asset_type", label="Type"),
                dp.Field(key="max_investment", label="Max Investment"),
                dp.Field(key="comment", label="Comment"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["company", "percent", "asset_type", "max_investment"], [repeat_field(4, "comment")]]
        )


class GeographicFocusDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="percent", label="Percent"),
                dp.Field(key="country", label="Location"),
                dp.Field(key="comment", label="Comment"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["company", "percent", "country"], [repeat_field(3, "comment")]])
