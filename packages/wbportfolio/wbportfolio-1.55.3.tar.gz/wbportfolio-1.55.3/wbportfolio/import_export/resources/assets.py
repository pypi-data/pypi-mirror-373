from import_export import fields
from import_export.widgets import DecimalWidget, ForeignKeyWidget
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.io.resources import ViewResource
from wbfdm.models import Exchange

from wbportfolio.models import AssetPosition


class AssetPositionResource(ViewResource):
    """
    The resource to download AssetPositions
    """

    exchange = fields.Field(
        column_name="exchange",
        attribute="exchange",
        widget=ForeignKeyWidget(Exchange, field="name"),
    )

    price = fields.Field(column_name="price", attribute="price", widget=DecimalWidget())
    shares = fields.Field(column_name="shares", attribute="shares", widget=DecimalWidget())
    total_value = fields.Field(column_name="total_value", attribute="total_value", widget=DecimalWidget())
    currency_fx_rate = fields.Field(
        column_name="currency_fx_rate", attribute="currency_fx_rate", widget=DecimalWidget()
    )
    total_value_fx_portfolio = fields.Field(
        column_name="total_value_fx_portfolio", attribute="total_value_fx_portfolio", widget=DecimalWidget()
    )
    total_value_fx_usd = fields.Field(
        column_name="total_value_fx_portfolio", attribute="total_value_fx_portfolio", widget=DecimalWidget()
    )

    currency = fields.Field(
        column_name="currency",
        attribute="currency",
        widget=ForeignKeyWidget(Currency, field="key"),
    )

    class Meta:
        import_id_fields = ("id",)
        fields = (
            "date",
            "exchange",
            "price",
            "shares",
            "total_value",
            "currency",
            "currency_fx_rate",
            "total_value_fx_portfolio",
            "total_value_fx_usd",
            "weighting",
        )
        export_order = (
            "date",
            "underlying_quote_name",
            "underlying_quote_ticker",
            "underlying_quote_isin",
            "exchange",
            "price",
            "shares",
            "total_value",
            "currency",
            "currency_fx_rate",
            "total_value_fx_portfolio",
            "total_value_fx_usd",
            "weighting",
        )
        model = AssetPosition
