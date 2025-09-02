from django.contrib import admin

from wbportfolio.models import Fees
from wbportfolio.models.transactions.fees import FeeCalculation


@admin.register(Fees)
class FeesAdmin(admin.ModelAdmin):
    list_filter = ["product"]
    list_display = [
        "transaction_subtype",
        "fee_date",
        "product",
        "currency",
        "total_value",
    ]
    fieldsets = (
        (
            "Fees Information",
            {
                "fields": (
                    ("transaction_subtype", "calculated", "fee_date", "product"),
                    ("currency", "currency_fx_rate"),
                    ("total_value", "total_value_fx_portfolio"),
                    ("created", "updated"),
                )
            },
        ),
    )
    autocomplete_fields = ["currency", "product"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product", "currency")

    def calculate(self, request, queryset):
        for fees in queryset:
            fees.calculate_as_task.delay(fees)

    calculate.short_description = "Recalculate selected Fees"
    actions = [calculate]
    readonly_fields = ["total_value_fx_portfolio", "created", "updated"]


@admin.register(FeeCalculation)
class FeeCalculationModelAdmin(admin.ModelAdmin):
    search_fields = ("name",)
