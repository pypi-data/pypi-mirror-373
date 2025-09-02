from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework.serializers import ValidationError
from wbcore import serializers
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import EntryRepresentationSerializer
from wbcrm.models import Account
from wbcrm.serializers.accounts import TerminalAccountRepresentationSerializer

from wbportfolio.models import Product, Trade
from wbportfolio.models.transactions.claim import Claim
from wbportfolio.serializers.products import (
    ProductCustomerRepresentationSerializer,
    ProductRepresentationSerializer,
)
from wbportfolio.serializers.transactions.trades import (
    TradeClaimRepresentationSerializer,
)


class ClaimAPIModelSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Product.objects.all(), default=serializers.DefaultFromGET("product")
    )
    product_repr = serializers.StringRelatedField(source="product")
    claimant_repr = serializers.StringRelatedField(source="claimant")
    isin = serializers.SerializerMethodField()

    def get_isin(self, obj):
        return obj.product.isin

    @cached_property
    def user_profile(self) -> Person | None:
        if request := self.context.get("request"):
            return request.user.profile
        return None

    def validate(self, data):
        if "creator" not in data:
            data["creator"] = self.user_profile

        if "claimant" not in data:
            data["claimant"] = self.user_profile

        if not self.instance and (request := self.context.get("request")):
            if "product" not in data and "isin" not in request.data:
                raise ValidationError({"product": "Either product or ISIN has to be supplied"})

            if "isin" in request.data:
                try:
                    data["product"] = Product.objects.get(isin=request.data["isin"])
                except Product.DoesNotExist:
                    raise ValidationError({"isin": "A product with this ISIN does not exist."})
        if trade := data.get("trade", None):
            if not trade.is_claimable:
                raise ValidationError({"trade": "Only a claimable trade can be selected"})
        return data

    class Meta:
        model = Claim
        fields = (
            "id",
            "status",
            "product",
            "product_repr",
            "claimant",
            "claimant_repr",
            "date",
            "bank",
            "reference",
            "shares",
            "isin",
            "external_id",
        )


class ClaimRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="wbportfolio:claim-detail")

    class Meta:
        model = Claim
        fields = (
            "id",
            "shares",
            "bank",
            "account",
            "_detail",
        )


class ClaimModelSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Account.objects.all(),
        default=serializers.DefaultFromGetOrKwargs("account", "account_id"),
        many=False,
    )
    _account = TerminalAccountRepresentationSerializer(source="account")
    _trade = TradeClaimRepresentationSerializer(
        source="trade",
        optional_get_parameters={"product": "underlying_instrument", "date": "pivot_date"},
        depends_on=[{"field": "product", "options": {}}],
    )
    _product = ProductRepresentationSerializer(source="product")
    _creator = EntryRepresentationSerializer(source="creator")
    claimant = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Person.objects.all(),
        default=serializers.CurrentUserDefault("profile"),
        many=False,
        read_only=lambda view: not view.request.user.profile.is_internal,
    )
    _claimant = EntryRepresentationSerializer(source="claimant")

    product = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Product.objects.all(), default=serializers.DefaultFromGET("product"), many=False
    )

    creator = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Person.objects.all(), default=serializers.CurrentUserDefault("profile"), many=False
    )

    currency = serializers.CharField(read_only=True, required=False)
    last_nav = serializers.FloatField(
        default=0, read_only=True, label="NAV", required=False, help_text="The latest product's NAV"
    )
    total_value = serializers.FloatField(
        default=0,
        read_only=True,
        label="Value",
        required=False,
        help_text="The total value (shares * Nav) in the trade currency",
    )
    total_value_usd = serializers.FloatField(
        default=0, read_only=True, label="Value ($)", required=False, help_text="The total value (shares * Nav) in USD"
    )
    date = serializers.DateField(default=lambda: timezone.now().date())
    trade_comment = serializers.TextField(read_only=True, required=False)

    def validate(self, data):
        # If shares or nominal_amount is supplied we can just continue
        if "shares" in data or "nominal_amount" in data:
            # Pop the trade_type and quantity fields, as they are not needed anymore
            data.pop("trade_type", None)
            data.pop("quantity", None)
            return data

        # If we do not have a trade type and instance is None, then we have to raise an error
        if "trade_type" not in data and self.instance is None:
            raise ValidationError({"trade_type": "Trade type is required"})

        trade_type = data.pop("trade_type", self.instance.shares > 0 if self.instance else True)
        as_shares = data.get("as_shares", self.instance.as_shares if self.instance else True)

        # If a new quantity is provided, we take that one, if not we take the value from the instance, depending on the as_shares flag from before this instance was saved
        quantity = data.pop(
            "quantity",
            (
                abs(self.instance.shares)
                if self.instance and self.instance.as_shares
                else abs(self.instance.nominal_amount)
                if self.instance
                else None
            ),
        )
        if quantity is None:
            raise ValidationError({"quantity": "You must provide a quantity"})

        # We set shares/nominal_amount properly based on as_shares and the given quantity
        if as_shares:
            data["nominal_amount"] = None
            data["shares"] = quantity if trade_type else quantity * -1
        else:
            data["shares"] = None
            data["nominal_amount"] = quantity if trade_type else quantity * -1
        return data

    def create(self, validated_data):
        instance = super().create(validated_data)

        # We need to attach the two virtual fields back to the instance, as it won't be reloaded from the db
        instance.trade_type = instance.shares > 0
        instance.quantity = instance.shares if instance.as_shares else instance.nominal_amount
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        # We need to attach the two virtual fields back to the instance, as it won't be reloaded from the db
        instance.trade_type = instance.shares > 0
        instance.quantity = instance.shares if instance.as_shares else instance.nominal_amount
        return instance

    trade_type = serializers.BooleanField(
        labels=["Subscription", "Redemption"],
        values=[True, False],
        active_background_color=["#2e7d32", "white", "#d32f2f"],
        active_color=["white", "black", "white"],
        required=False,
    )
    as_shares = serializers.BooleanField(labels=["Shares", "Nominal"], values=[True, False], label="Quantity Type")
    quantity = serializers.DecimalField(
        max_digits=15,
        decimal_places=4,  # the number of decimal for quantity needs to match the number for the shares field
        signed=False,
        depends_on=[{"field": "trade_type", "options": {}}, {"field": "as_shares", "options": {}}],
        required=False,
    )

    class Meta:
        model = Claim
        decorators = {
            "last_nav": serializers.decorator(decorator_type="text", position="left", value="{{currency}}"),
            "total_value": serializers.decorator(decorator_type="text", position="left", value="{{currency}}"),
            "total_value_usd": serializers.decorator(decorator_type="text", position="left", value="$"),
        }
        fields = (
            "id",
            "status",
            "account",
            "_account",
            "trade",
            "_trade",
            "product",
            "_product",
            "claimant",
            "_claimant",
            "creator",
            "_creator",
            "date",
            "bank",
            "reference",
            "shares",
            "last_nav",
            "total_value",
            "total_value_usd",
            "currency",
            "trade_type",
            "quantity",
            "as_shares",
            "nominal_amount",
            "trade_comment",
            "_additional_resources",
            "_buttons",
        )


class ClaimCustomerModelSerializer(ClaimModelSerializer):
    _product = ProductCustomerRepresentationSerializer(source="product")

    class Meta:
        model = Claim
        fields = (
            "id",
            "status",
            "account",
            "_account",
            "account",
            "product",
            "_product",
            "claimant",
            "_claimant",
            "creator",
            "_creator",
            "date",
            "bank",
            "last_nav",
            "total_value",
            "total_value_usd",
            "reference",
            "shares",
            "nominal_amount",
            "trade_type",
            "quantity",
            "as_shares",
            "_additional_resources",
        )


class ClaimTradeModelSerializer(ClaimModelSerializer):
    bank = serializers.CharField(default=serializers.DefaultFromView("trade.bank"))
    product = serializers.PrimaryKeyRelatedField(
        default=serializers.DefaultFromView("trade.product"),
        many=False,
        queryset=Product.objects.all(),
    )
    date = serializers.DateField(default=serializers.DefaultFromView("trade.transaction_date"))

    def validate(self, data):
        trade = Trade.objects.get(id=self.context["view"].kwargs["trade_id"])
        data["date"] = trade.transaction_date
        data["product"] = trade.product
        data["bank"] = trade.bank
        return super().validate(data)


class ClaimAccountSerializer(ClaimModelSerializer):
    _account = TerminalAccountRepresentationSerializer(source="account")


class NegativeTermimalAccountPerProductModelSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyCharField(read_only=True)
    product_repr = serializers.CharField(read_only=True)
    account_repr = serializers.CharField(read_only=True)
    product_id = serializers.PrimaryKeyField(read_only=True)
    account_id = serializers.PrimaryKeyField(read_only=True)
    sum_shares = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)

    class Meta:
        model = Claim
        fields = ("id", "product_repr", "account_repr", "product_id", "account_id", "sum_shares")
