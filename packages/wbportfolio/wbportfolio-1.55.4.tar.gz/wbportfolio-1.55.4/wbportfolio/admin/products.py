from django.contrib import admin
from wbfdm.admin import InstrumentModelAdmin

from wbportfolio.models import FeeProductPercentage, Product

from .roles import PortfolioRoleInline


class FeeProductPercentagTabularInline(admin.TabularInline):
    model = FeeProductPercentage
    fk_name = "product"
    fields = [
        "type",
        "vat_deduction",
        "percent",
        "timespan",
    ]


@admin.register(Product)
class ProductAdmin(InstrumentModelAdmin):
    search_fields = ("name", "isin", "ticker")
    list_display = ("name", "ticker", "isin", "bank", "primary_benchmark", "_is_invested")
    autocomplete_fields = [
        "country",
        "jurisdiction",
        "white_label_customers",
        "bank",
        "default_account",
        "parent",
        *InstrumentModelAdmin.autocomplete_fields,
    ]
    fieldsets = (
        ("Instrument Information", InstrumentModelAdmin.fieldsets[0][1]),
        (
            "Product Information",
            {
                "fields": (
                    ("share_price", "initial_high_water_mark", "bank"),
                    ("fee_calculation", "net_asset_value_computation_method_path", "order_routing_custodian_adapter"),
                    (
                        "white_label_customers",
                        "default_account",
                        "bank_account",
                    ),
                )
            },
        ),
        (
            "Factsheet",
            {
                "fields": (
                    ("type_of_return", "asset_class", "legal_structure"),
                    ("investment_index", "liquidity", "risk_scale"),
                    (
                        "jurisdiction",
                        "dividend",
                        "termsheet",
                    ),
                    ("external_webpage", "minimum_subscription", "cut_off_time"),
                )
            },
        ),
    )

    inlines = [FeeProductPercentagTabularInline, PortfolioRoleInline, *InstrumentModelAdmin.inlines]
    raw_id_fields = [
        "country",
        "jurisdiction",
        "white_label_customers",
        "bank",
        "default_account",
        "parent",
        *InstrumentModelAdmin.raw_id_fields,
    ]

    def update_preferred_classification_per_instrument(self, request, queryset):
        for product in queryset.all():
            if portfolio := product.portfolio:
                portfolio.update_preferred_classification_per_instrument()

    actions = [update_preferred_classification_per_instrument]
