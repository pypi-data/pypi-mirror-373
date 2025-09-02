import logging
from contextlib import suppress
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from django.db.models import (
    Case,
    CharField,
    Exists,
    ExpressionWrapper,
    F,
    FloatField,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
    Window,
)
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property
from pandas._libs.tslibs.offsets import BDay
from wbcore.contrib.currency.models import Currency, CurrencyFXRates
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.signals import pre_merge
from wbfdm.models import Classification, ClassificationGroup, Instrument
from wbfdm.models.instruments.instrument_prices import InstrumentPrice
from wbfdm.signals import add_instrument_to_investable_universe

from wbportfolio.import_export.handlers.asset_position import AssetPositionImportHandler
from wbportfolio.models.portfolio_relationship import (
    InstrumentPortfolioThroughModel,
    PortfolioInstrumentPreferredClassificationThroughModel,
)
from wbportfolio.models.roles import PortfolioRole
from wbportfolio.pms.typing import Position as PositionDTO

logger = logging.getLogger("pms")

MARKETCAP_S = 2_000_000_000
MARKETCAP_M = 10_000_000_000
MARKETCAP_L = 50_000_000_000
MARKETCAP_XL = 300_000_000_000
LIQUIDITY_SMALL = 3.0
LIQUIDITY_LARGE = 5.0

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24

if TYPE_CHECKING:
    pass


class AssetPositionDefaultQueryset(QuerySet):
    def annotate_classification_for_group(
        self, classification_group: ClassificationGroup, classification_height: int = 0, **kwargs
    ) -> QuerySet:
        return classification_group.annotate_queryset(self, classification_height, "underlying_instrument", **kwargs)

    def annotate_preferred_classification_for_group(
        self, classification_group: ClassificationGroup, classification_height: int = 0
    ) -> QuerySet:
        ref_title = f"classification__{'parent__' * classification_height}name"
        ref_code = f"classification__{'parent__' * classification_height}code_aggregated"

        base_qs = PortfolioInstrumentPreferredClassificationThroughModel.objects.filter(
            classification_group=classification_group,
            instrument=OuterRef("underlying_instrument"),
            instrument__tree_id=models.OuterRef("underlying_instrument__tree_id"),
            instrument__lft__lte=models.OuterRef("underlying_instrument__lft"),
            instrument__rght__gte=models.OuterRef("underlying_instrument__rght"),
            portfolio=models.OuterRef("portfolio"),
        )
        return self.annotate(
            classification_id=Subquery(base_qs.values(ref_code)[:1]),
            classification_title=Subquery(base_qs.values(ref_title)[:1]),
        )

    def annotate_hedged_currency_fx_rate(self, hedged_currency: Currency | None) -> QuerySet:
        return self.annotate(
            _is_hedged=Case(
                When(
                    underlying_instrument__currency__isnull=False,
                    underlying_instrument__currency=hedged_currency,
                    then=Value(True),
                ),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
            hedged_currency_fx_rate=Case(
                When(_is_hedged=True, then=Value(Decimal(1.0))),
                default=F("currency_fx_rate"),
                output_field=models.BooleanField(),
            ),
        )


class DefaultAssetPositionManager(models.Manager):
    def annotate_classification_for_group(
        self, classification_group, classification_height: int = 0, **kwargs
    ) -> QuerySet:
        return self.get_queryset().annotate_classification_for_group(
            classification_group, classification_height=classification_height, **kwargs
        )

    def annotate_preferred_classification_for_group(
        self, classification_group, classification_height: int = 0
    ) -> QuerySet:
        return self.get_queryset().annotate_preferred_classification_for_group(
            classification_group, classification_height=classification_height
        )

    def annotate_hedged_currency_fx_rate(self, hedged_currency: Currency | None) -> QuerySet:
        return self.get_queryset().annotate_hedged_currency_fx_rate(hedged_currency)

    def get_queryset(self) -> AssetPositionDefaultQueryset:
        return AssetPositionDefaultQueryset(self.model).annotate(
            adjusting_factor=Coalesce(
                F("applied_adjustment__cumulative_factor") * F("applied_adjustment__factor"), Decimal(1.0)
            ),
            shares=F("initial_shares") / F("adjusting_factor"),
            price=Coalesce(F("underlying_quote_price__net_value"), F("initial_price")),
            market_capitalization=ExpressionWrapper(
                Coalesce(
                    F("underlying_quote_price__market_capitalization_consolidated"),
                    F("underlying_quote_price__market_capitalization"),
                ),
                output_field=models.DecimalField(),
            ),
            beta=ExpressionWrapper(F("underlying_quote_price__beta"), output_field=models.DecimalField()),
            correlation=ExpressionWrapper(
                F("underlying_quote_price__correlation"), output_field=models.DecimalField()
            ),
            sharpe_ratio=ExpressionWrapper(
                F("underlying_quote_price__sharpe_ratio"), output_field=models.DecimalField()
            ),
            volume=Coalesce(
                ExpressionWrapper(F("underlying_quote_price__volume"), output_field=models.DecimalField()),
                Decimal(0),
            ),
            volume_50d=Coalesce(
                ExpressionWrapper(F("underlying_quote_price__volume_50d"), output_field=models.DecimalField()),
                Decimal(0),
            ),
            volume_200d=Coalesce(
                ExpressionWrapper(F("underlying_quote_price__volume_200d"), output_field=models.DecimalField()),
                Decimal(0),
            ),
            currency_fx_rate_instrument_to_usd_rate=Case(
                When(currency_fx_rate_instrument_to_usd__value=0, then=Value(Decimal(1.0))),
                default=1 / F("currency_fx_rate_instrument_to_usd__value"),
            ),
            currency_fx_rate_portfolio_to_usd_rate=F("currency_fx_rate_portfolio_to_usd__value"),
            currency_fx_rate=Coalesce(
                F("currency_fx_rate_portfolio_to_usd_rate") * F("currency_fx_rate_instrument_to_usd_rate"),
                F("initial_currency_fx_rate"),
            ),
            currency_symbol=F("currency__symbol"),
            portfolio_currency_symbol=F("portfolio__currency__symbol"),
            price_fx_usd=F("price") * F("currency_fx_rate_instrument_to_usd_rate"),
            price_fx_portfolio=F("price") * F("currency_fx_rate"),
            total_value=F("price") * F("shares"),
            total_value_fx_usd=F("price") * F("shares") * F("currency_fx_rate_instrument_to_usd_rate"),
            total_value_fx_portfolio=F("price") * F("shares") * F("currency_fx_rate"),
            market_share=Case(
                When(market_capitalization=0, then=Value(None)),
                default=F("total_value") / F("market_capitalization"),
            ),
            liquidity=Case(
                When(volume_50d=0, then=Value(None)),
                default=ExpressionWrapper(F("shares") / F("volume_50d") / 0.33, output_field=FloatField()),
            ),
            market_capitalization_usd=F("market_capitalization") * F("currency_fx_rate_instrument_to_usd_rate"),
            volume_usd=ExpressionWrapper(
                (F("price_fx_portfolio") * F("currency_fx_rate_instrument_to_usd_rate") * F("volume_50d")),
                output_field=FloatField(),
            ),
            is_invested=Case(
                When(
                    Q(portfolio__invested_timespan__startswith__lte=F("date"))
                    & Q(portfolio__invested_timespan__endswith__gt=F("date")),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
        )


class AnalyticalAssetPositionManager(DefaultAssetPositionManager):
    def get_queryset(self):
        qs_default = super().get_queryset()
        return qs_default.annotate(
            last_portfolio_date=Subquery(
                qs_default.filter(
                    portfolio=OuterRef("portfolio"),
                    date__lt=OuterRef("date"),
                )
                .order_by("-date")
                .values("date")[:1]
            ),
            previous_price_usd=Subquery(
                qs_default.filter(
                    date=OuterRef("last_portfolio_date"),
                    underlying_quote=OuterRef("underlying_quote"),
                    portfolio=OuterRef("portfolio"),
                )
                .order_by("-date")
                .values("price_fx_usd")[:1]
            ),
            performance=ExpressionWrapper(F("price_fx_usd") / F("previous_price_usd") - 1, output_field=FloatField()),
            contribution=ExpressionWrapper(F("performance") * F("weighting"), output_field=FloatField()),
            cumulative_contribution=Window(Sum("contribution"), order_by=F("date").asc()),
        )


class AssetPositionGroupBy(models.TextChoices):
    INDUSTRY = "classification", "Industry"
    INSTRUMENT_TYPE = "instrument_type", "Type"
    COUNTRY = "country", "Country"
    CURRENCY = "currency", "Currency"
    CASH = "is_cash", "Cash"


class AssetPosition(ImportMixin, models.Model):
    """
    The Asset Model holds all information needed to compute the value of the asset and contribution to its wbportfolio. All
    information which are regarded as Meta-Information, such as country, industry, currency allocation is held in the
    asset information, which is accessible through a FK, depending on the asset type of the asset.
    """

    import_export_handler_class = AssetPositionImportHandler
    is_estimated = models.BooleanField(
        default=False,
        verbose_name="Estimated Asset",
        help_text="True if the data is "
        "forward-estimated "
        "based on last day "
        "data. If the data is "
        "overridden by the "
        "importer or by the "
        "synchronization, "
        "this field becomes "
        "False.",
    )

    date = models.DateField(default=date.today)

    initial_price = models.DecimalField(max_digits=16, decimal_places=4, verbose_name="Initial Price")
    initial_currency_fx_rate = models.DecimalField(
        decimal_places=14,
        max_digits=28,
        verbose_name="Initial Currency FX Rate",
        help_text="The Currency Exchange Rate that is applied to the Asset to convert it into the Portfolio's currency.",
        default=Decimal(1),
    )
    initial_shares = models.DecimalField(
        decimal_places=4,
        max_digits=18,
        null=True,
        blank=True,
        verbose_name="Initial Quantity",
        help_text="The amount of Units of the Asset on the price date of the Asset.",
    )
    applied_adjustment = models.ForeignKey(
        "wbportfolio.Adjustment", on_delete=models.SET_NULL, blank=True, null=True, related_name="adjustmented_assets"
    )

    asset_valuation_date = models.DateField(
        verbose_name="Alternate Valuation Date",
        help_text="An alternate Valuation Date, if the price date of the Asset is different from the overlying Portfolio.",
    )

    exchange = models.ForeignKey(
        to="wbfdm.Exchange",
        null=True,
        blank=True,
        related_name="assets",
        on_delete=models.PROTECT,
        verbose_name="Exchange",
        help_text="The exchange where this asset is.",
    )

    ########################################################
    #                      VALUATION                       #
    ########################################################

    class PriceDenotation(models.TextChoices):
        PERCENT = "PERCENT", "%"
        CURRENCY = "CURRENCY", "Currency"

    price_denotation = models.CharField(
        max_length=16,
        choices=PriceDenotation.choices,
        default=PriceDenotation.CURRENCY,
        verbose_name="Price Denotation",
        help_text="The denotation of the price.",
    )

    # adjusting_factor = models.DecimalField(
    #     decimal_places=4,
    #     max_digits=16,
    #     default=Decimal(1),
    #     verbose_name="Share Multiplier",
    #     help_text="The Share Multiplier of an Asset.",
    # )

    weighting = models.DecimalField(
        decimal_places=8,
        max_digits=9,
        default=Decimal(0),
        verbose_name="Weight",
        help_text="The Weight of the Asset on the price date of the Asset.",
    )

    ########################################################
    #                      PORTFOLIO                       #
    ########################################################

    portfolio = models.ForeignKey(
        to="wbportfolio.Portfolio",
        related_name="assets",
        on_delete=models.CASCADE,
        verbose_name="Portfolio",
        help_text="The Portfolio the Asset belongs to.",
    )

    portfolio_created = models.ForeignKey(
        to="wbportfolio.Portfolio",
        null=True,
        blank=True,
        related_name="assets_created",
        on_delete=models.CASCADE,
        verbose_name="Portfolio Created",
        help_text="The Portfolio that created the Asset.",
    )

    ########################################################
    #                       CURRENCY                       #
    ########################################################

    currency = models.ForeignKey(
        to="currency.Currency",
        related_name="portfolio_currencies_asset",
        on_delete=models.PROTECT,
        verbose_name="Currency",
        help_text="The Currency of the Asset.",
    )

    currency_fx_rate_instrument_to_usd = models.ForeignKey(
        to="currency.CurrencyFXRates",
        related_name="instrument_assets",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Instrument Currency Rate",
        help_text="Rate to between instrument currency and USD",
    )
    currency_fx_rate_portfolio_to_usd = models.ForeignKey(
        to="currency.CurrencyFXRates",
        related_name="portfolio_assets",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Portfolio Currency Rate",
        help_text="Rate to between portfolio currency and USD",
    )
    ########################################################
    #                      Underlying                      #
    ########################################################

    underlying_instrument = models.ForeignKey(
        to="wbfdm.Instrument",
        related_name="instrument_assets",
        on_delete=models.PROTECT,
        verbose_name="Underlying Instrument",
        help_text="The instrument that is this asset.",
    )

    underlying_quote = models.ForeignKey(
        to="wbfdm.Instrument",
        related_name="assets",
        limit_choices_to=models.Q(children__isnull=True),
        on_delete=models.PROTECT,
        verbose_name="Underlying Quote",
        help_text="The quote that is this asset.",
    )

    underlying_quote_price = models.ForeignKey(
        to="wbfdm.InstrumentPrice",
        related_name="assets",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Underlying Instrument Price",
        help_text="The instrument price that is this asset.",
    )
    # objects = models.Manager()
    objects = DefaultAssetPositionManager()
    analytical_objects = AnalyticalAssetPositionManager()
    unannotated_objects = models.Manager()

    def pre_save(
        self, create_underlying_quote_price_if_missing: bool = False, infer_underlying_quote_price: bool = True
    ):
        if not self.asset_valuation_date:
            self.asset_valuation_date = self.date

        if (
            (not hasattr(self, "underlying_instrument") or not self.underlying_instrument)
            and hasattr(self, "underlying_quote")
            and self.underlying_quote
        ):
            self.underlying_instrument = (
                self.underlying_quote.parent if self.underlying_quote.parent else self.underlying_quote
            )
        elif (
            hasattr(self, "underlying_instrument")
            and self.underlying_instrument
            and (not hasattr(self, "underlying_quote") or not self.underlying_quote)
        ):
            try:
                self.underlying_quote = self.underlying_instrument.children.get(is_primary=True)
            except:
                self.underlying_quote = self.underlying_instrument

        if not getattr(self, "currency", None):
            self.currency = self.underlying_quote.currency
        if not self.underlying_quote_price and (infer_underlying_quote_price or not self.initial_price):
            try:
                # We get only the instrument price (and don't create it) because we don't want to create product instrument price on asset position propagation
                # Instead, we decided to opt for a post_save based system that will assign the missing position price when a price is created
                self.underlying_quote_price = InstrumentPrice.objects.get(
                    calculated=False, instrument=self.underlying_quote, date=self.asset_valuation_date
                )
            except InstrumentPrice.DoesNotExist:
                # if we create instrument price automatically, we need to ensure that the position is not estimated and not from a fake portfolio (e.g. JPM morgan root portfolio)
                if create_underlying_quote_price_if_missing and not self.is_estimated:
                    net_value = self.initial_price
                    # in case the position currency and the linked underlying_quote currency don't correspond, we convert the rate accordingly
                    if self.currency != self.underlying_quote.currency:
                        net_value *= self.currency.convert(self.asset_valuation_date, self.underlying_quote.currency)
                    self.underlying_quote_price = InstrumentPrice.objects.create(
                        calculated=False,
                        instrument=self.underlying_quote,
                        date=self.asset_valuation_date,
                        net_value=net_value,
                        import_source=self.import_source,  # we set the import source to know where this price is coming from
                    )
                    self.underlying_quote_price.fill_market_capitalization()
                    self.underlying_quote_price.save()
                else:  # sometime, the asset valuation date does not correspond to a valid market date. In that case, we get the latest valid instrument price for that product
                    self.underlying_quote_price = (
                        InstrumentPrice.objects.filter(
                            calculated=False,
                            instrument=self.underlying_quote,
                            date__lte=self.asset_valuation_date,
                        )
                        .order_by("date")
                        .last()
                    )

        if not self.currency_fx_rate_instrument_to_usd or (self.currency_fx_rate_instrument_to_usd.date != self.date):
            with suppress(CurrencyFXRates.DoesNotExist):
                self.currency_fx_rate_instrument_to_usd = CurrencyFXRates.objects.get(
                    date=self.date, currency=self.underlying_quote.currency
                )

        if not self.currency_fx_rate_portfolio_to_usd or (self.currency_fx_rate_portfolio_to_usd.date != self.date):
            with suppress(CurrencyFXRates.DoesNotExist):
                self.currency_fx_rate_portfolio_to_usd = CurrencyFXRates.objects.get(
                    date=self.date, currency=self.portfolio.currency
                )

        if not self.initial_price and self.underlying_quote_price:
            self.initial_price = self.underlying_quote_price.net_value
        if self.initial_currency_fx_rate is None:
            self.initial_currency_fx_rate = Decimal(1.0)
            if self.currency_fx_rate_portfolio_to_usd and self.currency_fx_rate_instrument_to_usd:
                try:
                    self.initial_currency_fx_rate = (
                        self.currency_fx_rate_portfolio_to_usd.value / self.currency_fx_rate_instrument_to_usd.value
                    )
                except InvalidOperation:
                    self.initial_currency_fx_rate = Decimal(0.0)

        # we set the initial shares from the previous position shares number if portfolio allows it
        if self.initial_shares is None and not self.portfolio.only_weighting:
            with suppress(AssetPosition.DoesNotExist):
                previous_pos = AssetPosition.objects.get(
                    date=(self.date - BDay(1)).date(),
                    underlying_quote=self.underlying_quote,
                    portfolio=self.portfolio,
                    portfolio_created=self.portfolio_created,
                )
                self.initial_shares = previous_pos.initial_shares
        if self.underlying_quote:
            self.exchange = self.underlying_quote.exchange

    def save(self, *args, create_underlying_quote_price_if_missing: bool = False, **kwargs):
        self.pre_save(create_underlying_quote_price_if_missing=create_underlying_quote_price_if_missing)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asset Position"
        verbose_name_plural = "Asset Positions"
        indexes = [
            models.Index(fields=["date", "underlying_instrument", "portfolio"]),
            models.Index(fields=["date", "underlying_instrument"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(date__week_day__in=[1, 7]),
                name="%(app_label)s_%(class)s_weekday_constraint",
            ),
            models.UniqueConstraint(
                fields=["portfolio", "date", "underlying_quote", "portfolio_created"],
                name="unique_asset_position",
                nulls_distinct=False,
            ),
        ]

    def __str__(self):
        return f"{self.initial_price} - {self.initial_shares} ({self.date}) ({str(self.underlying_quote)})"

    def set_weighting(self, new_weighting: Decimal):
        # Use this method to set the new weighting and ensure that the relative shares are updated accordingly
        self.weighting = new_weighting
        if self.initial_shares is not None:
            if self.weighting == 0 or self.initial_shares == 0:
                self.initial_shares = new_weighting * self.get_portfolio_total_asset_value()
            else:
                self.initial_shares = (new_weighting / self.weighting) * self.initial_shares

    def get_portfolio_total_asset_value(self) -> Decimal:
        return self.portfolio.get_total_asset_value(self.date)

    def _build_dto(self, **kwargs) -> PositionDTO:
        """
        Data Transfer Object
        Returns:
            DTO position object
        """
        parameters = dict(
            underlying_instrument=self.underlying_quote.id,
            weighting=self.weighting,
            shares=self._shares,
            date=self.date,
            asset_valuation_date=self.asset_valuation_date,
            instrument_type=self.underlying_quote.security_instrument_type.id,
            currency=self.underlying_quote.currency.id,
            country=self.underlying_quote.country.id if self.underlying_quote.country else None,
            is_cash=self.underlying_quote.is_cash or self.underlying_quote.is_cash_equivalent,
            primary_classification=(
                self.underlying_quote.primary_classification.id
                if self.underlying_quote.primary_classification
                else None
            ),
            favorite_classification=(
                self.underlying_quote.favorite_classification.id
                if self.underlying_quote.favorite_classification
                else None
            ),
            market_capitalization_usd=self._market_capitalization_usd,
            market_share=self._market_share,
            daily_liquidity=self._liquidity,
            volume_usd=self._volume_usd,
            price=self._price,
            currency_fx_rate=self._currency_fx_rate,
            portfolio_created=self.portfolio_created.id if self.portfolio_created else None,
        )
        parameters.update(kwargs)
        return PositionDTO(**parameters)

    @cached_property
    @admin.display(description="Adjusting Factor (adjustment)")
    def _adjusting_factor(self) -> Decimal:
        return (
            self.applied_adjustment.cumulative_factor * self.applied_adjustment.factor
            if self.applied_adjustment
            else Decimal(1.0)
        )

    @cached_property
    @admin.display(description="Price (Portfolio)")
    def _shares(self) -> Decimal:
        if self.initial_shares:
            return self.initial_shares / self._adjusting_factor
        return Decimal(0)

    @cached_property
    @admin.display(description="Market Capitalization")
    def _market_capitalization(self) -> float:
        return self.underlying_quote_price.market_capitalization_consolidated if self.underlying_quote_price else None

    @cached_property
    @admin.display(description="Volume 50d")
    def _volume_50d(self) -> float:
        return self.underlying_quote_price.volume_50d if self.underlying_quote_price else None

    @cached_property
    @admin.display(description="Price (Instrument)")
    def _price(self) -> Decimal:
        return self.underlying_quote_price.net_value if self.underlying_quote_price else self.initial_price

    @cached_property
    @admin.display(description="FX rate")
    def _currency_fx_rate(self) -> Decimal:
        return (
            self.currency_fx_rate_portfolio_to_usd.value / self.currency_fx_rate_instrument_to_usd.value
            if (self.currency_fx_rate_portfolio_to_usd and self.currency_fx_rate_instrument_to_usd)
            else self.initial_currency_fx_rate
        )

    @cached_property
    @admin.display(description="Price (Portfolio)")
    def _price_fx_portfolio(self) -> Decimal:
        return self._price * self._currency_fx_rate

    @cached_property
    @admin.display(description="Total Value (Instrument)")
    def _total_value(self) -> Decimal:
        if self._shares is not None:
            return self._price * self._shares
        return Decimal(0)

    @cached_property
    def fx_usd(self) -> Decimal:
        if self.currency_fx_rate_instrument_to_usd:
            return self.currency_fx_rate_instrument_to_usd.value
        return Decimal(1.0)

    @cached_property
    @admin.display(description="Total Value (USD)")
    def _total_value_fx_usd(self) -> Decimal:
        if self._shares is not None:
            return self._price * self._shares * self.fx_usd
        return Decimal(0)

    @cached_property
    @admin.display(description="Total Value (Portfolio)")
    def _total_value_fx_portfolio(self) -> Decimal:
        if self._shares is not None:
            return self._price * self._shares * self._currency_fx_rate
        return Decimal(0)

    @cached_property
    @admin.display(description="Market Share")
    def _market_share(self) -> Decimal:
        if self._total_value is not None and self._market_capitalization:
            return self._total_value / Decimal(self._market_capitalization)
        return Decimal(0)

    @cached_property
    @admin.display(description="Liquidity")
    def _liquidity(self) -> float:
        if self._total_value is not None and self._volume_50d:
            return float(self._shares) / self._volume_50d / 0.33
        return 0.0

    @cached_property
    @admin.display(description="Market Capitalization (USD)")
    def _market_capitalization_usd(self) -> float:
        if self._market_capitalization is not None:
            return self._market_capitalization * float(self.fx_usd)
        return 0.0

    @cached_property
    @admin.display(description="Volume (USD)")
    def _volume_usd(self) -> float:
        if self._price_fx_portfolio is not None and self._volume_50d is not None:
            return float(self._price_fx_portfolio) * float(self.fx_usd) * self._volume_50d
        return 0.0

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbportfolio:assetposition"

    @classmethod
    def currency_group_by(cls, qs, field_name: str | None = "key"):
        return (
            qs.filter(currency__isnull=False)
            .values("currency")
            .annotate(
                groupby_id=models.F("currency__id"),
                aggregated_title=models.F(f"currency__{field_name}"),
            )
        )

    @classmethod
    def country_group_by(cls, qs, field_name: str | None = "name"):
        return (
            qs.filter(underlying_instrument__country__isnull=False)
            .values("underlying_instrument__country")
            .annotate(
                groupby_id=models.F("underlying_instrument__country__id"),
                aggregated_title=models.F(f"underlying_instrument__country__{field_name}"),
            )
        )

    @classmethod
    def exchange_group_by(cls, qs, field_name: str | None = "name"):
        return qs.values("exchange").annotate(
            groupby_id=models.F("exchange"),
            aggregated_title=models.F(f"exchange__{field_name}"),
        )

    @classmethod
    def cash_group_by(cls, qs, **kwargs):
        return (
            qs.annotate(
                underlying_security_instrument_type_name_repr=Case(  # Annotate the parent security if exists
                    When(
                        underlying_instrument__isnull=False,
                        then=F("underlying_instrument__instrument_type__name_repr"),
                    ),
                    default=F("underlying_instrument__instrument_type__name_repr"),
                ),
                is_cash=Case(
                    When(
                        Q(underlying_instrument__is_cash=True) | Q(underlying_instrument__is_cash_equivalent=True),
                        then=Value("Cash"),
                    ),
                    default=F("underlying_security_instrument_type_name_repr"),
                    output_field=CharField(),
                ),
            )
            .values("is_cash")
            .annotate(groupby_id=models.F("is_cash"), aggregated_title=models.F("is_cash"))
        )

    @classmethod
    def equity_group_by(cls, qs, field_name: str | None = "name"):
        return (
            qs.filter(underlying_instrument__isnull=False)
            .values("underlying_instrument")
            .annotate(
                groupby_id=models.F("underlying_instrument__id"),
                aggregated_title=models.F(f"underlying_instrument__{field_name}"),
            )
        )

    @classmethod
    def marketcap_group_by(cls, qs, **kwargs):
        qs = qs.filter(market_capitalization_usd__isnull=False).annotate(
            mktcap_allocation=Case(
                When(market_capitalization_usd__isnull=True, then=Value("None")),
                When(market_capitalization_usd__gt=MARKETCAP_XL, then=Value("> 300B")),
                When(
                    market_capitalization_usd__gt=MARKETCAP_L,
                    then=Value("50B to 300B"),
                ),
                When(
                    market_capitalization_usd__gt=MARKETCAP_M,
                    then=Value("10B to 50B"),
                ),
                When(
                    market_capitalization_usd__gt=MARKETCAP_S,
                    then=Value("2B to 10B"),
                ),
                default=Value("< 2B"),
                output_field=CharField(),
            )
        )
        return qs.values("mktcap_allocation").annotate(
            groupby_id=F("mktcap_allocation"), aggregated_title=F("mktcap_allocation")
        )

    @classmethod
    def liquidity_group_by(cls, qs, **kwargs):
        qs = qs.annotate(
            liquidity_allocation=Case(
                When(liquidity__isnull=True, then=Value("None")),
                When(
                    liquidity__gt=LIQUIDITY_LARGE,
                    then=Value(f"More than {int(LIQUIDITY_LARGE)} days to liquidate"),
                ),
                When(
                    liquidity__lt=LIQUIDITY_SMALL,
                    then=Value(f"Less than {int(LIQUIDITY_SMALL)} days to liquidate"),
                ),
                default=Value(f"{int(LIQUIDITY_SMALL)} to {int(LIQUIDITY_LARGE)} days to liquidate"),
                output_field=CharField(),
            ),
        )
        return qs.values("liquidity_allocation").annotate(
            groupby_id=F("liquidity_allocation"), aggregated_title=F("liquidity_allocation")
        )

    @classmethod
    def group_by_primary(cls, qs: models.QuerySet, height: int = 0, **kwargs):
        qs = (
            qs.annotate_classification_for_group(
                ClassificationGroup.objects.get(is_primary=True), classification_height=height, unique=True
            )
            .annotate(
                classification_id=F("classifications"),
                classification_title=Subquery(
                    Classification.objects.filter(id=OuterRef("classifications")).values("name")[:1]
                ),
            )
            .filter(classification_id__isnull=False)
        )
        return qs.values("classification_id").annotate(
            groupby_id=F("classification_id"), aggregated_title=F("classification_title")
        )

    @classmethod
    def group_by_preferred_classification(cls, qs: models.QuerySet, height: int, **kwargs):
        qs = qs.annotate_preferred_classification_for_group(
            ClassificationGroup.objects.get(is_primary=True), classification_height=height
        )
        return qs.values("classification_id").annotate(
            id=F("classification_id"), aggregated_title=F("classification_title")
        )

    @classmethod
    def get_shown_positions(cls, person):
        from wbportfolio.models.portfolio import Portfolio

        today = date.today()
        if person.user_account.is_superuser:
            return AssetPosition.objects.all()
        else:
            portfolios = Portfolio.objects.annotate(
                nb_roles=Coalesce(
                    Subquery(
                        PortfolioRole.objects.filter(
                            (
                                (
                                    Q(person=person)
                                    & Q(
                                        role_type__in=[
                                            PortfolioRole.RoleType.MANAGER,
                                            PortfolioRole.RoleType.RISK_MANAGER,
                                        ]
                                    )
                                )
                                | (
                                    Q(person=person)
                                    & Q(
                                        role_type__in=[
                                            PortfolioRole.RoleType.PORTFOLIO_MANAGER,
                                            PortfolioRole.RoleType.ANALYST,
                                        ]
                                    )
                                    & (Q(instrument=OuterRef("instruments")) | Q(instrument__isnull=True))
                                )
                            )
                            & (Q(start__isnull=True) | Q(start__lte=today))
                            & (Q(end__isnull=True) | Q(end__gte=today))
                        )
                        .annotate(c=models.Count("*"))
                        .values("c")[:1]
                    ),
                    0,
                )
            ).filter(nb_roles__gt=0)
            return AssetPosition.objects.filter(portfolio__id__in=portfolios.values_list("id", flat=True))

    @classmethod
    def get_invested_instruments(cls, only_on_date: date, portfolio=None):
        product_portfolios = InstrumentPortfolioThroughModel.objects.filter(instrument__instrument_type__key="product")
        if portfolio:
            product_portfolios = product_portfolios.filter(portfolio=portfolio)
        asset_positions = AssetPosition.objects.filter(
            portfolio__in=product_portfolios.values("portfolio"), date=only_on_date
        )
        return (
            Instrument.annotated_objects.filter(is_investable_universe=True)
            .annotate(has_position=Exists(asset_positions.filter(underlying_quote=OuterRef("id"))))
            .filter(has_position=True)
        )


@receiver(post_save, sender="wbfdm.InstrumentPrice")
def post_instrument_price_creation(sender, instance, created, raw, **kwargs):
    if not raw and created and not instance.calculated:
        AssetPosition.objects.filter(
            Q(asset_valuation_date=instance.date)
            & Q(underlying_quote=instance.instrument)
            & (Q(underlying_quote_price__isnull=True) | ~Q(asset_valuation_date=F("underlying_quote_price__date")))
        ).update(underlying_quote_price=instance)


@receiver(pre_merge, sender="wbfdm.Instrument")
def pre_merge_instrument(sender: models.Model, merged_object: Instrument, main_object: Instrument, **kwargs):
    """
    Simply reassign the instrument price linked to the merged instrument to the main instrument if they don't already exist. Otherwise, delete them
    """
    merged_object.assets.annotate(
        new_price=InstrumentPrice.objects.filter(
            instrument=main_object, date=OuterRef("date"), calculated=False
        ).values("id")[:1]
    ).update(
        underlying_quote=main_object,
        underlying_instrument=main_object.parent if main_object.parent else main_object,
        underlying_quote_price=F("new_price"),
    )


@receiver(add_instrument_to_investable_universe, sender="wbfdm.Instrument")
def add_instrument_to_investable_universe(sender: models.Model, **kwargs) -> list[int]:
    """
    register all instrument linked to assets as within the investible universe
    """
    return list(
        (
            Instrument.objects.annotate(
                assets_exists=Exists(
                    AssetPosition.objects.filter(portfolio__is_tracked=True, underlying_quote=OuterRef("pk"))
                )
            ).filter(Q(assets_exists=True) | Q(portfolios__isnull=False))
        )
        .distinct()
        .values_list("id", flat=True)
    )
