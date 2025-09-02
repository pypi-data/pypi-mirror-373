from django.db.models import Exists, OuterRef
from wbcore import filters as wb_filters

from wbportfolio.models import InstrumentPortfolioThroughModel, OrderProposal


class OrderProposalFilterSet(wb_filters.FilterSet):
    has_custodian_adapter = wb_filters.BooleanFilter(
        method="filter_has_custodian_adapter", label="Has Custodian Adapter"
    )
    waiting_for_input = wb_filters.BooleanFilter(method="filter_waiting_for_input", label="Waiting for Input")
    is_automatic_rebalancing = wb_filters.BooleanFilter(
        method="filter_is_automatic_rebalancing", label="Automatic Rebalancing"
    )

    def filter_has_custodian_adapter(self, queryset, name, value):
        queryset = queryset.annotate(
            has_custodian_adapter=Exists(
                InstrumentPortfolioThroughModel.objects.filter(
                    portfolio=OuterRef("portfolio"), instrument__net_asset_value_computation_method_path__isnull=False
                )
            )
        )
        if value is True:
            queryset = queryset.filter(has_custodian_adapter=True)
        elif value is False:
            queryset = queryset.filter(has_custodian_adapter=False)
        return queryset

    def filter_waiting_for_input(self, queryset, name, value):
        if value is True:
            queryset = queryset.filter(
                status__in=[OrderProposal.Status.PENDING, OrderProposal.Status.DRAFT, OrderProposal.Status.APPROVED]
            )
        elif value is False:
            queryset = queryset.exclude(
                status__in=[OrderProposal.Status.PENDING, OrderProposal.Status.DRAFT, OrderProposal.Status.APPROVED]
            )
        return queryset

    def filter_is_automatic_rebalancing(self, queryset, name, value):
        if value is True:
            queryset = queryset.filter(rebalancing_model__isnull=False)
        elif value is False:
            queryset = queryset.filter(rebalancing_model__isnull=True)
        return queryset

    class Meta:
        model = OrderProposal
        fields = {
            "trade_date": ["exact"],
            "status": ["exact"],
            "rebalancing_model": ["exact"],
            "portfolio": ["exact"],
            "creator": ["exact"],
            "approver": ["exact"],
            "execution_status": ["exact"],
        }
