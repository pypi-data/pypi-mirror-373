from datetime import timedelta

from django.db.models import Count, OuterRef, Subquery
from wbcore import filters as wb_filters
from wbcrm.models.accounts import Account
from wbfdm.models import Classification, Instrument

from wbportfolio.models import Portfolio, Product, Trade
from wbportfolio.models.transactions.claim import Claim

from .mixins import OppositeSharesFieldMethodMixin
from .utils import get_transaction_default_date_range


class TradeFilter(OppositeSharesFieldMethodMixin, wb_filters.FilterSet):
    transaction_date = wb_filters.DateRangeFilter(
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
        label="Date Range",
        initial=get_transaction_default_date_range,
    )

    portfolio = wb_filters.ModelChoiceFilter(
        label="Portfolio",
        queryset=Portfolio.objects.all(),
        endpoint=Portfolio.get_representation_endpoint(),
        value_key=Portfolio.get_representation_value_key(),
        label_key=Portfolio.get_representation_label_key(),
    )

    # we have to redefine the mixin fields because django_filters does not allow class extension with mixin
    opposite_shares = wb_filters.NumberFilter(
        field_name="shares",
        label="Opposite Shares",
        method="filter_opposite_shares",
        lookup_icon="±",
        lookup_label="Opposite",
    )
    opposite_approximate_shares = wb_filters.NumberFilter(
        field_name="shares",
        label="Opposite Approximite Shares",
        method="filter_opposite_approximate_shares",
        lookup_icon="≈±",
        lookup_label="Opposite Approximate (+- 10%)",
    )
    underlying_instrument = wb_filters.ModelChoiceFilter(
        label="Instrument",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params={"is_investable": True},
    )
    only_internal_trade = wb_filters.BooleanFilter(label="Only Internal Trade", method="boolean_only_internal_trade")

    completely_claimed = wb_filters.BooleanFilter(label="Completely Claimed", method="boolean_completely_claimed")
    completely_claimed_if_approved = wb_filters.BooleanFilter(
        label="Completely Claimed if approved", method="boolean_completely_claimed_if_approved"
    )

    claimed_shares__gte = wb_filters.NumberFilter(
        label="Claimed Shares", lookup_expr="gte", field_name="claimed_shares"
    )
    claimed_shares__lte = wb_filters.NumberFilter(
        label="Claimed Shares", field_name="claimed_shares", lookup_expr="lte"
    )
    claims = wb_filters.ModelChoiceFilter(
        label="Customer Accounts",
        queryset=Account.objects.all(),
        endpoint=Account.get_representation_endpoint(),
        value_key=Account.get_representation_value_key(),
        label_key=Account.get_representation_label_key(),
        method="filter_customer",
    )
    is_customer_trade = wb_filters.BooleanFilter(label="Is Customer Trade?", method="boolean_is_customer_trade")
    # register = wb_filters.ModelChoiceFilter(
    #     label="Register",
    #     queryset=Register.objects.all(),
    #     endpoint=Register.get_representation_endpoint(),
    #     value_key=Register.get_representation_value_key(),
    #     label_key = Register.get_representation_label_key(),
    # )
    marked_for_deletion = wb_filters.BooleanFilter(
        label="Marked For Deletion", initial=False, field_name="marked_for_deletion", lookup_expr="exact"
    )
    pivot_date = wb_filters.DateFilter(hidden=True, method="filter_pivot_date")

    def filter_pivot_date(self, queryset, name, value):
        if value:
            return queryset.filter(
                transaction_date__gte=value - timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
                transaction_date__lte=value + timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
            )
        return queryset

    def filter_customer(self, queryset, name, value):
        if value:
            accounts = value.get_descendants(include_self=True)
            queryset = queryset.annotate(
                filtered_claims=Subquery(
                    Claim.objects.filter(trade=OuterRef("pk"), account__in=accounts)
                    .values("account")
                    .annotate(c=Count("account"))
                    .values("c")[:1]
                )
            )
            return queryset.filter(filtered_claims__gt=0)
        return queryset

    def boolean_is_customer_trade(self, queryset, name, value):
        if value is True:
            return queryset.filter(transaction_subtype__in=[Trade.Type.SUBSCRIPTION, Trade.Type.REDEMPTION])
        elif value is False:
            return queryset.exclude(transaction_subtype__in=[Trade.Type.SUBSCRIPTION, Trade.Type.REDEMPTION])
        else:
            return queryset

    def boolean_completely_claimed(self, queryset, name, value):
        if value is True:
            return queryset.filter(completely_claimed=True)
        elif value is False:
            return queryset.filter(completely_claimed=False)
        else:
            return queryset

    def boolean_completely_claimed_if_approved(self, queryset, name, value):
        if value is True:
            return queryset.filter(completely_claimed_if_approved=True)
        elif value is False:
            return queryset.filter(completely_claimed_if_approved=False)
        else:
            return queryset

    def boolean_only_internal_trade(self, queryset, name, value):
        if value:
            return queryset.exclude(transaction_subtype__in=[Trade.Type.SUBSCRIPTION, Trade.Type.REDEMPTION]).filter(
                underlying_instrument__instrument_type__key="product"
            )
        return queryset

    class Meta:
        model = Trade
        fields = {
            "shares": ["gte", "lte", "exact"],
            "bank": ["exact", "icontains"],
            "price": ["gte", "lte", "exact"],
            "currency": ["exact"],
            "currency_fx_rate": ["gte", "exact", "lte"],
            "total_value": ["gte", "exact", "lte"],
            "total_value_fx_portfolio": ["gte", "exact", "lte"],
            "comment": ["icontains"],
            "portfolio": ["exact"],
            "register": ["exact"],
            # 'total_value_gross_fx_portfolio': ["gte", "exact", "lte"],
            "transaction_subtype": ["exact"],
            "pending": ["exact"],
        }


class TradePortfolioFilter(TradeFilter):
    portfolio = None

    class Meta:
        model = Trade
        fields = {
            "shares": ["gte", "lte", "exact"],
            "bank": ["exact", "icontains"],
            "price": ["gte", "lte", "exact"],
            "currency": ["exact"],
            "currency_fx_rate": ["gte", "exact", "lte"],
            "total_value": ["gte", "exact", "lte"],
            "total_value_fx_portfolio": ["gte", "exact", "lte"],
            "comment": ["icontains"],
            "register": ["exact"],
            "transaction_subtype": ["exact"],
        }


class SubscriptionRedemptionFilterSet(TradeFilter):
    is_customer_trade = None
    underlying_instrument = wb_filters.ModelChoiceFilter(
        label="Product",
        queryset=Product.objects.all(),
        endpoint=Product.get_representation_endpoint(),
        value_key=Product.get_representation_value_key(),
        label_key=Product.get_representation_label_key(),
    )
    underlying_instrument__classifications = wb_filters.ModelMultipleChoiceFilter(
        label="Classifications",
        queryset=Classification.objects.all(),
        endpoint=Classification.get_representation_endpoint(),
        value_key=Classification.get_representation_value_key(),
        label_key=Classification.get_representation_label_key(),
        filter_params={"instrument_type_key": "product"},
    )

    class Meta:
        model = Trade
        fields = {
            "shares": ["gte", "lte", "exact"],
            "bank": ["exact", "icontains"],
            "price": ["gte", "lte", "exact"],
            "currency": ["exact"],
            "total_value": ["gte", "exact", "lte"],
            "comment": ["icontains"],
            "portfolio": ["exact"],
            "register": ["exact"],
            # 'total_value_gross_fx_portfolio': ["gte", "exact", "lte"],
            "transaction_subtype": ["exact"],
            "marked_for_deletion": ["exact"],
            "custodian": ["exact"],
            "pending": ["exact"],
        }


class TradeInstrumentFilterSet(TradeFilter):
    is_customer_trade = underlying_instrument = completely_claimed = completely_claimed_if_approved = (
        claimed_shares__gte
    ) = claimed_shares__lte = claims = total_value_usd__gte = None

    class Meta:
        model = Trade
        fields = {
            "shares": ["gte", "lte", "exact"],
            "bank": ["exact", "icontains"],
            "price": ["gte", "lte", "exact"],
            "currency_fx_rate": ["gte", "exact", "lte"],
            "total_value": ["gte", "exact", "lte"],
            "total_value_fx_portfolio": ["gte", "exact", "lte"],
            "total_value_gross": ["gte", "exact", "lte"],
            "total_value_gross_fx_portfolio": ["gte", "exact", "lte"],
            "comment": ["icontains"],
            "portfolio": ["exact"],
            "register": ["exact"],
            "transaction_subtype": ["exact"],
        }


class SubscriptionRedemptionPortfolioFilterSet(TradeFilter):
    is_customer_trade = None

    class Meta:
        model = Trade
        fields = {
            "shares": ["gte", "lte", "exact"],
            "bank": ["exact", "icontains"],
            "price": ["gte", "lte", "exact"],
            "currency": ["exact"],
            "total_value": ["gte", "exact", "lte"],
            "comment": ["icontains"],
            "register": ["exact"],
            # 'total_value_gross_fx_portfolio': ["gte", "exact", "lte"],
            "transaction_subtype": ["exact"],
            "custodian": ["exact"],
        }
