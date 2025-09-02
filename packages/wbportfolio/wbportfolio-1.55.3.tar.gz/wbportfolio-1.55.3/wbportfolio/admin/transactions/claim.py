from django.contrib import admin

from wbportfolio.models.transactions.claim import Claim


class ClaimTabularInline(admin.TabularInline):
    extra = 0
    model = Claim
    list_display = ["reference_id", "product", "shares", "nominal_value", "claimant"]
    autocomplete_fields = ["account", "product", "claimant"]


@admin.register(Claim)
class ClaimModelAdmin(admin.ModelAdmin):
    list_display = ["date", "reference_id", "product", "account", "shares", "nominal_value"]
    autocomplete_fields = ["account", "product", "claimant"]
    raw_id_fields = ["trade", "account", "product", "claimant", "creator"]
