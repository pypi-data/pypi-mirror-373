from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbportfolio.models import Rebalancer, RebalancingModel
from wbportfolio.serializers import (
    RebalancerModelSerializer,
    RebalancerRepresentationSerializer,
    RebalancingModelRepresentationSerializer,
)

from .configs.display import RebalancerDisplayConfig
from .configs.endpoints import RebalancerEndpointConfig


class RebalancingModelRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:rebalancingmodel"
    queryset = RebalancingModel.objects.all()
    serializer_class = RebalancingModelRepresentationSerializer


class RebalancerRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:rebalancingmodel"
    queryset = Rebalancer.objects.all()
    serializer_class = RebalancerRepresentationSerializer


class RebalancerModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    queryset = Rebalancer.objects.select_related("rebalancing_model", "portfolio")
    serializer_class = RebalancerModelSerializer
    display_config_class = RebalancerDisplayConfig
    endpoint_config_class = RebalancerEndpointConfig
