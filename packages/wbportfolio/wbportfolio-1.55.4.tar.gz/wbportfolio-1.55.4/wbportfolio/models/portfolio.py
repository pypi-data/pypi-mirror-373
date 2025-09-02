import logging
from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Generator, Iterable

import numpy as np
import pandas as pd
from celery import shared_task
from django.contrib.postgres.fields import DateRangeField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Exists, F, OuterRef, Q, QuerySet, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from pandas._libs.tslibs.offsets import BDay
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.models import WBModel
from wbcore.utils.importlib import import_from_dotted_path
from wbcore.utils.models import ActiveObjectManager, DeleteToDisableMixin
from wbfdm.models import Cash, Instrument, InstrumentType
from wbfdm.models.instruments.instrument_prices import InstrumentPrice
from wbfdm.signals import investable_universe_updated

from wbportfolio.models.asset import AssetPosition
from wbportfolio.models.builder import AssetPositionBuilder
from wbportfolio.models.indexes import Index
from wbportfolio.models.portfolio_relationship import (
    InstrumentPortfolioThroughModel,
    PortfolioInstrumentPreferredClassificationThroughModel,
)
from wbportfolio.models.products import Product
from wbportfolio.pms.analytics.portfolio import Portfolio as AnalyticPortfolio
from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.pms.typing import Position as PositionDTO

from ..constants import EQUITY_TYPE_KEYS
from ..order_routing.adapters import BaseCustodianAdapter
from . import ProductGroup

logger = logging.getLogger("pms")
if TYPE_CHECKING:
    pass

MARKET_HOLIDAY_MAX_DURATION = 15


class DefaultPortfolioQueryset(QuerySet):
    def filter_invested_at_date(self, val_date: date) -> QuerySet:
        """
        Filter the queryset to get only portfolio invested at the given date
        """
        return self.filter(
            (Q(invested_timespan__startswith__lte=val_date) | Q(invested_timespan__startswith__isnull=True))
            & (Q(invested_timespan__endswith__gt=val_date) | Q(invested_timespan__endswith__isnull=True))
        )

    def filter_active_and_tracked(self):
        return self.annotate(
            has_product=Exists(
                InstrumentPortfolioThroughModel.objects.filter(
                    instrument__instrument_type=InstrumentType.PRODUCT, portfolio=OuterRef("pk")
                )
            )
        ).filter((Q(has_product=True) | Q(is_manageable=True)) & Q(is_active=True) & Q(is_tracked=True))

    def to_dependency_iterator(self, val_date: date) -> Iterable["Portfolio"]:
        """
        A method to sort the given queryset to return undependable portfolio first. This is very useful if a routine needs to be applied sequentially on portfolios by order of dependence.
        """
        MAX_ITERATIONS: int = (
            5  # in order to avoid circular dependency and infinite loop, we need to stop recursion at a max depth
        )
        remaining_portfolios = set(self)

        def _iterator(p, iterator_counter=0):
            iterator_counter += 1
            parent_portfolios = remaining_portfolios & set(
                map(lambda o: o[0], p.get_parent_portfolios(val_date))
            )  # get composition parent portfolios
            dependency_relationships = PortfolioPortfolioThroughModel.objects.filter(
                portfolio=p, dependency_portfolio__in=remaining_portfolios
            )  # get dependency portfolios
            if iterator_counter >= MAX_ITERATIONS or (
                not dependency_relationships.exists() and not bool(parent_portfolios)
            ):  # if not dependency portfolio or parent portfolio that remained, then we yield
                remaining_portfolios.remove(p)
                yield p
            else:
                # otherwise, we iterate of the dependency portfolio first
                deps_portfolios = parent_portfolios.union(
                    set([r.dependency_portfolio for r in dependency_relationships])
                )
                for deps_p in deps_portfolios:
                    yield from _iterator(deps_p, iterator_counter=iterator_counter)

        while len(remaining_portfolios) > 0:
            portfolio = next(iter(remaining_portfolios))
            yield from _iterator(portfolio)


class DefaultPortfolioManager(ActiveObjectManager):
    def get_queryset(self):
        return DefaultPortfolioQueryset(self.model).filter(is_active=True)

    def filter_invested_at_date(self, val_date: date):
        return self.get_queryset().filter_invested_at_date(val_date)

    def filter_active_and_tracked(self):
        return self.get_queryset().filter_active_and_tracked()


class ActiveTrackedPortfolioManager(DefaultPortfolioManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(asset_exists=Exists(AssetPosition.unannotated_objects.filter(portfolio=OuterRef("pk"))))
            .filter(Q(asset_exists=True) & (Q(is_tracked=True) | Q(is_manageable=True)))
        )


class PortfolioPortfolioThroughModel(models.Model):
    class Type(models.TextChoices):
        PRIMARY = "PRIMARY", "Primary"
        MODEL = "MODEL", "Model"
        CUSTODIAN = "CUSTODIAN", "Custodian"

    portfolio = models.ForeignKey("wbportfolio.Portfolio", on_delete=models.CASCADE, related_name="dependency_through")
    dependency_portfolio = models.ForeignKey(
        "wbportfolio.Portfolio", on_delete=models.CASCADE, related_name="dependent_through"
    )
    type = models.CharField(choices=Type.choices, default=Type.PRIMARY, verbose_name="Type")

    def __str__(self):
        return f"{self.portfolio} dependant on {self.dependency_portfolio} ({self.Type[self.type].label})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["portfolio", "type"], name="unique_primary", condition=Q(type="PRIMARY")),
            models.UniqueConstraint(fields=["portfolio", "type"], name="unique_model", condition=Q(type="MODEL")),
        ]


class Portfolio(DeleteToDisableMixin, WBModel):
    assets: models.QuerySet[AssetPosition]
    builder: AssetPositionBuilder

    name = models.CharField(
        max_length=255,
        verbose_name="Name",
        default="",
        help_text="The Name of the Portfolio",
    )

    currency = models.ForeignKey(
        to="currency.Currency",
        related_name="portfolios",
        on_delete=models.PROTECT,
        verbose_name="Currency",
        help_text="The currency of the portfolio.",
    )
    hedged_currency = models.ForeignKey(
        to="currency.Currency",
        related_name="hedged_portfolios",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Hedged Currency",
        help_text="The hedged currency of the portfolio.",
    )
    depends_on = models.ManyToManyField(
        "wbportfolio.Portfolio",
        symmetrical=False,
        related_name="dependent_portfolios",
        through="wbportfolio.PortfolioPortfolioThroughModel",
        through_fields=("portfolio", "dependency_portfolio"),
        blank=True,
        verbose_name="The portfolios this portfolio depends on",
    )

    preferred_instrument_classifications = models.ManyToManyField(
        "wbfdm.Instrument",
        limit_choices_to=(models.Q(instrument_type__is_classifiable=True) & models.Q(level=0)),
        related_name="preferred_portfolio_classifications",
        through="wbportfolio.PortfolioInstrumentPreferredClassificationThroughModel",
        through_fields=("portfolio", "instrument"),
        blank=True,
        verbose_name="The Preferred classification per instrument",
    )
    instruments = models.ManyToManyField(
        "wbfdm.Instrument",
        through=InstrumentPortfolioThroughModel,
        related_name="portfolios",
        blank=True,
        verbose_name="Instruments",
        help_text="Instruments linked to this instrument",
    )
    invested_timespan = DateRangeField(
        null=True, blank=True, help_text="Define when this portfolio is considered invested"
    )

    is_manageable = models.BooleanField(
        default=False,
        help_text="True if the portfolio can be manually modified (e.g. Order Proposal be submitted or total weight recomputed)",
    )
    is_tracked = models.BooleanField(
        default=True,
        help_text="True if the internal updating mechanism (e.g., Next weights or Look-Through computation, rebalancing etc...) needs to apply to this portfolio",
    )
    only_weighting = models.BooleanField(
        default=False,
        help_text="Indicates that this portfolio is only utilizing weights and disregards shares, e.g. a model portfolio",
    )
    is_lookthrough = models.BooleanField(
        default=False,
        help_text="Indicates that this portfolio is a look-through portfolio",
    )
    is_composition = models.BooleanField(
        default=False, help_text="If true, this portfolio is a composition of other portfolio"
    )
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name="Updated At")
    last_position_date = models.DateField(blank=True, null=True, verbose_name="Last Position Date")
    initial_position_date = models.DateField(blank=True, null=True, verbose_name="Last Position Date")

    bank_accounts = models.ManyToManyField(
        to="directory.BankingContact",
        related_name="wbportfolio_portfolios",
        through="wbportfolio.PortfolioBankAccountThroughModel",
        blank=True,
    )

    objects = DefaultPortfolioManager()
    tracked_objects = ActiveTrackedPortfolioManager()

    def __init__(self, *args, **kwargs):
        self.builder = AssetPositionBuilder(self)
        super().__init__(*args, **kwargs)

    @property
    def primary_portfolio(self):
        with suppress(PortfolioPortfolioThroughModel.DoesNotExist):
            return PortfolioPortfolioThroughModel.objects.get(
                portfolio=self, type=PortfolioPortfolioThroughModel.Type.PRIMARY
            ).dependency_portfolio

    @property
    def model_portfolio(self):
        with suppress(PortfolioPortfolioThroughModel.DoesNotExist):
            return PortfolioPortfolioThroughModel.objects.get(
                portfolio=self, type=PortfolioPortfolioThroughModel.Type.MODEL
            ).dependency_portfolio

    @property
    def composition_portfolio(self):
        with suppress(PortfolioPortfolioThroughModel.DoesNotExist):
            return PortfolioPortfolioThroughModel.objects.get(
                portfolio=self,
                type=PortfolioPortfolioThroughModel.Type.MODEL,
                dependency_portfolio__is_composition=True,
            ).dependency_portfolio

    @property
    def is_model(self) -> bool:
        return PortfolioPortfolioThroughModel.objects.filter(
            type=PortfolioPortfolioThroughModel.Type.MODEL,
            dependency_portfolio=self,
        ).exists()

    @property
    def imported_assets(self):
        return self.assets.filter(is_estimated=False)

    @cached_property
    def pms_instruments(self):
        instruments = [i for i in Product.objects.filter(portfolios=self)]
        instruments.extend([i for i in ProductGroup.objects.filter(portfolios=self)])
        instruments.extend([i for i in Index.objects.filter(portfolios=self)])
        return instruments

    @property
    def cash_component(self) -> Cash:
        return Cash.objects.get_or_create(
            currency=self.currency, defaults={"is_cash": True, "name": self.currency.title}
        )[0]

    def get_authenticated_custodian_adapter(self, **kwargs) -> BaseCustodianAdapter | None:
        supported_instruments_for_routing = list(
            filter(lambda o: o.order_routing_custodian_adapter, self.pms_instruments)
        )
        if not supported_instruments_for_routing:
            raise ValueError("No custodian adapter for this portfolio")

        pms_instrument = supported_instruments_for_routing[
            0
        ]  # for simplicity we support only one instrument per portfolio that is allowed to support order routing
        adapter = import_from_dotted_path(pms_instrument.order_routing_custodian_adapter)(
            isin=pms_instrument.isin, identifier=pms_instrument.identifier, **kwargs
        )
        adapter.authenticate()
        if not adapter.is_valid():
            raise ValueError("This portfolio is not valid for rebalancing")
        return adapter

    @property
    def can_be_rebalanced(self):
        return self.is_manageable and not self.is_lookthrough

    def delete(self, **kwargs):
        super().delete(**kwargs)
        # We check if for all linked instruments, this portfolio was the last active one (if yes, we disable the instrument)
        if self.id:
            for instrument in self.instruments.iterator():
                if not instrument.portfolios.filter(is_active=True).exists():
                    instrument.delisted_date = date.today() - timedelta(days=1)
                    instrument.save()

    def _build_dto(self, val_date: date, **extra_kwargs) -> PortfolioDTO:
        "returns the dto representation of this portfolio at the specified date"
        assets = self.assets.filter(date=val_date, **extra_kwargs)
        try:
            last_returns, _ = self.get_analytic_portfolio(val_date, use_dl=True).get_contributions()
            last_returns = last_returns.to_dict()
        except ValueError:
            last_returns = {}
        positions = []
        for asset in assets:
            positions.append(asset._build_dto(daily_return=last_returns.get(asset.underlying_quote.id, Decimal("0"))))

        return PortfolioDTO(positions)

    def get_weights(self, val_date: date) -> dict[int, float]:
        """
        A convenience utility method to returns the portfolio weights for this portfolio as a dictionary (instrument id as key and weights as value)

        Args:
            val_date: The date at which to return the weights for this portfolio

        Returns:
            A dictionary containing the weights for this portfolio
        """
        return dict(
            map(
                lambda r: (r[0], float(r[1])),
                self.assets.filter(date=val_date)
                .values("underlying_quote")
                .annotate(sum_weight=Sum("weighting"))
                .values_list("underlying_quote", "sum_weight"),
            )
        )

    def get_analytic_portfolio(
        self, val_date: date, weights: dict[int, float] | None = None, use_dl: bool = True, **kwargs
    ) -> AnalyticPortfolio:
        """
        Return the analytic portfolio associated with this portfolio at the given date

        the analytic portfolio inherit from SKFolio Portfolio and can be used to access all this library methods
        Args:
            val_date: the date to calculate the portfolio for

        Returns:
            The instantiated analytic portfolio
        """
        if not weights:
            weights = self.get_weights(val_date)
        return_date = (val_date + BDay(1)).date()
        returns = self.load_builder_returns(val_date, return_date, use_dl=use_dl).copy()
        if pd.Timestamp(return_date) not in returns.index:
            raise ValueError()
        returns = returns.loc[:return_date, :]
        returns = returns.fillna(0)  # not sure this is what we want
        return AnalyticPortfolio(
            X=returns,
            weights=weights,
        )

    def is_invested_at_date(self, val_date: date) -> bool:
        return (
            self.invested_timespan
            and self.invested_timespan.upper > val_date
            and self.invested_timespan.lower <= val_date
        )

    def __str__(self):
        return f"{self.id:06}: {self.name}"

    class Meta:
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

        notification_types = [
            create_notification_type(
                "wbportfolio.portfolio.check_custodian_portfolio",
                "Check Custodian Portfolio",
                "Sends a notification when a portfolio does not match with its custodian portfolio",
                True,
                True,
                True,
            ),
            create_notification_type(
                "wbportfolio.portfolio.replay_done",
                "Portfolio Replay finished",
                "Sends a notification when a the requested order proposal replay is done",
                True,
                True,
                True,
            ),
        ]

    def is_active_at_date(self, val_date: date) -> bool:
        """
        Return if the base instrument has a total aum greater than 0
        :val_date: the date at which we need to evaluate if the portfolio is considered active
        """
        active_portfolio = self.is_active or self.deletion_datetime.date() > val_date
        if self.instruments.exists():
            return active_portfolio and any(
                [instrument.is_active_at_date(val_date) for instrument in self.instruments.all()]
            )
        return active_portfolio

    def get_total_asset_value(self, val_date: date) -> Decimal:
        """
        Return the total asset under management of the portfolio at the specified valuation date
        Args:
            val_date: The date at which aum needs to be computed
        Returns:
            The total AUM (0 if there is no position)
        """
        return self.assets.filter(date=val_date).aggregate(s=Sum("total_value_fx_portfolio"))["s"] or Decimal(0.0)

    def get_total_asset_under_management(self, val_date):
        from wbportfolio.models.transactions.trades import Trade

        trades = Trade.valid_customer_trade_objects.filter(portfolio=self, transaction_date__lte=val_date)

        total_aum = Decimal(0)
        for underlying_instrument_id, sum_shares in (
            trades.values("underlying_instrument")
            .annotate(
                sum_shares=Sum("shares"),
            )
            .values_list("underlying_instrument", "sum_shares")
        ):
            with suppress(Instrument.DoesNotExist, InstrumentPrice.DoesNotExist):
                instrument = Instrument.objects.get(id=underlying_instrument_id)
                last_price = instrument.valuations.filter(date__lte=val_date).latest("date").net_value
                fx_rate = instrument.currency.convert(val_date, self.currency)
                total_aum += last_price * sum_shares * fx_rate
        return total_aum

    def _get_assets(self, with_estimated=True, with_cash=True):
        qs = self.assets
        if not with_estimated:
            qs = qs.filter(is_estimated=False)
        if not with_cash:
            qs = qs.exclude(underlying_instrument__is_cash=True)
        return qs

    def get_earliest_asset_position_date(self, val_date=None, with_estimated=False):
        qs = self._get_assets(with_estimated=with_estimated)
        if val_date:
            qs = qs.filter(date__gte=val_date)
        if qs.exists():
            return qs.earliest("date").date
        return None

    def get_latest_asset_position_date(self, val_date=None, with_estimated=False):
        qs = self._get_assets(with_estimated=with_estimated)
        if val_date:
            qs = qs.filter(date__lte=val_date)

        if qs.exists():
            return qs.latest("date").date
        return None

    # Asset Position Utility Functions
    def get_holding(self, val_date, exclude_cash=True, exclude_index=True):
        qs = self._get_assets(with_cash=not exclude_cash).filter(date=val_date, weighting__gt=0)
        if exclude_index:
            qs = qs.exclude(underlying_instrument__instrument_type=InstrumentType.INDEX)
        return (
            qs.values("underlying_instrument__name")
            .annotate(total_value_fx_portfolio=Sum("total_value_fx_portfolio"), weighting=Sum("weighting"))
            .order_by("-total_value_fx_portfolio")
        )

    def _get_groupedby_df(
        self,
        group_by,
        val_date: date,
        exclude_cash: bool | None = False,
        exclude_index: bool | None = False,
        extra_filter_parameters: dict[str, Any] = None,
        **groupby_kwargs,
    ):
        qs = self._get_assets(with_cash=not exclude_cash).filter(date=val_date)
        if exclude_index:
            # We exclude only index that are not considered as cash. Setting exclude_cash to true convers this case.
            qs = qs.exclude(
                Q(underlying_instrument__instrument_type=InstrumentType.INDEX)
                & Q(underlying_instrument__is_cash=False)
            )
        if extra_filter_parameters:
            qs = qs.filter(**extra_filter_parameters)
        qs = group_by(qs, **groupby_kwargs).annotate(sum_weighting=Sum(F("weighting"))).order_by("-sum_weighting")
        df = pd.DataFrame(
            qs.values_list("aggregated_title", "sum_weighting"), columns=["aggregated_title", "weighting"]
        )
        if not df.empty:
            df.weighting = df.weighting.astype("float")
            df.weighting = df.weighting / df.weighting.sum()
            df = df.sort_values(by=["weighting"])
        return df.where(pd.notnull(df), None)

    def get_geographical_breakdown(self, val_date, **kwargs):
        df = self._get_groupedby_df(
            AssetPosition.country_group_by, val_date=val_date, exclude_cash=True, exclude_index=True, **kwargs
        )
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_currency_exposure(self, val_date, **kwargs):
        df = self._get_groupedby_df(AssetPosition.currency_group_by, val_date=val_date, **kwargs)
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_equity_market_cap_distribution(self, val_date, **kwargs):
        df = self._get_groupedby_df(
            AssetPosition.marketcap_group_by,
            val_date=val_date,
            exclude_cash=True,
            exclude_index=True,
            extra_filter_parameters={"underlying_instrument__instrument_type__key__in": EQUITY_TYPE_KEYS},
            **kwargs,
        )
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_equity_liquidity(self, val_date, **kwargs):
        df = self._get_groupedby_df(
            AssetPosition.liquidity_group_by,
            val_date=val_date,
            exclude_cash=True,
            exclude_index=True,
            extra_filter_parameters={"underlying_instrument__instrument_type__key__in": EQUITY_TYPE_KEYS},
            **kwargs,
        )
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_industry_exposure(self, val_date=None, **kwargs):
        df = self._get_groupedby_df(
            AssetPosition.group_by_primary, val_date=val_date, exclude_cash=True, exclude_index=True, **kwargs
        )
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_asset_allocation(self, val_date=None, **kwargs):
        df = self._get_groupedby_df(AssetPosition.cash_group_by, val_date=val_date, **kwargs)
        if not df.empty:
            df = df[df["weighting"] != 0]
        return df

    def get_adjusted_child_positions(self, val_date):
        if (
            child_positions := self.assets.exclude(underlying_instrument__is_cash=True).filter(date=val_date)
        ).count() == 1:
            if portfolio := child_positions.first().underlying_instrument.primary_portfolio:
                child_positions = portfolio.assets.exclude(underlying_instrument__is_cash=True).filter(date=val_date)
        for position in child_positions:
            if child_portfolio := position.underlying_instrument.primary_portfolio:
                index_positions = child_portfolio.assets.exclude(underlying_instrument__is_cash=True).filter(
                    date=val_date
                )

                for index_position in index_positions.all():
                    weighting = index_position.weighting * position.weighting
                    if weighting != 0:
                        yield {
                            "underlying_instrument_id": index_position.underlying_instrument.id,
                            "weighting": weighting,
                        }

    def get_longshort_distribution(self, val_date):
        df = pd.DataFrame(self.get_adjusted_child_positions(val_date))

        if not df.empty:
            df["is_cash"] = df.underlying_instrument_id.apply(lambda x: Instrument.objects.get(id=x).is_cash)
            df = df[~df["is_cash"]]
            df = (
                df[["underlying_instrument_id", "weighting"]].groupby("underlying_instrument_id").sum().astype("float")
            )
            df.weighting = df.weighting / df.weighting.sum()
            short_weight = df[df.weighting < 0].weighting.abs().sum()
            long_weight = df[df.weighting > 0].weighting.sum()
            total_weight = long_weight + short_weight
            return pd.DataFrame(
                [
                    {"title": "Long", "weighting": long_weight / total_weight},
                    {"title": "Short", "weighting": short_weight / total_weight},
                ]
            )
        return df

    def get_portfolio_contribution_df(
        self,
        start: date,
        end: date,
        with_cash: bool = True,
        hedged_currency: Currency | None = None,
        only_equity: bool = False,
    ) -> pd.DataFrame:
        qs = self._get_assets(with_cash=with_cash).filter(date__gte=start, date__lte=end)
        if only_equity:
            qs = qs.filter(underlying_instrument__instrument_type__key__in=EQUITY_TYPE_KEYS)
        qs = qs.annotate_hedged_currency_fx_rate(hedged_currency)
        df = Portfolio.get_contribution_df(
            qs.select_related("underlying_instrument").values_list(
                "date", "price", "hedged_currency_fx_rate", "underlying_instrument", "weighting"
            )
        )
        df = df.rename(columns={"group_key": "underlying_instrument"})
        df["underlying_instrument__name_repr"] = df["underlying_instrument"].map(
            dict(Instrument.objects.filter(id__in=df["underlying_instrument"]).values_list("id", "name_repr"))
        )
        return df

    def check_related_portfolio_at_date(self, val_date: date, related_portfolio: "Portfolio"):
        assets = AssetPosition.objects.filter(
            date=val_date, underlying_instrument__is_cash=False, underlying_instrument__is_cash_equivalent=False
        ).values("underlying_instrument", "shares")
        assets1 = assets.filter(portfolio=self)
        assets2 = assets.filter(portfolio=related_portfolio)
        return assets1.difference(assets2)

    def get_child_portfolios(self, val_date: date) -> set["Portfolio"]:
        child_portfolios = set()
        instrument_rel = InstrumentPortfolioThroughModel.objects.filter(portfolio=self)
        if instrument_rel.exists():
            for parent_portfolio in Portfolio.objects.filter(
                id__in=AssetPosition.unannotated_objects.filter(
                    date=val_date, underlying_quote__in=instrument_rel.values("instrument")
                ).values("portfolio")
            ):
                child_portfolios.add(parent_portfolio)
        return child_portfolios

    def get_parent_portfolios(self, val_date: date) -> set["Portfolio"]:
        for asset in self.assets.filter(date=val_date, underlying_instrument__portfolios__isnull=False).distinct(
            "underlying_instrument"
        ):
            if portfolio := asset.underlying_instrument.portfolio:
                yield portfolio, asset.weighting

    def get_next_rebalancing_date(self, start_date: date) -> date | None:
        if automatic_rebalancer := getattr(self, "automatic_rebalancer", None):
            return automatic_rebalancer.get_next_rebalancing_date(start_date)

    def fix_quantization(self, val_date: date):
        assets = self.assets.filter(date=val_date)
        total_weighting = assets.aggregate(s=Sum("weighting"))["s"]
        if total_weighting and (quantization_error := Decimal("1") - total_weighting):
            cash = self.cash_component
            try:
                cash_pos = assets.get(underlying_quote=cash)
                cash_pos.weighting += quantization_error
            except AssetPosition.DoesNotExist:
                cash_pos = AssetPosition(
                    portfolio=self,
                    underlying_quote=cash,
                    weighting=quantization_error,
                    initial_price=Decimal("1"),
                    date=val_date,
                    is_estimated=True,
                )
            cash_pos.save(create_underlying_quote_price_if_missing=True)

    def change_at_date(
        self,
        val_date: date,
        fix_quantization: bool = False,
        evaluate_rebalancer: bool = True,
        changed_portfolio: AnalyticPortfolio | None = None,
        broadcast_changes_at_date: bool = True,
        **kwargs,
    ):
        logger.info(f"change at date for {self} at {val_date}")

        if fix_quantization:
            # We assume all ptf total weight is 100% but quantization error can occur. In that case, we create a cash component and add the weight there.
            self.fix_quantization(val_date)

        # We check if there is an instrument attached to the portfolio with calculated NAV and price computation method
        self.estimate_net_asset_values(
            (val_date + BDay(1)).date(), analytic_portfolio=changed_portfolio
        )  # updating weighting in t0 influence nav in t+1
        if evaluate_rebalancer:
            self.evaluate_rebalancing(val_date)

        self.updated_at = timezone.now()
        if self.assets.filter(date=val_date).exists():
            if not self.last_position_date or self.last_position_date < val_date:
                self.last_position_date = val_date
            if not self.initial_position_date or self.initial_position_date > val_date:
                self.initial_position_date = val_date
        self.save()
        if broadcast_changes_at_date:
            self.handle_controlling_portfolio_change_at_date(
                val_date,
                fix_quantization=fix_quantization,
                changed_portfolio=changed_portfolio,
                **kwargs,
            )

    def handle_controlling_portfolio_change_at_date(self, val_date: date, **kwargs):
        if self.is_tracked:
            for rel in PortfolioPortfolioThroughModel.objects.filter(
                dependency_portfolio=self,
                type=PortfolioPortfolioThroughModel.Type.PRIMARY,
                portfolio__is_lookthrough=True,
            ):
                rel.portfolio.compute_lookthrough(val_date)
            for rel in PortfolioPortfolioThroughModel.objects.filter(
                dependency_portfolio=self, type=PortfolioPortfolioThroughModel.Type.MODEL
            ):
                rel.portfolio.evaluate_rebalancing(val_date)
            for dependent_portfolio in self.get_child_portfolios(val_date):
                # dependent_portfolio.change_at_date(val_date, **kwargs)
                dependent_portfolio.handle_controlling_portfolio_change_at_date(val_date, **kwargs)

    def get_model_portfolio_relationships(
        self, val_date: date
    ) -> Generator[PortfolioPortfolioThroughModel, None, None]:
        for rel in PortfolioPortfolioThroughModel.objects.filter(
            dependency_portfolio=self, type=PortfolioPortfolioThroughModel.Type.MODEL
        ):
            if rel.portfolio.is_active_at_date(val_date):
                yield rel
        for dependent_portfolio in self.get_child_portfolios(val_date):
            yield from dependent_portfolio.get_model_portfolio_relationships(val_date)

    def evaluate_rebalancing(self, val_date: date):
        if hasattr(self, "automatic_rebalancer"):
            # if the portfolio has an automatic rebalancer and the next business day is suitable with the rebalancer, we create a order proposal automatically
            next_business_date = (val_date + BDay(1)).date()
            if self.automatic_rebalancer.is_valid(val_date):  # we evaluate the rebalancer in t0 and t+1
                logger.info(f"Evaluate Rebalancing for {self} at {val_date}")
                self.automatic_rebalancer.evaluate_rebalancing(val_date)
            if self.automatic_rebalancer.is_valid(next_business_date):
                logger.info(f"Evaluate Rebalancing for {self} at {next_business_date}")
                self.automatic_rebalancer.evaluate_rebalancing(next_business_date)

    def estimate_net_asset_values(self, val_date: date, analytic_portfolio: AnalyticPortfolio | None = None):
        effective_portfolio_date = (val_date - BDay(1)).date()
        with suppress(ValueError):
            if not analytic_portfolio:
                analytic_portfolio = self.get_analytic_portfolio(effective_portfolio_date, use_dl=False)
            for instrument in self.pms_instruments:
                # we assume that in t-1 we will have a portfolio (with at least estimate position). If we use the latest position date before val_date, we run into the problem of being able to compute nav at every date
                last_price = instrument.get_latest_price(effective_portfolio_date)
                if (
                    instrument.is_active_at_date(val_date)
                    and (net_asset_value_computation_method_path := instrument.net_asset_value_computation_method_path)
                    and last_price
                ):
                    logger.info(f"Estimate NAV of {val_date:%Y-%m-%d} for instrument {instrument}")
                    net_asset_value_computation_method = import_from_dotted_path(
                        net_asset_value_computation_method_path
                    )
                    estimated_net_asset_value = net_asset_value_computation_method(last_price, analytic_portfolio)
                    if estimated_net_asset_value is not None:
                        InstrumentPrice.objects.update_or_create(
                            instrument=instrument,
                            date=val_date,
                            calculated=True,
                            defaults={
                                "gross_value": estimated_net_asset_value,
                                "net_value": estimated_net_asset_value,
                            },
                        )
                        if (
                            val_date == instrument.last_price_date
                        ):  # if price date is the latest instrument price date, we recompute the last valuation data
                            instrument.update_last_valuation_date()

    def drift_weights(
        self, start_date: date, end_date: date, stop_at_rebalancing: bool = False
    ) -> Generator[tuple[date, dict[int, float]], None, models.Model]:
        logger.info(f"drift weights for {self} from {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}")

        rebalancer = getattr(self, "automatic_rebalancer", None)
        # Get initial weights
        weights = self.get_weights(start_date)  # initial weights
        if not weights:
            previous_date = self.assets.filter(date__lte=start_date).latest("date").date
            _, weights = next(self.drift_weights(previous_date, start_date))
        last_order_proposal = None
        for to_date_ts in pd.date_range(start_date + timedelta(days=1), end_date, freq="B"):
            to_date = to_date_ts.date()
            to_is_active = self.is_active_at_date(to_date)
            logger.info(f"Processing {to_date:%Y-%m-%d}")
            order_proposal = None
            try:
                last_returns = self.builder.returns.loc[[to_date_ts], :]
                analytic_portfolio = AnalyticPortfolio(weights=weights, X=last_returns)
                drifted_weights = analytic_portfolio.get_next_weights()
            except KeyError:  # if no return for that date, we break and continue
                break
            try:
                order_proposal = self.order_proposals.get(
                    trade_date=to_date, rebalancing_model__isnull=True, status="APPLIED"
                )
            except ObjectDoesNotExist:
                if rebalancer and rebalancer.is_valid(to_date):
                    rebalancer.portfolio = self  # ensure reference is the same to access cached returns
                    effective_portfolio = PortfolioDTO(
                        positions=[
                            PositionDTO(
                                date=to_date,
                                underlying_instrument=i,
                                weighting=Decimal(w),
                                daily_return=Decimal(last_returns.iloc[-1][i]),
                            )
                            for i, w in weights.items()
                        ]
                    )
                    order_proposal = rebalancer.evaluate_rebalancing(to_date, effective_portfolio=effective_portfolio)
            if order_proposal:
                last_order_proposal = order_proposal
                if stop_at_rebalancing:
                    break
                next_weights = {
                    trade.underlying_instrument.id: float(trade._target_weight)
                    for trade in order_proposal.get_orders()
                }
                yield to_date, next_weights
            else:
                next_weights = drifted_weights
                if to_is_active:
                    yield to_date, next_weights
                else:
                    yield (
                        to_date,
                        {underlying_quote_id: 0.0 for underlying_quote_id in weights.keys()},
                    )  # if we have no return or portfolio is not active anymore, we return an emptied portfolio
                    break
            weights = next_weights
        return last_order_proposal

    def propagate_or_update_assets(self, from_date: date, to_date: date):
        """
        Create a new portfolio at `to_date` based on the portfolio in `from_date`.

        Args:
            from_date: The date to propagate the portfolio from
            to_date:  The date to create the new portfolio at

        """
        # we don't propagate on already imported portfolio by default
        is_target_portfolio_imported = self.assets.filter(date=to_date, is_estimated=False).exists()
        if (
            not self.is_lookthrough and not is_target_portfolio_imported and self.is_active_at_date(from_date)
        ):  # we cannot propagate a new portfolio for untracked, or look-through or already imported or inactive portfolios
            self.load_builder_returns(from_date, to_date)
            for pos_date, weights in self.drift_weights(from_date, to_date):
                self.builder.add((pos_date, weights))
            self.builder.bulk_create_positions(delete_leftovers=True)
            self.builder.schedule_change_at_dates()
            self.builder.schedule_metric_computation()

    def load_builder_returns(self, from_date: date, to_date: date, use_dl: bool = True) -> pd.DataFrame:
        instruments_ids = list(self.get_weights(from_date).keys())
        for tp in self.order_proposals.filter(trade_date__gte=from_date, trade_date__lte=to_date):
            instruments_ids.extend(tp.orders.values_list("underlying_instrument", flat=True))
        self.builder.load_returns(
            set(instruments_ids), (from_date - BDay(1)).date(), (to_date + BDay(1)).date(), use_dl=use_dl
        )
        return self.builder.returns

    def get_lookthrough_positions(
        self,
        sync_date: date,
        portfolio_total_asset_value: Decimal | None = None,
        with_intermediary_position: bool = False,
    ):
        """Recursively calculates the look-through position for a portfolio

        Arguments:
            sync_date {datetime.date} -- The date on which the assets will be computed
            portfolio_total_value: {Decimal} -- The total value of the portfolio (needed to compute initial shares)
        """

        def _crawl_portfolio(
            parent_portfolio,
            adjusted_weighting,
            adjusted_currency_fx_rate,
            adjusted_is_estimated,
            path=None,
        ):
            if not path:
                path = []
            path.append(parent_portfolio)
            for position in parent_portfolio.assets.filter(date=sync_date):
                position.id = None
                position.weighting = adjusted_weighting * position.weighting
                position.initial_currency_fx_rate = adjusted_currency_fx_rate * position.currency_fx_rate
                position.is_estimated = (adjusted_is_estimated or position.is_estimated) and not (
                    position.weighting == 1.0
                )
                # to get from which portfolio this position is created, we need to differantiate between:
                # * Composition portfolio: where the portfolio created is the second encountered portfolio
                # * Other: portfolio created is the last encountered portfolio
                # If `path` is empty, we use None as portfolio_created
                try:
                    if self.is_composition:
                        position.portfolio_created = path[1]
                    else:
                        position.portfolio_created = path[-1]
                except IndexError:
                    position.portfolio_created = None

                setattr(position, "path", path)
                position.initial_shares = None
                if portfolio_total_asset_value and (price_fx_portfolio := position.price * position.currency_fx_rate):
                    position.initial_shares = (position.weighting * portfolio_total_asset_value) / price_fx_portfolio
                if child_portfolio := position.underlying_quote.primary_portfolio:
                    if with_intermediary_position:
                        yield position
                    yield from _crawl_portfolio(
                        child_portfolio,
                        position.weighting,
                        position.currency_fx_rate,
                        position.is_estimated,
                        path=path.copy(),
                    )
                elif position.weighting:  # we do not yield position with weight 0 because of issue with certain multi-thematic portfolios which contain duplicates
                    yield position

        yield from _crawl_portfolio(self, Decimal(1.0), Decimal(1.0), False)

    def get_positions(self, val_date: date, **kwargs) -> Iterable[AssetPosition]:
        if self.is_composition:
            assets = list(self.get_lookthrough_positions(val_date, **kwargs))
        else:
            assets = list(self.assets.filter(date=val_date))
        return assets

    def compute_lookthrough(self, from_date: date, to_date: date | None = None):
        if not self.primary_portfolio or not self.is_lookthrough:
            raise ValueError(
                "Lookthrough position can only be computed on lookthrough portfolio with a primary portfolio"
            )
        if not to_date:
            to_date = from_date
        for from_date in pd.date_range(from_date, to_date, freq="B").date:
            logger.info(f"Compute Look-Through for {self} at {from_date}")
            portfolio_total_asset_value = (
                self.primary_portfolio.get_total_asset_under_management(from_date) if not self.only_weighting else None
            )
            self.builder.add(
                list(self.primary_portfolio.get_lookthrough_positions(from_date, portfolio_total_asset_value)),
                infer_underlying_quote_price=True,
            )
        self.builder.bulk_create_positions(delete_leftovers=True)
        self.builder.schedule_change_at_dates()
        self.builder.schedule_metric_computation()

    def update_preferred_classification_per_instrument(self):
        # Function to automatically assign Preferred instrument based on the assets' underlying instruments of the
        # attached wbportfolio
        instruments = filter(
            None,
            map(
                lambda x: Instrument.objects.get(id=x["underlying_instrument"]).get_classifable_ancestor(
                    include_self=True
                ),
                self.assets.values("underlying_instrument").distinct("underlying_instrument"),
            ),
        )
        leftovers_instruments = list(
            PortfolioInstrumentPreferredClassificationThroughModel.objects.filter(portfolio=self).values_list(
                "instrument", flat=True
            )
        )
        for instrument in instruments:
            other_classifications = instrument.classifications.filter(group__is_primary=False)
            default_classification = None
            if other_classifications.count() == 1:
                default_classification = other_classifications.first()
            if not PortfolioInstrumentPreferredClassificationThroughModel.objects.filter(
                portfolio=self, instrument=instrument
            ).exists():
                PortfolioInstrumentPreferredClassificationThroughModel.objects.create(
                    portfolio=self,
                    instrument=instrument,
                    classification=default_classification,
                    classification_group=default_classification.group if default_classification else None,
                )
            if instrument.id in leftovers_instruments:
                leftovers_instruments.remove(instrument.id)

        for instrument_id in leftovers_instruments:
            PortfolioInstrumentPreferredClassificationThroughModel.objects.filter(
                portfolio=self, instrument=instrument_id
            ).delete()

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:portfolio"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:portfoliorepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

    @classmethod
    def _get_or_create_portfolio(cls, instrument_handler, portfolio_data):
        if isinstance(portfolio_data, int):
            return Portfolio.all_objects.get(id=portfolio_data)
        instrument = portfolio_data
        if isinstance(portfolio_data, dict):
            instrument = instrument_handler.process_object(instrument, only_security=False, read_only=True)[0]
        return instrument.primary_portfolio

    def check_share_diff(self, val_date: date) -> bool:
        return self.assets.filter(Q(date=val_date) & ~Q(initial_shares=F("initial_shares_at_custodian"))).exists()

    @classmethod
    def get_contribution_df(cls, data, need_normalize: bool = False):
        df = pd.DataFrame(
            data,
            columns=[
                "date",
                "price",
                "currency_fx_rate",
                "group_key",
                "value",
            ],
        )
        if not df.empty:
            df = df[df["value"] != 0]
            df.date = pd.to_datetime(df.date)
            df["price_fx_portfolio"] = df.price * df.currency_fx_rate

            df[["price", "price_fx_portfolio", "value", "currency_fx_rate"]] = df[
                ["price", "price_fx_portfolio", "value", "currency_fx_rate"]
            ].astype("float")

            df["group_key"] = df["group_key"].fillna(0)

            df = (
                df[
                    [
                        "group_key",
                        "date",
                        "price",
                        "price_fx_portfolio",
                        "value",
                        "currency_fx_rate",
                    ]
                ]
                .groupby(["date", "group_key"], dropna=False)
                .agg(
                    {
                        "price": "mean",
                        "price_fx_portfolio": "mean",
                        "value": "sum",
                        "currency_fx_rate": "mean",
                    }
                )
                .reset_index()
                .set_index("date")
                .sort_index()
            )
            df["value"] = df["value"].fillna(0)
            value = df.pivot_table(
                index="date",
                columns=["group_key"],
                values="value",
                fill_value=0,
                aggfunc="sum",
            )
            weights_ = value
            if need_normalize:
                total_value_price = df["value"].groupby("date", dropna=False).sum()
                weights_ = value.divide(total_value_price, axis=0)
            prices_usd = (
                df.pivot_table(
                    index="date",
                    columns=["group_key"],
                    values="price_fx_portfolio",
                    aggfunc="mean",
                )
                .replace(0, np.nan)
                .bfill()
            )

            rates_fx = (
                df.pivot_table(
                    index="date",
                    columns=["group_key"],
                    values="currency_fx_rate",
                    aggfunc="mean",
                )
                .replace(0, np.nan)
                .bfill()
            )

            prices_usd = prices_usd.ffill()
            performance_prices = prices_usd / prices_usd.shift(1, axis=0) - 1
            contributions_prices = performance_prices.multiply(weights_.shift(1, axis=0)).dropna(how="all")
            total_contrib_prices = (1 + contributions_prices.sum(axis=1)).shift(1, fill_value=1.0).cumprod()
            contributions_prices = contributions_prices.multiply(total_contrib_prices, axis=0).sum(skipna=False)
            monthly_perf_prices = (1 + performance_prices).dropna(how="all").product(axis=0, skipna=False) - 1

            rates_fx = rates_fx.ffill()
            performance_rates_fx = rates_fx / rates_fx.shift(1, axis=0) - 1
            contributions_rates_fx = performance_rates_fx.multiply(weights_.shift(1, axis=0)).dropna(how="all")
            total_contrib_rates_fx = (1 + contributions_rates_fx.sum(axis=1)).shift(1, fill_value=1.0).cumprod()
            contributions_rates_fx = contributions_rates_fx.multiply(total_contrib_rates_fx, axis=0).sum(skipna=False)
            monthly_perf_rates_fx = (1 + performance_rates_fx).dropna(how="all").product(axis=0, skipna=False) - 1

            res = pd.concat(
                [
                    monthly_perf_prices,
                    monthly_perf_rates_fx,
                    contributions_prices,
                    contributions_rates_fx,
                    weights_.iloc[0, :],
                    weights_.iloc[-1, :],
                    value.iloc[0, :],
                    value.iloc[-1, :],
                ],
                axis=1,
            ).reset_index()
            res.columns = [
                "group_key",
                "performance_total",
                "performance_forex",
                "contribution_total",
                "contribution_forex",
                "allocation_start",
                "allocation_end",
                "total_value_start",
                "total_value_end",
            ]

            return res.replace([np.inf, -np.inf, np.nan], 0)
        return pd.DataFrame()

    def get_or_create_index(self):
        index = Index.objects.create(name=self.name, currency=self.currency)
        index.portfolios.all().delete()
        InstrumentPortfolioThroughModel.objects.update_or_create(instrument=index, defaults={"portfolio": self})
        return index

    @classmethod
    def create_model_portfolio(cls, name: str, currency: Currency, with_index: bool = True):
        portfolio = cls.objects.create(
            is_manageable=True,
            name=name,
            currency=currency,
        )
        if with_index:
            portfolio.get_or_create_index()
        return portfolio


def default_estimate_net_value(last_price: Decimal, analytic_portfolio: AnalyticPortfolio) -> float | None:
    with suppress(IndexError, ValueError):  # we silent any indexerror introduced by no returns for the past days
        return analytic_portfolio.get_estimate_net_value(float(last_price.net_value))


@receiver(post_save, sender="wbportfolio.PortfolioPortfolioThroughModel")
def post_portfolio_relationship_creation(sender, instance, created, raw, **kwargs):
    if (
        not raw
        and created
        and instance.portfolio.is_lookthrough
        and instance.type == PortfolioPortfolioThroughModel.Type.PRIMARY
    ):
        with suppress(AssetPosition.DoesNotExist):
            earliest_primary_position_date = instance.dependency_portfolio.assets.earliest("date").date
            compute_lookthrough_as_task.delay(instance.portfolio.id, earliest_primary_position_date, date.today())


@shared_task(queue="portfolio")
def trigger_portfolio_change_as_task(portfolio_id, val_date, **kwargs):
    portfolio = Portfolio.all_objects.get(id=portfolio_id)
    portfolio.change_at_date(val_date, **kwargs)


@shared_task(queue="portfolio")
def compute_lookthrough_as_task(portfolio_id: int, start: date, end: date):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    portfolio.compute_lookthrough(start, to_date=end)


@receiver(investable_universe_updated, sender="wbfdm.Instrument")
def update_portfolio_after_investable_universe(*args, end_date: date | None = None, **kwargs):
    if not end_date:
        end_date = date.today()
    end_date = (end_date + timedelta(days=1) - BDay(1)).date()  # shift in case of business day
    from_date = (end_date - BDay(1)).date()
    for portfolio in Portfolio.tracked_objects.all().to_dependency_iterator(from_date):
        if not portfolio.is_lookthrough:
            try:
                portfolio.propagate_or_update_assets(from_date, end_date)
            except Exception as e:
                logger.error(f"Exception while propagating portfolio assets {portfolio}: {e}")
        portfolio.estimate_net_asset_values(end_date)
