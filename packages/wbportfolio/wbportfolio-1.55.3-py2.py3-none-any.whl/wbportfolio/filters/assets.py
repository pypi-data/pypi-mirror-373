from contextlib import suppress
from datetime import date, timedelta

from django.db.models import Exists, IntegerField, Max, OuterRef, Q, QuerySet, Sum
from django.db.models.functions import Cast
from pandas.tseries.offsets import BDay, BQuarterEnd
from wbcore import filters as wb_filters
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.geography.models import Geography
from wbcore.pandas.filterset import PandasFilterSetMixin
from wbcore.utils.date import current_financial_month
from wbfdm.models import Classification, ClassificationGroup, Instrument, InstrumentType
from wbfdm.preferences import get_default_classification_group

from wbportfolio.models import AssetPosition, AssetPositionGroupBy, Portfolio, Product


class FilterByPositionMixin:
    def _get_products(self):
        return Product.objects.all()

    def _filter_by_positions(
        self,
        qs: QuerySet,
        underlying_instrument__key: str,
        current_positions: bool = False,
    ) -> QuerySet:
        asset_positions = AssetPosition.objects
        if current_positions:
            last_date = asset_positions.latest("date").date
            asset_positions = asset_positions.filter(date=last_date).exclude(weighting=0)
        products = self._get_products()
        return qs.filter(
            Exists(
                asset_positions.filter(
                    underlying_instrument_id=OuterRef(underlying_instrument__key),
                    portfolio__instruments__in=products,
                ).distinct()
            )
        )


def get_asset_filter_param(request, view):
    filter_params = {"is_investable": True}
    if portfolio_id := view.kwargs.get("portfolio_id", None):
        filter_params["portfolio"] = portfolio_id
    if date := request.GET.get("date", None):
        filter_params["date"] = date
    return filter_params


def get_latest_asset_position(field, request, view):
    qs = AssetPosition.objects
    with suppress(Instrument.DoesNotExist):
        instrument = Instrument.objects.get(
            id=view.kwargs.get("instrument_id", request.GET.get("underlying_instrument", None))
        )
        qs = qs.filter(underlying_instrument__in=instrument.get_descendants(include_self=True))
    if "portfolio_id" in view.kwargs:
        qs = qs.filter(portfolio__id=view.kwargs["portfolio_id"])
    if "portfolio" in request.GET:
        qs = qs.filter(portfolio__id=request.GET["portfolio"])
    if qs.exists():
        return qs.latest("date").date
    return date.today()


def get_latest_end_quarter_date_asset_position(field, request, view):
    val_date = get_latest_asset_position(field, request, view)
    if val_date:
        return (val_date - BQuarterEnd()).date()
    return None


def get_last_weekday(field, request, view):
    t = date.today() - timedelta(days=1)
    while t.weekday() > 4:
        t = t - timedelta(days=1)
    return t


def get_related_products(field, request, view):
    if "equity_id" in view.kwargs:
        return Product.objects.filter(equity_positions__equity__id=view.kwargs["equity_id"])
    return Product.objects.all()


def get_default_product_id(field, request, view):
    return get_related_products(field, request, view).first().id


def get_portfolio_filter_params(request, view):
    if underlying_instrument := request.GET.get("underlying_instrument", None):
        return {"instrument": underlying_instrument}
    return {}


def get_portfolio_default(field, request, view):
    portfolio = Portfolio.objects.get(id=view.kwargs.get("portfolio_id"))
    if portfolio.assets.exists():
        return portfolio.id
    return Portfolio.objects.first().id


def latest_portfolio_date_based_on_instrument(field, request, view):
    portfolio = Portfolio.objects.filter(id=get_portfolio_default(field, request, view))
    if portfolio.exists() and portfolio.first().assets.exists():
        return portfolio.first().assets.latest("date").date
    return date.today()


class DateFilterMixin:
    def start_filter(self, queryset, name, value):
        if value:
            if value.weekday() in [5, 6]:
                value = value - BDay(1)
            return queryset.filter(date__gte=value)
        return queryset

    def end_filter(self, queryset, name, value):
        return queryset.filter(date__lte=value)


class AssetPositionFilter(wb_filters.FilterSet):
    date = wb_filters.DateFilter(
        label="Date", lookup_expr="exact", field_name="date", initial=get_latest_asset_position, required=True
    )

    underlying_instrument__is_cash = wb_filters.BooleanFilter(
        label="With Cash", exclude=True, lookup_expr="exact", field_name="underlying_instrument__is_cash"
    )
    underlying_instrument__instrument_type = wb_filters.ModelChoiceFilter(
        label="Instrument Type",
        endpoint=InstrumentType.get_representation_endpoint(),
        value_key=InstrumentType.get_representation_value_key(),
        label_key=InstrumentType.get_representation_label_key(),
        queryset=InstrumentType.objects.all(),
        lookup_expr="exact",
        field_name="underlying_instrument__instrument_type",
    )

    classification = wb_filters.ModelChoiceFilter(
        label="Industry Classification",
        queryset=Classification.objects.all(),
        endpoint=Classification.get_representation_endpoint(),
        value_key=Classification.get_representation_value_key(),
        label_key=Classification.get_representation_label_key(),
        method="filter_classification",
        filter_params=get_asset_filter_param,
    )

    underlying_instrument__country = wb_filters.ModelChoiceFilter(
        label="Country",
        queryset=Geography.countries.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
        lookup_expr="exact",
        field_name="underlying_instrument__country",
    )

    portfolio_instrument = wb_filters.ModelChoiceFilter(
        label="Portfolio Instrument",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params={"is_managed": True},
        method="filter_portfolio_instrument",
    )

    underlying_instrument = wb_filters.ModelChoiceFilter(
        label="Underlying Instrument",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params=get_asset_filter_param,
    )
    hide_empty_position = wb_filters.BooleanFilter(
        initial=False, method="boolean_hide_empty_position", label="Hide Empty Position"
    )

    total_value_fx_usd = wb_filters.NumberFilter(label="Total Value ($)")
    total_value_fx_usd__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="total_value_fx_usd", label="Total Value ($)"
    )
    total_value_fx_usd__lte = wb_filters.NumberFilter(
        lookup_expr="lte",
        label="Total Value ($)",
        field_name="total_value_fx_usd",
    )

    price = wb_filters.NumberFilter(label="Price")
    price__gte = wb_filters.NumberFilter(lookup_expr="gte", field_name="price", label="Price")
    price__lte = wb_filters.NumberFilter(
        lookup_expr="lte",
        label="Price",
        field_name="price",
    )

    total_value_fx_portfolio = wb_filters.NumberFilter(label="Total Value (Portfolio)")
    total_value_fx_portfolio__gte = wb_filters.NumberFilter(
        lookup_expr="gte", field_name="total_value_fx_portfolio", label="Total Value (Portfolio)"
    )
    total_value_fx_portfolio__lte = wb_filters.NumberFilter(
        lookup_expr="lte",
        label="Total Value (Portfolio)",
        field_name="total_value_fx_portfolio",
    )

    currency_fx_rate = wb_filters.NumberFilter(label="FX Rates")
    currency_fx_rate__gte = wb_filters.NumberFilter(lookup_expr="gte", field_name="currency_fx_rate", label="FX Rates")
    currency_fx_rate__lte = wb_filters.NumberFilter(
        lookup_expr="lte",
        label="FX Rates",
        field_name="currency_fx_rate",
    )

    shares = wb_filters.NumberFilter(label="Shares")
    shares__gte = wb_filters.NumberFilter(lookup_expr="gte", field_name="shares", label="Shares")
    shares__lte = wb_filters.NumberFilter(
        lookup_expr="lte",
        label="Shares",
        field_name="shares",
    )

    def filter_classification(self, queryset, name, value):
        if value:
            return queryset.filter(underlying_instrument__in=value.get_classified_instruments())
        return queryset

    def filter_portfolio_instrument(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(portfolio__product=value) | Q(portfolio__product_group=value) | Q(portfolio__index=value)
            ).distinct()
        return queryset

    def boolean_hide_empty_position(self, queryset, name, value):
        if value:
            return queryset.exclude(
                (Q(shares__isnull=False) & Q(shares=0)) | Q(weighting=0) & Q(weighting__isnull=False)
            )
        return queryset

    class Meta:
        model = AssetPosition
        fields = {
            "is_estimated": ["exact"],
            # "exchange": ["exact"],
            "weighting": ["gte", "exact", "lte"],
            "portfolio": ["exact"],
            "portfolio_created": ["exact"],
            "currency": ["exact"],
            "underlying_instrument": ["exact"],
            "underlying_instrument__isin": ["exact"],
            "underlying_instrument__ticker": ["exact"],
        }


class AssetPositionPortfolioFilter(AssetPositionFilter):
    portfolio_instrument = portfolio = None
    aggregate = wb_filters.BooleanFilter(initial=False, required=True, label="Aggregate", method="filter_aggregate")

    def filter_aggregate(self, queryset, name, value):
        if value:
            annotate_map = {
                "id": Max("id"),
                "is_estimated": Max(Cast("is_estimated", output_field=IntegerField())),
                "asset_valuation_date": Max("asset_valuation_date"),
                "price": Max("price"),
                "shares": Sum("shares"),
                "total_value": Sum("total_value"),
                "currency_fx_rate": Max("currency_fx_rate"),
                "total_value_fx_portfolio": Sum("total_value_fx_portfolio"),
                "total_value_fx_usd": Sum("total_value_fx_usd"),
                "weighting": Sum("weighting"),
                "market_share": Max("market_share"),
                "liquidity": Max("liquidity"),
                "currency_symbol": Max("currency__symbol"),
                "underlying_quote_name": Max("underlying_quote__name"),
                "underlying_quote_ticker": Max("underlying_quote__ticker"),
                "underlying_quote_isin": Max("underlying_quote__isin"),
                "portfolio_currency_symbol": Max("portfolio__currency__symbol"),
            }
            for key in self.view._metric_serializer_fields.keys():
                annotate_map[key] = Max(key)

            return queryset.values(
                "underlying_instrument__name",
                "underlying_instrument__isin",
                "underlying_instrument__ticker",
            ).annotate(**annotate_map)
        return queryset

    class Meta:
        model = AssetPosition
        fields = {
            "is_estimated": ["exact"],
            "exchange": ["exact"],
            "weighting": ["gte", "exact", "lte"],
            "portfolio_created": ["exact"],
            "currency": ["exact"],
            "underlying_instrument": ["exact"],
        }


class AssetPositionInstrumentFilter(AssetPositionFilter):
    hide_empty_position = hide_aggregated_position = instrument_type = portfolio_instrument = is_cash = (
        classification
    ) = country = None
    date = wb_filters.DateFilter(
        label="Date",
        lookup_expr="exact",
        field_name="date",
        initial=get_latest_asset_position,
        method="filter_date",
        required=True,
    )
    filter_last_positions = wb_filters.BooleanFilter(label="Fetch last position", method="fake_filter")

    hide_aggregated_position = wb_filters.BooleanFilter(
        initial=False, method="boolean_hide_aggregated_position", label="Hide Position from Aggregated Product"
    )

    def boolean_hide_aggregated_position(self, queryset, name, value):
        if value:
            return queryset.exclude(is_invested=False)
        return queryset

    def filter_date(self, queryset, name, value):
        if value and self.request.GET.get("filter_last_positions", "false") == "false":
            return queryset.filter(date=value)
        return queryset

    class Meta:
        model = AssetPosition
        fields = {
            "exchange": ["exact"],
            "weighting": ["gte", "exact", "lte"],
            "portfolio": ["exact"],
            "portfolio_created": ["exact"],
        }


class AssetPositionProductGroupFilter(AssetPositionInstrumentFilter):
    pass


class AssetPositionIndexGroupFilter(AssetPositionInstrumentFilter):
    pass


class AssetPositionEquityGroupFilter(AssetPositionInstrumentFilter):
    pass


class CashPositionPortfolioFilterSet(wb_filters.FilterSet):
    underlying_instrument__instrument_type = wb_filters.ModelChoiceFilter(
        label="Instrument Type",
        endpoint=InstrumentType.get_representation_endpoint(),
        value_key=InstrumentType.get_representation_value_key(),
        label_key=InstrumentType.get_representation_label_key(),
        queryset=InstrumentType.objects.all(),
        lookup_expr="exact",
        field_name="underlying_instrument__instrument_type",
    )

    date = wb_filters.DateFilter(
        label="Date", lookup_expr="exact", field_name="date", initial=get_latest_asset_position, required=True
    )

    class Meta:
        model = AssetPosition
        fields = {
            "portfolio": ["exact"],
            "currency": ["exact"],
        }
        df_fields = {
            "total_value_fx_usd__gte": wb_filters.NumberFilter(
                lookup_expr="gte", field_name="total_value_fx_usd", label="Total Value ($)"
            ),
            "total_value_fx_usd__lte": wb_filters.NumberFilter(
                lookup_expr="lte",
                label="Total Value ($)",
                field_name="total_value_fx_usd",
            ),
        }


class DistributionFilter(wb_filters.FilterSet):
    date = wb_filters.DateFilter(
        label="Date",
        lookup_expr="exact",
        field_name="date",
        initial=latest_portfolio_date_based_on_instrument,
        required=True,
    )

    group_by = wb_filters.ChoiceFilter(
        label="Group By",
        choices=AssetPositionGroupBy.choices,
        initial=AssetPositionGroupBy.INDUSTRY.value,
        method="fake_filter",
        clearable=False,
        required=True,
    )

    portfolio = wb_filters.ModelChoiceFilter(
        label="Portfolio",
        queryset=Portfolio.objects.all(),
        endpoint=Portfolio.get_representation_endpoint(),
        value_key=Portfolio.get_representation_value_key(),
        label_key=Portfolio.get_representation_label_key(),
        filter_params=get_portfolio_filter_params,
        initial=get_portfolio_default,
        required=True,
        clearable=False,
    )

    group_by_classification_group = wb_filters.ModelChoiceFilter(
        initial=lambda k, v, f: get_default_classification_group().id,
        method=lambda queryset, label, value: queryset,
        label="Group by Classification Group",
        queryset=ClassificationGroup.objects.all(),
        endpoint=ClassificationGroup.get_representation_endpoint(),
        value_key=ClassificationGroup.get_representation_value_key(),
        label_key=ClassificationGroup.get_representation_label_key(),
        depends_on=[{"field": "group_by", "options": {"activates_on": [AssetPositionGroupBy.INDUSTRY.value]}}],
    )

    group_by_classification_height = wb_filters.NumberFilter(
        method="fake_filter",
        label="Classification Height",
        initial=0,
        depends_on=[{"field": "group_by", "options": {"activates_on": [AssetPositionGroupBy.INDUSTRY.value]}}],
    )

    class Meta:
        model = AssetPosition
        fields = {}


def get_default_hedged_currency(field, request, view):
    with suppress(AttributeError, Portfolio.DoesNotExist, KeyError):
        return Portfolio.objects.get(id=view.kwargs["portfolio_id"]).hedged_currency.id


class ContributionChartFilter(wb_filters.FilterSet):
    date = wb_filters.FinancialPerformanceDateRangeFilter(
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
        label="Date Range",
        required=True,
        clearable=False,
        initial=current_financial_month,
    )
    hedged_currency = wb_filters.ModelChoiceFilter(
        label="Hedged Currency",
        queryset=Currency.objects.all(),
        endpoint=Currency.get_representation_endpoint(),
        value_key=Currency.get_representation_value_key(),
        label_key=Currency.get_representation_label_key(),
        method=lambda queryset, label, value: queryset,
        initial=get_default_hedged_currency,
    )

    class Meta:
        model = AssetPosition
        fields = {}


class CompositionContributionChartFilter(ContributionChartFilter):
    show_lookthrough = wb_filters.BooleanFilter(
        label="Show Lookthrough", initial=False, required=True, method="fake_filter"
    )


class AssetPositionUnderlyingInstrumentChartFilter(DateFilterMixin, wb_filters.FilterSet):
    portfolio = wb_filters.ModelMultipleChoiceFilter(
        label="Portfolios",
        queryset=Portfolio.objects.all(),
        endpoint=Portfolio.get_representation_endpoint(),
        value_key=Portfolio.get_representation_value_key(),
        label_key=Portfolio.get_representation_label_key(),
    )

    class Meta:
        model = AssetPosition
        fields = {"underlying_instrument": ["exact"]}


class CompositionModelPortfolioPandasFilter(PandasFilterSetMixin, wb_filters.FilterSet):
    date = wb_filters.DateFilter(label="Date", lookup_expr="exact", initial=get_latest_asset_position, required=True)

    class Meta:
        model = AssetPosition
        fields = {}
