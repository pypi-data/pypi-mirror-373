from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer
from wbfdm.serializers import SecurityRepresentationSerializer

from wbportfolio.models import Adjustment


class AdjustmentModelSerializer(wb_serializers.ModelSerializer):
    _instrument = SecurityRepresentationSerializer(source="instrument")
    _last_handler = PersonRepresentationSerializer(source="last_handler")

    class Meta:
        model = Adjustment
        fields = (
            "id",
            "date",
            "instrument",
            "_instrument",
            "status",
            "factor",
            "cumulative_factor",
            "_last_handler",
            "last_handler",
            "_additional_resources",
        )
