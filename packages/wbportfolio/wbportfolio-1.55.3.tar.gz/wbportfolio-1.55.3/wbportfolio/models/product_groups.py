from decimal import Decimal

import pandas as pd
from django.db import models
from django.db.models import F, Q, Sum
from wbcore.models import WBModel
from wbfdm.models import InstrumentType
from wbfdm.models.instruments.instrument_prices import InstrumentPrice

from wbportfolio.models.products import FeeProductPercentage, Product

from .mixins.instruments import PMSInstrumentAbstractModel


class ProductGroup(PMSInstrumentAbstractModel):
    class ProductGroupType(models.TextChoices):
        FUND = "Fund"

    class ProductGroupCategory(models.TextChoices):
        UCITS = "UCITS", "UCITS"
        OTHER_FUNDS = "OTHER_FUNDS", "Other funds for traditional investments"

    type = models.CharField(
        max_length=64,
        verbose_name="Type",
        choices=ProductGroupType.choices,
        default=ProductGroupType.FUND,
    )
    category = models.CharField(
        max_length=64,
        choices=ProductGroupCategory.choices,
        default=ProductGroupCategory.UCITS,
    )

    umbrella = models.CharField(max_length=255, null=True, blank=True)
    management_company = models.ForeignKey(
        "directory.Company",
        related_name="management_company_product_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    depositary = models.ForeignKey(
        "directory.Company",
        related_name="depositary_product_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    transfer_agent = models.ForeignKey(
        "directory.Company",
        related_name="transfer_agent_product_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    administrator = models.ForeignKey(
        "directory.Company",
        related_name="administrator_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    investment_manager = models.ForeignKey(
        "directory.Company",
        related_name="investment_manager_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    auditor = models.ForeignKey(
        "directory.Company",
        related_name="auditor_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    paying_agent = models.ForeignKey(
        "directory.Company",
        related_name="paying_agent_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @property
    def products(self):  # for backward compatibility
        return Product.objects.filter(id__in=self.children.values("id"))

    def save(self, *args, **kwargs):
        self.instrument_type = InstrumentType.objects.get_or_create(
            key="product_group", defaults={"name": "Product Group", "short_name": "Product Group"}
        )[0]
        self.is_managed = True
        super().save(*args, **kwargs)

    def active_products(self, val_date):
        return self.products.filter(
            Q(inception_date__isnull=False)
            & Q(inception_date__lte=val_date)
            & (Q(delisted_date__isnull=True) | Q(delisted_date__gt=val_date))
        )

    def compute_str(self):
        return f"{self.name} ({self.umbrella})"

    class Meta:
        verbose_name = "Product Group"
        verbose_name_plural = "Product Groups"

    def get_fund_product_table(self, val_date):
        products = self.active_products(val_date).annotate(
            current_net_value=InstrumentPrice.subquery_closest_value("net_value", val_date, instrument_pk_name="pk"),
        )
        df = pd.DataFrame(
            products.values(
                "name",
                "isin",
                "ticker",
                "refinitiv_identifier_code",
                "currency__key",
                "currency__symbol",
                "dividend",
                "minimum_subscription",
                "inception_date",
                "current_net_value",
            )
        )

        if not df.empty:
            df["total_performance_fee"] = df["isin"].apply(
                lambda x: Product.objects.get(isin=x).get_fees_percent(
                    val_date, fee_type=FeeProductPercentage.Type.PERFORMANCE, net=False
                )
            )
            df["management_fees"] = df["isin"].apply(
                lambda x: Product.objects.get(isin=x).get_fees_percent(
                    val_date, fee_type=FeeProductPercentage.Type.MANAGEMENT
                )
            )
            df.management_fees = df.management_fees.apply(lambda x: f"{x:,.2%}" if x is not None else "")
            df.total_performance_fee = df.total_performance_fee.apply(lambda x: f"{x:,.2%}" if x is not None else "")
            df.current_net_value = df.current_net_value.apply(lambda x: f"{x:,.2f}" if x is not None else "")
            df.inception_date = df.inception_date.apply(lambda x: f"{x:%Y-%m-%d}" if x is not None else "")

            df = df[
                [
                    "name",
                    "isin",
                    "ticker",
                    "refinitiv_identifier_code",
                    "currency__key",
                    "currency__symbol",
                    "dividend",
                    "management_fees",
                    "total_performance_fee",
                    "minimum_subscription",
                    "current_net_value",
                    "inception_date",
                ]
            ]
            df = df.rename(
                columns={
                    "name": "share class",
                    "ticker": "bloomberg",
                    "currency__key": "currency",
                    "currency__symbol": "currency symbol",
                    "minimum_subscription": "min subscription",
                    "management_fees": "mgmt. fees",
                    "total_performance_fee": "perf. fees",
                    "inception_date": "launch date",
                    "refinitiv_identifier_code": "reuters",
                    "current_net_value": "price",
                }
            )

            return df

    def get_total_fund_aum(self, val_date=None):
        return Product.annotate_last_aum(
            Product.objects.filter(parent=self, is_invested=True), val_date=val_date
        ).aggregate(s=Sum(F("assets_under_management_usd")))["s"] or Decimal(0)

    def total_shares(self, val_date):
        return sum([product.total_shares(val_date) for product in self.products.all()])

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name_repr}}"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:product_grouprepresentation-list"


class ProductGroupRepresentant(WBModel):
    product_group = models.ForeignKey("ProductGroup", related_name="representants", on_delete=models.CASCADE)
    representant = models.ForeignKey("directory.Company", on_delete=models.PROTECT)
    country = models.ForeignKey(
        "geography.Geography", on_delete=models.PROTECT, limit_choices_to={"level": 1}, null=True, blank=True
    )

    def __str__(self):
        return f"{self.product_group.identifier} {self.representant.name} ({self.country.name})"

    class Meta:
        verbose_name = "Product Group Representant"
        verbose_name_plural = "Product Group Representants"
        constraints = [
            models.UniqueConstraint(fields=("product_group", "country"), name="unique_country_product_group")
        ]

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{representant}} {{country}}"

    @classmethod
    def get_representation_endpoint(cls):
        return None

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:product_group"
