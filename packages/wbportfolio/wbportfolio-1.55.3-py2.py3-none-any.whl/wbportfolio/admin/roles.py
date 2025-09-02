from django.contrib import admin

from wbportfolio.models import PortfolioRole


class PortfolioRoleInline(admin.TabularInline):
    model = PortfolioRole
    extra = 0

    autocomplete_fields = ["instrument", "person"]


@admin.register(PortfolioRole)
class PortfolioRoleAdmin(admin.ModelAdmin):
    list_display = ["role_type", "instrument", "person", "start", "end"]

    autocomplete_fields = [
        "instrument",
        "person",
    ]
