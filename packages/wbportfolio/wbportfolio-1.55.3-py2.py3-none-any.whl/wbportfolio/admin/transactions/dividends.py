from django.contrib import admin

from wbportfolio.models import DividendTransaction


@admin.register(DividendTransaction)
class DividendAdmin(admin.ModelAdmin):
    search_fields = ["portfolio__name", "underlying_instrument__computed_str"]
    list_filter = ("distribution_method", "portfolio")
    list_display = (
        "distribution_method",
        "portfolio",
        "underlying_instrument",
        "value_date",
        "currency",
        "currency_fx_rate",
        "total_value",
        "total_value_fx_portfolio",
    )
    fieldsets = (
        (
            "Dividend Information",
            {
                "fields": (
                    (
                        "portfolio",
                        "underlying_instrument",
                        "import_source",
                    ),
                    ("ex_date", "record_date", "value_date"),
                    ("currency", "currency_fx_rate"),
                    ("price", "shares", "retrocession"),
                    ("total_value", "total_value_gross"),
                    ("total_value_fx_portfolio", "total_value_gross_fx_portfolio"),
                    ("created", "updated"),
                    ("comment",),
                )
            },
        ),
    )
    readonly_fields = [
        "total_value",
        "total_value_gross",
        "total_value_fx_portfolio",
        "total_value_gross_fx_portfolio",
        "created",
        "updated",
    ]
    autocomplete_fields = ["portfolio", "underlying_instrument", "currency"]
    ordering = ("-value_date",)
    raw_id_fields = ["import_source"]
