from datetime import date, timedelta
from datetime import date as date_lib
from decimal import Decimal

from django.db import models
from django.db.models import (
    DateField,
    Exists,
    ExpressionWrapper,
    OuterRef,
    Q,
    QuerySet,
    Sum,
)
from django.db.models.functions import Greatest
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from wbcore.contrib.ai.llm.config import add_llm_prompt
from wbcore.contrib.authentication.models import User
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.directory.models import Entry
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.models import WBModel
from wbcore.signals import pre_merge
from wbcore.signals.models import pre_collection
from wbcore.utils.enum import ChoiceEnum
from wbcore.utils.strings import ReferenceIDMixin
from wbcrm.models import AccountRole
from wbcrm.models.accounts import Account
from wbfdm.models.instruments.instrument_prices import InstrumentPrice

from ..custodians import Custodian
from ..llm.wbcrm.analyze_relationship import get_performances_prompt
from ..roles import PortfolioRole
from .trades import Trade


def can_administrate_claim(claim, user):
    today = date_lib.today()
    return (
        user.profile.portfolio_roles.filter(
            Q(role_type=PortfolioRole.RoleType.MANAGER)
            & (Q(start__isnull=True) | Q(start__lte=today))
            & (Q(end__isnull=True) | Q(end__gte=today))
        ).exists()
        or user.is_superuser
    )


def can_edit_claim(claim, user):
    return (claim.claimant and claim.claimant.id == user.profile.id) or user.profile.is_internal or user.is_superuser


class ClaimGroupbyChoice(ChoiceEnum):
    ROOT_ACCOUNT = "Root Account"
    ACCOUNT = "Account"
    ROOT_ACCOUNT_OWNER = "Root Account Owner"
    ACCOUNT_OWNER = "Account Owner"
    PRODUCT = "Product"
    PRODUCT_GROUP = "ProductGroup"
    CLASSIFICATION = "Classification"

    @classmethod
    @property
    def map(cls):
        return {
            "ROOT_ACCOUNT": {
                "pk": "root_account",
                "title_key": "root_account_repr",
                "search_fields": ["root_account_repr"],
            },
            "ACCOUNT": {
                "pk": "account",
                "title_key": "account__computed_str",
                "search_fields": ["account__computed_str"],
            },
            "ROOT_ACCOUNT_OWNER": {
                "pk": "root_account_owner",
                "title_key": "root_account_owner_repr",
                "search_fields": ["root_account_owner_repr"],
            },
            "ACCOUNT_OWNER": {
                "pk": "account__owner",
                "title_key": "account__owner__computed_str",
                "search_fields": ["account__owner__computed_str"],
            },
            "PRODUCT": {
                "pk": "product",
                "title_key": "product__computed_str",
                "search_fields": ["product__computed_str"],
            },
            "PRODUCT_GROUP": {
                "pk": "product__parent",
                "title_key": "product__parent__name",
                "search_fields": ["product__parent__name"],
            },
            "CLASSIFICATION": {
                "pk": "classification_id",
                "title_key": "classification_title",
                "search_fields": ["classification_title"],
            },
        }

    @classmethod
    def get_map(cls, name):
        return cls.map[name]


class ClaimDefaultQueryset(QuerySet):
    def filter_for_user(self, user: User, validity_date: date_lib | None = None) -> QuerySet:
        """
        Protect the chained queryset and filter the claims that this user cannot see based on the following rules:
        """
        if user.has_perm("wbcrm.administrate_account"):
            return self
        allowed_accounts = Account.objects.filter_for_user(user, validity_date=validity_date).values(
            "id"
        )  # This is way faster
        # accounts = self.annotate(can_see_account=Exists(allowed_accounts.filter(id=OuterRef("account"))))
        if user.profile.is_internal:
            return self.filter(Q(account__isnull=True) | Q(account__in=allowed_accounts))
        return self.filter(Q(account__in=allowed_accounts) | (Q(account__isnull=True) & Q(creator_id=user.profile.id)))

    def filter_for_customer(self, customer: Entry, include_related_roles: bool = False) -> QuerySet:
        """
        Filter the chained queryset to return only the claim that belongs to a certain customer
        """
        customer_account_ids = Account.get_accounts_for_customer(customer).values("id")

        if not include_related_roles:
            return self.filter(account__in=customer_account_ids)
        return self.annotate(
            role_exists=Exists(AccountRole.objects.filter(entry=customer, account=OuterRef("account")))
        ).filter(Q(account__in=customer_account_ids) | Q(role_exists=True))

    def annotate_asset_under_management_for_date(self, val_date: date):
        return self.annotate(
            net_value=InstrumentPrice.subquery_closest_value("net_value", val_date, instrument_pk_name="product"),
            fx_rate=CurrencyFXRates.get_fx_rates_subquery(val_date),
            asset_under_management=models.ExpressionWrapper(
                models.F("net_value") * models.F("shares"),
                output_field=models.DecimalField(max_digits=16, decimal_places=4, default=0.0),
            ),
            asset_under_management_usd=models.ExpressionWrapper(
                models.F("asset_under_management") * models.F("fx_rate"),
                output_field=models.DecimalField(max_digits=16, decimal_places=4, default=0.0),
            ),
        )


class ClaimManager(models.Manager):
    def get_queryset(self) -> ClaimDefaultQueryset:
        return ClaimDefaultQueryset(self.model)

    def filter_for_user(self, user: User, validity_date: date_lib | None = None) -> QuerySet:
        return self.get_queryset().filter_for_user(user, validity_date=validity_date)

    def filter_for_customer(self, customer: Entry, include_related_roles: bool = False) -> QuerySet:
        return self.get_queryset().filter_for_customer(customer)

    def annotate_asset_under_management_for_date(self, val_date: date) -> QuerySet:
        return self.get_queryset().annotate_asset_under_management_for_date(val_date)


# @workflow.register(serializer_class="wbportfolio.serializers.transactions.claim.ClaimModelSerializer") #we don't register for now. Uncomment as soon as we want to enable workflow on that model
class Claim(ReferenceIDMixin, WBModel):
    """A customer can claim that a trade or part of a trade was executed my them"""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"
        DRAFT = "DRAFT", "Draft"
        AUTO_MATCHED = "AUTO_MATCHED", "Auto-Matched"

    status = FSMField(default=Status.DRAFT, choices=Status.choices, verbose_name="Status")
    account = models.ForeignKey(
        to="wbcrm.Account",
        related_name="claims",
        null=True,
        blank=True,
        limit_choices_to=models.Q(is_terminal_account=True),
        on_delete=models.SET_NULL,
        verbose_name="Account",
        # help_text="The account the claim is assigned to. If no sub-account is provided it will be tried to be assigned to a sub account based on the given claimant."
    )

    trade = models.ForeignKey(
        to="wbportfolio.Trade",
        related_name="claims",
        blank=True,
        null=True,
        on_delete=models.PROTECT,  # We protect the claim in case of trade deletion. This needs to be handled upstream
        verbose_name="Trade",
        help_text="Please select a Product first. The customer-trade the claim is consolidated against. The customer-trade and the claim don't necessarily have to have the same date, number of shares, etc.",
    )
    product = models.ForeignKey(
        to="wbportfolio.Product", related_name="claims", on_delete=models.PROTECT, verbose_name="Product"
    )
    claimant = models.ForeignKey(
        to="directory.Entry",
        related_name="claimed",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Claimant",
        # help_text="The person / company that claims this trade. If no claimant is given, it will assigned to the current user."
    )
    creator = models.ForeignKey(
        to="directory.Entry",
        related_name="claims_created",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Creator",
    )
    date = models.DateField(verbose_name="Trade Date")
    bank = models.CharField(max_length=255, blank=True, verbose_name="Bank")
    reference = models.CharField(max_length=255, null=True, blank=True, verbose_name="Additional Reference")
    shares = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        help_text="The amount of shares purchased / sold.",
        null=True,
        blank=True,
        verbose_name="Shares",
    )

    nominal_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="The nominal amount purchased / sold. Either shares or nominal_amount has to be provided.",
        null=True,
        blank=True,
        verbose_name="Nominal Amount",
    )
    external_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="An External ID to reference a claim.",
        verbose_name="External Identifier",
    )
    as_shares = models.BooleanField(default=True)

    objects = ClaimManager()

    class Meta:
        verbose_name = "Claim"
        verbose_name_plural = "Claims"

    def __str__(self):
        return f"{self.reference_id} {self.product.name} ({self.bank} - {self.shares:,} shares - {self.date}) "

    def save(self, *args, auto_match: bool = True, **kwargs):
        assert (
            self.shares is not None or self.nominal_amount is not None
        ), f"Either shares or nominal amount have to be provided. Shares={self.shares}, Nominal={self.nominal_amount}"
        if self.product:
            if self.shares is not None:
                self.nominal_amount = self.shares * self.product.share_price
            else:
                self.shares = self.nominal_amount / self.product.share_price
        if not self.trade and self.status == self.Status.DRAFT and auto_match:
            self.trade = self.auto_match()
        if self.status == self.Status.WITHDRAWN and self.trade:
            self.trade = None
        if self.trade:
            if not self.trade.is_claimable:
                raise ValueError("The selected trade is not a valid customer trade")
            if self.product and self.trade.underlying_instrument.id != self.product.id:
                raise ValueError("The selected product does not match the trade underlying instrument")
        super().save(*args, **kwargs)

    @classmethod
    def get_valid_and_approved_claims(cls, val_date: date_lib | None = None, account: Account | None = None):
        claims = cls.objects.annotate(
            date_considered=ExpressionWrapper(
                Greatest("trade__transaction_date", "date") + 1, output_field=DateField()
            )
        ).filter(Q(account__is_terminal_account=True) & Q(account__is_active=True) & Q(status=cls.Status.APPROVED))
        if val_date:
            claims = claims.filter(date_considered__lt=val_date)
        if account:
            claims = claims.filter(account__in=account.get_descendants(include_self=True))
        return claims

    @property
    def nominal_value(self):
        """Returns the nominal value of a claim

        Shares x Share Price

        Returns:
            Decimal -- Nominal Value
        """
        return self.shares * self.product.share_price

    @transition(
        status,
        [Status.PENDING, Status.AUTO_MATCHED],
        Status.APPROVED,
        permission=can_administrate_claim,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:claim",),
                icon=WBIcon.APPROVE.icon,
                color=ButtonDefaultColor.SUCCESS,
                key="approve",
                label="Approve",
                action_label="Approve",
                description_fields="<p>Date: {{date}}</p><p>Shares: {{shares}}</p><p>Product: {{_product.name}} ({{_product.isin}})</p>",
                instance_display=create_simple_display(
                    [
                        ["date", "shares", "bank"],
                        ["product", "claimant", "."],
                        ["account", "account", "account"],
                        ["trade", "trade", "trade"],
                    ]
                ),
            )
        },
    )
    def approve(self, **kwargs):
        pass

    def can_approve(self):
        errors = dict()

        if not self.trade:
            errors["trade"] = [_("With this status, this has to be provided.")]

        if not self.product:
            errors["product"] = [_("With this status, this has to be provided.")]

        if not self.account:
            errors["account"] = [_("With this status, this has to be provided.")]

        # check if the specified product have a valid nav at the specified date
        if (
            (product := self.product)
            and (claim_date := self.date)
            and not product.valuations.filter(date=claim_date).exists()
        ):
            if (prices_qs := product.valuations.filter(date__lt=claim_date)).exists():
                errors["date"] = [
                    f"For product {product.name}, the latest valid valuation date before {claim_date:%Y-%m-%d} is {prices_qs.latest('date').date:%Y-%m-%d}: Please select a valid date."
                ]
            else:
                errors["date"] = [
                    f"There is no valuation before {claim_date:%Y-%m-%d} for product {product.name}: Please select a valid date."
                ]
        return errors

    @transition(
        status,
        [Status.PENDING, Status.AUTO_MATCHED],
        Status.DRAFT,
        permission=lambda claim, user: user.profile.is_internal or user.is_superuser,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.ERROR,
                identifiers=("wbportfolio:claim",),
                icon=WBIcon.UNDO.icon,
                key="backtodraft",
                label="Back to Draft",
                action_label="Back to Draft",
                description_fields="<p>Date: {{date}}</p><p>Shares: {{shares}}</p>",
            )
        },
    )
    def backtodraft(self, **kwargs):
        pass

    @transition(
        status,
        [Status.DRAFT],
        Status.WITHDRAWN,
        permission=can_edit_claim,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:claim",),
                color=ButtonDefaultColor.ERROR,
                icon=WBIcon.DELETE.icon,
                key="withdraw",
                label="Withdraw",
                action_label="Withdraw",
                description_fields="<p>Date: {{date}}</p><p>Shares: {{shares}}</p>",
            )
        },
    )
    def withdraw(self, **kwargs):
        pass

    @transition(
        status,
        [Status.APPROVED],
        Status.DRAFT,
        permission=lambda claim, user: user.profile.is_internal or user.is_superuser,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:claim",),
                icon=WBIcon.EDIT.icon,
                color=ButtonDefaultColor.WARNING,
                key="revise",
                label="Revise",
                action_label="Revise",
                description_fields="<p>Date: {{date}}</p><p>Product: {{_product.name}}</p>",
            )
        },
    )
    def revise(self, **kwargs):
        pass

    @transition(
        status,
        [Status.DRAFT, Status.AUTO_MATCHED],
        Status.PENDING,
        permission=lambda claim, user: user.profile.is_internal or user.is_superuser,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:claim",),
                icon=WBIcon.SEND.icon,
                color=ButtonDefaultColor.WARNING,
                key="submit",
                label="Submit for approval",
                action_label="Submit",
                description_fields="<p>Date: {{date}}</p><p>Product: {{_product.name}}</p>",
            )
        },
    )
    def submit(self, **kwargs):
        pass

    def can_submit(self):
        return self.can_approve()

    def auto_match(self) -> Trade | None:
        SHARES_EPSILON = 1  # share
        auto_match_trade = None
        # Obvious filtering
        trades = Trade.valid_customer_trade_objects.filter(
            Q(transaction_date__gte=self.date - timedelta(days=Trade.TRADE_WINDOW_INTERVAL))
            & Q(transaction_date__lte=self.date + timedelta(days=Trade.TRADE_WINDOW_INTERVAL))
        )
        if self.product:
            trades = trades.filter(underlying_instrument=self.product)
        # Find trades by shares (or remaining to be claimed)
        trades = trades.filter(
            Q(diff_shares__lte=self.shares + SHARES_EPSILON) & Q(diff_shares__gte=self.shares - SHARES_EPSILON)
        )
        if trades.count() == 1:
            auto_match_trade = trades.first()

        # Find trades by custodian
        if (
            not auto_match_trade
            and self.bank
            and (custodian := Custodian.get_by_mapping(self.bank, use_similarity=True, create_missing=False))
        ):
            if trades.filter(custodian=custodian).exists():
                trades = trades.filter(custodian=custodian)
            if trades.count() == 1:
                auto_match_trade = trades.first()

        # Find trades by external_id
        if not auto_match_trade and self.external_id and trades.count() > 1:
            trades = trades.filter(
                Q(external_id__icontains=self.external_id) | Q(external_id_alternative__icontains=self.external_id)
            )
            if trades.count() == 1:
                auto_match_trade = trades.first()

        if auto_match_trade:
            self.status = self.Status.AUTO_MATCHED
            return auto_match_trade

    @classmethod
    def subquery_assets_under_management_for_account(cls, claims, price_date, account_key="account__pk"):
        """Returns a subquery which annotates the assets in USD for each Sub Account based on a given queryset

        Arguments:
            claims {QuerySet<commission.Claim>} -- Prefiltered queryset of claims
            price_date {datetime.date} -- the date which is used to calculate everything
            account_key {str} -- the outer reference to the sub account pk (default: account__pk)

        Returns:
            Subquery -- Sub Account with assets in USD
        """

        return models.Subquery(
            claims.filter(
                status=cls.Status.APPROVED,
                account__pk=models.OuterRef(account_key),
                trade__transaction_date__lte=price_date,
            )
            .annotate_asset_under_management_for_date(price_date)
            .values("account")
            .annotate(sum_assets_usd=models.Sum("assets_under_management_usd"))
            .values("sum_assets_usd")[:1],
            output_field=models.DecimalField(max_digits=16, decimal_places=4, default=0.0),
        )

    @classmethod
    def subquery_claim_sum_for_account(cls, claims, price_date, account_key="account__pk"):
        return models.Subquery(
            claims.filter(
                status=cls.Status.APPROVED,
                account__pk=models.OuterRef(account_key),
                trade__transaction_date__lte=price_date,
            )
            .values("account")
            .annotate(claim_sum=models.Sum("shares"))
            .values("claim_sum")[:1],
            output_field=models.DecimalField(max_digits=16, decimal_places=0, default=0.0),
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:claim"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:claimrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{shares}} ({{account}})"


@receiver(models.signals.post_save, sender="wbportfolio.Trade")
def post_save_trade(sender, instance, created, raw, **kwargs):
    """
    For every claimable trade, first try to autoclaim the already existing draft claims with this new trade. And auto claim them as well if the product has a default sub account
    """
    if not raw and instance.is_claimable and created:
        min_transaction_date = instance.transaction_date - timedelta(days=Trade.TRADE_WINDOW_INTERVAL)
        max_transaction_date = instance.transaction_date + timedelta(days=Trade.TRADE_WINDOW_INTERVAL)
        unlinked_claims = Claim.objects.filter(
            status=Claim.Status.DRAFT,
            date__gte=min_transaction_date,
            date__lte=max_transaction_date,
            trade__isnull=True,
            product__id=instance.underlying_instrument.id,
        )
        for claim in unlinked_claims.all():
            claim.trade = claim.auto_match()
            claim.save()
        if instance.product and (account := instance.product.default_account):
            shares = instance.shares or Decimal(0)
            claimed_shares = instance.claims.filter(status=Claim.Status.APPROVED).aggregate(s=models.Sum("shares"))[
                "s"
            ] or Decimal(0)
            rest_shares = shares - claimed_shares
            if rest_shares != 0:
                Claim.objects.create(
                    trade=instance,
                    shares=rest_shares,
                    bank=instance.bank,
                    date=instance.transaction_date,
                    product=instance.product,
                    account=account,
                    claimant=account.owner,
                )
            for claim in instance.claims.exclude(status=Claim.Status.APPROVED):
                if claim.status == Claim.Status.DRAFT:
                    claim.submit()
                if claim.status == Claim.Status.PENDING:
                    claim.approve()
                claim.save()


@receiver(pre_collection, sender="wbportfolio.Trade")
def pre_trade_deletion(sender, instance, **kwargs):
    # We can't use pre_delete signal here because the collector is collected before the signal and thus, it will
    for claim in instance.claims.filter(
        status__in=[Claim.Status.DRAFT, Claim.Status.AUTO_MATCHED, Claim.Status.WITHDRAWN]
    ).all():
        claim.trade = None
        claim.save(auto_match=False)

    if (instance.marked_for_deletion or instance.pending) and instance.claims.exists():
        # If a default account exists on the trade's product, it means that the product's trade are automatically claims. In that case, we are sure that a valid trade still exists and the marked for deletion's claim can be safely remove
        if instance.product and instance.product.default_account:
            instance.claims.all().delete()
        else:
            similar_trades = Trade.objects.filter(
                underlying_instrument=instance.underlying_instrument,
                portfolio=instance.portfolio,
                marked_for_deletion=True,
                transaction_date=instance.transaction_date,
            )
            # We check if the sum of marked for deletion trades share sums to 0, in that case, we delete them without regards and set their potential claims to draft
            if similar_trades.exists() and similar_trades.aggregate(s=Sum("shares"))["s"] == 0:
                for t in similar_trades.all():
                    t.claims.update(trade=None, status=Claim.Status.DRAFT)
            elif (other_unclaims_similar_trades := instance.get_alternative_valid_trades()).exists():
                if other_unclaims_similar_trades.count() > 1:
                    other_unclaims_similar_trades = other_unclaims_similar_trades.filter(bank=instance.bank)
                if other_trade := other_unclaims_similar_trades.first():
                    # If we find an unclaim trade with similar attributes, we forward the marked_for_deletion attribute to it, which will be handled/deleted in a next delete iteration
                    instance.claims.update(trade=other_trade)


@receiver(pre_merge, sender="wbcrm.Account")
def handle_pre_merge_account_for_claim(
    sender: models.Model, merged_object: "Account", main_object: "Account", **kwargs
):
    """
    Simply reassign the claim linked to the merged account to the main account
    """
    Claim.objects.filter(account=merged_object).update(account=main_object, reference=merged_object.reference_id)


@receiver(add_llm_prompt, sender="wbcrm.Account")
def add_holdings_to_account_heat(sender, instance, key, **kwargs):
    if key == "analyze_relationship":
        return get_performances_prompt(instance)
    return []
