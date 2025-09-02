from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbportfolio.filters import PortfolioRoleFilterSet
from wbportfolio.models import PortfolioRole
from wbportfolio.serializers import (
    PortfolioRoleModelSerializer,
    PortfolioRoleProjectModelSerializer,
)

from .configs import (
    PortfolioRoleDisplayConfig,
    PortfolioRoleInstrumentDisplayConfig,
    PortfolioRoleInstrumentEndpointConfig,
    PortfolioRoleInstrumentTitleConfig,
    PortfolioRoleTitleConfig,
)


class PortfolioRoleModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    filterset_class = PortfolioRoleFilterSet

    serializer_class = PortfolioRoleModelSerializer
    queryset = PortfolioRole.objects.select_related(
        "person",
        "instrument",
    )

    ordering_fields = ("start", "end", "weighting", "instrument__computed_str")
    ordering = ["instrument__computed_str"]
    search_fields = ("person__computed_str", "instrument__computed_str")

    display_config_class = PortfolioRoleDisplayConfig
    title_config_class = PortfolioRoleTitleConfig


class PortfolioRoleInstrumentModelViewSet(PortfolioRoleModelViewSet):
    serializer_class = PortfolioRoleProjectModelSerializer

    display_config_class = PortfolioRoleInstrumentDisplayConfig
    title_config_class = PortfolioRoleInstrumentTitleConfig
    endpoint_config_class = PortfolioRoleInstrumentEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(instrument__id=self.kwargs["instrument_id"])
