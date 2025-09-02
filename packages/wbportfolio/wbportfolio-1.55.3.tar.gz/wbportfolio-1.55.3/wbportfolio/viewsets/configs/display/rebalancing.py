from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import Display, create_simple_display
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class RebalancerDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="portfolio", label="Portfolio"),
                dp.Field(key="rebalancing_model", label="Rebalancing Model"),
                dp.Field(key="apply_order_proposal_automatically", label="Approve automatically"),
                dp.Field(key="frequency_repr", label="Frequency"),
                dp.Field(key="activation_date", label="Activation Date"),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["rebalancing_model", "apply_order_proposal_automatically"],
                ["frequency", "activation_date"],
                ["rebalancing_dates", "rebalancing_dates"],
            ]
        )
