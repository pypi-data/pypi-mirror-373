from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class AccountReconciliationDisplayViewConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="reconciliation_date", label="Reconciliation Date"),
                dp.Field(key="account", label="Account"),
                dp.Field(key="creator", label="Creator"),
                dp.Field(key="approved_by", label="Approved By"),
                dp.Field(key="approved_dt", label="Approved Timestamp"),
            ],
            formatting=[
                dp.Formatting(
                    column="approved_dt",
                    formatting_rules=[dp.FormattingRule(condition=("∃", True), style={"backgroundColor": "#77DD77"})],
                ),
            ],
            legends=[dp.Legend(items=[dp.LegendItem(label="Agreed Reconciliations", icon="#77DD77")])],
        )

    def get_instance_display(self) -> dp.Display:
        return dp.Display(
            pages=[
                dp.Page(
                    layouts={
                        dp.default(): dp.Layout(
                            grid_template_areas=[
                                ["reconciliation_date", "account", "creator", "approved_by", "approved_dt"],
                                [repeat_field(5, "lines")],
                            ],
                            grid_template_rows=["min-content", "1fr"],
                            inlines=[dp.Inline(key="lines", endpoint="lines")],
                        )
                    }
                )
            ]
        )


class AccountReconciliationLineDisplayViewConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        difference = [
            dp.FormattingRule(condition=("<", 0), style={"fontWeight": "bold", "color": "#FF6961"}),
            dp.FormattingRule(condition=(">", 0), style={"fontWeight": "bold", "color": "green"}),
        ]
        editable = [dp.FormattingRule(style={"fontWeight": "bold"})]
        equal = [dp.FormattingRule(condition=("==", False, "is_equal"), style={"backgroundColor": "orange"})]
        borderLeft = [
            dp.FormattingRule(
                style={
                    "borderLeft": "1px solid #bdc3c7",
                }
            )
        ]
        borderRight = [
            dp.FormattingRule(
                style={
                    "borderRight": "1px solid #bdc3c7",
                }
            )
        ]

        return dp.ListDisplay(
            hide_control_bar=True,
            fields=[
                dp.Field(
                    key="product",
                    label="Product",
                    width=450,
                ),
                dp.Field(
                    key="price_date",
                    label="Date",
                    width=100,
                ),
                dp.Field(
                    label="Our Calculations",
                    key="system",
                    children=[
                        dp.Field(
                            key="shares",
                            label="Shares",
                            width=90,
                        ),
                        dp.Field(
                            key="nominal_value",
                            label="Nominal",
                            width=90,
                        ),
                        dp.Field(
                            key="price",
                            label="Price",
                            width=100,
                        ),
                        dp.Field(
                            key="assets_under_management",
                            label="AuM",
                            width=120,
                        ),
                    ],
                ),
                dp.Field(
                    label="Your Input (Please adjust the columns in bold if necessary)",
                    key="confirmation",
                    children=[
                        dp.Field(
                            key="shares_external",
                            label="Shares",
                            width=90,
                            formatting_rules=[*equal, *editable, *borderLeft],
                        ),
                        dp.Field(
                            key="nominal_value_external",
                            label="Nominal",
                            width=90,
                            formatting_rules=[*equal, *editable],
                        ),
                        dp.Field(
                            key="price",
                            label="Price",
                            width=100,
                        ),
                        dp.Field(
                            key="assets_under_management_external",
                            label="AuM",
                            width=120,
                            formatting_rules=[*equal, *borderRight],
                        ),
                    ],
                ),
                dp.Field(
                    label="Differences",
                    key="differences",
                    children=[
                        dp.Field(key="pct_diff", label="Shares", width=90, formatting_rules=difference),
                        dp.Field(key="shares_diff", label="Shares", width=90, formatting_rules=difference),
                        dp.Field(key="nominal_value_diff", label="Nominal", width=90, formatting_rules=difference),
                        dp.Field(
                            key="assets_under_management_diff",
                            label="AuM",
                            width=120,
                            formatting_rules=difference,
                        ),
                    ],
                ),
            ],
        )
