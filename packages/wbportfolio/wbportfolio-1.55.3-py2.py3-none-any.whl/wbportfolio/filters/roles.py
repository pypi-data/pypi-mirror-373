from django.db.models import Q
from django.utils import timezone
from wbcore import filters as wb_filters

from wbportfolio.models import PortfolioRole


class PortfolioRoleFilterSet(wb_filters.FilterSet):
    is_active = wb_filters.BooleanFilter(method="filter_is_active", initial=True, label="Is Active")

    def filter_is_active(self, queryset, name, value):
        if value is True:
            return queryset.filter(Q(end__isnull=True) | Q(end__gte=timezone.now())).distinct()
        elif value is False:
            return queryset.filter(end__lte=timezone.now())
        return queryset

    class Meta:
        model = PortfolioRole
        fields = {
            "role_type": ["exact"],
            "person": ["exact"],
            "start": ["gte", "exact", "lte"],
            "end": ["gte", "exact", "lte"],
            "weighting": ["gte", "exact", "lte"],
            "instrument": ["exact"],
        }
