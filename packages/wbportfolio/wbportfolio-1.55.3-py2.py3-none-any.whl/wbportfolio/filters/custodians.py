from wbcore import filters as wb_filters

from wbportfolio.models import Custodian


class CustodianFilterSet(wb_filters.FilterSet):
    mapping = wb_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Custodian
        fields = {"name": ["exact", "icontains"]}
