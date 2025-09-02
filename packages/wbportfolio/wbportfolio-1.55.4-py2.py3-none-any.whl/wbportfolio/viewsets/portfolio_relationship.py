from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbportfolio.models import (
    InstrumentPortfolioThroughModel,
    PortfolioInstrumentPreferredClassificationThroughModel,
)
from wbportfolio.serializers import (
    InstrumentPortfolioThroughModelSerializer,
    InstrumentPreferedClassificationThroughProductModelSerializer,
)

from .configs import (
    InstrumentPortfolioThroughPortfolioModelDisplayConfig,
    InstrumentPortfolioThroughPortfolioModelEndpointConfig,
    PortfolioInstrumentPreferredClassificationThroughDisplayConfig,
    PortfolioInstrumentPreferredClassificationThroughEndpointConfig,
)


class InstrumentPreferedClassificationThroughProductModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    serializer_class = InstrumentPreferedClassificationThroughProductModelSerializer
    queryset = PortfolioInstrumentPreferredClassificationThroughModel.objects.all()

    search_fields = ("instrument__computed_str", "classification__computed_str")
    ordering_fields = ordering = ["instrument__computed_str"]
    filterset_fields = {"instrument": ["exact"], "classification": ["exact"]}
    display_config_class = PortfolioInstrumentPreferredClassificationThroughDisplayConfig
    endpoint_config_class = PortfolioInstrumentPreferredClassificationThroughEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(portfolio=self.kwargs["portfolio_id"])


class InstrumentPortfolioThroughPortfolioModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    serializer_class = InstrumentPortfolioThroughModelSerializer
    queryset = InstrumentPortfolioThroughModel.objects.all()

    search_fields = ("instrument__name",)
    ordering_fields = ["instrument__name"]
    ordering = ["instrument__name"]

    display_config_class = InstrumentPortfolioThroughPortfolioModelDisplayConfig
    endpoint_config_class = InstrumentPortfolioThroughPortfolioModelEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(portfolio=self.kwargs["portfolio_id"])
