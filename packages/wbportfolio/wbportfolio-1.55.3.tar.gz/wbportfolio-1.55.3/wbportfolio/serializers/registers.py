from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.geography.serializers import GeographyRepresentationSerializer

from wbportfolio.models import Register


class RegisterRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="wbportfolio:register-detail")

    class Meta:
        model = Register
        fields = ("id", "computed_str", "_detail")


class RegisterModelSerializer(serializers.ModelSerializer):
    _custodian_country = GeographyRepresentationSerializer(source="custodian_country", filter_params={"level": 1})
    _custodian_city = GeographyRepresentationSerializer(source="custodian_city", filter_params={"level": 3})
    _outlet_city = GeographyRepresentationSerializer(source="outlet_city", filter_params={"level": 3})
    _outlet_country = GeographyRepresentationSerializer(source="outlet_country", filter_params={"level": 1})
    _citizenship = GeographyRepresentationSerializer(source="citizenship", filter_params={"level": 1})
    _residence = GeographyRepresentationSerializer(source="residence", filter_params={"level": 1})

    @serializers.register_only_instance_resource()
    def trades(self, instance, request, user, **kwargs):
        if instance.trades.exists():
            base_url = reverse("wbportfolio:trade-list", request=request)
            return {"trades": f"{base_url}?register={instance.id}"}
        return {}

    class Meta:
        model = Register
        fields = (
            "id",
            "register_reference",
            "register_name_1",
            "register_name_2",
            "global_register_reference",
            "external_register_reference",
            "custodian_reference",
            "custodian_name_1",
            "custodian_name_2",
            "custodian_address",
            "custodian_postcode",
            "custodian_city",
            "custodian_country",
            "sales_reference",
            "dealer_reference",
            "outlet_reference",
            "outlet_name",
            "outlet_address",
            "outlet_postcode",
            "outlet_city",
            "_outlet_city",
            "outlet_country",
            "citizenship",
            "residence",
            "investor_type",
            "status",
            "status_message",
            "opened",
            "opened_reference_1",
            "opened_reference_2",
            "updated_reference_1",
            "updated_reference_2",
            # Related Fields
            "_custodian_country",
            "_custodian_city",
            "_outlet_country",
            "_citizenship",
            "_residence",
            "_additional_resources",
        )
