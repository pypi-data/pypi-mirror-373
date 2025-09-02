from django.db.models import Q, TextChoices
from django.utils.timezone import localdate
from wbcore import filters as wb_filters
from wbcore.pandas.filterset import PandasFilterSetMixin
from wbcore.utils.date import current_financial_month
from wbfdm.filters.utils import last_period_date_range
from wbfdm.models import Instrument

from wbportfolio.models import Product

from .products import BaseProductFilterSet


def current_date(*args, **kwargs):
    return localdate()


class PerformancePandasFilter(PandasFilterSetMixin, BaseProductFilterSet):
    class PerformanceBy(TextChoices):
        NNM = "NNM", "NNM"
        AUM = "AUM", "AUM"
        PRICE = "PRICE", "Price"

    is_forex_fix = wb_filters.BooleanFilter(label="Fix Forex rate", method="fake_filter", initial=False, required=True)

    date = wb_filters.FinancialPerformanceDateRangeFilter(
        label="Date Range",
        method=lambda queryset, label, value: queryset,
        required=True,
        clearable=False,
        initial=current_financial_month,
    )

    performance_by = wb_filters.ChoiceFilter(
        label="Performance By",
        choices=PerformanceBy.choices,
        initial=PerformanceBy.PRICE.name,
        method="fake_filter",
        clearable=False,
        required=True,
    )
    white_label_customers = classifications = classifications_neq = unclassified = invested = portfolio = (
        content_type
    ) = tags = None

    class Meta:
        model = Product
        fields = {}
        df_fields = {
            "diff__gte": wb_filters.NumberFilter(
                precision=2, label="Difference", lookup_expr="gte", field_name="diff"
            ),
            "perf__gte": wb_filters.NumberFilter(
                precision=2, label="Performance", lookup_expr="gte", field_name="perf"
            ),
            "n1__gte": wb_filters.NumberFilter(precision=2, label="N1", lookup_expr="gte", field_name="n1"),
            "n2__gte": wb_filters.NumberFilter(precision=2, label="N2", lookup_expr="gte", field_name="n2"),
            "n1_usd__gte": wb_filters.NumberFilter(
                precision=2, label="N1 (USD)", lookup_expr="gte", field_name="n1_usd"
            ),
            "n2_usd__gte": wb_filters.NumberFilter(
                precision=2, label="N2 (USD)", lookup_expr="gte", field_name="n2_usd"
            ),
            "diff_usd__gte": wb_filters.NumberFilter(
                precision=2, label="Difference (USD)", lookup_expr="gte", field_name="diff_usd"
            ),
            "perf_usd__gte": wb_filters.NumberFilter(
                precision=2, label="Performance (USD)", lookup_expr="gte", field_name="perf_usd"
            ),
            "diff__lte": wb_filters.NumberFilter(
                precision=2, label="Difference", lookup_expr="lte", field_name="diff"
            ),
            "perf__lte": wb_filters.NumberFilter(
                precision=2, label="Performance", lookup_expr="lte", field_name="perf"
            ),
            "n1__lte": wb_filters.NumberFilter(precision=2, label="N1", lookup_expr="lte", field_name="n1"),
            "n2__lte": wb_filters.NumberFilter(precision=2, label="N2", lookup_expr="lte", field_name="n2"),
            "n1_usd__lte": wb_filters.NumberFilter(
                precision=2, label="N1 (USD)", lookup_expr="lte", field_name="n1_usd"
            ),
            "n2_usd__lte": wb_filters.NumberFilter(
                precision=2, label="N2 (USD)", lookup_expr="lte", field_name="n2_usd"
            ),
            "diff_usd__lte": wb_filters.NumberFilter(
                precision=2, label="Difference (USD)", lookup_expr="lte", field_name="diff_usd"
            ),
            "perf_usd__lte": wb_filters.NumberFilter(
                precision=2, label="Performance (USD)", lookup_expr="lte", field_name="perf_usd"
            ),
        }


class ProductPerformanceNetNewMoneyFilter(PandasFilterSetMixin, BaseProductFilterSet):
    is_active = wb_filters.BooleanFilter(label="Is Active", method="filter_active_products", initial=True)
    net_negative_money__gte = wb_filters.NumberFilter(
        label="Net Negative money", lookup_expr="gte", field_name="net_negative_money"
    )
    net_negative_money__lte = wb_filters.NumberFilter(
        label="Net Negative money", lookup_expr="lte", field_name="net_negative_money"
    )
    net_positive_money__gte = wb_filters.NumberFilter(
        label="Net Positive money", lookup_expr="gte", field_name="net_positive_money"
    )
    net_positive_money__lte = wb_filters.NumberFilter(
        label="Net Positive money", lookup_expr="lte", field_name="net_positive_money"
    )
    net_positive_money_usd__gte = wb_filters.NumberFilter(
        label="Net Positive money ($)", lookup_expr="gte", field_name="net_positive_money_usd"
    )
    net_positive_money_usd__lte = wb_filters.NumberFilter(
        label="Net Positive money ($)", lookup_expr="lte", field_name="net_positive_money_usd"
    )
    net_negative_money_usd__gte = wb_filters.NumberFilter(
        label="Net Negative money ($)", lookup_expr="gte", field_name="net_negative_money_usd"
    )
    net_negative_money_usd__lte = wb_filters.NumberFilter(
        label="Net Negative money ($)", lookup_expr="lte", field_name="net_negative_money_usd"
    )
    net_money__gte = wb_filters.NumberFilter(label="Net Money", lookup_expr="gte", field_name="net_money")
    net_money__lte = wb_filters.NumberFilter(label="Net Money", lookup_expr="lte", field_name="net_money")
    net_money_usd__gte = wb_filters.NumberFilter(label="Net Money ($)", lookup_expr="gte", field_name="net_money_usd")
    net_money_usd__lte = wb_filters.NumberFilter(label="Net Money ($)", lookup_expr="lte", field_name="net_money_usd")

    date = wb_filters.DateRangeFilter(
        label="Date Range",
        method=lambda queryset, label, value: queryset,
        required=True,
        clearable=False,
        initial=last_period_date_range,
    )

    def filter_active_products(self, queryset, name, value):
        if value is True:
            return queryset.filter(~Q(net_money=0.0))
        elif value is False:
            return queryset.filter(Q(net_money=0.0))

        return queryset

    white_label_customers = classifications = classifications_neq = unclassified = invested = portfolio = (
        content_type
    ) = tags = None

    class Meta:
        model = Product
        fields = {
            "computed_str": ["exact", "icontains"],
        }


class PerformanceComparisonFilter(PandasFilterSetMixin, BaseProductFilterSet):
    classifications = unclassified = invested = None
    dates = wb_filters.FinancialPerformanceDateRangeFilter(
        method=lambda q, n, v: q, label="Compute Performance between these dates"
    )

    comparison_instrument = wb_filters.ModelChoiceFilter(
        label="Compare with...",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params={"level": 0},
        method="fake_filter",
    )
    compare_primary_benchmark = wb_filters.BooleanFilter(
        initial=False, label="Compare against primary benchmark", method="fake_filter"
    )

    class Meta:
        model = Product
        fields = {}
