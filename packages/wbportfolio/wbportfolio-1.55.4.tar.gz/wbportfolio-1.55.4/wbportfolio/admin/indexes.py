from django.contrib import admin
from wbfdm.admin import InstrumentModelAdmin

from wbportfolio.models import Index


@admin.register(Index)
class IndexAdmin(InstrumentModelAdmin):
    fieldsets = (
        ("Instrument Information", InstrumentModelAdmin.fieldsets[0][1]),
        (
            "Index Information",
            {"fields": (("net_asset_value_computation_method_path", "order_routing_custodian_adapter"),)},
        ),
    )
