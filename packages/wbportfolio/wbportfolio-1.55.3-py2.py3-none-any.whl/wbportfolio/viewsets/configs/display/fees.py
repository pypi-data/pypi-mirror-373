from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class FeesDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="portfolio", label="Portfolio"),
                dp.Field(key="transaction_subtype", label="Type"),
                dp.Field(key="fee_date", label="Date"),
                dp.Field(
                    label="Value",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="total_value", label="Value"),
                        dp.Field(key="total_value_fx_portfolio", label="Value (Portfolio)"),
                        dp.Field(key="total_value_usd", label="Value ($)"),
                        dp.Field(key="total_value_gross", label="Value Gross"),
                        dp.Field(key="total_value_gross_fx_portfolio", label="Value Gross (Portfolio)"),
                        dp.Field(key="total_value_gross_usd", label="Value Gross ($)"),
                    ],
                ),
                dp.Field(
                    label="Information",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="currency_fx_rate", label="FX rate"),
                        dp.Field(key="currency", label="Currency"),
                        dp.Field(key="calculated", label="Calculated"),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "portfolio"), "transaction_subtype"],
                ["fee_date", "value_date", "book_date"],
                ["currency_fx_rate", "currency", "."],
                ["total_value", "total_value_fx_portfolio", "."],
                ["total_value_gross", "total_value_gross_fx_portfolio", "."],
                [repeat_field(3, "comment")],
            ]
        )


class FeesProductDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="transaction_subtype", label="Type"),
                dp.Field(key="fee_date", label="Date"),
                dp.Field(
                    label="Value",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(
                            label="Net",
                            open_by_default=False,
                            key=None,
                            children=[
                                dp.Field(key="total_value", label="Value"),
                                dp.Field(key="total_value_fx_portfolio", label="Value (Portfolio)", show="open"),
                                dp.Field(key="total_value_usd", label="Value ($)", show="open"),
                            ],
                        ),
                        dp.Field(
                            label="Gross",
                            open_by_default=False,
                            key=None,
                            children=[
                                dp.Field(key="total_value_gross", label="Value Gross", show="open"),
                                dp.Field(
                                    key="total_value_gross_fx_portfolio", label="Value Gross (Portfolio)", show="open"
                                ),
                                dp.Field(key="total_value_gross_usd", label="Value Gross ($)", show="open"),
                            ],
                        ),
                    ],
                ),
                dp.Field(
                    label="Information",
                    open_by_default=False,
                    key=None,
                    children=[
                        dp.Field(key="calculated", label="Calculated"),
                        dp.Field(key="currency_fx_rate", label="FX rate", show="open"),
                        dp.Field(key="currency", label="Currency", show="open"),
                        dp.Field(key="product", label="Product", show="open"),
                    ],
                ),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(3, "transaction_subtype")],
                ["fee_date", "value_date", "book_date"],
                ["currency_fx_rate", "currency", "."],
                ["total_value", "total_value_fx_portfolio", "."],
                ["total_value_gross", "total_value_gross_fx_portfolio", "."],
                [repeat_field(3, "comment")],
            ]
        )


class FeesAggregatedProductPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="fee_date", label="Date"),
                dp.Field(key="TRANSACTION", label="Transactions"),
                dp.Field(key="PERFORMANCE_CRYSTALIZED", label="Performance"),
                dp.Field(key="PERFORMANCE", label="Performance Crystalized"),
                dp.Field(key="MANAGEMENT", label="Management"),
                dp.Field(key="ISSUER", label="Issuer"),
                dp.Field(key="OTHER", label="Other"),
                dp.Field(key="total", label="Total"),
            ]
        )
