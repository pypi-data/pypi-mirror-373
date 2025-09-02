from django.contrib.messages import warning
from django.core.exceptions import ValidationError
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer
from wbcore.serializers import CharField, DefaultFromView

from wbportfolio.models import OrderProposal, Portfolio, RebalancingModel

from .. import PortfolioRepresentationSerializer, RebalancingModelRepresentationSerializer


class OrderProposalRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:orderproposal-detail")

    class Meta:
        model = OrderProposal
        fields = ("id", "trade_date", "status", "_detail")


class OrderProposalModelSerializer(wb_serializers.ModelSerializer):
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")
    rebalancing_model = wb_serializers.PrimaryKeyRelatedField(queryset=RebalancingModel.objects.all(), required=False)
    _rebalancing_model = RebalancingModelRepresentationSerializer(source="rebalancing_model")
    target_portfolio = wb_serializers.PrimaryKeyRelatedField(
        queryset=Portfolio.objects.all(), write_only=True, required=False
    )
    _target_portfolio = PortfolioRepresentationSerializer(source="target_portfolio")
    trade_date = wb_serializers.DateField(
        read_only=lambda view: not view.new_mode, default=DefaultFromView("default_trade_date")
    )
    _creator = PersonRepresentationSerializer(source="creator")
    _approver = PersonRepresentationSerializer(source="approver")
    execution_status_repr = wb_serializers.SerializerMethodField(label="Status", field_class=CharField, read_only=True)

    def get_execution_status_repr(self, obj):
        repr = obj.execution_status
        if obj.execution_status_detail:
            repr += f" (Custodian: {obj.execution_status_detail})"
        return repr

    def create(self, validated_data):
        target_portfolio = validated_data.pop("target_portfolio", None)
        rebalancing_model = validated_data.get("rebalancing_model", None)
        if request := self.context.get("request"):
            validated_data["creator"] = request.user.profile
        obj = super().create(validated_data)

        target_portfolio_dto = None
        if target_portfolio:
            target_portfolio_dto = target_portfolio._build_dto(obj.trade_date)
        elif rebalancing_model:
            target_portfolio_dto = rebalancing_model.get_target_portfolio(
                obj.portfolio, obj.trade_date, obj.last_effective_date
            )

        try:
            obj.reset_orders(target_portfolio=target_portfolio_dto)
        except ValidationError as e:
            if request := self.context.get("request"):
                warning(request, str(e), extra_tags="auto_close=0")
        return obj

    @wb_serializers.register_only_instance_resource()
    def additional_resources(self, instance, request, user, **kwargs):
        res = {}
        if instance.status == OrderProposal.Status.APPLIED:
            res["replay"] = reverse("wbportfolio:orderproposal-replay", args=[instance.id], request=request)
        if instance.status == OrderProposal.Status.DRAFT:
            res["reset"] = reverse("wbportfolio:orderproposal-reset", args=[instance.id], request=request)
            res["normalize"] = reverse("wbportfolio:orderproposal-normalize", args=[instance.id], request=request)
            res["deleteall"] = reverse("wbportfolio:orderproposal-deleteall", args=[instance.id], request=request)
        res["orders"] = reverse(
            "wbportfolio:orderproposal-order-list",
            args=[instance.id],
            request=request,
        )
        return res

    class Meta:
        model = OrderProposal
        only_fsm_transition_on_instance = True
        percent_fields = ["total_cash_weight"]
        fields = (
            "id",
            "trade_date",
            "portfolio",
            "_portfolio",
            "total_cash_weight",
            "comment",
            "status",
            "min_order_value",
            "_rebalancing_model",
            "rebalancing_model",
            "target_portfolio",
            "_target_portfolio",
            "creator",
            "approver",
            "_creator",
            "_approver",
            "execution_status",
            "execution_status_detail",
            "execution_comment",
            "execution_status_repr",
            "_additional_resources",
        )


class ReadOnlyOrderProposalModelSerializer(OrderProposalModelSerializer):
    class Meta(OrderProposalModelSerializer.Meta):
        read_only_fields = OrderProposalModelSerializer.Meta.fields
