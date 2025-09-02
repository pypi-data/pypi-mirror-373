from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbportfolio.models import Adjustment


class AdjustmentDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="instrument", label="Equity")
                if not self.view.kwargs.get("instrument_id", None)
                else None,
                dp.Field(key="date", label="Date"),
                dp.Field(key="factor", label="Factor"),
                dp.Field(key="cumulative_factor", label="Cumulative Factor"),
                dp.Field(key="last_handler", label="Last Handler"),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=Adjustment.Status.PENDING.label,
                            value=Adjustment.Status.PENDING.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_DARK.value,
                            label=Adjustment.Status.APPLIED.label,
                            value=Adjustment.Status.APPLIED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=Adjustment.Status.DENIED.label,
                            value=Adjustment.Status.DENIED.value,
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
                            condition=("==", Adjustment.Status.PENDING.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_DARK.value},
                            condition=("==", Adjustment.Status.APPLIED.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", Adjustment.Status.DENIED.value),
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        if "instrument_id" in self.view.kwargs:
            fields = [
                [repeat_field(3, "status")],
                ["date", "factor", "cumulative_factor"],
            ]
        else:
            fields = [
                [repeat_field(3, "status")],
                [repeat_field(3, "instrument")],
                ["date", "factor", "cumulative_factor"],
            ]
        return create_simple_display(fields)
