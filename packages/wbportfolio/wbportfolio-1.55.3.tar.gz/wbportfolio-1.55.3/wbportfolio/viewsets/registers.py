from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbportfolio.models import Register
from wbportfolio.serializers import (
    RegisterModelSerializer,
    RegisterRepresentationSerializer,
)
from wbportfolio.viewsets.configs.buttons.registers import RegisterButtonConfig
from wbportfolio.viewsets.configs.display.registers import RegisterDisplayConfig
from wbportfolio.viewsets.configs.titles.registers import RegisterTitleConfig


class RegisterRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    serializer_class = RegisterRepresentationSerializer

    queryset = Register.objects.all()
    ordering = ["register_reference"]
    search_fields = [
        "register_reference",
        "register_name_1",
        "register_name_2",
        "custodian_reference",
        "custodian_name_1",
        "custodian_name_2",
        "outlet_reference",
        "outlet_name",
    ]


class RegisterModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    queryset = Register.objects.all()
    serializer_class = RegisterModelSerializer

    filterset_fields = {
        "register_reference": ["icontains"],
        "register_name_1": ["icontains"],
        "register_name_2": ["icontains"],
        "custodian_reference": ["icontains"],
        "custodian_name_1": ["icontains"],
        "custodian_name_2": ["icontains"],
        "outlet_reference": ["icontains"],
        "outlet_name": ["icontains"],
        "status": ["exact"],
        "status_message": ["icontains"],
        "global_register_reference": ["exact"],
    }
    ordering = ["register_reference"]
    search_fields = [
        "register_reference",
        "register_name_1",
        "register_name_2",
        "custodian_reference",
        "custodian_name_1",
        "custodian_name_2",
        "outlet_reference",
        "outlet_name",
    ]

    display_config_class = RegisterDisplayConfig
    title_config_class = RegisterTitleConfig
    button_config_class = RegisterButtonConfig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "custodian_country",
                "custodian_city",
                "outlet_city",
                "outlet_country",
                "citizenship",
                "residence",
            )
        )
