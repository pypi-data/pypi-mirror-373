from wbcore import serializers as wb_serializers

from wbportfolio.models import AssetPosition


class AggregatedAssetPositionModelSerializer(wb_serializers.ModelSerializer):
    id = wb_serializers.PrimaryKeyCharField()
    aggregated_title = wb_serializers.CharField(read_only=True)

    sum_total_value_start = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=4)
    sum_total_value = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=4)
    weighting = wb_serializers.DecimalField(
        read_only=True,
        max_digits=9,
        decimal_places=8,
        percent=True,
        decorators=[{"position": "right", "value": "%"}],
    )
    performance = wb_serializers.DecimalField(
        read_only=True,
        max_digits=6,
        decimal_places=4,
        percent=True,
        decorators=[{"position": "right", "value": "%"}],
    )
    performance_local = wb_serializers.DecimalField(
        read_only=True,
        max_digits=6,
        decimal_places=4,
        percent=True,
        decorators=[{"position": "right", "value": "%"}],
    )
    contribution = wb_serializers.DecimalField(
        read_only=True,
        max_digits=6,
        decimal_places=4,
        percent=True,
        decorators=[{"position": "right", "value": "%"}],
    )
    contribution_local = wb_serializers.DecimalField(
        read_only=True,
        max_digits=6,
        decimal_places=4,
        percent=True,
        decorators=[{"position": "right", "value": "%"}],
    )
    difference_performance = wb_serializers.DecimalField(
        read_only=True,
        max_digits=6,
        decimal_places=4,
        percent=True,
        decorators=[{"position": "right", "value": "%"}],
    )
    difference_contribution = wb_serializers.DecimalField(
        read_only=True,
        max_digits=6,
        decimal_places=4,
        percent=True,
        decorators=[{"position": "right", "value": "%"}],
    )

    class Meta:
        model = AssetPosition
        fields = (
            "id",
            "aggregated_title",
            "sum_total_value_start",
            "sum_total_value",
            "weighting",
            "performance",
            "performance_local",
            "contribution",
            "contribution_local",
            "difference_performance",
            "difference_contribution",
            "_additional_resources",
        )
