from django.db.models import Case, F, Value, When
from wbcore import viewsets

from wbportfolio.models import DailyPortfolioCashFlow
from wbportfolio.serializers import DailyPortfolioCashFlowModelSerializer
from wbportfolio.viewsets.configs.display import DailyPortfolioCashFlowDisplayConfig
from wbportfolio.viewsets.configs.titles import DailyPortfolioCashFlowTitleConfig


class DailyPortfolioCashFlowModelViewSet(viewsets.ModelViewSet):
    queryset = DailyPortfolioCashFlow.objects.all()
    serializer_class = DailyPortfolioCashFlowModelSerializer

    display_config_class = DailyPortfolioCashFlowDisplayConfig
    title_config_class = DailyPortfolioCashFlowTitleConfig

    ordering_fields = ("value_date",)
    ordering = ("-value_date",)

    def get_queryset(self):
        queryset = super().get_queryset()

        if portfolio_id := self.kwargs.get("portfolio_id", None):
            queryset = queryset.filter(portfolio_id=portfolio_id)

        return queryset.annotate(
            swing_pricing_indicator=Case(
                When(cash_flow_asset_ratio__lt=F("swing_pricing__negative_threshold"), then=Value("neg")),
                When(cash_flow_asset_ratio__gt=F("swing_pricing__positive_threshold"), then=Value("pos")),
                default=None,
            )
        )
