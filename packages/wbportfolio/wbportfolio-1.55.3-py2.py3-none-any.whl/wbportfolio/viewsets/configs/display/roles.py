from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class PortfolioRoleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="role_type", label="Type"),
                dp.Field(key="person", label="Person"),
                dp.Field(key="start", label="Start"),
                dp.Field(key="end", label="End"),
                dp.Field(key="weighting", label="Weighting"),
                dp.Field(key="instrument", label="Instrument"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["role_type", repeat_field(2, "person")], ["start", "end", "weighting"], [repeat_field(3, "instrument")]]
        )


class PortfolioRoleInstrumentDisplayConfig(PortfolioRoleDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="role_type", label="Type"),
                dp.Field(key="person", label="Person"),
                dp.Field(key="start", label="Start"),
                dp.Field(key="end", label="End"),
                dp.Field(key="weighting", label="Weighting"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["role_type", repeat_field(2, "person")],
                ["start", "end", "weighting"],
            ]
        )
