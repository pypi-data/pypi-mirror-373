from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class RegisterDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="register_reference", label="Register Reference"),
                dp.Field(key="register_name_1", label="Register Name 1"),
                dp.Field(key="register_name_2", label="Register Name 2"),
                dp.Field(key="custodian_reference", label="Custodian Reference"),
                dp.Field(key="custodian_name_1", label="Custodian Name 1"),
                dp.Field(key="custodian_name_2", label="Custodian Name 2"),
                dp.Field(key="outlet_reference", label="Outlet Reference"),
                dp.Field(key="outlet_name", label="Outlet Name"),
                dp.Field(key="status", label="Status"),
                dp.Field(key="status_message", label="Status Message"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["register_reference", "register_name_1", "register_name_2"],
                ["global_register_reference", "external_register_reference", "."],
                ["citizenship", "residence", "investor_type"],
                [repeat_field(3, "custodian_section")],
                [repeat_field(3, "outlet_section")],
                [repeat_field(3, "information_section")],
            ],
            [
                create_simple_section(
                    "custodian_section",
                    "Custodian",
                    [
                        ["custodian_reference", "custodian_name_1", "custodian_name_2"],
                        [repeat_field(3, "custodian_address")],
                        ["custodian_postcode", "custodian_city", "custodian_country"],
                    ],
                ),
                create_simple_section(
                    "outlet_section",
                    "Outlet",
                    [
                        ["sales_reference", repeat_field(2, "dealer_reference")],
                        ["outlet_reference", repeat_field(2, "outlet_name")],
                        [repeat_field(3, "outlet_address")],
                        ["outlet_postcode", "outlet_city", "outlet_country"],
                    ],
                ),
                create_simple_section(
                    "information_section",
                    "Information",
                    [
                        ["opened", repeat_field(2, "status")],
                        [".", "opened_reference_1", "opened_reference_2"],
                        [".", "updated_reference_1", "updated_reference_2"],
                        [repeat_field(3, "status_message")],
                    ],
                ),
            ],
        )
