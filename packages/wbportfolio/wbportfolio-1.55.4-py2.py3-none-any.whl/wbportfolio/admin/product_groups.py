from django.contrib import admin
from wbfdm.admin.instruments import InstrumentModelAdmin

from wbportfolio.models import ProductGroup, ProductGroupRepresentant

from .portfolio_relationships import InstrumentPortfolioThroughModelAdmin


@admin.register(ProductGroup)
class ProductGroupAdmin(InstrumentModelAdmin):
    search_fields = ("name", "currency")

    autocomplete_fields = [
        "management_company",
        "depositary",
        "transfer_agent",
        "administrator",
        "investment_manager",
        "auditor",
        "paying_agent",
        "currency",
    ] + InstrumentModelAdmin.autocomplete_fields

    fieldsets = (
        ("Instrument Information", InstrumentModelAdmin.fieldsets[0][1]),
        (
            "Group Information",
            {
                "fields": (
                    ("type", "category", "umbrella"),
                    ("management_company", "depositary", "transfer_agent", "administrator"),
                    ("investment_manager", "auditor", "paying_agent"),
                    ("net_asset_value_computation_method_path", "order_routing_custodian_adapter", "risk_scale"),
                )
            },
        ),
    )

    inlines = [InstrumentPortfolioThroughModelAdmin]


@admin.register(ProductGroupRepresentant)
class ProductGroupRepresentantModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ["representant"]
