from django.contrib import admin

from wbportfolio.models.orders import Order


class OrderTabularInline(admin.TabularInline):
    model = Order
    fk_name = "order_proposal"

    readonly_fields = [
        "_effective_weight",
        "_target_weight",
        "_effective_shares",
        "_target_shares",
        "total_value",
        "total_value_gross",
        "total_value_fx_portfolio",
        "total_value_gross_fx_portfolio",
        "created",
        "updated",
    ]

    fields = [
        "underlying_instrument",
        "_effective_weight",
        "_target_weight",
        "weighting",
        "shares",
        "daily_return",
    ]
