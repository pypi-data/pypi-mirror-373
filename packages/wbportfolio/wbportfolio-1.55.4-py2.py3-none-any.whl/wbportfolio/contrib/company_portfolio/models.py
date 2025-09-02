from contextlib import suppress
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from dynamic_preferences.registries import global_preferences_registry
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.directory.models import Company, CustomerStatus
from wbcore.models import WBModel
from wbcore.utils.importlib import import_from_dotted_path

from wbportfolio.models import Claim, Product


def get_total_assets_under_management(val_date: date) -> Decimal:
    return sum([product.get_total_aum_usd(val_date) for product in Product.active_objects.all()])


def get_lost_client_customer_status():
    global_preferences = global_preferences_registry.manager()
    return global_preferences["wbportfolio__lost_client_customer_status"]


def get_returning_client_customer_status():
    global_preferences = global_preferences_registry.manager()
    return global_preferences["wbportfolio__returning_client_customer_status"]


def get_tpm_customer_status():
    global_preferences = global_preferences_registry.manager()
    return global_preferences["wbportfolio__tpm_customer_status"]


def get_client_customer_status():
    global_preferences = global_preferences_registry.manager()
    return global_preferences["wbportfolio__client_customer_status"]


class Updater:
    def __init__(self, val_date: date):
        self.val_date = val_date
        self.total_assets_under_management = get_total_assets_under_management(val_date)

    def update_company_data(self, company):
        # save company portfolio data
        company_portfolio_data = CompanyPortfolioData.objects.get_or_create(company=company)[0]
        if (
            invested_assets_under_management_usd := company_portfolio_data.get_assets_under_management_usd(
                self.val_date
            )
        ) is not None:
            company_portfolio_data.invested_assets_under_management_usd = invested_assets_under_management_usd
        if (potential := company_portfolio_data.get_potential(self.val_date)) is not None:
            company_portfolio_data.potential = potential
        company_portfolio_data.save()

        # update the company object itself
        if (tier := company_portfolio_data.get_tiering(self.total_assets_under_management)) is not None:
            company.tier = tier
        company.customer_status = company_portfolio_data.get_customer_status()
        company.save()

    # def update_all_companies(self, val_date: date):
    #     for company in tqdm(qs, total=qs.count()):
    #         with suppress(CompanyPortfolioData.DoesNotExist):
    #             company_portfolio = CompanyPortfolioData.objects.get(company=company)
    #             company_portfolio.update_data(date.today())


class CompanyPortfolioData(models.Model):
    class InvestmentDiscretion(models.TextChoices):
        FULLY_DISCRETIONAIRY = "FULLY_DISCRETIONAIRY", "Fully Discretionairy"
        MOSTLY_DISCRETIONAIRY = "MOSTLY_DISCRETIONAIRY", "Mostly Discretionairy"
        MIXED = "MIXED", "Mixed"
        MOSTLY_ADVISORY = "MOSTLY_ADVISORY", "Mostly Advisory"
        FULLY_ADVISORY = "FULLY_ADVISORY", "Fully Advisory"

    potential_help_text = """
        The potential reflects how much potential a company (regardless whether client/propective) has. The formula to calculate the potential is:

        AUM * Asset Allocation Percent * Asset Allocation Max Investment - Invested AUM.
    """

    company = models.OneToOneField(
        to="directory.Company", related_name="portfolio_data", on_delete=models.CASCADE, unique=True
    )

    assets_under_management_currency = models.ForeignKey(
        to="currency.Currency",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="AUM Currency",
    )

    assets_under_management = models.DecimalField(
        max_digits=17,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="AUM",
        help_text="The Assets under Management (AUM) that is managed by this company or this person's primary employer.",
    )
    invested_assets_under_management_usd = models.DecimalField(
        max_digits=17,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The invested Assets under Management (AUM).",
        verbose_name="Invested AUM ($)",
    )

    investment_discretion = models.CharField(
        max_length=21,
        choices=InvestmentDiscretion.choices,
        default=InvestmentDiscretion.MIXED,
        help_text="What discretion this company or this person's primary employer has to invest its assets.",
        verbose_name="Investment Discretion",
    )

    potential = models.DecimalField(
        decimal_places=2, max_digits=19, null=True, blank=True, help_text=potential_help_text
    )
    potential_currency = models.ForeignKey(
        to="currency.Currency",
        related_name="wbportfolio_potential_currencies",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    def get_assets_under_management_usd(self, val_date: date) -> Decimal:
        return Claim.objects.filter(status=Claim.Status.APPROVED).filter_for_customer(
            self.company
        ).annotate_asset_under_management_for_date(val_date).aggregate(
            invested_aum_usd=models.Sum("asset_under_management_usd")
        )["invested_aum_usd"] or Decimal(0)

    def _get_default_potential(self, val_date: date) -> Decimal:
        with suppress(CurrencyFXRates.DoesNotExist):
            fx = CurrencyFXRates.objects.get(currency=self.assets_under_management_currency, date=val_date).value

            aum_usd = self.assets_under_management / fx
            aum_potential = Decimal(0)
            for asset_allocation in self.company.asset_allocations.all():
                aum_potential += aum_usd * asset_allocation.percent * asset_allocation.max_investment
            invested_aum = self.invested_assets_under_management_usd or Decimal(0.0)

            return aum_potential - invested_aum

    def get_potential(self, val_date: date) -> Decimal:
        if module_path := getattr(settings, "PORTFOLIO_COMPANY_DATA_POTENTIAL_METHOD", None):
            with suppress(ModuleNotFoundError):
                return import_from_dotted_path(module_path)(self, val_date)
        return self._get_default_potential(val_date)

    def _get_default_tiering(self, total_asset_under_management: Decimal) -> Company.Tiering:
        if self.company.customer_status and self.company.customer_status in [
            get_client_customer_status(),
            get_tpm_customer_status(),
        ]:
            invested_aum = self.invested_assets_under_management_usd or Decimal(0)
            match invested_aum / total_asset_under_management:
                case share if share >= 0.1:  # noqa: F821
                    return Company.Tiering.ONE
                case share if share >= 0.05:  # noqa: F821
                    return Company.Tiering.TWO
                case share if share >= 0.02:  # noqa: F821
                    return Company.Tiering.THREE
                case share if share >= 0.01:  # noqa: F821
                    return Company.Tiering.FOUR
                case _:
                    return Company.Tiering.FIVE

        elif self.assets_under_management and self.assets_under_management_currency:
            fx = self.assets_under_management_currency.fx_rates.latest("date").value

            match self.assets_under_management / fx:
                case aum if aum >= 10_000_000_000:  # noqa: F821
                    return Company.Tiering.ONE
                case aum if aum >= 5_000_000_000:  # noqa: F821
                    return Company.Tiering.TWO
                case aum if aum >= 1_000_000_000:  # noqa: F821
                    return Company.Tiering.THREE
                case aum if aum >= 500_000_000:  # noqa: F821
                    return Company.Tiering.FOUR
                case _:
                    return Company.Tiering.FIVE

        return None

    def get_tiering(self, total_asset_under_management: Decimal) -> Decimal:
        if module_path := getattr(settings, "PORTFOLIO_COMPANY_DATA_TIERING_METHOD", None):
            with suppress(ModuleNotFoundError):
                return import_from_dotted_path(module_path)(self, total_asset_under_management)
        return self._get_default_tiering(total_asset_under_management)

    def get_customer_status(self) -> CustomerStatus:
        if aum := self.invested_assets_under_management_usd:
            if aum > 0 and self.company.customer_status == get_lost_client_customer_status():
                return get_returning_client_customer_status()

            if aum > 0 and self.company.customer_status not in [
                get_tpm_customer_status(),
                get_returning_client_customer_status(),
            ]:
                return get_client_customer_status()

        if (
            not self.invested_assets_under_management_usd
            and self.company.customer_status == get_client_customer_status()
        ):
            return get_lost_client_customer_status()

        return self.company.customer_status

    def __str__(self) -> str:
        return f"{self.company}"

    class Meta:
        verbose_name = "Company Portfolio Data"
        verbose_name_plural = "Company Portfolio Data"


@receiver(post_save, sender="directory.Company")
def create_company_portfolio_data(sender, instance, created, **kwargs):
    CompanyPortfolioData.objects.get_or_create(company=instance)


class AssetAllocationType(WBModel):
    name = models.CharField(max_length=255)
    default_max_investment = models.DecimalField(
        decimal_places=4,
        max_digits=5,
        default=0.1,
        help_text="The default percentage this allocation is counted towards the potential.",
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = "Asset Allocation Type"
        verbose_name_plural = "Asset Allocation Types"

    @classmethod
    def get_endpoint_basename(cls):
        return "company_portfolio:assetallocationtype"

    @classmethod
    def get_representation_endpoint(cls):
        return "company_portfolio:assetallocationtyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"


class AssetAllocation(models.Model):
    company = models.ForeignKey(to="directory.Company", related_name="asset_allocations", on_delete=models.CASCADE)
    asset_type = models.ForeignKey(
        to="company_portfolio.AssetAllocationType", related_name="asset_allocations", on_delete=models.PROTECT
    )
    percent = models.DecimalField(decimal_places=4, max_digits=5)
    max_investment = models.DecimalField(
        decimal_places=4,
        max_digits=5,
        null=True,
        blank=True,
        help_text="The percentage this allocation is counted towards the potential. Defaults to the default provided in the asset type.",
    )
    comment = models.TextField(default="")

    def save(self, *args, **kwargs):
        # If max investment is none, we are using the default one given by the asset_type
        if self.max_investment is None:
            self.max_investment = self.asset_type.default_max_investment

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.company}: {self.percent:.2%} {self.asset_type}"

    class Meta:
        verbose_name = "Asset Allocation"
        verbose_name_plural = "Asset Allocations"

    @classmethod
    def get_endpoint_basename(cls):
        return "company_portfolio:assetallocation"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{company}}: {{percent}} {{asset_type}}"


class GeographicFocus(models.Model):
    company = models.ForeignKey(to="directory.Company", related_name="geographic_focuses", on_delete=models.CASCADE)
    country = models.ForeignKey(to="geography.Geography", on_delete=models.PROTECT, verbose_name="Location")
    percent = models.DecimalField(decimal_places=4, max_digits=5)
    comment = models.TextField(default="")

    def __str__(self) -> str:
        return f"{self.company}: {self.percent:.2%} {self.country}"

    class Meta:
        verbose_name = "Geographic Focus"
        verbose_name_plural = "Geographic Focuses"

    @classmethod
    def get_endpoint_basename(cls):
        return "company_portfolio:geographicfocus"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{company}}: {{percent}} {{country}}"
