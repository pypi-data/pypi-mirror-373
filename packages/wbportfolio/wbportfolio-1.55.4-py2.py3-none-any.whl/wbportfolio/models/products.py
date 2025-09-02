from contextlib import suppress
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from celery import shared_task
from django.contrib import admin
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateRangeField, RangeOperators
from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    DecimalField,
    ExpressionWrapper,
    F,
    OuterRef,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.db.models.signals import pre_save
from django.dispatch import receiver
from pandas.tseries.offsets import BDay
from wbcore.contrib.ai.llm.config import add_llm_prompt
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.directory.models import Entry
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.permissions.shortcuts import get_internal_users
from wbcore.signals import pre_merge
from wbcore.utils.enum import ChoiceEnum
from wbcrm.models.accounts import Account
from wbfdm.models.instruments.instrument_prices import InstrumentPrice
from wbfdm.models.instruments.instruments import InstrumentManager, InstrumentType
from wbreport.models import Report

from wbportfolio.models.portfolio_relationship import InstrumentPortfolioThroughModel

from ..preferences import get_product_termination_notice_period
from . import PortfolioRole
from .llm.wbcrm.analyze_relationship import get_holding_prompt
from .mixins.instruments import PMSInstrument, PMSInstrumentAbstractModel


class TypeOfReturn(ChoiceEnum):
    TOTAL_RETURN = "Total return"
    YIELD = "Yield"
    PRICE_RETURN = "Price return"
    ABSOLUT_RETURN = "Absolut return"


class AssetClass(ChoiceEnum):
    EQUITY = "Equity"
    FIXED_INCOME = "Fixed income"
    PRIVATE_EQUITY = "Private equity"
    DERIVATIVE = "Derivative"
    CASH = "Cash"
    CRYPTOCURRENCY = "Cryptocurrency"
    COMMODITY = "Commodity"
    HEDGE_FUND = "Hedge Fund"
    MULTI_ASSET = "Multi Asset"


class LegalStructure(ChoiceEnum):
    AMC = "Actively Managed Certificate"
    SICAV_UCITS = "SICAV (UCITS)"
    PLC_UCITS = "PLC (UCITS)"
    SICAV_AIF = "SICAV (AIFs)"
    SCF_UCITS = "Swiss Contractual Fund (UCITS)"
    FCP_AIF = "FCP (AIFs)"
    PLC_AIF = "PLC (AIFs)"
    SCF_AIF = "Swiss Contractual Fund (AIF) "


class InvestmentIndex(ChoiceEnum):
    LONG = "Long"
    SHORT = "Short"
    LONG_SHORT = "Long/Short"


class Liquidy(ChoiceEnum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUATERLY = "Quaterly"
    YEARLY = "Yearly"


class DefaultProductManager(InstrumentManager):
    def get_queryset(self):
        today = date.today()
        return (
            super()
            .get_queryset()
            .annotate(
                value_date=Case(
                    When(last_valuation_date__isnull=False, then=F("last_valuation_date")),
                    default=Value(today),
                    output_field=models.DateField(),
                ),
                is_invested=models.Exists(
                    InstrumentPortfolioThroughModel.objects.filter(
                        instrument=models.OuterRef("pk"),
                        portfolio__invested_timespan__startswith__lte=OuterRef("value_date"),
                        portfolio__invested_timespan__endswith__gt=OuterRef("value_date"),
                    )
                ),
                current_bank_fees=Coalesce(
                    Subquery(
                        FeeProductPercentage.objects.filter(
                            product=OuterRef("pk"),
                            type=FeeProductPercentage.Type.BANK,
                            timespan__startswith__lte=OuterRef("value_date"),
                            timespan__endswith__gt=OuterRef("value_date"),
                        ).values("percent")[:1]
                    ),
                    Decimal(0),
                ),
                current_management_fees=Coalesce(
                    Subquery(
                        FeeProductPercentage.objects.filter(
                            product=OuterRef("pk"),
                            type=FeeProductPercentage.Type.MANAGEMENT,
                            timespan__startswith__lte=OuterRef("value_date"),
                            timespan__endswith__gt=OuterRef("value_date"),
                        ).values("percent")[:1]
                    ),
                    Decimal(0),
                ),
                current_performance_fees=Coalesce(
                    Subquery(
                        FeeProductPercentage.objects.filter(
                            product=OuterRef("pk"),
                            type=FeeProductPercentage.Type.PERFORMANCE,
                            timespan__startswith__lte=OuterRef("value_date"),
                            timespan__endswith__gt=OuterRef("value_date"),
                        ).values("percent")[:1]
                    ),
                    Decimal(0),
                ),
                current_performance_fees_vat_deduction=Coalesce(
                    Subquery(
                        FeeProductPercentage.objects.filter(
                            product=OuterRef("pk"),
                            type=FeeProductPercentage.Type.PERFORMANCE,
                            timespan__startswith__lte=OuterRef("value_date"),
                            timespan__endswith__gt=OuterRef("value_date"),
                        ).values("vat_deduction")[:1]
                    ),
                    Decimal(0),
                ),
                current_gross_performance_fees_percent=F("current_performance_fees")
                + F("current_performance_fees_vat_deduction"),
                current_total_issuer_fees=F("current_bank_fees") + F("current_management_fees"),
            )
        )


class FeeProductPercentage(models.Model):
    class Type(models.TextChoices):
        MANAGEMENT = "MANAGEMENT", "Management"
        PERFORMANCE = "PERFORMANCE", "Performance"
        BANK = "BANK", "Bank"

    product = models.ForeignKey("wbportfolio.Product", related_name="fees_percentages", on_delete=models.CASCADE)
    type = models.CharField(max_length=16, default=Type.MANAGEMENT, choices=Type.choices)
    vat_deduction = models.DecimalField(
        max_digits=6,
        decimal_places=6,
        default=Decimal(0),
        verbose_name="VAT Deduction",
        help_text="The VAT deducted from this fees percentage",
    )
    percent = models.DecimalField(max_digits=6, decimal_places=6)
    timespan = DateRangeField()

    class Meta:
        verbose_name = "Fees Percentage"
        verbose_name_plural = "Fees Percentage"
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_product_fees_type",
                expressions=[
                    ("timespan", RangeOperators.OVERLAPS),
                    ("product", RangeOperators.EQUAL),
                    ("type", RangeOperators.EQUAL),
                ],
            ),
        ]

    @property
    def net_percent(self) -> Decimal:
        return self.percent

    @property
    def gross_percent(self) -> Decimal:
        return self.percent + self.vat_deduction


class Product(PMSInstrumentAbstractModel):
    reports = GenericRelation(Report)

    share_price = models.PositiveIntegerField(
        default=100,
        verbose_name="Share Price",
        help_text="The initial share price that is used to calculate the nominal value of a product.",
    )
    initial_high_water_mark = models.PositiveIntegerField(
        default=100,
        verbose_name="Initial High Water Mark",
        help_text="Initial High Water Mark",
    )

    bank = models.ForeignKey(
        "directory.Company",
        related_name="issues_products",
        on_delete=models.PROTECT,
        verbose_name="Bank",
        help_text="The Bank that holds the product. A company from the CRM.",
    )

    white_label_customers = models.ManyToManyField(
        "directory.Entry",
        related_name="white_label_customer_products",
        blank=True,
        verbose_name="White Label Customers",
        help_text="Specifies whether a product is a white label product or not. If at least one customer is specified, this product becomes a white label product and can only be seen by the respected customers.",
    )

    default_account = models.ForeignKey(
        "wbcrm.Account",
        related_name="default_product_accounts",
        limit_choices_to=models.Q(is_terminal_account=True),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Default Account",
        help_text="If a default Account is set, then all newly created tradesare automatically matched to this sub account.",
    )

    fee_calculation = models.ForeignKey(
        "wbportfolio.FeeCalculation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
        verbose_name="Fee Calculation Method",
    )

    termsheet = models.FileField(max_length=256, null=True, blank=True, upload_to="portfolio/product/termsheets")

    class Dividend(models.TextChoices):
        CAPITALISATION = "CAPITALISATION", "Capitalisation"
        DISTRIBUTION = "DISTRIBUTION", "Distribution"

    type_of_return = models.CharField(
        max_length=16,
        default=TypeOfReturn.TOTAL_RETURN.name,
        choices=TypeOfReturn.choices(),
        verbose_name="Type of Return",
    )
    asset_class = models.CharField(
        max_length=16,
        default=AssetClass.EQUITY.name,
        choices=AssetClass.choices(),
        verbose_name="Asset Class",
    )
    legal_structure = models.CharField(
        max_length=16,
        default=LegalStructure.AMC.name,
        choices=LegalStructure.choices(),
        verbose_name="Legal Structure",
    )
    investment_index = models.CharField(
        max_length=16,
        default=InvestmentIndex.LONG.name,
        choices=InvestmentIndex.choices(),
        verbose_name="Long/Short Strategy",
    )
    liquidity = models.CharField(
        max_length=16,
        default=Liquidy.DAILY.name,
        choices=Liquidy.choices(),
        verbose_name="Liquidity",
    )

    jurisdiction = models.ForeignKey(
        "geography.Geography",
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Country on which this product is issued and bonded by law",
        help_text="The country of jurisdiction",
        limit_choices_to={"level": 1},
    )

    dividend = models.CharField(
        max_length=16,
        default=Dividend.CAPITALISATION,
        choices=Dividend.choices,
        verbose_name="Type of Dividends",
    )

    minimum_subscription = models.IntegerField(
        default=100,
        help_text="Minimum subscription amount allowed to invest in the fund",
    )

    cut_off_time = models.TimeField(default=time(13, 0, 0))
    external_webpage = models.URLField(blank=True, null=True)

    bank_account = models.ForeignKey(
        to="directory.BankingContact",
        related_name="wbportfolio_products",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    objects = DefaultProductManager()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        notification_types = [
            create_notification_type(
                "wbportfolio.product.termination_notice",
                "Product Termination Notice",
                "Sends a notification when a product is expected termination in the near future",
                True,
                True,
                True,
                is_lock=True,
            ),
        ]

    def pre_save(self):
        super().pre_save()
        self.instrument_type = InstrumentType.PRODUCT
        if "market_data" not in self.dl_parameters:
            # we default to the internal dataloader
            self.dl_parameters["market_data"] = {
                "path": "wbfdm.contrib.internal.dataloaders.market_data.MarketDataDataloader"
            }

        self.is_managed = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.delisted_date and self.delisted_date <= date.today():
            self.reports.update(is_active=False)

    def get_title(self):
        if self.parent:
            return f"{self.parent.name} ({self.name})"
        return self.name

    def compute_str(self):
        computed_str = f"{self.get_title()} - {self.bank.name} - {self.currency.key}"
        if self.id:
            fees = (self.bank_fees + self.management_fees) * 100
            computed_str += f" - {fees:.2f} % Mgmt Fees"
        computed_str += f" ({self.isin})"
        return computed_str

    def check_and_notify_product_termination_on_date(self, today: date) -> bool:
        """
        Checks if today is the expected notice date for product termination and sends notifications if applicable.

        The expected notice date is calculated by subtracting the product termination notice period from the product's delisted date. Notifications are sent to users associated with the product's portfolio roles.

        Args:
            today (date): The date to check against the expected notice date.

        Returns:
            bool: True if termination is due, False otherwise.
        """
        if self.delisted_date:
            product_termination_expected_notice_date = self.delisted_date - timedelta(
                days=get_product_termination_notice_period()
            )
            if today == product_termination_expected_notice_date:
                roles = PortfolioRole.objects.filter(
                    (models.Q(instrument=self) | models.Q(instrument__isnull=True))
                    & (models.Q(start__isnull=True) | models.Q(start__gte=today))
                    & (models.Q(end__isnull=True) | models.Q(end__lte=today))
                    & models.Q(person__user_account__isnull=False)
                )
                for user in get_internal_users().filter(is_active=True, id__in=roles.values("person__user_account")):
                    send_notification(
                        code="wbportfolio.product.termination_notice",
                        title="Product Termination Notice",
                        body=f"The product {self} will be terminated on the {self.delisted_date:%Y-%m-%d}",
                        user=user,
                    )
                return True
        return False

    @property
    def white_label_product(self):
        return self.white_label_customers.all().count() > 0

    @property
    def urlify_title(self):
        url = self.name + "-" + self.bank.name + "-" + self.isin + "-" + self.currency.key
        return url.lower()

    @property
    @admin.display(description="Invested")
    def _is_invested(self) -> bool:
        """
        Return True if the associated asset portfolio is invested
        """
        return getattr(self, "is_invested", self.portfolio and self.portfolio.is_invested_at_date(date.today()))

    @property
    def group(self):  # for backward compatibility
        from wbportfolio.models.product_groups import ProductGroup

        if self.parent:
            with suppress(ProductGroup.DoesNotExist):
                return ProductGroup.objects.get(id=self.parent.id)
        return None

    def get_fees_percent(self, val_date: date, fee_type: FeeProductPercentage.Type, net: bool = True) -> Decimal:
        try:
            fee = FeeProductPercentage.objects.get(
                product=self, type=fee_type, timespan__startswith__lte=val_date, timespan__endswith__gt=val_date
            )
            percent = fee.percent
            if not net:
                percent += fee.vat_deduction
            return percent
        except FeeProductPercentage.DoesNotExist:
            return Decimal(0)

    @property
    def bank_fees(self) -> Decimal:
        return self.get_fees_percent(date.today(), FeeProductPercentage.Type.BANK)

    @property
    def management_fees(self) -> Decimal:
        return self.get_fees_percent(date.today(), FeeProductPercentage.Type.MANAGEMENT)

    @property
    def performance_fees(self) -> Decimal:
        return self.get_fees_percent(date.today(), FeeProductPercentage.Type.PERFORMANCE)

    @property
    def gross_performance_fees(self) -> Decimal:
        return self.get_fees_percent(date.today(), FeeProductPercentage.Type.PERFORMANCE, net=False)

    def get_high_water_mark(self, val_date: date) -> Decimal:
        """Returns the high water mark of a instrument

        The high water mark is the highest previously reached net price

        Returns:
            decimal.Decimal -- High Water Mark
        """
        latest_high_water_mark = (
            self.valuations.filter(date__lt=val_date).aggregate(high_water_mark=models.Max(F("net_value")))[
                "high_water_mark"
            ]
            or self.share_price
        )
        return max(latest_high_water_mark, self.initial_high_water_mark)

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:product"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:productrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{computed_str}} ({{bank_name}})"

    @classmethod
    def get_last_valid_active_product_date(cls):
        current_date = (datetime.today() - BDay(1)).date()
        filter_date = current_date
        for product in Product.active_objects.all():
            if product.valuations.filter(date__lte=current_date).exists():
                last_valid_date = product.valuations.filter(date__lte=current_date).latest("date").date
                if last_valid_date < filter_date:
                    filter_date = last_valid_date
        return filter_date

    @classmethod
    def get_products(cls, person, base_qs: models.QuerySet | None = None):
        if base_qs is None:
            base_qs = cls.objects.all()
        if person.is_internal or person.user_account.is_superuser:
            return base_qs.all()
        return base_qs.filter(
            models.Q(white_label_customers__isnull=True)
            | models.Q(white_label_customers__in=[person, *person.employers.all()])
        ).distinct()

    @classmethod
    def subquery_is_white_label_product(cls, product_pk_name="pk"):
        return Coalesce(
            models.Subquery(
                Entry.objects.filter(white_label_customer_products__pk=models.OuterRef(product_pk_name))
                .values("white_label_customer_products")
                .annotate(
                    num_white_label_customers=models.Count("*"),
                    is_white_label_product=models.Case(
                        models.When(num_white_label_customers__gt=0, then=True),
                        output_field=models.BooleanField(),
                    ),
                )
                .values("is_white_label_product")[:1]
            ),
            False,
            output_field=models.BooleanField(),
        )

    @classmethod
    def annotate_last_aum(cls, qs, val_date=None, date_key="last_valuation_date"):
        if val_date:
            fx_rate_subquery = CurrencyFXRates.get_fx_rates_subquery(
                val_date, currency="currency", lookup_expr="exact"
            )
        else:
            fx_rate_subquery = CurrencyFXRates.get_fx_rates_subquery(
                date_key, currency="currency", lookup_expr="exact"
            )

        qs = InstrumentPrice.annotate_sum_shares(qs, val_date, date_key=date_key).annotate(
            net_value=Subquery(
                InstrumentPrice.objects.filter(
                    calculated=False, instrument=OuterRef("pk"), date=OuterRef("last_valuation_date")
                ).values("net_value")[:1]
            ),
            assets_under_management=Coalesce(F("sum_shares") * F("net_value"), Decimal(0)),
            fx_rate=Coalesce(
                fx_rate_subquery,
                Decimal(1.0),
            ),
            assets_under_management_usd=ExpressionWrapper(
                F("assets_under_management") * F("fx_rate"),
                output_field=DecimalField(),
            ),
            is_white_label=Case(
                When(white_label_customers__isnull=True, then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            ),
        )
        return qs.distinct()


@shared_task(queue="portfolio")
def update_outstanding_shares_as_task(instrument_id: int, clear: bool = False):
    instrument = PMSInstrument.objects.get(id=instrument_id)
    instrument.update_outstanding_shares(clear=clear)


@receiver(pre_merge, sender="wbcrm.Account")
def handle_pre_merge_account_for_product(sender: models.Model, merged_object: Account, main_object: Account, **kwargs):
    """
    Simply reassign the product's default account linked to the merged account to the main account
    """
    Product.objects.filter(default_account=merged_object).update(default_account=main_object)


@receiver(pre_save, sender="wbfdm.Instrument")
def pre_save_instrument(sender, instance, raw, **kwargs):
    if not raw and instance.id:
        # Remove duplicates if existings
        instance.old_isins = list(set(instance.old_isins))
        pre_instance = sender.objects.get(id=instance.id)
        if (
            pre_instance.isin
            and instance.isin
            and pre_instance.isin != instance.isin
            and pre_instance.isin not in instance.old_isins
        ):
            instance.old_isins = [*instance.old_isins, pre_instance.isin]
        if pre_instance.currency != instance.currency:
            # currency has changed we need to recompute currency_fx_rate
            instance.prices.annotate(
                new_currency_fx_rate_to_usd_id=models.Subquery(
                    CurrencyFXRates.objects.filter(currency=instance.currency, date=models.OuterRef("date")).values(
                        "id"
                    )[:1]
                )
            ).update(currency_fx_rate_to_usd=models.F("new_currency_fx_rate_to_usd_id"))
            instance.assets.annotate(
                new_currency_fx_rate_instrument_to_usd_id=models.Subquery(
                    CurrencyFXRates.objects.filter(currency=instance.currency, date=models.OuterRef("date")).values(
                        "id"
                    )[:1]
                )
            ).update(currency_fx_rate_instrument_to_usd=models.F("new_currency_fx_rate_instrument_to_usd_id"))


@receiver(add_llm_prompt, sender="wbcrm.Account")
def add_performance_to_account_heat(sender, instance, key, **kwargs):
    if key == "analyze_relationship":
        return get_holding_prompt(instance)
    return []
