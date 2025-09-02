from datetime import date

from wbcore import serializers as wb_serializers
from wbcore.serializers import DefaultFromGET

from wbportfolio.models import Portfolio, Rebalancer, RebalancingModel


class RebalancingModelRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RebalancingModel
        fields = (
            "id",
            "name",
        )


class RebalancerRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:rebalancer-detail")

    class Meta:
        model = Rebalancer
        fields = ("id", "computed_str", "_detail")


class RebalancerModelSerializer(wb_serializers.ModelSerializer):
    _rebalancing_model = RebalancingModelRepresentationSerializer(source="rebalancing_model")
    frequency_repr = wb_serializers.SerializerMethodField()
    portfolio = wb_serializers.PrimaryKeyRelatedField(
        queryset=Portfolio.objects.all(), default=DefaultFromGET("portfolio")
    )
    activation_date = wb_serializers.DateField(default=lambda: date.today())

    rebalancing_dates = wb_serializers.SerializerMethodField(
        label="Next 10 Rebalancing Dates", field_class=wb_serializers.ListField
    )

    def get_rebalancing_dates(self, obj):
        return list(map(lambda d: d.strftime("%Y-%m-%d"), obj.get_rrule(count=10)))

    def get_frequency_repr(self, obj):
        return obj.frequency_repr

    class Meta:
        model = Rebalancer
        fields = (
            "id",
            "portfolio",
            "computed_str",
            "_rebalancing_model",
            "rebalancing_model",
            "apply_order_proposal_automatically",
            "activation_date",
            "frequency",
            "frequency_repr",
            "rebalancing_dates",
        )
