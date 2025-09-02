from django.db.models import Q
from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import Company, Entry
from wbfdm.filters.instruments import InstrumentFilterSet
from wbfdm.filters.utils import last_period_date_range
from wbfdm.models import Classification

from wbportfolio.models import Product, ProductGroup


class BaseProductFilterSet(InstrumentFilterSet):
    classifications = wb_filters.ModelChoiceFilter(
        label="Classification",
        queryset=Classification.objects.all(),
        endpoint=Classification.get_representation_endpoint(),
        value_key=Classification.get_representation_value_key(),
        label_key=Classification.get_representation_label_key(),
        filter_params={"instrument_type_key": "product"},
        method="filter_classification",
    )

    bank = wb_filters.ModelMultipleChoiceFilter(
        label="Bank",
        queryset=Company.objects.all(),
        endpoint=Company.get_representation_endpoint(),
        filter_params={"notnull_related_name": "issues_products"},
        value_key=Company.get_representation_value_key(),
        label_key=Company.get_representation_label_key(),
    )
    white_label_customers = wb_filters.ModelMultipleChoiceFilter(
        label="White Label Customers",
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
    )
    parent = wb_filters.ModelChoiceFilter(
        label="Group",
        queryset=ProductGroup.objects.all(),
        endpoint=ProductGroup.get_representation_endpoint(),
        value_key=ProductGroup.get_representation_value_key(),
        label_key=ProductGroup.get_representation_label_key(),
    )
    is_invested = wb_filters.BooleanFilter(label="Invested")
    is_active = wb_filters.BooleanFilter(label="Only Active", method="filter_is_active", initial=True)

    class Meta:
        model = Product
        fields = {"currency": ["exact"]}


class ProductFilter(BaseProductFilterSet):
    is_white_label = wb_filters.BooleanFilter(label="Is White Label", method="filter_is_white_label")

    net_value = wb_filters.NumberFilter(label="Last NAV")
    net_value__gte = wb_filters.NumberFilter(field_name="net_value", label="Last NAV", lookup_expr="gte")
    net_value__lte = wb_filters.NumberFilter(field_name="net_value", label="Last NAV", lookup_expr="lte")

    assets_under_management__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="assets_under_management", label="Asset under management"
    )
    assets_under_management__lte = wb_filters.NumberFilter(
        lookup_expr="lte", field_name="assets_under_management", label="Asset under management"
    )

    assets_under_management_usd__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="assets_under_management_usd", label="Asset under management ($)"
    )
    assets_under_management_usd__lte = wb_filters.NumberFilter(
        lookup_expr="lte", field_name="assets_under_management_usd", label="Asset under management ($)"
    )

    last_valuation_date = wb_filters.DateFilter(
        field_name="last_valuation_date", lookup_expr="exact", label="Last Valuation Date"
    )

    def filter_is_white_label(self, queryset, name, value):
        if value:
            return queryset.filter(is_white_label=True)
        return queryset

    class Meta(BaseProductFilterSet.Meta):
        fields = {
            "isin": ["exact", "icontains"],
            "ticker": ["exact", "icontains"],
            "currency": ["exact"],
        }


class ProductCustomerFilter(wb_filters.FilterSet):
    net_value = wb_filters.NumberFilter(label="Net Value")
    net_value__gte = wb_filters.NumberFilter(field_name="net_value", label="Last NAV", lookup_expr="gte")
    net_value__lte = wb_filters.NumberFilter(field_name="net_value", label="Last NAV", lookup_expr="lte")

    class Meta:
        model = Product
        fields = {}


class ProductFeeFilter(BaseProductFilterSet):
    sum_management_fees = wb_filters.NumberFilter(label="Sum Management Fees")
    sum_management_fees__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="sum_management_fees", label="Sum Management Fees"
    )
    sum_management_fees__lte = wb_filters.NumberFilter(
        lookup_expr="lte", field_name="sum_management_fees", label="Sum Management Fees"
    )

    sum_management_fees_usd__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="sum_management_fees_usd", label="Sum Management Fees (USD)"
    )
    sum_performance_fees_net__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="sum_performance_fees_net", label="Sum Performance Fees"
    )
    sum_performance_fees_net_usd__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="sum_performance_fees_net_usd", label="Sum Performance Fees (USD)"
    )
    sum_total_usd__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="sum_total_usd", label="Total Fees (USD)"
    )

    sum_management_fees_usd__lte = wb_filters.NumberFilter(
        lookup_expr="lte", field_name="sum_management_fees_usd", label="Sum Management Fees (USD)"
    )
    sum_performance_fees_net__lte = wb_filters.NumberFilter(
        lookup_expr="lte", field_name="sum_performance_fees_net", label="Sum Performance Fees"
    )
    sum_performance_fees_net_usd__lte = wb_filters.NumberFilter(
        lookup_expr="lte", field_name="sum_performance_fees_net_usd", label="Sum Performance Fees (USD)"
    )
    sum_total_usd__lte = wb_filters.NumberFilter(
        lookup_expr="lte", field_name="sum_total_usd", label="Total Fees (USD)"
    )

    assets_under_management__gte = assets_under_management__lte = assets_under_management_usd__gte = (
        assets_under_management_usd__lte
    ) = date = net_value = net_value__lte = net_value__gte = assets_under_management_usd = name = ticker = None

    date = wb_filters.DateRangeFilter(
        label="Date Range",
        method=lambda queryset, label, value: queryset,
        required=True,
        clearable=False,
        initial=last_period_date_range(),
    )

    def filter_active_products(self, queryset, name, value):
        if value:
            return queryset.filter(~(Q(sum_management_fees=0.0) & Q(sum_performance_fees_net=0.0)))
        return queryset

    class Meta:
        model = Product
        fields = {"currency": ["exact"]}
