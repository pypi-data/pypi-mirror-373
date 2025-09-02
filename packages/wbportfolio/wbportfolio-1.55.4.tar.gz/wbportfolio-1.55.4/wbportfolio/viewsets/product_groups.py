from wbcore import viewsets
from wbfdm.viewsets.configs.buttons.instruments import InstrumentButtonViewConfig

from wbportfolio.models import ProductGroup
from wbportfolio.serializers import (
    ProductGroupModelSerializer,
    ProductGroupRepresentationSerializer,
)

from .configs import (
    ProductGroupDisplayConfig,
    ProductGroupEndpointConfig,
    ProductGroupTitleConfig,
)


class ProductGroupRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:product_group"
    serializer_class = ProductGroupRepresentationSerializer

    search_fields = ("computed_str",)

    queryset = ProductGroup.active_objects.all()


class ProductGroupModelViewSet(viewsets.ModelViewSet):
    queryset = ProductGroup.objects.all()
    serializer_class = ProductGroupModelSerializer

    title_config_class = ProductGroupTitleConfig
    endpoint_config_class = ProductGroupEndpointConfig
    display_config_class = ProductGroupDisplayConfig
    button_config_class = InstrumentButtonViewConfig

    ordering_fields = (
        "name",
        "identifier",
        "umbrella",
        "type",
        "category",
        "management_company",
        "depositary",
        "transfer_agent",
        "administrator",
        "investment_manager",
        "auditor",
        "paying_agent",
    )
    ordering = ("identifier",)
    search_fields = ("name", "identifier", "umbrella", "category", "type")

    filterset_fields = {
        "identifier": ["exact"],
        "name": ["exact"],
        "umbrella": ["exact"],
        "type": ["exact"],
        "category": ["exact"],
        "management_company": ["exact"],
        "depositary": ["exact"],
        "transfer_agent": ["exact"],
        "administrator": ["exact"],
        "investment_manager": ["exact"],
        "auditor": ["exact"],
        "paying_agent": ["exact"],
    }

    def get_serializer_class(self):
        return ProductGroupModelSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "management_company",
                "depositary",
                "transfer_agent",
                "administrator",
                "investment_manager",
                "auditor",
                "paying_agent",
                "instrument_ptr",
            )
            .prefetch_related("representants")
        )
