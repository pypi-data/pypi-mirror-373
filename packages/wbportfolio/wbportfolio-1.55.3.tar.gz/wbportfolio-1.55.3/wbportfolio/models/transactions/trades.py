from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.db import models
from django.db.models import (
    Case,
    DateField,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
    Subquery,
    Sum,
    When,
)
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.signals import pre_merge
from wbcore.signals.models import pre_collection
from wbfdm.models import Instrument
from wbfdm.models.instruments.instrument_prices import InstrumentPrice
from wbfdm.signals import add_instrument_to_investable_universe

from wbportfolio.import_export.handlers.trade import TradeImportHandler
from wbportfolio.models.custodians import Custodian

from .transactions import TransactionMixin


class ValidCustomerTradeManager(models.Manager):
    def __init__(self, without_internal_trade: bool = False):
        self.without_internal_trade = without_internal_trade
        super().__init__()

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(
                transaction_subtype__in=[Trade.Type.SUBSCRIPTION, Trade.Type.REDEMPTION],
                marked_for_deletion=False,
                pending=False,
            )
        )
        if self.without_internal_trade:
            qs = qs.exclude(marked_as_internal=True)
        return qs


class Trade(TransactionMixin, ImportMixin, models.Model):
    import_export_handler_class = TradeImportHandler

    TRADE_WINDOW_INTERVAL = 7

    class Type(models.TextChoices):
        REBALANCE = "REBALANCE", "Rebalance"
        DECREASE = "DECREASE", "Decrease"
        INCREASE = "INCREASE", "Increase"
        SUBSCRIPTION = "SUBSCRIPTION", "Subscription"
        REDEMPTION = "REDEMPTION", "Redemption"
        BUY = "BUY", "Buy"
        SELL = "SELL", "Sell"
        NO_CHANGE = "NO_CHANGE", "No Change"  # default transaction subtype if weighing is 0

    transaction_subtype = models.CharField(
        max_length=32, default=Type.BUY, choices=Type.choices, verbose_name="Trade Type"
    )
    transaction_date = models.DateField(
        verbose_name="Trade Date",
        help_text="The date that this transaction was traded.",
    )
    book_date = models.DateField(
        verbose_name="Trade Date",
        help_text="The date that this transaction was booked.",
    )
    shares = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal("0.0"),
        help_text="The number of shares that were traded.",
        verbose_name="Shares",
    )

    weighting = models.DecimalField(
        max_digits=9,
        decimal_places=8,
        default=Decimal(0),
        help_text="The weight to be multiplied against the target",
        verbose_name="Weight",
    )
    claimed_shares = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal(0),
        help_text="The number of shares that were claimed.",
        verbose_name="Claimed Shares",
    )
    diff_shares = models.GeneratedField(
        expression=F("shares") - F("claimed_shares"),
        output_field=models.DecimalField(max_digits=15, decimal_places=4),
        db_persist=True,
    )
    internal_trade = models.OneToOneField(
        "wbportfolio.Trade",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="internal_subscription_redemption_trade",
    )
    marked_for_deletion = models.BooleanField(
        default=False,
        help_text="If this is checked, then the trade is supposed to be deleted.",
        verbose_name="To be deleted",
    )
    marked_as_internal = models.BooleanField(
        default=False,
        help_text="If this is checked, then this subscription or redemption is considered internal and will not be considered in any AUM computation",
        verbose_name="Internal",
    )
    pending = models.BooleanField(default=False)
    exclude_from_history = models.BooleanField(default=False)
    bank = models.CharField(
        max_length=255,
        help_text="The bank/counterparty/custodian the trade went through.",
        verbose_name="Counterparty",
    )
    custodian = models.ForeignKey(
        "wbportfolio.Custodian", null=True, blank=True, on_delete=models.SET_NULL, related_name="trades"
    )
    register = models.ForeignKey(
        to="wbportfolio.Register",
        null=True,
        blank=True,
        related_name="trades",
        on_delete=models.PROTECT,
    )
    external_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="An external identifier that was supplied.",
        verbose_name="External Identifier",
    )
    external_id_alternative = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="A second external identifier that was supplied.",
        verbose_name="Alternative External Identifier",
    )

    # Manager
    objects = models.Manager()
    valid_customer_trade_objects = ValidCustomerTradeManager()
    valid_external_customer_trade_objects = ValidCustomerTradeManager(without_internal_trade=True)

    @property
    def product(self):
        from wbportfolio.models.products import Product

        try:
            return Product.objects.get(id=self.underlying_instrument.id)
        except Product.DoesNotExist:
            return None

    class Meta:
        verbose_name = "Trade"
        verbose_name_plural = "Trades"
        indexes = [
            models.Index(fields=["underlying_instrument", "transaction_date"]),
            models.Index(fields=["portfolio", "underlying_instrument", "transaction_date"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(marked_as_internal=False)
                | (
                    models.Q(marked_as_internal=True)
                    & models.Q(transaction_subtype__in=["REDEMPTION", "SUBSCRIPTION"])
                ),
                name="marked_as_internal_only_for_subred",
            ),
            models.CheckConstraint(
                check=models.Q(internal_trade__isnull=True)
                | (
                    models.Q(internal_trade__isnull=False)
                    & models.Q(transaction_subtype__in=["REDEMPTION", "SUBSCRIPTION"])
                ),
                name="internal_trade_set_only_for_subred",
            ),
        ]
        # notification_email_template = "portfolio/email/trade_notification.html"

    def save(self, *args, **kwargs):
        if abs(self.weighting) < 10e-6:
            self.weighting = Decimal("0")
        if not self.price:
            # we try to get the price if not provided directly from the underlying instrument
            self.price = self.get_price()

        if not self.custodian and self.bank:
            self.custodian = Custodian.get_by_mapping(self.bank)

        if self.transaction_subtype is None:
            # if subtype not provided, we extract it automatically from the existing data.
            self._set_type()
        if self.id and hasattr(self, "claims"):
            self.claimed_shares = self.claims.filter(status="APPROVED").aggregate(s=Sum("shares"))["s"] or Decimal(0)
        if self.internal_trade:
            self.marked_as_internal = True
        if not self.value_date:
            self.value_date = self.transaction_date
        if not self.book_date:
            self.book_date = self.transaction_date
        super().save(*args, **kwargs)

    def _set_type(self):
        if self.weighting == 0:
            self.transaction_subtype = Trade.Type.NO_CHANGE
        if self.underlying_instrument.instrument_type.key == "product":
            if self.shares is not None:
                if self.shares > 0:
                    self.transaction_subtype = Trade.Type.SUBSCRIPTION
                elif self.shares < 0:
                    self.transaction_subtype = Trade.Type.REDEMPTION
        elif self.weighting is not None:
            if self.weighting > 0:
                self.transaction_subtype = Trade.Type.INCREASE
            elif self.weighting < 0:
                self.transaction_subtype = Trade.Type.DECREASE
        else:
            self.transaction_subtype = Trade.Type.REBALANCE

    def get_price(self) -> Decimal:
        try:
            return self.underlying_instrument.get_price(self.transaction_date)
        except ValueError:
            return Decimal("0")

    def delete(self, **kwargs):
        pre_collection.send(sender=self.__class__, instance=self)
        super().delete(**kwargs)

    def __str__(self):
        ticker = f"{self.underlying_instrument.ticker}:" if self.underlying_instrument.ticker else ""
        return f"{ticker}{self.shares} ({self.bank})"

    def get_alternative_valid_trades(self, share_delta: float = 0):
        return Trade.objects.filter(
            Q(underlying_instrument=self.underlying_instrument)
            & Q(portfolio=self.portfolio)
            & (
                Q(transaction_date__gte=self.transaction_date - timedelta(days=self.TRADE_WINDOW_INTERVAL))
                & Q(transaction_date__lte=self.transaction_date + timedelta(days=self.TRADE_WINDOW_INTERVAL))
            )
            & Q(transaction_subtype=self.transaction_subtype)
            & Q(shares__gte=self.shares * Decimal(1 - share_delta))
            & Q(shares__lte=self.shares * Decimal(1 + share_delta))
            & Q(marked_for_deletion=False)
            & Q(claims__isnull=True)
            & Q(pending=False)
        ).exclude(id=self.id)

    @property
    def is_claimable(self) -> bool:
        return self.is_customer_trade and not self.marked_for_deletion and not self.pending

    @property
    def is_customer_trade(self) -> bool:
        return self.transaction_subtype in [Trade.Type.REDEMPTION.name, Trade.Type.SUBSCRIPTION.name]

    @classmethod
    def subquery_shares_per_underlying_instrument(
        cls, val_date, underlying_instrument_name="pk", only_customer_trade=True
    ):
        """Returns a Subquery that returns the shares at a certain price date
        or 0

        Arguments:
            val_date {datetime.date} -- The  date that is used to determine which tradesare filtered

        Keyword Arguments:
            underlying_instrument_name {str} -- The reference to the underlying_instrument pk of the outer query (default: {"pk"})

        Returns:
            django.db.models.Subquery -- Subquery containing the sum of shares of each underlying_instrument
        """

        qs = cls.valid_customer_trade_objects
        if not only_customer_trade:
            qs = cls.objects
        qs = qs.filter(
            underlying_instrument=OuterRef(underlying_instrument_name),
            transaction_date__lt=val_date,
        )
        return Coalesce(
            Subquery(
                qs.values("underlying_instrument").annotate(sum_shares=Sum("shares")).values("sum_shares")[:1],
                output_field=models.DecimalField(),
            ),
            Decimal(0),
        )

    def link_to_internal_trade(self):
        qs = Trade.objects.filter(
            Q(underlying_instrument__instrument_type__key="product")
            & Q(shares=self.shares)
            & Q(underlying_instrument=self.underlying_instrument)
            & Q(transaction_date__gte=self.transaction_date - timedelta(days=self.TRADE_WINDOW_INTERVAL))
            & Q(transaction_date__lte=self.transaction_date + timedelta(days=self.TRADE_WINDOW_INTERVAL))
        ).exclude(id=self.id)
        if self.transaction_subtype in [Trade.Type.REDEMPTION, Trade.Type.SUBSCRIPTION]:
            qs = qs.exclude(transaction_subtype__in=[Trade.Type.REDEMPTION, Trade.Type.SUBSCRIPTION])
            if qs.count() == 1:
                self.internal_trade = qs.first()
                self.save()
        else:
            qs = qs.filter(transaction_subtype__in=[Trade.Type.REDEMPTION, Trade.Type.SUBSCRIPTION])
            if qs.count() == 1:
                trade = qs.first()
                trade.internal_trade = self
                trade.save()

    @classmethod
    def subquery_net_money(
        cls, date_gte=None, date_lte=None, underlying_instrument_name="pk", only_positive=False, only_negative=False
    ):
        """Return a subquery which computes the net negative/positive money per underlying_instrument

        Arguments:
            val_date1 {datetime.date} -- The start date, including
            val_date2 {datetime.date} -- The end date, including

        Keyword Arguments:
            underlying_instrument_name {str} -- The reference to the underlying_instrument pk from the outer query (default: {"pk"})

        Returns:
            django.db.models.Subquery -- The subquery containing the net negative money per underlying_instrument
        """
        qs = cls.valid_external_customer_trade_objects.annotate(
            date_considered=ExpressionWrapper(F("transaction_date") + 1, output_field=DateField())
        )

        if date_gte:
            qs = qs.filter(date_considered__gte=date_gte)
        if date_lte:
            qs = qs.filter(date_considered__lte=date_lte)

        if only_positive:
            qs = qs.filter(shares__gt=0)
        elif only_negative:
            qs = qs.filter(shares__lt=0)
        return Coalesce(
            Subquery(
                qs.filter(underlying_instrument=OuterRef(underlying_instrument_name))
                .annotate(
                    _price=Case(
                        When(
                            price__isnull=True,
                            then=InstrumentPrice.subquery_closest_value(
                                "net_value",
                                date_name="date_considered",
                                instrument_pk_name="underlying_instrument__pk",
                            ),
                        ),
                        default=F("price"),
                    ),
                    net_value=ExpressionWrapper(F("shares") * F("_price"), output_field=models.FloatField()),
                )
                .values("underlying_instrument")
                .annotate(sum_net_value=Sum(F("net_value")))
                .values("sum_net_value"),
                output_field=models.FloatField(),
            ),
            0.0,
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:trade"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:traderepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{|:-}}{{transaction_date}}{{|::}}{{bank}}{{|-:}} {{claimed_shares}} / {{shares}} (∆ {{diff_shares}})"

    @classmethod
    def get_representation_value_key(cls):
        return "id"


@shared_task
def align_custodian():
    unaligned_qs = Trade.objects.annotate(
        proper_custodian_id=Subquery(Custodian.objects.filter(mapping__contains=OuterRef("bank")).values("id")[:1])
    ).exclude(custodian__id=F("proper_custodian_id"))

    unaligned_qs.update(custodian__id=F("proper_custodian_id"))


@receiver(post_save, sender="wbportfolio.Claim")
def compute_claimed_shares_on_claim_save(sender, instance, created, raw, **kwargs):
    if not raw and instance.trade:
        instance.trade.save()


@receiver(pre_merge, sender="wbfdm.Instrument")
def pre_merge_instrument(sender: models.Model, merged_object: "Instrument", main_object: "Instrument", **kwargs):
    """
    Simply reassign the transactions linked to the merged instrument to the main instrument
    """
    merged_object.trades.update(underlying_instrument=main_object)


@receiver(add_instrument_to_investable_universe, sender="wbfdm.Instrument")
def add_instrument_to_investable_universe_from_transactions(sender: models.Model, **kwargs) -> list[int]:
    """
    register all instrument linked to assets as within the investible universe
    """
    return list(
        (
            Instrument.objects.annotate(
                transaction_exists=models.Exists(Trade.objects.filter(underlying_instrument=models.OuterRef("pk")))
            ).filter(transaction_exists=True)
        )
        .distinct()
        .values_list("id", flat=True)
    )
