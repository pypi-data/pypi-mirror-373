from django.contrib import admin

from wbportfolio.models import OrderProposal

from .orders import OrderTabularInline


@admin.register(OrderProposal)
class OrderProposalAdmin(admin.ModelAdmin):
    search_fields = ["portfolio__name", "comment"]

    list_display = ("portfolio", "rebalancing_model", "trade_date", "status")
    autocomplete_fields = ["portfolio", "rebalancing_model"]
    inlines = [OrderTabularInline]
