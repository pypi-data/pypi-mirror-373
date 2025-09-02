from collections import defaultdict
from typing import Optional

from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ESGMetricAggregationPortfolioPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(
                key=None,
                label="Portfolio Data",
                children=[
                    dp.Field(
                        key="underlying_instrument_repr",
                        label="Name",
                        width=Unit.PIXEL(300),
                    ),
                    dp.Field(key="weighting", label="Weight", width=Unit.PIXEL(100)),
                    dp.Field(key="total_value_fx_usd", label="Total Asset (USD)", width=Unit.PIXEL(150)),
                ],
            )
        ]
        esg_data_fields = [
            dp.Field(
                key="esg_data",
                label=self.view.esg_aggregation.get_esg_code().name,
                width=Unit.PIXEL(150),
            )
        ]
        for extra in self.view.dataloader.extra_esg_data_logs:
            esg_data_fields.append(dp.Field(key=extra.series.name, label=extra.label, width=Unit.PIXEL(150)))
        fields.append(
            dp.Field(key=None, label="ESG Data", children=esg_data_fields),
        )
        if self.view.dataloader.intermediary_logs:
            intermediary_fields = []
            intermediary_groups = defaultdict(list)

            for intermediary in self.view.dataloader.intermediary_logs:
                field = dp.Field(
                    key=intermediary.series.name,
                    label=intermediary.label,
                    width=Unit.PIXEL(100),
                )
                if intermediary.group:
                    intermediary_groups[intermediary.group].append(field)

                else:
                    intermediary_fields.append(
                        dp.Field(
                            key=intermediary.series.name,
                            label=intermediary.label,
                            width=Unit.PIXEL(150),
                        )
                    )
            for group_name, intermediary_groups_fields in intermediary_groups.items():
                intermediary_fields.append(dp.Field(key=None, label=group_name, children=intermediary_groups_fields))
            fields.append(
                dp.Field(key=None, label="Intermediary", children=intermediary_fields),
            )
        fields.append(
            dp.Field(
                key=None,
                label="Metric",
                children=[
                    dp.Field(key="metric", label=self.view.esg_aggregation.value, width=Unit.PIXEL(150)),
                    dp.Field(
                        key="weights_in_coverage",
                        label="Weight in Coverage",
                        width=Unit.PIXEL(100),
                    ),
                ],
            )
        )
        return dp.ListDisplay(fields=fields)
