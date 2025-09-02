from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Case, F, Q, When
from django.db.models.functions import Cast
from django.utils.translation import gettext_lazy as _
from wbcore.models import WBModel
from wbcrm.models import Account
from wbfdm.models.instruments import InstrumentPrice

from wbportfolio.models.transactions.claim import Claim

if TYPE_CHECKING:
    from wbportfolio.models import AccountReconciliation


class AccountReconciliationLineQuerySet(models.QuerySet):
    def update_or_create_for_reconciliation(self, reconciliation: "AccountReconciliation"):
        holding_per_product = (
            Claim.objects.filter(
                status=Claim.Status.APPROVED,
                account__in=reconciliation.account.get_descendants(include_self=True),
                account__status=Account.Status.OPEN,
                date__lte=reconciliation.reconciliation_date,
            )
            .values("product")
            .annotate(
                holdings=models.Sum("shares"),
                price=InstrumentPrice.subquery_closest_value(
                    "net_value", val_date=reconciliation.reconciliation_date, instrument_pk_name="product_id"
                ),
                price_date=InstrumentPrice.subquery_closest_value(
                    "date", val_date=reconciliation.reconciliation_date, instrument_pk_name="product_id"
                ),
            )
            .filter(~Q(holdings=0))
            .values("product_id", "holdings", "price", "price_date")
        )
        lines = []
        for holding in holding_per_product:
            line = AccountReconciliationLine(
                reconciliation=reconciliation,
                product_id=holding["product_id"],
                shares=holding["holdings"],
                shares_external=holding["holdings"],
                price=holding["price"],
                price_date=holding["price_date"],
            )
            line.calculate_fields()
            lines.append(line)

        return AccountReconciliationLine.objects.bulk_create(
            lines,
            update_conflicts=True,
            update_fields=["shares", "nominal_value", "price", "price_date"],
            unique_fields=["reconciliation", "product"],
        )

    def annotate_currency(self) -> "AccountReconciliationLineQuerySet":
        return self.annotate(currency=F("product__currency__symbol"))

    def annotate_currency_key(self) -> "AccountReconciliationLineQuerySet":
        return self.annotate(currency_key=F("product__currency__key"))

    def annotate_assets_under_management(self) -> "AccountReconciliationLineQuerySet":
        return self.annotate(assets_under_management=F("shares") * F("price"))

    def annotate_assets_under_management_external(self) -> "AccountReconciliationLineQuerySet":
        return self.annotate(assets_under_management_external=F("shares_external") * F("price"))

    def annotate_is_equal(self) -> "AccountReconciliationLineQuerySet":
        return self.annotate(
            is_equal=models.Case(
                models.When(shares=F("shares_external"), then=True), default=False, output_field=models.BooleanField()
            )
        )

    def annotate_shares_diff(self) -> "AccountReconciliationLineQuerySet":
        return self.annotate(shares_diff=F("shares_external") - F("shares"))

    def annotate_pct_diff(self) -> "AccountReconciliationLineQuerySet":
        ff = models.FloatField()
        return self.annotate(
            pct_diff=Case(
                When(~Q(shares=0), then=(Cast("shares_external", ff) - Cast("shares", ff)) / Cast("shares", ff)),
                default=None,
            )
        )

    def annotate_nominal_value_diff(self) -> "AccountReconciliationLineQuerySet":
        return self.annotate(nominal_value_diff=F("nominal_value_external") - F("nominal_value"))

    def annotate_assets_under_management_diff(self) -> "AccountReconciliationLineQuerySet":
        """Annotates the AuM diff. This will fail if annotate_assets_under_management was not called beforehand"""
        return self.annotate(
            assets_under_management_diff=F("assets_under_management_external") - F("assets_under_management")
        )


class AccountReconciliationLine(WBModel):
    reconciliation = models.ForeignKey(
        to="wbportfolio.AccountReconciliation",
        related_name="lines",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        to="wbportfolio.Product",
        related_name="account_reconciliation_lines",
        on_delete=models.CASCADE,
    )

    price = models.DecimalField(
        decimal_places=4,
        max_digits=18,
        default=Decimal(0),
        help_text=_("The last share price of the product"),
    )

    price_date = models.DateField()

    shares = models.DecimalField(
        decimal_places=4,
        max_digits=18,
        default=Decimal(0),
        help_text=_("The number of shares computed through the Workbench"),
    )
    nominal_value = models.DecimalField(
        decimal_places=4,
        max_digits=18,
        default=Decimal(0),
        help_text=_("The nominal value computed through the Workbench"),
    )
    shares_external = models.DecimalField(
        decimal_places=4,
        max_digits=18,
        default=Decimal(0),
        help_text=_(
            "The number of shares externally provided through the Account holder. Initially set to the number of shares computed through the Workbench"
        ),
    )
    nominal_value_external = models.DecimalField(
        decimal_places=4,
        max_digits=18,
        default=Decimal(0),
        help_text=_(
            "The nominal value externally provided through the Account holder. Initially set to the number of shares computed through the Workbench"
        ),
    )

    objects = AccountReconciliationLineQuerySet.as_manager()

    class Meta:
        verbose_name = _("Account Reconciliation (Product)")
        verbose_name_plural = _("Account Reconciliation (Products)")
        constraints = [
            models.UniqueConstraint(fields=["reconciliation", "product"], name="unique_reconcilation_product"),
        ]

    def save(self, *args, **kwargs):
        self.calculate_fields()
        super().save(*args, **kwargs)

    def calculate_fields(self):
        if self.shares is not None:
            self.nominal_value = self.shares * self.product.share_price
        elif self.nominal_value is not None:
            self.shares = self.nominal_value / self.product.share_price

        if self.shares_external is not None:
            self.nominal_value_external = self.shares_external * self.product.share_price
        elif self.nominal_value_external is not None:
            self.shares_external = self.nominal_value_external / self.product.share_price

    def __str__(self) -> str:
        return f"{self.reconciliation}: {self.product} {self.shares} shares"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:accountreconciliationline"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:accountreconciliationlinerepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{reconciliation}}"
