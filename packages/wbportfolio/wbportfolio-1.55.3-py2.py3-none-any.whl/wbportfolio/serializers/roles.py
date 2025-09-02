from rest_framework import serializers
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer
from wbfdm.serializers import InvestableInstrumentRepresentationSerializer

from wbportfolio.models import PortfolioRole


class PortfolioRoleModelSerializer(wb_serializers.ModelSerializer):
    """Model Serializer for Portfolio Roles"""

    _person = PersonRepresentationSerializer(source="person")
    _instrument = InvestableInstrumentRepresentationSerializer(source="instrument")

    def create(self, validated_data):
        instrument = validated_data.get("instrument", None)
        role_type = validated_data.get("role_type")

        if instrument is not None and role_type in [
            PortfolioRole.RoleType.MANAGER,
            PortfolioRole.RoleType.RISK_MANAGER,
        ]:
            raise serializers.ValidationError(
                {"instrument": [PortfolioRole.default_error_messages["manager"].format(model="instrument")]}
            )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        instrument = validated_data.get("instrument", None)
        role_type = validated_data.get("role_type", instance.role_type)

        if instrument is not None and role_type in [
            PortfolioRole.RoleType.MANAGER,
            PortfolioRole.RoleType.RISK_MANAGER,
        ]:
            raise serializers.ValidationError(
                {"instrument": [PortfolioRole.default_error_messages["manager"].format(model="instrument")]}
            )

        return super().update(instance, validated_data)

    class Meta:
        model = PortfolioRole
        fields = (
            "id",
            "role_type",
            "person",
            "_person",
            "start",
            "end",
            "weighting",
            "instrument",
            "_instrument",
        )


class PortfolioRoleProjectModelSerializer(PortfolioRoleModelSerializer):
    """Model Serializer for Portfolio Roles for Products"""

    role_type = wb_serializers.ChoiceField(choices=PortfolioRole.RoleType.choices)
