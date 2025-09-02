from django.contrib import admin

from wbportfolio.models import AssetPosition


@admin.register(AssetPosition)
class AssetPositionModelAdmin(admin.ModelAdmin):
    list_filter = ("underlying_instrument", "portfolio")
    search_fields = (
        "underlying_instrument__name",
        "underlying_instrument__ticker",
    )
    # date_hierarchy = "date"
    list_filter = ("underlying_instrument__instrument_type",)
    list_display = (
        "date",
        "_price",
        "currency",
        "_currency_fx_rate",
        "_shares",
        "_total_value_fx_usd",
        "weighting",
        "portfolio",
        "underlying_instrument",
    )
    readonly_fields = [
        "_market_capitalization",
        "_price",
        "_currency_fx_rate",
        "_price_fx_portfolio",
        "_total_value",
        "_total_value_fx_usd",
        "_total_value_fx_portfolio",
        "_market_share",
    ]
    autocomplete_fields = [
        "portfolio",
        "currency",
        "underlying_instrument",
    ]
    ordering = ("-date",)
    raw_id_fields = [
        "import_source",
        "applied_adjustment",
        "underlying_quote_price",
        "currency_fx_rate_instrument_to_usd",
        "currency_fx_rate_portfolio_to_usd",
    ]
