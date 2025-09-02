from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbportfolio.filters import CustodianFilterSet
from wbportfolio.models import Custodian
from wbportfolio.serializers import (
    CustodianModelSerializer,
    CustodianRepresentationSerializer,
)

from .configs import (
    CustodianButtonConfig,
    CustodianDisplayConfig,
    CustodianEndpointConfig,
    CustodianTitleConfig,
)


class CustodianRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:custodian"

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    queryset = Custodian.objects.all()
    serializer_class = CustodianRepresentationSerializer

    search_fields = ("name",)
    ordering_fields = search_fields
    ordering = ["name"]


class CustodianModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    queryset = Custodian.objects.all()
    filterset_class = CustodianFilterSet
    serializer_class = CustodianModelSerializer

    search_fields = ("name", "mapping")
    ordering_fields = search_fields
    ordering = ["name"]

    display_config_class = CustodianDisplayConfig
    button_config_class = CustodianButtonConfig
    title_config_class = CustodianTitleConfig
    endpoint_config_class = CustodianEndpointConfig

    @action(detail=True, methods=["PATCH"])
    def merge(self, request, pk=None):
        if (merged_custodian_id := request.POST.get("merged_custodian", None)) and merged_custodian_id != pk:
            merged_custodian = get_object_or_404(Custodian, pk=merged_custodian_id)
            base_custodian = get_object_or_404(Custodian, pk=pk)
            base_custodian.merge(merged_custodian)
            return Response({"send": True})
        return Response({"send": True})

    @action(detail=True, methods=["PATCH"])
    def split(self, request, pk=None):
        if mapping_choice := request.POST.get("mapping_choice", None):
            custodian = get_object_or_404(Custodian, pk=pk)
            custodian.split_off(mapping_choice)
        return Response({"send": True})
