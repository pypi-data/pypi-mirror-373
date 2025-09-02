from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbfdm.serializers import InvestableUniverseRepresentationSerializer

from wbportfolio.models import DividendTransaction
from wbportfolio.serializers import PortfolioRepresentationSerializer


class DividendRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = DividendTransaction
        fields = ("id", "value_date")


class DividendModelSerializer(wb_serializers.ModelSerializer):
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")
    _underlying_instrument = InvestableUniverseRepresentationSerializer(source="underlying_instrument")
    _currency = CurrencyRepresentationSerializer(source="currency")

    total_value = wb_serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True, required=False)
    total_value_fx_portfolio = wb_serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True, required=False
    )
    total_value_gross = wb_serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True, required=False)
    total_value_gross_fx_portfolio = wb_serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True, required=False
    )

    class Meta:
        model = DividendTransaction
        fields = (
            "id",
            "value_date",
            "record_date",
            "ex_date",
            "portfolio",
            "underlying_instrument",
            "currency",
            "_portfolio",
            "_underlying_instrument",
            "_currency",
            "total_value",
            "total_value_fx_portfolio",
            "total_value_gross",
            "total_value_gross_fx_portfolio",
        )
