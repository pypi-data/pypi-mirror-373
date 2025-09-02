from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer

from wbportfolio.models import Fees
from wbportfolio.serializers.products import ProductRepresentationSerializer


class FeesRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:fees-detail")

    class Meta:
        model = Fees
        fields = ("transaction_subtype", "total_value", "_detail")


class FeesModelSerializer(wb_serializers.ModelSerializer):
    _product = ProductRepresentationSerializer(source="product")
    _currency = CurrencyRepresentationSerializer(source="currency")
    total_value_fx_portfolio = wb_serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True, required=False
    )
    total_value_gross_fx_portfolio = wb_serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True, required=False
    )

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        if (view := request.parser_context.get("view")) and view.is_manager and instance.import_source:
            return {"import_source": instance.import_source.file.url}
        return {}

    class Meta:
        model = Fees
        decorators = {
            "total_value": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "total_value_fx_portfolio": wb_serializers.decorator(
                position="left", value="{{_portfolio.currency_symbol}}"
            ),
            "total_value_gross": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "total_value_gross_fx_portfolio": wb_serializers.decorator(
                position="left", value="{{_portfolio.currency_symbol}}"
            ),
        }
        fields = (
            "id",
            "_additional_resources",
            "transaction_subtype",
            "calculated",
            "fee_date",
            "product",
            "currency",
            "_product",
            "_currency",
            "total_value",
            "total_value_fx_portfolio",
            "total_value_gross",
            "total_value_gross_fx_portfolio",
        )
