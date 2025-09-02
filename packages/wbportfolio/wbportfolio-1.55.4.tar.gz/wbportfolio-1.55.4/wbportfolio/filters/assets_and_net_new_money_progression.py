from wbcore import filters
from wbcore.utils.date import financial_year_to_date
from wbcrm.models.accounts import Account

from wbportfolio.models.products import Product
from wbportfolio.models.transactions.claim import Claim


class AssetsAndNetNewMoneyProgressionFilterSet(filters.FilterSet):
    period = filters.DateRangeFilter(
        label="Period",
        method=lambda queryset, label, value: queryset,
        required=True,
        clearable=False,
        initial=financial_year_to_date,
    )

    product = filters.ModelChoiceFilter(
        label="Product",
        endpoint=Product.get_representation_endpoint(),
        value_key=Product.get_representation_value_key(),
        label_key=Product.get_representation_label_key(),
        queryset=Product.objects.all(),
        lookup_expr="exact",
        field_name="product",
        method=lambda queryset, label, value: queryset,
    )

    account = filters.ModelChoiceFilter(
        label="Account",
        endpoint=Account.get_representation_endpoint(),
        value_key=Account.get_representation_value_key(),
        label_key=Account.get_representation_label_key(),
        queryset=Account.objects.all(),
        lookup_expr="exact",
        field_name="account",
        filter_params={"level": 0},
        method=lambda queryset, label, value: queryset,
    )

    class Meta:
        model = Claim
        fields = {}
