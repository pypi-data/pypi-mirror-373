from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers

from wbportfolio.models import Custodian


class CustodianRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:custodian-detail")

    class Meta:
        model = Custodian
        fields = ("id", "name", "_detail")


class CustodianModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_resource()
    def _addition_resources(self, instance, request, user):
        res = {
            "merge": reverse("wbportfolio:custodian-merge", args=[instance.id], request=request),
        }
        if len(instance.mapping) > 1:
            res["split"] = reverse("wbportfolio:custodian-split", args=[instance.id], request=request)
        return res

    class Meta:
        model = Custodian
        fields = ("id", "name", "mapping", "_additional_resources")
