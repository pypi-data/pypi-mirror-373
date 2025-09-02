from datetime import date, timedelta

from wbcore import filters as wb_filters
from wbfdm.models import Instrument

from wbportfolio.filters.assets import get_latest_asset_position
from wbportfolio.models import Portfolio


class PortfolioFilterSet(wb_filters.FilterSet):
    is_tracked = wb_filters.BooleanFilter(initial=True, label="Is tracked")
    instrument = wb_filters.ModelChoiceFilter(
        label="Instrument",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params={"is_managed": True},
        method="filter_instrument",
    )
    modeled_after = wb_filters.ModelChoiceFilter(
        label="Modeled After",
        queryset=Portfolio.objects.all(),
        endpoint=Portfolio.get_representation_endpoint(),
        value_key=Portfolio.get_representation_value_key(),
        label_key=Portfolio.get_representation_label_key(),
        method="filter_modeled_after",
    )

    def filter_modeled_after(self, queryset, name, value):
        if value:
            modeled_after_portfolio_ids = list(
                map(
                    lambda p: p.portfolio.id, value.get_model_portfolio_relationships(date.today() - timedelta(days=7))
                )
            )
            return queryset.filter(id__in=modeled_after_portfolio_ids)
        return queryset

    def filter_instrument(self, queryset, name, value):
        if value:
            return queryset.filter(instruments=value)
        return queryset

    class Meta:
        model = Portfolio
        fields = {
            "currency": ["exact"],
            "hedged_currency": ["exact"],
            "is_manageable": ["exact"],
            "only_weighting": ["exact"],
            "is_lookthrough": ["exact"],
            "is_composition": ["exact"],
            "bank_accounts": ["exact"],
            "depends_on": ["exact"],
        }


class PortfolioTreeGraphChartFilterSet(wb_filters.FilterSet):
    date = wb_filters.DateFilter(method="fake_filter", initial=get_latest_asset_position, required=True)

    class Meta:
        model = Portfolio
        fields = {}
