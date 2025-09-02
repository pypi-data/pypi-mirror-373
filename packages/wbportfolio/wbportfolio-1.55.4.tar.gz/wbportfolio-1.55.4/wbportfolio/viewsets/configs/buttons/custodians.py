from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbportfolio.models import Custodian
from wbportfolio.serializers import CustodianRepresentationSerializer


class CustodianButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        custodians_qs = Custodian.objects.all()
        if self.view.kwargs.get("pk", None):
            custodians_qs = custodians_qs.exclude(id=self.view.kwargs["pk"])

        class CustodianMergeModelSerializer(wb_serializers.ModelSerializer):
            merged_custodian = wb_serializers.PrimaryKeyRelatedField(
                required=True, queryset=custodians_qs, label="Custodian to be merged"
            )
            _merged_custodian = CustodianRepresentationSerializer(source="merged_custodian")

            class Meta:
                model = Custodian
                fields = ("id", "merged_custodian", "_merged_custodian")

        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:custodian",),
                key="merge",
                icon=WBIcon.TRADE.icon,
                label="Merge custodians",
                description_fields="""
                <p>Merge the custodian <strong>{{name}}</strong> with another custodian in the list bellow</p>
                """,
                serializer=CustodianMergeModelSerializer,
                action_label="Merge",
                title="Merge custodians",
                instance_display=create_simple_display([["merged_custodian"]]),
            )
        }

    def get_custom_instance_buttons(self):
        if custodian_id := self.view.kwargs.get("pk", None):
            custodian = Custodian.objects.get(id=custodian_id)

            class AdjustmentModelSerializer(wb_serializers.ModelSerializer):
                mapping_choice = wb_serializers.ChoiceField(
                    required=True, choices={m: m for m in custodian.mapping}, label="Mapping to split off"
                )

                class Meta:
                    model = Custodian
                    fields = ("id", "mapping_choice", "name")

            merge_button = {
                bt.ActionButton(
                    method=RequestType.PATCH,
                    identifiers=("wbportfolio:custodian",),
                    key="split",
                    icon=WBIcon.TRADE.icon,
                    label="Adjustment custodians",
                    description_fields="""
                    <p>Adjustment the custodian <strong>{{name}}</strong> with another custodian in the list bellow</p>
                    """,
                    serializer=AdjustmentModelSerializer,
                    action_label="Adjustment",
                    title="Adjustment custodians",
                    instance_display=create_simple_display([["mapping_choice"]]),
                )
            }
            return self.get_custom_list_instance_buttons() | merge_button
        return self.get_custom_list_instance_buttons()
