from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.display import Display
from wbcore.metadata.configs.display.instance_display.layouts.layouts import Layout
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.instance_display.pages import Page
from wbcore.metadata.configs.display.instance_display.styles import Style
from wbcore.metadata.configs.display.instance_display.utils import repeat
from wbfdm.viewsets.configs.display.instruments import InstrumentDisplayConfig


class ProductGroupDisplayConfig(InstrumentDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="identifier", label="Identifier"),
                dp.Field(key="name", label="Name"),
                dp.Field(key="umbrella", label="Umbrella"),
                dp.Field(key="type", label="Type"),
                dp.Field(key="category", label="Category"),
                dp.Field(key="management_company", label="Management"),
                dp.Field(key="depositary", label="Depositary"),
                dp.Field(key="transfer_agent", label="TA"),
                dp.Field(key="administrator", label="Administrator"),
                dp.Field(key="investment_manager", label="Manager"),
                dp.Field(key="auditor", label="Auditor"),
                dp.Field(key="paying_agent", label="Paying Agent"),
            ]
        )

    def get_instance_display(self) -> Display:
        display = super().get_instance_display()
        return Display(
            pages=[
                display.pages[0],
                Page(
                    title="Product Group Information",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["type", "category", "umbrella", "."],
                                ["management_company", "depositary", "transfer_agent", "administrator"],
                                ["investment_manager", "auditor", "paying_agent", "."],
                            ],
                            grid_template_columns=[
                                repeat(4, Style.fr(1)),
                            ],
                        )
                    },
                ),
                *display.pages[1:],
            ]
        )
