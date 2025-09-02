from decimal import Decimal
from typing import Type

from django.db.models import Exists, OuterRef, Sum
from django.db.models.expressions import F
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from wbcore import serializers
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.serializers.serializers import Serializer
from wbcrm.models import Account
from wbhuman_resources.models.kpi import KPI, KPIHandler
from wbhuman_resources.serializers import KPIModelSerializer
from wbportfolio.models.transactions.claim import Claim


class NetNewMoneyKPISerializer(KPIModelSerializer):
    transaction_subtype = serializers.ChoiceField(
        default="all",
        choices=[("SUBSCRIPTION", "Only Subscriptions"), ("REDEMPTION", "Only Redemptions"), ("all", "All")],
    )
    nnm_from = serializers.ChoiceField(
        default="all",
        label="NNM from",
        choices=[("new_clients", "New clients"), ("existing_clients", "Existing clients"), ("all", "All")],
    )
    only_approved = serializers.BooleanField(
        default=False, label="Only Approved claims", help_text="Filter only approve claims"
    )

    creator = serializers.BooleanField(
        default=True, label="Creator of claim", help_text="NNM considered are related to the creator of claim"
    )
    claimant = serializers.BooleanField(
        default=True, label="Claimant of claim", help_text="NNM considered are related to the claimant"
    )
    in_charge_of_customer = serializers.BooleanField(
        default=True,
        label="In charge of customer",
        help_text="NNM considered are related to the persons in charge of customer",
    )

    def update(self, instance, validated_data):
        transaction_subtype = validated_data.get(
            "transaction_subtype",
            instance.additional_data["serializer_data"].get("transaction_subtype", "all"),
        )
        only_approved = validated_data.get(
            "only_approved",
            instance.additional_data["serializer_data"].get("only_approved", False),
        )
        nnm_from = validated_data.get(
            "nnm_from",
            instance.additional_data["serializer_data"].get("nnm_from", "all"),
        )

        creator = validated_data.get(
            "creator",
            instance.additional_data["serializer_data"].get("creator", True),
        )
        claimant = validated_data.get(
            "claimant",
            instance.additional_data["serializer_data"].get("claimant", True),
        )
        in_charge_of_customer = validated_data.get(
            "in_charge_of_customer",
            instance.additional_data["serializer_data"].get("in_charge_of_customer", True),
        )

        additional_data = instance.additional_data
        additional_data["serializer_data"]["only_approved"] = only_approved
        additional_data["serializer_data"]["transaction_subtype"] = transaction_subtype
        additional_data["serializer_data"]["nnm_from"] = nnm_from
        additional_data["serializer_data"]["creator"] = creator
        additional_data["serializer_data"]["claimant"] = claimant
        additional_data["serializer_data"]["in_charge_of_customer"] = in_charge_of_customer

        additional_data["list_data"] = instance.get_handler().get_list_data(additional_data["serializer_data"])
        validated_data["additional_data"] = additional_data

        return super().update(instance, validated_data)

    class Meta(KPIModelSerializer.Meta):
        fields = (
            *KPIModelSerializer.Meta.fields,
            "transaction_subtype",
            "nnm_from",
            "creator",
            "claimant",
            "in_charge_of_customer",
            "only_approved",
        )


class NetNewMoneyKPI(KPIHandler):
    def get_name(self) -> str:
        return "Net New Money"

    def get_serializer(self) -> Type[Serializer]:
        return NetNewMoneyKPISerializer

    def annotate_parameters(self, queryset: QuerySet[KPI]) -> QuerySet[KPI]:
        return queryset.annotate(
            transaction_subtype=F("additional_data__serializer_data__transaction_subtype"),
            nnm_from=F("additional_data__serializer_data__nnm_from"),
            creator=F("additional_data__serializer_data__creator"),
            claimant=F("additional_data__serializer_data__claimant"),
            in_charge_of_customer=F("additional_data__serializer_data__in_charge_of_customer"),
            only_approved=F("additional_data__serializer_data__only_approved"),
        )

    def get_list_data(self, serializer_data: dict) -> list[str]:
        return [
            f"Claim Area: {serializer_data['transaction_subtype']}",
            f"NNM from: {serializer_data['nnm_from']}",
            f"Creator: {serializer_data['creator']}",
            f"Claimant: {serializer_data['claimant']}",
            f"In charge of customer: {serializer_data['in_charge_of_customer']}",
            f"Only Approved: {serializer_data['only_approved']}",
        ]

    def get_display_grid(self) -> list[list[str]]:
        return [
            ["nnm_from"] * 3,
            ["only_approved"] * 3,
            ["transaction_subtype"] * 3,
            ["creator", "claimant", "in_charge_of_customer"],
        ]

    def evaluate(self, kpi: "KPI", evaluated_person, evaluation_date=None) -> int:
        serializer_data = kpi.additional_data.get("serializer_data")
        to_date = evaluation_date if evaluation_date else kpi.period.upper
        claims = (
            Claim.objects.exclude(status=Claim.Status.WITHDRAWN)
            .filter(date__gte=kpi.period.lower, date__lte=to_date, account__isnull=False)
            .annotate(
                existing_client=Exists(Claim.objects.filter(date__lte=kpi.period.lower, account=OuterRef("account")))
            )
        )

        if serializer_data.get("only_approved") is True:
            claims = claims.filter(status=Claim.Status.APPROVED)

        if (nnm_from := serializer_data.get("nnm_from")) and (nnm_from != "all"):
            if nnm_from == "new_clients":
                claims = claims.filter(existing_client=False)
            elif nnm_from == "existing_clients":
                claims = claims.filter(existing_client=True)

        # TODO This introduced duplicates and can't be removed easily with distinct("id") because of the aggregation
        accounts_ids = list(
            Account.get_managed_accounts_for_entry(evaluated_person.entry_ptr).values_list("id", flat=True)
        )
        for employer in evaluated_person.employers.all():
            accounts_ids.extend(list(Account.get_managed_accounts_for_entry(employer).values_list("id", flat=True)))
        accounts = Account.objects.filter(id__in=accounts_ids)
        claims = claims.filter(account__in=accounts)

        return claims.annotate(
            net_new_money=F("trade__price") * F("shares"),
            fx_rate=CurrencyFXRates.get_fx_rates_subquery("date", currency="product__currency", lookup_expr="exact"),
            net_new_money_usd=Coalesce(F("net_new_money") * F("fx_rate"), Decimal(0)),
        ).aggregate(s=Sum("net_new_money"))["s"] or Decimal(0)
