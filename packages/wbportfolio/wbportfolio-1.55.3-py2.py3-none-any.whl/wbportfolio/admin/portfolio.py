from django.contrib import admin

from wbportfolio.models import (
    DailyPortfolioCashFlow,
    InstrumentPortfolioThroughModel,
    Portfolio,
    PortfolioBankAccountThroughModel,
    PortfolioCashTarget,
    PortfolioPortfolioThroughModel,
    PortfolioSwingPricing,
)

from .portfolio_relationships import (
    PortfolioInstrumentPreferredClassificationThroughInlineModelAdmin,
)


@admin.register(PortfolioBankAccountThroughModel)
class PortfolioBankAccountThroughModelModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ["bank_account", "portfolio"]
    list_display = ["bank_account", "portfolio", "portfolio_bank_account_type"]


class InstrumentPortfolioThroughModelAdmin(admin.TabularInline):
    model = InstrumentPortfolioThroughModel
    fk_name = "portfolio"
    raw_id_fields = ["portfolio", "instrument"]


class PortfolioPortfolioThroughModelInlineAdmin(admin.TabularInline):
    model = PortfolioPortfolioThroughModel
    fk_name = "portfolio"
    fields = ["dependency_portfolio", "type"]
    autocomplete_fields = ["portfolio", "dependency_portfolio"]


@admin.register(PortfolioPortfolioThroughModel)
class PortfolioPortfolioThroughModelModelAdmin(admin.ModelAdmin):
    list_display = ["portfolio", "dependency_portfolio", "type"]


class PortfolioBankAccountThroughModelAdmin(admin.TabularInline):
    model = PortfolioBankAccountThroughModel
    fields = ["bank_account", "portfolio_bank_account_type"]


@admin.register(Portfolio)
class PortfolioModelAdmin(admin.ModelAdmin):
    search_fields = ("name",)

    fieldsets = (
        (
            "Main Information",
            {
                "fields": (
                    ("name", "updated_at"),
                    ("currency", "hedged_currency"),
                    (
                        "invested_timespan",
                        "is_manageable",
                        "is_active",
                    ),
                    ("is_tracked", "only_weighting", "is_lookthrough"),
                )
            },
        ),
    )
    readonly_fields = ["updated_at"]
    list_display = (
        "is_active",
        "name",
        "currency",
        "hedged_currency",
        "is_manageable",
        "is_tracked",
        "is_lookthrough",
    )
    inlines = [
        PortfolioBankAccountThroughModelAdmin,
        InstrumentPortfolioThroughModelAdmin,
        PortfolioInstrumentPreferredClassificationThroughInlineModelAdmin,
        PortfolioPortfolioThroughModelInlineAdmin,
    ]
    raw_id_fields = [
        "depends_on",
        "preferred_instrument_classifications",
        "currency",
        "hedged_currency",
    ]
    autocomplete_fields = ["currency", "hedged_currency"]

    def get_queryset(self, request):
        return Portfolio.all_objects.all()

    def update_preferred_classification_per_instrument(self, request, queryset):
        for portfolio in queryset.all():
            portfolio.update_preferred_classification_per_instrument()

    actions = [update_preferred_classification_per_instrument]


@admin.register(DailyPortfolioCashFlow)
class DailyPortfolioCashFlowModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ["portfolio"]
    raw_id_fields = ["import_source"]
    list_display = [
        "portfolio",
        "value_date",
    ]
    readonly_fields = [
        "estimated_total_assets",
        "true_cash",
        "true_cash_pct",
        "cash_pct",
        "target_cash",
        "excess_cash",
        "min_target_cash_pct",
        "target_cash_pct",
        "max_target_cash_pct",
        "proposed_rebalancing",
        "rebalancing",
    ]


@admin.register(PortfolioCashTarget)
class PortfolioCashTargetModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ["portfolio"]


@admin.register(PortfolioSwingPricing)
class PortfolioSwingPricingModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ["portfolio"]
