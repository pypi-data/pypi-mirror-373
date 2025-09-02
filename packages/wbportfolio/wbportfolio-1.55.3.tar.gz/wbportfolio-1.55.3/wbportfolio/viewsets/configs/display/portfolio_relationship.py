from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class PortfolioInstrumentPreferredClassificationThroughDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display([["instrument", "classification"]])

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="instrument", label="Instrument"),
                dp.Field(key="classification_group", label="Preferred Classification Group"),
                dp.Field(key="classification", label="Preferred Classification"),
            ]
        )


class InstrumentPortfolioThroughPortfolioModelDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="instrument", label="Instrument"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["instrument"],
            ]
        )
