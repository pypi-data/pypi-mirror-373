from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbportfolio.models import Adjustment
from wbportfolio.serializers import AdjustmentModelSerializer

from .configs import (
    AdjustmentButtonConfig,
    AdjustmentDisplayConfig,
    AdjustmentEndpointConfig,
    AdjustmentEquityEndpointConfig,
    AdjustmentTitleConfig,
)


class AdjustmentModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    queryset = Adjustment.objects.select_related(
        "instrument",
        "last_handler",
    )
    serializer_class = AdjustmentModelSerializer

    filterset_fields = {
        "date": ["gte", "exact", "lte"],
        "instrument": ["exact"],
        "factor": ["gte", "exact", "lte"],
        "status": ["exact"],
        "last_handler": ["exact"],
    }
    ordering = ["-date"]
    ordering_fields = ["date", "instrument", "factor"]

    display_config_class = AdjustmentDisplayConfig
    title_config_class = AdjustmentTitleConfig
    endpoint_config_class = AdjustmentEndpointConfig
    button_config_class = AdjustmentButtonConfig


class AdjustmentEquityModelViewSet(AdjustmentModelViewSet):
    filterset_fields = {
        "date": ["gte", "exact", "lte"],
        "factor": ["gte", "exact", "lte"],
        "status": ["exact"],
        "last_handler": ["exact"],
    }
    endpoint_config_class = AdjustmentEquityEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(instrument=self.kwargs["instrument_id"])
