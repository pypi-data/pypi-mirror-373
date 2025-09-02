from django.contrib import admin

from wbportfolio.models import Rebalancer, RebalancingModel


@admin.register(RebalancingModel)
class RebalancingModelAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = (
        "name",
        "class_path",
    )


@admin.register(Rebalancer)
class RebalancerAdmin(admin.ModelAdmin):
    search_fields = ("rebalancing_model__name",)
    list_display = (
        "computed_str",
        "rebalancing_model",
        "portfolio",
        "parameters",
        "apply_order_proposal_automatically",
        "activation_date",
        "frequency",
    )
