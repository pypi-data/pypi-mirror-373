from typing import TYPE_CHECKING, Any

from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.authentication.models import User
from wbcore.contrib.authentication.serializers import UserRepresentationSerializer
from wbcore.utils.urls import new_mode
from wbcrm.models import Account
from wbcrm.serializers.accounts import AccountRepresentationSerializer

from wbportfolio.models import AccountReconciliation
from wbportfolio.models.reconciliations import AccountReconciliationLine
from wbportfolio.serializers.products import ProductRepresentationSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class AccountReconciliationModelSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    _creator = UserRepresentationSerializer(source="creator")
    account = serializers.PrimaryKeyRelatedField(
        default=serializers.DefaultFromGET("account"), queryset=Account.objects.all()
    )
    _account = AccountRepresentationSerializer(source="account")
    approved_by = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    _approved_by = UserRepresentationSerializer(source="approved_by")

    def validate(self, data: dict) -> dict:
        data["creator"] = self.context["request"].user
        if (account := data.get("account", None)) and (isinstance(account, str) or isinstance(account, list)):
            account = account[0] if isinstance(account, list) else account
            data["account"] = Account.objects.get(id=account)
        return data

    @serializers.register_resource()
    def register_lines(self, instance: AccountReconciliation, request: "Request", user: "User") -> dict[str, str]:
        return {
            "lines": reverse(
                "wbportfolio:accountreconciliation-accountreconciliationline-list", args=[instance.id], request=request
            )
        }

    @serializers.register_resource()
    def register_reconcile(self, instance: AccountReconciliation, request: "Request", user: "User") -> dict[str, str]:
        if instance.approved_dt:
            return {}

        if not user.is_internal:
            if hasattr(instance, "unequal_exists") and instance.unequal_exists:
                return {
                    "disagree_customer": reverse(
                        "wbportfolio:accountreconciliation-disagree-customer", args=[instance.id], request=request
                    )
                }
            elif hasattr(instance, "unequal_exists") and not instance.unequal_exists:
                return {
                    "agree_customer": reverse(
                        "wbportfolio:accountreconciliation-agree-customer", args=[instance.id], request=request
                    )
                }

        return {}

    @serializers.register_resource()
    def register_claims(self, instance: AccountReconciliation, request: "Request", user: "User") -> dict[str, str]:
        return {
            "claims": reverse("wbportfolio:account-claim-list", args=[instance.account.id], request=request),
            "add-claim": new_mode(reverse("wbportfolio:claim-list", request=request)),
        }

    @serializers.register_resource()
    def register_recompute(self, instance: AccountReconciliation, request: "Request", user: "User") -> dict[str, str]:
        if instance.approved_dt:
            return {}

        if user.is_internal:
            return {
                "recalculate": reverse(
                    "wbportfolio:accountreconciliation-recompute", args=[instance.id], request=request
                ),
                "notify": reverse("wbportfolio:accountreconciliation-notify", args=[instance.id], request=request),
            }

        return {}

    class Meta:
        model = AccountReconciliation
        fields = (
            "id",
            "reconciliation_date",
            "creator",
            "_creator",
            "approved_by",
            "_approved_by",
            "approved_dt",
            "account",
            "_account",
            "_additional_resources",
        )


class AccountReconciliationLineModelSerializer(serializers.ModelSerializer):
    _product = ProductRepresentationSerializer(source="product")
    is_equal = serializers.BooleanField(read_only=True)

    assets_under_management = serializers.IntegerField(
        read_only=True,
        decorators=[serializers.decorator(position="left", value="{{currency_key}}", decorator_type="text")],
    )
    assets_under_management_external = serializers.IntegerField(
        read_only=True,
        decorators=[serializers.decorator(position="left", value="{{currency_key}}", decorator_type="text")],
    )
    assets_under_management_diff = serializers.IntegerField(
        read_only=True,
        decorators=[serializers.decorator(position="left", value="{{currency_key}}", decorator_type="text")],
    )
    shares_diff = serializers.IntegerField(read_only=True)
    nominal_value_diff = serializers.IntegerField(read_only=True)
    pct_diff = serializers.DecimalField(read_only=True, max_digits=5, decimal_places=4)

    price = serializers.DecimalField(read_only=True, max_digits=18, decimal_places=2, label="Price")

    currency = serializers.CharField(required=False)
    currency_key = serializers.CharField(required=False)

    @serializers.register_resource()
    def register_claims(self, instance: AccountReconciliationLine, request: "Request", user: "User") -> dict[str, str]:
        return {
            "product-claims": f'{reverse("wbportfolio:account-claim-list", args=[instance.reconciliation.account.id], request=request)}?product={instance.product.id}',
            "add-product-claim": new_mode(
                f'{reverse("wbportfolio:claim-list", request=request)}?product={instance.product.id}'
            ),
        }

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        # If we get either external shares or external nominal value, we have to set the other one explicitly to None
        # to be sure that the other side is correctly computed inside the save method
        if "shares_external" not in data and "nominal_value_external" in data:
            data["shares_external"] = None

        if "shares_external" in data and "nominal_value_external" not in data:
            data["nominal_value_external"] = None

        return super().validate(data)

    class Meta:
        model = AccountReconciliationLine
        read_only_fields = ("product", "shares", "nominal_value")
        decorators = {"price": serializers.decorator(position="left", value="{{currency_key}}", decorator_type="text")}
        percent_fields = ["pct_diff"]
        fields = (
            "id",
            "reconciliation",
            "price",
            "price_date",
            "currency",
            "currency_key",
            "product",
            "_product",
            "shares",
            "nominal_value",
            "assets_under_management",
            "shares_external",
            "nominal_value_external",
            "assets_under_management_external",
            "shares_diff",
            "nominal_value_diff",
            "assets_under_management_diff",
            "pct_diff",
            "is_equal",
            "_additional_resources",
        )
