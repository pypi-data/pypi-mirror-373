from wbcore import filters as wb_filters

from wbportfolio.models import Order


class OrderFilterSet(wb_filters.FilterSet):
    has_warnings = wb_filters.BooleanFilter()

    class Meta:
        model = Order
        fields = {"underlying_instrument": ["exact"], "order_type": ["exact"]}
