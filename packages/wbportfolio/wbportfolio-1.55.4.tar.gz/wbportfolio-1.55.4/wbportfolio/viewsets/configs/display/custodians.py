from typing import Optional

from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class CustodianDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label="Name", width=Unit.PIXEL(200)),
                dp.Field(key="mapping", label="Mapping", width=Unit.PIXEL(200)),
            ],
            formatting=[],
            legends=[],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["name", "mapping"]])
