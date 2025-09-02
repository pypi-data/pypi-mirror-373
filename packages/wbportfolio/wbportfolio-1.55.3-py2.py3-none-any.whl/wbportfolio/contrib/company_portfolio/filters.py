from wbcore import filters
from wbcore.contrib.directory.filters import CompanyFilter as CF
from wbcore.contrib.directory.filters import PersonFilter as PF
from wbcore.contrib.directory.models import Company, Person


class EntryPortfolioFilter(filters.FilterSet):
    asset_under_management_gte = filters.NumberFilter(
        label="AUM",
        help_text="Filter for the Assets under Management",
        field_name="asset_under_management",
        lookup_expr="gte",
        method="aum_filter_gte",
    )
    asset_under_management_lte = filters.NumberFilter(
        label="AUM",
        help_text="Filter for the Assets under Management",
        field_name="asset_under_management",
        lookup_expr="lte",
        method="aum_filter_lte",
    )

    def aum_filter_gte(self, queryset, name, value):
        if value:
            if self.view.get_model() is Person:
                return queryset.filter(employers__portfolio_data__asset_under_management__gte=value)
            elif self.view.get_model() is Company:
                return queryset.filter(portfolio_data__asset_under_management__gte=value)
        return queryset

    def aum_filter_lte(self, queryset, name, value):
        if value:
            if self.view.get_model() is Person:
                return queryset.filter(employers__portfolio_data__asset_under_management__lte=value)
            elif self.view.get_model() is Company:
                return queryset.filter(portfolio_data__asset_under_management__lte=value)
        return queryset

    invested_assets_under_management_usd_gte = filters.NumberFilter(
        label="Invested AUM",
        help_text="Filter for the invested Capital (AUM) with us",
        field_name="invested_assets_under_management_usd",
        lookup_expr="gte",
        method="filter_gte",
    )
    invested_assets_under_management_usd_lte = filters.NumberFilter(
        label="Invested AUM",
        help_text="Filter for the invested Capital (AUM) with us",
        field_name="invested_assets_under_management_usd",
        lookup_expr="lte",
        method="filter_lte",
    )

    def filter_gte(self, queryset, name, value):
        if value:
            if self.view.get_model() is Person:
                return queryset.filter(employers__portfolio_data__invested_assets_under_management_usd__gte=value)
            elif self.view.get_model() is Company:
                return queryset.filter(portfolio_data__invested_assets_under_management_usd__gte=value)
        return queryset

    def filter_lte(self, queryset, name, value):
        if value:
            if self.view.get_model() is Person:
                return queryset.filter(employers__portfolio_data__invested_assets_under_management_usd__lte=value)
            elif self.view.get_model() is Company:
                return queryset.filter(portfolio_data__invested_assets_under_management_usd__lte=value)
        return queryset

    potential_gte = filters.NumberFilter(
        label="Potential",
        help_text="Filter for the potential, e.g. how much potential is there to invest with us",
        field_name="potential",
        lookup_expr="gte",
        method="potential_filter_gte",
    )
    potential_lte = filters.NumberFilter(
        label="Potential",
        help_text="Filter for the potential, e.g. how much potential is there to invest with us",
        field_name="potential",
        lookup_expr="lte",
        method="potential_filter_lte",
    )

    def potential_filter_gte(self, queryset, name, value):
        if value:
            if self.view.get_model() is Person:
                return queryset.filter(employers__portfolio_data__potential__gte=value)
            elif self.view.get_model() is Company:
                return queryset.filter(portfolio_data__potential__gte=value)
        return queryset

    def potential_filter_lte(self, queryset, name, value):
        if value:
            if self.view.get_model() is Person:
                return queryset.filter(employers__portfolio_data__potential__lte=value)
            elif self.view.get_model() is Company:
                return queryset.filter(portfolio_data__potential__lte=value)
        return queryset


class CompanyFilter(CF, EntryPortfolioFilter):
    @classmethod
    def get_filter_class_for_remote_filter(cls):
        """
        Define which filterset class sender to user for remote filter registration
        """
        return CF

    class Meta(CF.Meta):
        fields = {
            **CF.Meta.fields,
        }


class PersonFilter(PF, EntryPortfolioFilter):
    @classmethod
    def get_filter_class_for_remote_filter(cls):
        """
        Define which filterset class sender to user for remote filter registration
        """
        return PF

    class Meta(PF.Meta):
        fields = {
            **PF.Meta.fields,
        }
