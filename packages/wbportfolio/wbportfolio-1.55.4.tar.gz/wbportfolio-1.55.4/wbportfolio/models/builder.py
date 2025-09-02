import logging
import math
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Iterable

import pandas as pd
from celery import chain, group
from django.contrib.contenttypes.models import ContentType
from pandas._libs.tslibs.offsets import BDay
from wbcore.contrib.currency.models import Currency, CurrencyFXRates
from wbfdm.contrib.metric.tasks import compute_metrics_as_task
from wbfdm.models import Instrument

from wbportfolio.models.asset import AssetPosition
from wbportfolio.pms.analytics.portfolio import Portfolio as AnalyticPortfolio

if TYPE_CHECKING:
    from wbportfolio.models import Portfolio
logger = logging.getLogger("pms")


MINIMUM_DECIMAL = 8
MIN_STEP = Decimal("0.00000001")


class AssetPositionBuilder:
    """
    Efficiently converts position data into AssetPosition models with batch operations
    and proper dependency management.

    Features:
    - Bulk database fetching for performance
    - Thread-safe operations
    - Clear type hints
    - Memory-efficient storage
    """

    _positions: dict[date, dict[tuple[int, int | None], "AssetPosition"]]

    _fx_rates: dict[date, dict[Currency, CurrencyFXRates]]
    _instruments: dict[int, Instrument]

    def __init__(
        self,
        portfolio: "Portfolio",
    ):
        self.portfolio = portfolio
        # Initialize data stores with type hints
        self._instruments = {}
        self._fx_rates = defaultdict(dict)
        self.prices = defaultdict(dict)
        self.returns = pd.DataFrame()
        self._compute_metrics_tasks = set()
        self._change_at_date_tasks = dict()
        self._positions = defaultdict(dict)

    def get_positions(self, fix_quantization: bool = True, **kwargs):
        # return an iterable excluding the position with a null weight if the portfolio is manageable (otherwise, we assume the 0-weight position is valid)
        for positions in self._positions.values():
            quantization_weight_error = round(
                Decimal("1") - sum(map(lambda o: o.weighting, positions.values()))
                if fix_quantization
                else Decimal("0"),
                MINIMUM_DECIMAL,
            )
            for position in sorted(positions.values(), key=lambda x: x.weighting, reverse=True):
                if position.weighting:
                    for k, v in kwargs.items():
                        setattr(position, k, v)
                    # if the total weight is not 100%, we add the quantization leftover to some random position (max 1e-8 per position, thus it is negligible)
                    if quantization_weight_error:
                        step = round(Decimal(math.copysign(MIN_STEP, quantization_weight_error)), MINIMUM_DECIMAL)
                        position.weighting += step
                        quantization_weight_error -= step
                    yield position

    def __bool__(self) -> bool:
        return len(self._positions.keys()) > 0

    def _get_instrument(self, instrument_id: int) -> Instrument:
        try:
            return self._instruments[instrument_id]
        except KeyError:
            instrument = Instrument.objects.get(id=instrument_id)
            self._instruments[instrument_id] = instrument
            return instrument

    def _get_fx_rate(self, val_date: date, currency: Currency) -> CurrencyFXRates | None:
        try:
            return self._fx_rates[val_date][currency]
        except KeyError:
            if currency.key == "USD":
                fx_rate = CurrencyFXRates.objects.get_or_create(
                    currency=currency, date=val_date, defaults={"value": Decimal("1")}
                )[0]
            else:
                try:
                    fx_rate = CurrencyFXRates.objects.get(
                        currency=currency, date=val_date
                    )  # we create a fx rate anyway to not fail the position. The fx rate expect to be there later on
                except CurrencyFXRates.DoesNotExist:
                    fx_rate = CurrencyFXRates.objects.filter(currency=currency, date__lt=val_date).latest("date")
            self._fx_rates[val_date][currency] = fx_rate
            return fx_rate

    def _get_price(self, val_date: date, instrument: Instrument) -> float | None:
        try:
            return self.prices[val_date][instrument.id]
        except KeyError:
            return None

    def _dict_to_model(
        self,
        val_date: date,
        instrument_id: int,
        weighting: float,
        **kwargs,
    ) -> "AssetPosition":
        underlying_quote = self._get_instrument(instrument_id)
        currency_fx_rate_portfolio_to_usd = self._get_fx_rate(val_date, self.portfolio.currency)
        currency_fx_rate_instrument_to_usd = self._get_fx_rate(val_date, underlying_quote.currency)
        price = self._get_price(val_date, underlying_quote)

        parameters = dict(
            underlying_quote=underlying_quote,
            weighting=round(weighting, MINIMUM_DECIMAL),
            date=val_date,
            asset_valuation_date=val_date,
            is_estimated=True,
            portfolio=self.portfolio,
            currency=underlying_quote.currency,
            initial_price=price,
            currency_fx_rate_portfolio_to_usd=currency_fx_rate_portfolio_to_usd,
            currency_fx_rate_instrument_to_usd=currency_fx_rate_instrument_to_usd,
            initial_currency_fx_rate=None,
            underlying_quote_price=None,
            underlying_instrument=None,
        )
        parameters.update(kwargs)
        position = AssetPosition(**parameters)
        return position

    def load_returns(self, instrument_ids: Iterable[int], from_date: date, to_date: date, use_dl: bool = True):
        if self.returns.empty:
            self.prices, self.returns = Instrument.objects.filter(id__in=instrument_ids).get_returns_df(
                from_date=from_date, to_date=to_date, to_currency=self.portfolio.currency, use_dl=use_dl
            )
        else:
            min_date = min(self.prices.keys())
            max_date = max(self.prices.keys())
            if from_date < min_date or to_date > max_date:
                # we need to refetch everything as we are missing index
                self.prices, self.returns = Instrument.objects.filter(
                    id__in=set(instrument_ids).union(set(self.returns.columns))
                ).get_returns_df(
                    from_date=min(from_date, min_date),
                    to_date=max(to_date, max_date),
                    to_currency=self.portfolio.currency,
                    use_dl=use_dl,
                )
            else:
                instruments = set(instrument_ids) - set(self.returns.columns)
                if instruments:
                    new_prices, new_returns = Instrument.objects.filter(id__in=instruments).get_returns_df(
                        from_date=min(from_date, min_date),
                        to_date=max(to_date, max_date),
                        to_currency=self.portfolio.currency,
                        use_dl=use_dl,
                    )
                    self.returns = self.returns.join(new_returns, how="left").fillna(0)
                    for d, p in new_prices.items():
                        self.prices[d].update(p)

    def add(
        self,
        positions: list["AssetPosition"] | tuple[date, dict[int, float]],
        infer_underlying_quote_price: bool = False,
    ):
        """
        Add multiple positions efficiently with batch processing

        Args:
            positions: Iterable of AssetPosition instances or dictionary of weight {instrument_id: weight} that needs to be converted into AssetPosition
        """
        if isinstance(positions, tuple):
            val_date = positions[0]
            positions = [(val_date, i, w) for i, w in positions[1].items()]  # unflatten data to make it iterable
        for position in positions:
            if not isinstance(position, AssetPosition):
                position = self._dict_to_model(*position)
            position.pre_save(
                infer_underlying_quote_price=infer_underlying_quote_price
            )  # inferring underlying quote price is potentially very slow for big dataset of positions, it's not very needed for model portfolio so we disable it
            # Generate unique composite key
            key = (
                position.underlying_quote.id,
                position.portfolio_created.id if position.portfolio_created else None,
            )
            # Merge duplicate positions
            if existing_position := self._positions[position.date].get(key):
                position.weighting += existing_position.weighting
                if existing_position.initial_shares:
                    position.initial_shares += existing_position.initial_shares
            # ensure the position portfolio is the iterator portfolio (could be different when computing look-through for instance)
            position.portfolio = self.portfolio
            position.weighting = Decimal(
                round(position.weighting, 8)
            )  # set the weight as it will be saved in the db to handle quantization error accordingly
            if position.initial_price is not None and position.initial_currency_fx_rate is not None:
                self._positions[position.date][key] = position
        return self

    def get_dates(self) -> list[date]:
        """Get sorted list of unique dates"""
        return list(sorted(self._positions.keys()))

    def _get_portfolio(self, val_date: date) -> AnalyticPortfolio:
        """Get weight structure with instrument IDs as keys"""
        positions = self._positions[val_date]
        next_returns = self.returns.loc[[(val_date + BDay(1)).date()], :]
        weights = dict(map(lambda row: (row[1].underlying_quote.id, float(row[1].weighting)), positions.items()))
        return AnalyticPortfolio(weights=weights, X=next_returns)

    def bulk_create_positions(self, delete_leftovers: bool = False, force_save: bool = False, **kwargs):
        positions = list(self.get_positions(**kwargs))

        # we need to delete the existing estimated portfolio because otherwise we risk to have existing and not
        # overlapping positions remaining (as they will not be updating by the bulk create). E.g. when someone
        # change completely the trades of a portfolio model and drift it.
        dates = self.get_dates()
        self.portfolio.assets.filter(date__in=dates, is_estimated=True).delete()

        if len(positions) > 0:
            if self.portfolio.is_tracked or force_save:  # if the portfolio is not "tracked", we do no drift weights
                leftover_positions_ids = list(
                    self.portfolio.assets.filter(date__in=dates).values_list("id", flat=True)
                )  # we need to get the ids otherwise the queryset is reevaluated later
                logger.info(f"bulk saving {len(positions)} positions ({len(leftover_positions_ids)} leftovers) ...")
                objs = AssetPosition.unannotated_objects.bulk_create(
                    positions,
                    update_fields=[
                        "weighting",
                        "initial_price",
                        "initial_currency_fx_rate",
                        "initial_shares",
                        "currency_fx_rate_instrument_to_usd",
                        "currency_fx_rate_portfolio_to_usd",
                        "underlying_quote_price",
                        "portfolio",
                        "portfolio_created",
                        "underlying_instrument",
                    ],
                    unique_fields=["portfolio", "date", "underlying_quote", "portfolio_created"],
                    update_conflicts=True,
                    batch_size=10000,
                )
                if delete_leftovers:
                    objs_ids = list(map(lambda x: x.id, objs))
                    leftover_positions_ids = list(filter(lambda i: i not in objs_ids, leftover_positions_ids))
                    logger.info(f"deleting {len(leftover_positions_ids)} leftover positions..")
                    AssetPosition.objects.filter(id__in=leftover_positions_ids).delete()

            for val_date in self.get_dates():
                if self.portfolio.is_tracked:
                    try:
                        changed_portfolio = self._get_portfolio(val_date)
                    except KeyError:
                        changed_portfolio = None
                    self._change_at_date_tasks[val_date] = changed_portfolio
                    self._compute_metrics_tasks.add(val_date)
        self._positions = defaultdict(dict)

    def schedule_metric_computation(self):
        if self._compute_metrics_tasks:
            basket_id = self.portfolio.id
            basket_content_type_id = ContentType.objects.get_by_natural_key("wbportfolio", "portfolio").id
            group(
                *[
                    compute_metrics_as_task.si(d, basket_id=basket_id, basket_content_type_id=basket_content_type_id)
                    for d in self._compute_metrics_tasks
                ]
            ).apply_async()
            self._change_at_date_tasks = dict()

    def schedule_change_at_dates(self, synchronous: bool = True, **task_kwargs):
        from wbportfolio.models.portfolio import trigger_portfolio_change_as_task

        if self._change_at_date_tasks:
            tasks = chain(
                *[
                    trigger_portfolio_change_as_task.si(
                        self.portfolio.id, d, changed_portfolio=portfolio, evaluate_rebalancer=False, **task_kwargs
                    )
                    for d, portfolio in self._change_at_date_tasks.items()
                ]
            )
            if synchronous:
                tasks.apply()
            else:
                tasks.apply_async()
            self._change_at_date_tasks = dict()
