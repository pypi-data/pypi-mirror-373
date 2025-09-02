from datetime import date

from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.models import BankingContact
from wbfdm.serializers import InstrumentRepresentationSerializer

from wbportfolio.models import Portfolio, PortfolioPortfolioThroughModel
from wbportfolio.serializers.rebalancing import RebalancerRepresentationSerializer


class PortfolioRepresentationSerializer(wb_serializers.RepresentationSerializer):
    def get_filter_params(self, request):
        return {"is_tracked": True}

    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:portfolio-detail")
    _detail_preview = wb_serializers.HyperlinkField(reverse_name="wbportfolio:portfolio-detail")

    class Meta:
        model = Portfolio
        fields = ("id", "name", "_detail", "_detail_preview")


class PortfolioModelSerializer(wb_serializers.ModelSerializer):
    _currency = CurrencyRepresentationSerializer(source="currency")
    _hedged_currency = CurrencyRepresentationSerializer(source="hedged_currency")
    _depends_on = PortfolioRepresentationSerializer(source="depends_on", many=True)
    automatic_rebalancer = wb_serializers.PrimaryKeyRelatedField(read_only=True)
    _automatic_rebalancer = RebalancerRepresentationSerializer(source="automatic_rebalancer")
    _instruments = InstrumentRepresentationSerializer(source="instruments", many=True)

    create_index = wb_serializers.BooleanField(write_only=True, default=False)

    last_asset_under_management_usd = wb_serializers.FloatField(read_only=True)
    last_positions = wb_serializers.FloatField(read_only=True)
    last_order_proposal_date = wb_serializers.DateField(read_only=True)
    next_expected_order_proposal_date = wb_serializers.SerializerMethodField(read_only=True)

    def get_next_expected_order_proposal_date(self, obj):
        if (automatic_rebalancer := getattr(obj, "automatic_rebalancer", None)) and (
            _d := automatic_rebalancer.get_next_rebalancing_date(date.today())
        ):
            return _d.strftime("%Y-%m-%d")

    def create(self, validated_data):
        create_index = validated_data.pop("create_index", False)
        obj = super().create(validated_data)
        if create_index:
            obj.get_or_create_index()
        return obj

    @wb_serializers.register_only_instance_resource()
    def cash_management(self, instance, request, user, **kwargs):
        additional_resources = dict()
        if instance.daily_cashflows.exists():
            additional_resources["daily_cashflows"] = reverse(
                "wbportfolio:portfolio-portfoliocashflow-list", args=[instance.id], request=request
            )
        b = BankingContact.objects.filter(wbportfolio_products__id__in=instance.instruments.all().values("id"))
        if b.exists():
            base_url = reverse("wbaccounting:futurecashflow-list", request=request)
            additional_resources["cash_flow"] = (
                f'{base_url}?banking_contact={",".join([str(i) for i in b.distinct("id").values_list("id", flat=True)])}'
            )

        return additional_resources

    @wb_serializers.register_only_instance_resource()
    def additional_resources(self, instance, request, user, **kwargs):
        additional_resources = dict()
        additional_resources["distribution_chart"] = reverse(
            "wbportfolio:portfolio-distributionchart-list", args=[instance.id], request=request
        )
        additional_resources["distribution_table"] = reverse(
            "wbportfolio:portfolio-distributiontable-list", args=[instance.id], request=request
        )
        if instance.assets.exists():
            additional_resources["assets"] = reverse(
                "wbportfolio:portfolio-asset-list", args=[instance.id], request=request
            )
            additional_resources["contributor"] = reverse(
                "wbportfolio:portfolio-contributor-list",
                args=[instance.id],
                request=request,
            )
        if user.profile.is_internal:
            additional_resources["instruments_list"] = reverse(
                "wbportfolio:portfolio-instrument-list",
                args=[instance.id],
                request=request,
            )

        additional_resources["dependencyportfolios"] = reverse(
            "wbportfolio:portfolio-dependencyportfolio-list",
            args=[instance.id],
            request=request,
        )

        additional_resources["preferredclassification"] = reverse(
            "wbportfolio:portfolio-preferredclassification-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["modelcomposition"] = reverse(
            "wbportfolio:portfolio-modelcompositionpandas-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["order_proposals"] = reverse(
            "wbportfolio:portfolio-orderproposal-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["rebalance"] = reverse(
            "wbportfolio:portfolio-rebalance",
            args=[instance.id],
            request=request,
        )
        if not getattr(instance, "automatic_rebalancer", None):
            additional_resources["add_automatic_rebalancer"] = reverse(
                "wbportfolio:portfolio-attachrebalancer",
                args=[instance.id],
                request=request,
            )
        if user.is_superuser and instance.is_lookthrough:
            additional_resources["recompute_lookthrough"] = reverse(
                "wbportfolio:portfolio-recomputelookthrough",
                args=[instance.id],
                request=request,
            )
        additional_resources["treegraphchart"] = reverse(
            "wbportfolio:portfolio-treegraphchart-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["topdowncomposition"] = reverse(
            "wbportfolio:portfolio-topdowncomposition-list",
            args=[instance.id],
            request=request,
        )
        return additional_resources

    class Meta:
        model = Portfolio
        fields = (
            "id",
            "name",
            "updated_at",
            "_depends_on",
            "depends_on",
            "_instruments",
            "instruments",
            "_currency",
            "currency",
            "_hedged_currency",
            "hedged_currency",
            "automatic_rebalancer",
            "_automatic_rebalancer",
            "invested_timespan",
            "is_manageable",
            "is_tracked",
            "only_weighting",
            "is_lookthrough",
            "is_composition",
            "_additional_resources",
            "create_index",
            "initial_position_date",
            "last_position_date",
            "last_asset_under_management_usd",
            "last_positions",
            "last_order_proposal_date",
            "next_expected_order_proposal_date",
        )


class PortfolioPortfolioThroughModelSerializer(wb_serializers.ModelSerializer):
    _portfolio = PortfolioRepresentationSerializer(source="portfolio")
    _dependency_portfolio = PortfolioRepresentationSerializer(source="dependency_portfolio")

    class Meta:
        model = PortfolioPortfolioThroughModel
        fields = (
            "id",
            "_portfolio",
            "portfolio",
            "_dependency_portfolio",
            "dependency_portfolio",
            "type",
        )
