from django.contrib import admin

from .models import (
    AssetAllocation,
    AssetAllocationType,
    CompanyPortfolioData,
    GeographicFocus,
)


@admin.register(CompanyPortfolioData)
class CompanyPortfolioDataModelAdmin(admin.ModelAdmin):
    pass


@admin.register(AssetAllocationType)
class AssetAllocationTypeModelAdmin(admin.ModelAdmin):
    pass


@admin.register(AssetAllocation)
class AssetAllocationModelAdmin(admin.ModelAdmin):
    pass


@admin.register(GeographicFocus)
class GeographicFocusModelAdmin(admin.ModelAdmin):
    pass
