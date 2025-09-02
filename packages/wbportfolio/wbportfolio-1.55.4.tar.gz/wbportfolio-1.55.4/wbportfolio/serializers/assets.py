from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbfdm.serializers import InvestableInstrumentRepresentationSerializer
from wbfdm.serializers.exchanges import ExchangeRepresentationSerializer

from wbportfolio.models import AssetPosition, Portfolio

from .portfolios import PortfolioRepresentationSerializer


class AssetPositionModelSerializer(wb_serializers.ModelSerializer):
    underlying_quote_isin = wb_serializers.CharField(read_only=True)
    underlying_quote_ticker = wb_serializers.CharField(read_only=True)
    underlying_quote_name = wb_serializers.CharField(read_only=True)
    _underlying_quote = InvestableInstrumentRepresentationSerializer(source="underlying_quote", label_key="name")
    _currency = CurrencyRepresentationSerializer(source="currency")
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")
    _exchange = ExchangeRepresentationSerializer(source="exchange")
    _portfolio_created = PortfolioRepresentationSerializer(source="portfolio_created")

    shares = wb_serializers.DecimalField(read_only=True, decimal_places=4, max_digits=14)
    total_value_fx_usd = wb_serializers.FloatField(read_only=True, precision=2)
    liquidity = wb_serializers.FloatField(read_only=True, default=0, precision=2)
    market_share = wb_serializers.FloatField(read_only=True, precision=6)
    market_capitalization = wb_serializers.FloatField(read_only=True)
    price = wb_serializers.DecimalField(read_only=True, decimal_places=4, max_digits=14)
    currency_fx_rate = wb_serializers.FloatField(read_only=True)
    price_fx_portfolio = wb_serializers.FloatField(read_only=True)
    total_value = wb_serializers.FloatField(read_only=True)
    total_value_fx_portfolio = wb_serializers.FloatField(read_only=True)

    is_invested = wb_serializers.BooleanField(read_only=True, default=False)
    currency_symbol = wb_serializers.CharField(read_only=True)
    portfolio_currency_symbol = wb_serializers.CharField(read_only=True)

    class Meta:
        decorators = {
            "total_value_fx_portfolio": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{portfolio_currency_symbol}}"
            ),
            "total_value": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{currency_symbol}}"
            ),
            "price": wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}"),
            "total_value_fx_usd": wb_serializers.decorator(decorator_type="text", position="left", value="$"),
        }
        percent_fields = ["weighting", "market_share"]
        model = AssetPosition
        fields = (
            "id",
            "asset_valuation_date",
            "exchange",
            "price_denotation",
            "date",
            "shares",
            "weighting",
            "portfolio",
            "portfolio_created",
            "currency",
            "_currency",
            "currency_fx_rate",
            "market_share",
            "market_capitalization",
            "currency_fx_rate",
            "price",
            "price_fx_portfolio",
            "total_value",
            "total_value_fx_usd",
            "total_value_fx_portfolio",
            "liquidity",
            "is_estimated",
            "underlying_quote_name",
            "underlying_quote_isin",
            "underlying_quote_ticker",
            "underlying_quote",
            "_underlying_quote",
            "_portfolio",
            "_portfolio_created",
            "_exchange",
            "exchange",
            "is_invested",
            "_additional_resources",
            "currency_symbol",
            "portfolio_currency_symbol",
        )


class AssetPositionPortfolioModelSerializer(AssetPositionModelSerializer):
    _portfolio = None

    class Meta(AssetPositionModelSerializer.Meta):
        fields = (
            "id",
            "is_estimated",
            "underlying_quote_name",
            "underlying_quote_isin",
            "underlying_quote_ticker",
            "underlying_quote",
            "_underlying_quote",
            "currency",
            "_currency",
            "exchange",
            "_exchange",
            "price",
            "shares",
            "total_value",
            "currency_fx_rate",
            "total_value_fx_portfolio",
            "total_value_fx_usd",
            "weighting",
            "portfolio_created",
            "_portfolio_created",
            "market_share",
            "asset_valuation_date",
            "liquidity",
            "currency_symbol",
            "portfolio_currency_symbol",
        )
        read_only_fields = fields


class AssetPositionAggregatedPortfolioModelSerializer(AssetPositionPortfolioModelSerializer):
    # If the aggregated serializer is used, we only show the related model representation for performance
    currency = wb_serializers.CharField()

    class Meta(AssetPositionModelSerializer.Meta):
        fields = (
            "id",
            "is_estimated",
            "underlying_quote_isin",
            "underlying_quote_ticker",
            "underlying_quote_name",
            "currency",
            "price",
            "shares",
            "total_value",
            "currency_fx_rate",
            "total_value_fx_portfolio",
            "total_value_fx_usd",
            "weighting",
            "market_share",
            "asset_valuation_date",
            "liquidity",
            "currency_symbol",
            "portfolio_currency_symbol",
        )
        read_only_fields = fields


class AssetPositionInstrumentModelSerializer(AssetPositionModelSerializer):
    class Meta(AssetPositionModelSerializer.Meta):
        fields = AssetPositionModelSerializer.Meta.fields


class CashPositionPortfolioModelSerializer(wb_serializers.ModelSerializer):
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")
    sum_total_value_fx_usd = wb_serializers.FloatField(read_only=True)
    portfolio = wb_serializers.PrimaryKeyRelatedField(queryset=Portfolio.objects.all())

    class Meta:
        decorators = {
            "sum_total_value_fx_usd": wb_serializers.decorator(decorator_type="text", position="left", value="$")
        }
        model = AssetPosition
        fields = ("id", "portfolio", "_portfolio", "sum_total_value_fx_usd", "date", "_additional_resources")
