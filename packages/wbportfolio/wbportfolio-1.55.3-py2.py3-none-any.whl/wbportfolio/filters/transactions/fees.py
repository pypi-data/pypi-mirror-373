from wbcore import filters as wb_filters
from wbcore.filters.defaults import current_quarter_date_range
from wbcore.pandas.filterset import PandasFilterSetMixin

from wbportfolio.models import Fees

from .utils import get_transaction_default_date_range


class FeesFilter(wb_filters.FilterSet):
    """FilterSet for Fees

    Currently filters:
    - date: daterange

    """

    fee_date = wb_filters.DateRangeFilter(
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
        label="Date Range",
        initial=get_transaction_default_date_range,
        required=True,
    )

    class Meta:
        model = Fees
        fields = {
            "transaction_subtype": ["exact"],
            "currency_fx_rate": ["gte", "exact", "lte"],
            "product": ["exact"],
            "currency": ["exact"],
            "total_value": ["gte", "exact", "lte"],
            "total_value_fx_portfolio": ["gte", "exact", "lte"],
        }


class FeesProductFilterSet(FeesFilter):
    portfolio = None

    class Meta:
        model = Fees
        fields = {
            "calculated": ["exact"],
            "transaction_subtype": ["exact"],
            "currency_fx_rate": ["gte", "exact", "lte"],
            "currency": ["exact"],
            "total_value": ["gte", "exact", "lte"],
            "total_value_fx_portfolio": ["gte", "exact", "lte"],
        }


class FeesAggregatedFilter(PandasFilterSetMixin, wb_filters.FilterSet):
    fee_date = wb_filters.DateRangeFilter(
        label="Date Range",
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
        required=True,
        clearable=False,
        initial=current_quarter_date_range,
    )

    class Meta:
        model = Fees
        fields = {}
