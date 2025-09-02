from wbcore import serializers as wb_serializers
from wbfdm.serializers import (
    ClassifiableInstrumentRepresentationSerializer,
    ClassificationIsFavoriteZeroHeightRepresentationSerializer,
    ManagedInstrumentRepresentationSerializer,
)
from wbfdm.serializers.instruments.classifications import (
    ClassificationGroupRepresentationSerializer,
)

from wbportfolio.models.portfolio_relationship import (
    InstrumentPortfolioThroughModel,
    PortfolioInstrumentPreferredClassificationThroughModel,
)

from .portfolios import PortfolioRepresentationSerializer


class InstrumentPortfolioThroughModelSerializer(wb_serializers.ModelSerializer):
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")
    _instrument = ManagedInstrumentRepresentationSerializer(source="instrument")

    class Meta:
        model = InstrumentPortfolioThroughModel
        fields = (
            "id",
            "_portfolio",
            "portfolio",
            "_instrument",
            "instrument",
        )


class InstrumentPreferedClassificationThroughProductModelSerializer(wb_serializers.ModelSerializer):
    _instrument = ClassifiableInstrumentRepresentationSerializer(source="instrument")
    _classification = ClassificationIsFavoriteZeroHeightRepresentationSerializer(
        source="classification", optional_get_parameters={"instrument": "instrument"}
    )
    _classification_group = ClassificationGroupRepresentationSerializer(source="classification_group")

    class Meta:
        model = PortfolioInstrumentPreferredClassificationThroughModel
        dependency_map = {"classification": ["instrument"]}
        fields = (
            "id",
            "portfolio",
            "_instrument",
            "instrument",
            "_classification",
            "classification",
            "classification_group",
            "_classification_group",
            "_additional_resources",
        )
