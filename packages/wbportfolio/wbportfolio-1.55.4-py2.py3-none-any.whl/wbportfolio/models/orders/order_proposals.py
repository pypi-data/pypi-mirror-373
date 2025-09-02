import logging
import math
from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, TypeVar

from celery import shared_task
from django.core.exceptions import ValidationError
from django.db import DatabaseError, models
from django.db.models import (
    F,
    OuterRef,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce, Round
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from pandas._libs.tslibs.offsets import BDay
from wbcompliance.models.risk_management.mixins import RiskCheckMixin
from wbcore.contrib.authentication.models import User
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton
from wbcore.models import WBModel
from wbcore.utils.models import CloneMixin
from wbfdm.models import InstrumentPrice
from wbfdm.models.instruments.instruments import Cash, Instrument

from wbportfolio.models.asset import AssetPosition
from wbportfolio.models.roles import PortfolioRole
from wbportfolio.pms.trading import TradingService
from wbportfolio.pms.typing import Order as OrderDTO
from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.pms.typing import Position as PositionDTO

from ...order_routing import ExecutionStatus, RoutingException
from ...order_routing.adapters import BaseCustodianAdapter
from .orders import Order
from .routing import cancel_rebalancing, execute_orders, get_execution_status

logger = logging.getLogger("pms")

SelfOrderProposal = TypeVar("SelfOrderProposal", bound="OrderProposal")


class OrderProposal(CloneMixin, RiskCheckMixin, WBModel):
    trade_date = models.DateField(verbose_name="Trading Date")

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        DENIED = "DENIED", "Denied"
        APPLIED = "APPLIED", "Applied"
        EXECUTION = "EXECUTION", "Execution"
        FAILED = "FAILED", "Failed"

    comment = models.TextField(default="", verbose_name="Order Comment", blank=True)
    status = FSMField(default=Status.DRAFT, choices=Status.choices, verbose_name="Status")
    rebalancing_model = models.ForeignKey(
        "wbportfolio.RebalancingModel",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="order_proposals",
        verbose_name="Rebalancing Model",
        help_text="Rebalancing Model that generates the target portfolio",
    )
    portfolio = models.ForeignKey(
        "wbportfolio.Portfolio", related_name="order_proposals", on_delete=models.PROTECT, verbose_name="Portfolio"
    )
    creator = models.ForeignKey(
        "directory.Person",
        blank=True,
        null=True,
        related_name="order_proposals",
        on_delete=models.PROTECT,
        verbose_name="Owner",
    )
    approver = models.ForeignKey(
        "directory.Person",
        blank=True,
        null=True,
        related_name="approver_order_proposals",
        on_delete=models.PROTECT,
        verbose_name="Approver",
    )
    min_order_value = models.IntegerField(
        default=0, verbose_name="Minimum Order Value", help_text="Minimum Order Value in the Portfolio currency"
    )
    total_cash_weight = models.DecimalField(
        default=Decimal("0"),
        decimal_places=4,
        max_digits=5,
        verbose_name="Total Cash Weight",
        help_text="The desired percentage for the cash component. The remaining percentage (100% minus this value) will be allocated to total target weighting. Default is 0%.",
    )
    total_effective_portfolio_contribution = models.DecimalField(
        default=Decimal("1"),
        max_digits=Order.ORDER_WEIGHTING_PRECISION * 2 + 3,
        decimal_places=Order.ORDER_WEIGHTING_PRECISION * 2,
    )
    execution_status = models.CharField(
        blank=True, default="", choices=ExecutionStatus.choices, verbose_name="Execution Status"
    )
    execution_status_detail = models.CharField(blank=True, default="", verbose_name="Execution Status Detail")
    execution_comment = models.CharField(blank=True, default="", verbose_name="Execution Comment")

    class Meta:
        verbose_name = "Order Proposal"
        verbose_name_plural = "Order Proposals"
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "trade_date"],
                name="unique_order_proposal",
            ),
        ]

        notification_types = [
            create_notification_type(
                "wbportfolio.order_proposal.push_model_changes",
                "Push Model Changes",
                "Sends a notification when a the change/orders are pushed to modeled after portfolios",
                True,
                True,
                True,
            )
        ]

    def save(self, *args, **kwargs):
        # if a order proposal is created before the existing earliest order proposal, we automatically shift the linked instruments inception date to allow automatic NAV computation since the new inception date
        if not self.portfolio.order_proposals.filter(trade_date__lt=self.trade_date).exists():
            # we need to set the inception date as the first order proposal trade date (and thus, the first position date). We expect a NAV at 100 then
            self.portfolio.instruments.filter(inception_date__gt=self.trade_date).update(
                inception_date=self.trade_date
            )
        super().save(*args, **kwargs)

    @property
    def check_evaluation_date(self):
        return self.trade_date

    @property
    def checked_object(self) -> Any:
        return self.portfolio

    @cached_property
    def portfolio_total_asset_value(self) -> Decimal:
        return self.portfolio.get_total_asset_value(self.last_effective_date)

    @cached_property
    def validated_trading_service(self) -> TradingService:
        """
        This property holds the validated trading services and cache it.This property expect to be set only if is_valid return True
        """
        target_portfolio = self.convert_to_portfolio()

        return TradingService(
            self.trade_date,
            effective_portfolio=self._get_default_effective_portfolio(),
            target_portfolio=target_portfolio,
            total_target_weight=target_portfolio.total_weight,
        )

    @cached_property
    def last_effective_date(self) -> date:
        try:
            return self.portfolio.assets.filter(date__lt=self.trade_date).latest("date").date
        except AssetPosition.DoesNotExist:
            return self.value_date

    @cached_property
    def custodian_adapter(self) -> BaseCustodianAdapter | None:
        try:
            return self.portfolio.get_authenticated_custodian_adapter(raise_exception=True)
        except ValueError as e:
            logger.warning("Error while instantiating custodian adapter: %s", e)

    @cached_property
    def value_date(self) -> date:
        return (self.trade_date - BDay(1)).date()

    @property
    def previous_order_proposal(self) -> SelfOrderProposal | None:
        future_proposals = OrderProposal.objects.filter(portfolio=self.portfolio).filter(
            trade_date__lt=self.trade_date, status=OrderProposal.Status.APPLIED
        )
        if future_proposals.exists():
            return future_proposals.latest("trade_date")
        return None

    @property
    def next_order_proposal(self) -> SelfOrderProposal | None:
        future_proposals = OrderProposal.objects.filter(portfolio=self.portfolio).filter(
            trade_date__gt=self.trade_date, status=OrderProposal.Status.APPLIED
        )
        if future_proposals.exists():
            return future_proposals.earliest("trade_date")
        return None

    @property
    def cash_component(self) -> Cash:
        return self.portfolio.cash_component

    @property
    def total_effective_portfolio_weight(self) -> Decimal:
        return Decimal("1.0")

    @property
    def total_expected_target_weight(self) -> Decimal:
        return self.total_effective_portfolio_weight - self.total_cash_weight

    @cached_property
    def total_effective_portfolio_cash_weight(self) -> Decimal:
        return self.portfolio.assets.filter(
            models.Q(date=self.last_effective_date)
            & (models.Q(underlying_quote__is_cash=True) | models.Q(underlying_quote__is_cash_equivalent=True))
        ).aggregate(Sum("weighting"))["weighting__sum"] or Decimal("0")

    @property
    def execution_instruction(self):
        # TODO make this dynamically configurable
        return "MARKET_ON_CLOSE"

    def get_orders(self):
        # TODO Issue here: the cash is subqueried on the portfolio, on portfolio such as the fund, there is multiple cash component, that we exclude in the orders (and use a unique cash position instead)
        # so the subquery returns the previous position (probably USD), but is missing the other cash aggregation. We need to find a way to handle that properly

        orders = self.orders.all().annotate(
            total_effective_portfolio_contribution=Value(self.total_effective_portfolio_contribution),
            last_effective_date=Subquery(
                AssetPosition.unannotated_objects.filter(
                    date__lt=OuterRef("value_date"),
                    portfolio=OuterRef("portfolio"),
                )
                .order_by("-date")
                .values("date")[:1]
            ),
            previous_weight=models.Case(
                models.When(
                    underlying_instrument__is_cash=False,
                    then=Coalesce(
                        Subquery(
                            AssetPosition.unannotated_objects.filter(
                                underlying_quote=OuterRef("underlying_instrument"),
                                date=OuterRef("last_effective_date"),
                                portfolio=OuterRef("portfolio"),
                            )
                            .values("portfolio")
                            .annotate(s=Sum("weighting"))
                            .values("s")[:1]
                        ),
                        Decimal(0),
                    ),
                ),
                default=Value(self.total_effective_portfolio_cash_weight),
            ),
            contribution=F("previous_weight") * (F("daily_return") + Value(Decimal("1"))),
            effective_weight=Round(
                models.Case(
                    models.When(total_effective_portfolio_contribution=Value(Decimal("0")), then=Value(Decimal("0"))),
                    default=F("contribution") / F("total_effective_portfolio_contribution"),
                ),
                precision=Order.ORDER_WEIGHTING_PRECISION,
            ),
            target_weight=Round(F("effective_weight") + F("weighting"), precision=Order.ORDER_WEIGHTING_PRECISION),
            effective_shares=Coalesce(
                Subquery(
                    AssetPosition.objects.filter(
                        underlying_quote=OuterRef("underlying_instrument"),
                        date=OuterRef("last_effective_date"),
                        portfolio=OuterRef("portfolio"),
                    )
                    .values("portfolio")
                    .annotate(s=Sum("shares"))
                    .values("s")[:1]
                ),
                Decimal(0),
            ),
            target_shares=F("effective_shares") + F("shares"),
        )

        if total_estimated_effective_weight := orders.aggregate(s=models.Sum("effective_weight"))["s"]:
            with suppress(Order.DoesNotExist):
                largest_order = orders.latest("effective_weight")
                if quant_error := self.total_effective_portfolio_weight - total_estimated_effective_weight:
                    orders = orders.annotate(
                        effective_weight=models.Case(
                            models.When(
                                id=largest_order.id,
                                then=models.F("effective_weight") + models.Value(Decimal(quant_error)),
                            ),
                            default=models.F("effective_weight"),
                        ),
                        target_weight=models.Case(
                            models.When(
                                id=largest_order.id,
                                then=models.F("target_weight") + models.Value(Decimal(quant_error)),
                            ),
                            default=models.F("target_weight"),
                        ),
                    )
        return orders.annotate(
            has_warnings=models.Case(
                models.When(
                    (models.Q(price=0) & ~models.Q(target_weight=0)) | models.Q(target_weight__lt=0), then=Value(True)
                ),
                default=Value(False),
            ),
        )

    def prepare_orders_for_execution(self) -> list[OrderDTO]:
        executable_orders = []
        for order in (
            self.get_orders().exclude(underlying_instrument__is_cash=True).select_related("underlying_instrument")
        ):
            instrument = order.underlying_instrument
            # we support only the instrument type provided by the Order DTO class
            asset_class = instrument.get_security_ancestor().instrument_type.key.upper()
            try:
                if instrument.refinitiv_identifier_code or instrument.ticker or instrument.sedol:
                    executable_orders.append(
                        OrderDTO(
                            id=order.id,
                            asset_class=OrderDTO.AssetType[asset_class],
                            weighting=float(order.weighting),
                            target_weight=float(order.target_weight),
                            trade_date=order.value_date,
                            shares=float(order.shares) if order.shares is not None else None,
                            target_shares=float(order.target_shares) if order.target_shares is not None else None,
                            refinitiv_identifier_code=instrument.refinitiv_identifier_code,
                            bloomberg_ticker=instrument.ticker,
                            sedol=instrument.sedol,
                            execution_instruction=self.execution_instruction,
                        )
                    )
                else:
                    order.execution_confirmed = False
                    order.execution_comment = "Underlying instrument does not have a valid identifier."
                    order.save()
            except (AttributeError, KeyError):
                order.execution_confirmed = False
                order.execution_comment = f"Unsupported asset class {asset_class.title()}."
                order.save()

        return executable_orders

    def __str__(self) -> str:
        return f"{self.portfolio.name}: {self.trade_date} ({self.status})"

    def convert_to_portfolio(
        self, use_effective: bool = False, with_cash: bool = True, use_desired_target_weight: bool = False
    ) -> PortfolioDTO:
        """
        Converts the internal portfolio state and pending orders into a PortfolioDTO.

        Args:
            use_effective: Use effective share quantities for positions if True.
            with_cash: Include a cash position in the result if True.
            use_desired_target_weight: Use desired target weights from orders if True.

        Returns:
            PortfolioDTO: Object that encapsulates all portfolio positions.
        """
        portfolio = {}

        # 1. Gather all non-cash, positively weighted assets from the existing portfolio.
        for asset in self.portfolio.assets.filter(
            date=self.last_effective_date,
            # underlying_quote__is_cash=False,
            # underlying_quote__is_cash_equivalent=False,
            weighting__gt=0,
        ):
            portfolio[asset.underlying_quote] = {
                "shares": asset._shares,
                "weighting": asset.weighting,
                "delta_weight": Decimal("0"),
                "price": asset._price,
                "currency_fx_rate": asset._currency_fx_rate,
            }

        # 2. Add or update non-cash orders, possibly overriding weights.
        for order in self.get_orders().filter(
            underlying_instrument__is_cash=False, underlying_instrument__is_cash_equivalent=False
        ):
            if use_desired_target_weight and order.desired_target_weight is not None:
                delta_weight = Decimal("0")
                weighting = order.desired_target_weight
            else:
                delta_weight = order.weighting
                weighting = order._previous_weight

            portfolio[order.underlying_instrument] = {
                "weighting": weighting,
                "delta_weight": delta_weight,
                "shares": order._target_shares if not use_effective else order._effective_shares,
                "price": order.price,
                "currency_fx_rate": order.currency_fx_rate,
            }

        # 3. Prepare a mapping from instrument IDs to weights for analytic calculations.
        previous_weights = {instrument.id: float(info["weighting"]) for instrument, info in portfolio.items()}

        # 4. Attempt to fetch analytic returns and portfolio contribution. Default on error.
        try:
            last_returns, contribution = self.portfolio.get_analytic_portfolio(
                self.value_date, weights=previous_weights, use_dl=True
            ).get_contributions()
            last_returns = last_returns.to_dict()
        except ValueError:
            last_returns, contribution = {}, 1

        positions = []
        total_weighting = Decimal("0")

        # 5. Build PositionDTO objects for all instruments.
        for instrument, row in portfolio.items():
            weighting = row["weighting"]
            daily_return = Decimal(last_returns.get(instrument.id, 0))

            # Optionally apply drift to weightings if required
            if not use_effective and not use_desired_target_weight:
                if contribution:
                    drifted_weight = round(
                        weighting * (daily_return + Decimal("1")) / Decimal(contribution),
                        Order.ORDER_WEIGHTING_PRECISION,
                    )
                else:
                    drifted_weight = weighting
                weighting = drifted_weight + row["delta_weight"]

            # Assemble the position object
            positions.append(
                PositionDTO(
                    underlying_instrument=instrument.id,
                    instrument_type=instrument.instrument_type.id,
                    weighting=weighting,
                    daily_return=daily_return if use_effective else Decimal("0"),
                    shares=row["shares"],
                    currency=instrument.currency.id,
                    date=self.last_effective_date if use_effective else self.trade_date,
                    is_cash=instrument.is_cash or instrument.is_cash_equivalent,
                    price=row["price"],
                    currency_fx_rate=row["currency_fx_rate"],
                )
            )
            total_weighting += weighting

        # 6. Optionally include a cash position to balance the total weighting.
        if (
            portfolio
            and with_cash
            and total_weighting
            and self.total_effective_portfolio_weight
            and (cash_weight := self.total_effective_portfolio_weight - total_weighting)
        ):
            cash_position = self.get_estimated_target_cash(target_cash_weight=cash_weight)
            positions.append(cash_position._build_dto())

        return PortfolioDTO(positions)

    # Start tools methods
    def _clone(self, **kwargs) -> SelfOrderProposal:
        """
        Method to clone self as a new order proposal. It will automatically shift the order date if a proposal already exists
        Args:
            **kwargs: The keyword arguments
        Returns:
            The cloned order proposal
        """
        trade_date = kwargs.get("clone_date", self.trade_date)

        # Find the next valid order date
        while OrderProposal.objects.filter(portfolio=self.portfolio, trade_date=trade_date).exists():
            trade_date += timedelta(days=1)

        order_proposal_clone = OrderProposal.objects.create(
            trade_date=trade_date,
            comment=kwargs.get("clone_comment", self.comment),
            status=OrderProposal.Status.DRAFT,
            rebalancing_model=self.rebalancing_model,
            portfolio=self.portfolio,
            creator=self.creator,
        )
        for order in self.orders.all():
            order.id = None
            order.order_proposal = order_proposal_clone
            order.save()

        return order_proposal_clone

    def normalize_orders(self):
        """
        Call the trading service with the existing orders and normalize them in order to obtain a total sum target weight of 100%
        The existing order will be modified directly with the given normalization factor
        """
        service = TradingService(
            self.trade_date,
            effective_portfolio=self._get_default_effective_portfolio(),
            target_portfolio=self.convert_to_portfolio(use_effective=False, with_cash=False),
            total_target_weight=self.total_expected_target_weight,
        )
        leftovers_orders = self.orders.all()
        for underlying_instrument_id, order_dto in service.trades_batch.trades_map.items():
            with suppress(Order.DoesNotExist):
                order = self.orders.get(underlying_instrument_id=underlying_instrument_id)
                order.weighting = round(order_dto.delta_weight, Order.ORDER_WEIGHTING_PRECISION)
                order.save()
                leftovers_orders = leftovers_orders.exclude(id=order.id)
        leftovers_orders.delete()
        self.fix_quantization()

    def fix_quantization(self):
        if self.orders.exists():
            orders = self.get_orders()
            t_weight = orders.aggregate(models.Sum("target_weight"))["target_weight__sum"] or Decimal("0.0")
            # we handle quantization error due to the decimal max digits. In that case, we take the biggest order (highest weight) and we remove the quantization error
            if quantize_error := (t_weight - self.total_expected_target_weight):
                biggest_order = orders.exclude(underlying_instrument__is_cash=True).latest("target_weight")
                biggest_order.weighting -= quantize_error
                biggest_order.save()

    def _get_default_target_portfolio(self, use_desired_target_weight: bool = False, **kwargs) -> PortfolioDTO:
        if self.rebalancing_model:
            params = {}
            if rebalancer := getattr(self.portfolio, "automatic_rebalancer", None):
                params.update(rebalancer.parameters)
            params.update(kwargs)
            return self.rebalancing_model.get_target_portfolio(
                self.portfolio, self.trade_date, self.value_date, **params
            )
        return self.convert_to_portfolio(use_effective=False, use_desired_target_weight=use_desired_target_weight)

    def _get_default_effective_portfolio(self):
        return self.convert_to_portfolio(use_effective=True)

    def reset_orders(
        self,
        target_portfolio: PortfolioDTO | None = None,
        effective_portfolio: PortfolioRole | None = None,
        validate_order: bool = True,
        use_desired_target_weight: bool = False,
    ):
        """
        Will delete all existing orders and recreate them from the method `create_or_update_trades`
        """
        if self.rebalancing_model:
            self.orders.all().delete()
        else:
            self.orders.filter(underlying_instrument__is_cash=True).delete()
        # delete all existing orders
        # Get effective and target portfolio
        if not target_portfolio:
            target_portfolio = self._get_default_target_portfolio(use_desired_target_weight=use_desired_target_weight)
        if not effective_portfolio:
            effective_portfolio = self._get_default_effective_portfolio()
        if target_portfolio:
            service = TradingService(
                self.trade_date,
                effective_portfolio=effective_portfolio,
                target_portfolio=target_portfolio,
                total_target_weight=self.total_expected_target_weight,
            )
            if validate_order:
                service.is_valid()
                orders = service.validated_trades
            else:
                orders = service.trades_batch.trades_map.values()

            objs = []
            for order_dto in orders:
                instrument = Instrument.objects.get(id=order_dto.underlying_instrument)
                currency_fx_rate = instrument.currency.convert(
                    self.value_date, self.portfolio.currency, exact_lookup=True
                )
                # we cannot do a bulk-create because Order is a multi table inheritance
                weighting = round(order_dto.delta_weight, Order.ORDER_WEIGHTING_PRECISION)
                daily_return = order_dto.daily_return
                try:
                    order = self.orders.get(underlying_instrument=instrument)
                    order.weighting = weighting
                    order.currency_fx_rate = currency_fx_rate
                    order.daily_return = daily_return
                except Order.DoesNotExist:
                    order = Order(
                        underlying_instrument=instrument,
                        order_proposal=self,
                        value_date=self.trade_date,
                        weighting=weighting,
                        daily_return=daily_return,
                        currency_fx_rate=currency_fx_rate,
                    )
                order.desired_target_weight = order_dto.target_weight
                order.order_type = Order.get_type(
                    weighting, round(order_dto.previous_weight, 8), round(order_dto.target_weight, 8)
                )
                order.pre_save()
                # # if we cannot automatically find a price, we consider the stock is invalid and we sell it
                # if not order.price and order.weighting > 0:
                #     order.price = Decimal("0.0")
                #     order.weighting = -order_dto.effective_weight
                objs.append(order)
            Order.objects.bulk_create(
                objs,
                update_fields=[
                    "value_date",
                    "weighting",
                    "daily_return",
                    "currency_fx_rate",
                    "order_type",
                    "portfolio",
                    "price",
                    "price_gross",
                    "desired_target_weight",
                    # "shares"
                ],
                unique_fields=["order_proposal", "underlying_instrument"],
                update_conflicts=True,
                batch_size=1000,
            )
        # final sanity check to make sure invalid order with effective and target weight of 0 are automatically removed:
        self.get_orders().exclude(underlying_instrument__is_cash=True).filter(
            target_weight=0, effective_weight=0
        ).delete()
        self.get_orders().filter(target_weight=0).exclude(effective_shares=0).update(shares=-F("effective_shares"))
        # self.fix_quantization()
        self.total_effective_portfolio_contribution = effective_portfolio.portfolio_contribution
        self.save()

    def apply_workflow(
        self,
        apply_automatically: bool = True,
        silent_exception: bool = False,
        force_reset_order: bool = False,
        **reset_order_kwargs,
    ):
        # before, we need to save all positions in the builder first because effective weight depends on it
        self.portfolio.builder.bulk_create_positions(delete_leftovers=True)
        if self.status == OrderProposal.Status.APPLIED:
            logger.info("Reverting order proposal ...")
            self.revert()
        if self.status == OrderProposal.Status.DRAFT:
            if (
                self.rebalancing_model or force_reset_order
            ):  # if there is no position (for any reason) or we the order proposal has a rebalancer model attached (orders are computed based on an aglo), we reapply this order proposal
                logger.info("Resetting orders ...")
                try:  # we silent any validation error while setting proposal, because if this happens, we assume the current order proposal state if valid and we continue to batch compute
                    self.reset_orders(**reset_order_kwargs)
                except (ValidationError, DatabaseError) as e:
                    self.status = OrderProposal.Status.FAILED
                    if not silent_exception:
                        raise ValidationError(e)
                    return
            logger.info("Submitting order proposal ...")
            self.submit()
        if self.status == OrderProposal.Status.PENDING:
            self.approve()
        if apply_automatically and self.portfolio.can_be_rebalanced:
            logger.info("Applying order proposal ...")
            self.apply(replay=False)

    def replay(
        self,
        broadcast_changes_at_date: bool = True,
        reapply_order_proposal: bool = False,
        synchronous: bool = False,
        **reset_order_kwargs,
    ):
        last_order_proposal = self
        last_order_proposal_created = False
        self.portfolio.load_builder_returns((self.trade_date - BDay(3)).date(), date.today())
        while last_order_proposal and last_order_proposal.status == OrderProposal.Status.APPLIED:
            last_order_proposal.portfolio = self.portfolio  # we set the same ptf reference
            if not last_order_proposal_created:
                if reapply_order_proposal or last_order_proposal.rebalancing_model:
                    logger.info(f"Replaying order proposal {last_order_proposal}")
                    last_order_proposal.apply_workflow(
                        silent_exception=True, force_reset_order=True, **reset_order_kwargs
                    )
                    last_order_proposal.save()
                else:
                    logger.info(f"Resetting order proposal {last_order_proposal}")
                    last_order_proposal.reset_orders(**reset_order_kwargs)
                if last_order_proposal.status != OrderProposal.Status.APPLIED:
                    break
            next_order_proposal = last_order_proposal.next_order_proposal
            if next_order_proposal:
                next_trade_date = next_order_proposal.trade_date - timedelta(days=1)
            elif next_expected_rebalancing_date := self.portfolio.get_next_rebalancing_date(
                last_order_proposal.trade_date
            ):
                next_trade_date = (
                    next_expected_rebalancing_date + timedelta(days=7)
                )  # we don't know yet if rebalancing is valid and can be executed on `next_expected_rebalancing_date`, so we add safety window of 7 days
            else:
                next_trade_date = date.today()
            next_trade_date = min(next_trade_date, date.today())
            gen = self.portfolio.drift_weights(
                last_order_proposal.trade_date, next_trade_date, stop_at_rebalancing=True
            )
            try:
                while True:
                    self.portfolio.builder.add(next(gen))
            except StopIteration as e:
                overriding_order_proposal = e.value

            self.portfolio.builder.bulk_create_positions(
                delete_leftovers=True,
            )
            for draft_tp in OrderProposal.objects.filter(
                portfolio=self.portfolio,
                trade_date__gt=last_order_proposal.trade_date,
                trade_date__lte=next_trade_date,
                status=OrderProposal.Status.DRAFT,
            ):
                draft_tp.reset_orders()
            if overriding_order_proposal:
                last_order_proposal_created = True
                last_order_proposal = overriding_order_proposal
            else:
                last_order_proposal_created = False
                last_order_proposal = next_order_proposal
        self.portfolio.builder.schedule_change_at_dates(
            synchronous=synchronous, broadcast_changes_at_date=broadcast_changes_at_date
        )

    def invalidate_future_order_proposal(self):
        # Delete all future automatic order proposals and set the manual one into a draft state
        self.portfolio.order_proposals.filter(
            trade_date__gt=self.trade_date, rebalancing_model__isnull=False, comment="Automatic rebalancing"
        ).delete()
        for future_order_proposal in self.portfolio.order_proposals.filter(
            trade_date__gt=self.trade_date, status=OrderProposal.Status.APPLIED
        ):
            future_order_proposal.revert()
            future_order_proposal.save()

    def get_estimated_shares(
        self, weight: Decimal, underlying_quote: Instrument, quote_price: Decimal
    ) -> Decimal | None:
        """
        Estimates the number of shares for a order based on the given weight and underlying quote.

        This method calculates the estimated shares by dividing the order's total value in the portfolio's currency by the price of the underlying quote in the same currency. It handles currency conversion and suppresses any ValueError that might occur during the price retrieval.

        Args:
            weight (Decimal): The weight of the order.
            underlying_quote (Instrument): The underlying instrument for the order.

        Returns:
            Decimal | None: The estimated number of shares or None if the calculation fails.
        """
        # Retrieve the price of the underlying quote on the order date TODO: this is very slow and probably due to the to_date argument to the dl which slowdown drastically the query

        # if an order exists for this estimation and the target weight is 0, then we return the inverse of the effective shares
        with suppress(Order.DoesNotExist):
            order = self.get_orders().get(underlying_instrument=underlying_quote)
            if order.target_weight == 0:
                return -order.effective_shares
        # Calculate the order's total value in the portfolio's currency
        trade_total_value_fx_portfolio = self.portfolio_total_asset_value * weight

        # Convert the quote price to the portfolio's currency
        price_fx_portfolio = quote_price * underlying_quote.currency.convert(
            self.trade_date, self.portfolio.currency, exact_lookup=False
        )

        # If the price is valid, calculate and return the estimated shares
        if price_fx_portfolio:
            return trade_total_value_fx_portfolio / price_fx_portfolio

    def get_round_lot_size(self, shares: Decimal, underlying_quote: Instrument) -> Decimal:
        if (round_lot_size := underlying_quote.round_lot_size) != 1 and (
            not underlying_quote.exchange or underlying_quote.exchange.apply_round_lot_size
        ):
            if shares > 0:
                shares = math.ceil(shares / round_lot_size) * round_lot_size
            elif abs(shares) > round_lot_size:
                shares = math.floor(shares / round_lot_size) * round_lot_size
        return shares

    def get_estimated_target_cash(self, target_cash_weight: Decimal | None = None) -> AssetPosition:
        """
        Estimates the target cash weight and shares for a order proposal.

        This method calculates the target cash weight by summing the weights of cash orders and adding any leftover weight from non-cash orders. It then estimates the target shares for this cash component if the portfolio is not only weighting-based.

        Args:
            target_cash_weight (Decimal): the expected target cash weight (Optional). If not provided, we estimate from the existing orders

        Returns:
            tuple[Decimal, Decimal]: A tuple containing the target cash weight and the estimated target shares.
        """
        # Retrieve orders with base information
        orders = self.get_orders()
        # Calculate the total target weight of all orders
        total_target_weight = orders.filter(
            underlying_instrument__is_cash=False, underlying_instrument__is_cash_equivalent=False
        ).aggregate(s=models.Sum("target_weight"))["s"] or Decimal(0)
        if target_cash_weight is None:
            target_cash_weight = Decimal("1") - total_target_weight

        # Initialize target shares to zero
        total_target_shares = Decimal(0)

        # Get or create a cash component for the portfolio's currency
        cash_component = self.cash_component
        # If the portfolio is not only weighting-based, estimate the target shares for the cash component
        if not self.portfolio.only_weighting:
            # Estimate the target shares for the cash component
            with suppress(ValueError):
                total_target_shares = self.get_estimated_shares(target_cash_weight, cash_component, Decimal("1.0"))

        # otherwise, we create a new position
        underlying_quote_price = InstrumentPrice.objects.get_or_create(
            instrument=cash_component,
            date=self.trade_date,
            calculated=False,
            defaults={"net_value": Decimal(1)},
        )[0]
        return AssetPosition(
            underlying_quote=cash_component,
            portfolio_created=None,
            portfolio=self.portfolio,
            date=self.trade_date,
            weighting=target_cash_weight,
            initial_price=underlying_quote_price.net_value,
            initial_shares=total_target_shares,
            asset_valuation_date=self.trade_date,
            underlying_quote_price=underlying_quote_price,
            currency=cash_component.currency,
            is_estimated=False,
        )

    # Start FSM logics

    @transition(
        field=status,
        source=Status.DRAFT,
        target=Status.PENDING,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        ),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.SEND.icon,
                key="submit",
                label="Submit",
                action_label="Submit",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def submit(self, by=None, description=None, **kwargs):
        orders = []
        orders_validation_warnings = []
        qs = self.get_orders()
        total_target_weight = Decimal("0")
        for order in qs:
            order_warnings = order.submit(
                by=by, description=description, portfolio_total_asset_value=self.portfolio_total_asset_value, **kwargs
            )
            if order_warnings:
                orders_validation_warnings.extend(order_warnings)
            orders.append(order)
            total_target_weight += order._target_weight

        Order.objects.bulk_update(orders, ["shares", "weighting", "desired_target_weight"])

        # If we estimate cash on this order proposal, we make sure to create the corresponding cash component
        estimated_cash_position = self.get_estimated_target_cash()
        target_portfolio = self.validated_trading_service.trades_batch.convert_to_portfolio(
            estimated_cash_position._build_dto()
        )
        self.evaluate_active_rules(self.trade_date, target_portfolio, asynchronously=True)
        self.total_cash_weight = Decimal("1") - total_target_weight
        return orders_validation_warnings

    def can_submit(self):
        errors = dict()
        errors_list = []
        service = self.validated_trading_service
        try:
            service.is_valid(ignore_error=True)
            # if service.trades_batch.total_abs_delta_weight == 0:
            #     errors_list.append(
            #         "There is no change detected in this order proposal. Please submit at last one valid order"
            #     )
            if len(service.validated_trades) == 0:
                errors_list.append(_("There is no valid order on this proposal"))
            if service.errors:
                errors_list.extend(service.errors)
            if errors_list:
                errors["non_field_errors"] = errors_list
        except ValidationError:
            errors["non_field_errors"] = service.errors
            with suppress(KeyError):
                del self.__dict__["validated_trading_service"]
        return errors

    @transition(
        field=status,
        source=Status.PENDING,
        target=Status.APPROVED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and not instance.has_non_successful_checks,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.APPROVE.icon,
                key="approve",
                label="Approve",
                action_label="Approve",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def approve(self, by=None, description=None, **kwargs):
        if by:
            self.approver = getattr(by, "profile", None)
        elif not self.approver:
            self.approver = self.creator

    def can_approve(self):
        pass

    @transition(
        field=status,
        source=Status.PENDING,
        target=Status.DENIED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and not instance.has_non_successful_checks,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.DENY.icon,
                key="deny",
                label="Deny",
                action_label="Deny",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def deny(self, by=None, description=None, **kwargs):
        pass

    def can_deny(self):
        pass

    @property
    def can_be_applied(self):
        return not self.has_non_successful_checks and self.portfolio.is_manageable

    @transition(
        field=status,
        source=Status.APPROVED,
        target=Status.APPLIED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.can_be_applied,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.SAVE.icon,
                key="apply",
                label="Apply",
                action_label="Apply",
            )
        },
    )
    def apply(self, by=None, description=None, replay: bool = True, **kwargs):
        # We validate order which will create or update the initial asset positions
        if not self.portfolio.can_be_rebalanced:
            raise ValueError("Non-Rebalanceable portfolio cannot be traded manually.")
        warnings = []
        # We do not want to create the estimated cash position if there is not orders in the order proposal (shouldn't be possible anyway)
        estimated_cash_position = self.get_estimated_target_cash()
        assets = {}
        for order in self.get_orders():
            with suppress(ValueError):
                # we add the corresponding asset only if it is not the cache position (already included in estimated_cash_position)
                if (
                    order.underlying_instrument != estimated_cash_position.underlying_quote
                    and order._target_weight > 0
                ):
                    assets[order.underlying_instrument.id] = order._target_weight

        # if there is cash leftover, we create an extra asset position to hold the cash component
        if estimated_cash_position.weighting > 0 and len(assets) > 0:
            warnings.append(
                f"We created automatically a cash position of weight {estimated_cash_position.weighting:.2%}"
            )
            assets[estimated_cash_position.underlying_quote.id] = estimated_cash_position.weighting
        self.portfolio.builder.add((self.trade_date, assets)).bulk_create_positions(
            force_save=True, is_estimated=False, delete_leftovers=True
        )
        if replay and self.portfolio.is_manageable:
            replay_as_task.delay(
                self.id, user_id=by.id if by else None, broadcast_changes_at_date=False, reapply_order_proposal=True
            )
        if by:
            self.approver = by.profile
        return warnings

    def can_apply(self):
        errors = dict()
        orders = self.get_orders()
        if not self.portfolio.can_be_rebalanced:
            errors["non_field_errors"] = [_("The portfolio does not allow manual rebalanced")]
        if not orders.exists():
            errors["non_field_errors"] = [
                _("At least one order needs to be submitted to be able to apply this proposal")
            ]
        if not self.portfolio.can_be_rebalanced:
            errors["portfolio"] = [
                [_("The portfolio needs to be a model portfolio in order to apply this order proposal manually")]
            ]
        if self.has_non_successful_checks:
            errors["non_field_errors"] = [_("The pre orders rules did not passed successfully")]
        if orders.filter(has_warnings=True).filter(
            underlying_instrument__is_cash=False, underlying_instrument__is_cash_equivalent=False
        ):
            errors["non_field_errors"] = [
                _("There is warning that needs to be addresses on the orders before approval.")
            ]
        return errors

    @transition(
        field=status,
        source=Status.PENDING,
        target=Status.DRAFT,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.has_all_check_completed
        or not instance.checks.exists(),  # we wait for all checks to succeed before proposing the back to draft transition
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.UNDO.icon,
                key="backtodraft",
                label="Back to Draft",
                action_label="backtodraft",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def backtodraft(self, **kwargs):
        with suppress(KeyError):
            del self.__dict__["validated_trading_service"]
        self.checks.delete()

    def can_backtodraft(self):
        pass

    @transition(
        field=status,
        source=Status.APPLIED,
        target=Status.DRAFT,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        ),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.REGENERATE.icon,
                key="revert",
                label="Revert",
                action_label="revert",
                description_fields="<p>Unapply orders and move everything back to draft (i.e. The underlying asset positions will change like the orders were never applied)</p>",
            )
        },
    )
    def revert(self, **kwargs):
        self.approver = None
        with suppress(KeyError):
            del self.__dict__["validated_trading_service"]
        self.portfolio.assets.filter(date=self.trade_date, is_estimated=False).update(
            is_estimated=True
        )  # we delete the existing portfolio as it has been reverted

    def can_revert(self):
        errors = dict()
        if not self.portfolio.can_be_rebalanced:
            errors["portfolio"] = [
                _("The portfolio needs to be a model portfolio in order to revert this order proposal manually")
            ]
        return errors

    @transition(
        field=status,
        source=Status.APPROVED,
        target=Status.EXECUTION,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and (user != instance.approver or user.is_superuser)
        and instance.custodian_adapter
        and not instance.has_non_successful_checks,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.DEAL_MONEY.icon,
                key="execute",
                label="Execute",
                action_label="Execute",
                description_fields="<p>Execute the orders through the setup custodian.</p>",
            )
        },
    )
    def execute(self, **kwargs):
        self.execution_status = ExecutionStatus.PENDING
        self.execution_comment = "Waiting for custodian confirmation"
        execute_orders_as_task.delay(self.id)

    def can_execute(self):
        if not self.custodian_adapter:
            return {"portfolio": ["No custodian adapter"]}

    @transition(
        field=status,
        source=Status.EXECUTION,
        target=Status.APPROVED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.execution_status in [ExecutionStatus.PENDING, ExecutionStatus.IN_DRAFT],
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.PREVIOUS.icon,
                key="cancelexecution",
                label="Cancel Execution",
                action_label="Cancel Execution",
                description_fields="<p>Cancel the current requested execution. Time sensitive operation.</p>",
            )
        },
    )
    def cancelexecution(self, **kwargs):
        warning = ""
        try:
            if cancel_rebalancing(self):
                self.execution_comment, self.execution_status_detail, self.execution_status = (
                    "",
                    "",
                    ExecutionStatus.CANCELLED,
                )
            else:
                warning = "We could not cancel the rebalancing. It is probably already executed. Please refresh status or check with an administrator."
        except (RoutingException, ValueError) as e:
            warning = f"Could not cancel orders proposal {self}: {str(e)}"
            logger.error(warning)
        return warning

    def can_cancelexecution(self):
        if not self.execution_status in [ExecutionStatus.PENDING, ExecutionStatus.IN_DRAFT]:
            return {"execution_status": "Execution can only be cancelled if it is not already executed"}

    def update_execution_status(self):
        try:
            self.execution_status, self.execution_status_detail = get_execution_status(self)
            self.save()
        except (RoutingException, ValueError) as e:
            logger.warning(f"Could not update rebalancing status: {str(e)}")

    # End FSM logics

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbportfolio:orderproposal"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbportfolio:orderproposalrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{_portfolio.name}} ({{trade_date}})"


@receiver(post_save, sender="wbportfolio.OrderProposal")
def post_fail_order_proposal(sender, instance: OrderProposal, created, raw, **kwargs):
    # if we have a order proposal in a fail state, we ensure that all future existing order proposal are either deleted (automatic one) or set back to draft
    if not raw and instance.status == OrderProposal.Status.FAILED:
        # we delete all order proposal that have a rebalancing model and are marked as "automatic" (quite hardcoded yet)
        instance.invalidate_future_order_proposal()


@shared_task(queue="portfolio")
def replay_as_task(order_proposal_id, user_id: int | None = None, **kwargs):
    order_proposal = OrderProposal.objects.get(id=order_proposal_id)
    order_proposal.replay(**kwargs)
    if user_id:
        user = User.objects.get(id=user_id)
        send_notification(
            code="wbportfolio.portfolio.replay_done",
            title="Order Proposal Replay Completed",
            body=f'We’ve successfully replayed your order proposal for "{order_proposal.portfolio}" from {order_proposal.trade_date:%Y-%m-%d}. You can now review its updated composition.',
            user=user,
            reverse_name="wbportfolio:portfolio-detail",
            reverse_args=[order_proposal.portfolio.id],
        )


@shared_task(queue="portfolio")
def execute_orders_as_task(order_proposal_id: int):
    order_proposal = OrderProposal.objects.get(id=order_proposal_id)
    try:
        status, comment = execute_orders(order_proposal)
    except (ValueError, RoutingException) as e:
        logger.error(f"Could not execute orders proposal {order_proposal}: {str(e)}")
        status = ExecutionStatus.FAILED
        comment = str(e)
    order_proposal.execution_status = status
    order_proposal.execution_comment = comment
    order_proposal.save()


@shared_task(queue="portfolio")
def push_model_change_as_task(
    model_order_proposal_id: int,
    user_id: int,
    only_for_portfolio_ids: list[int] | None = None,
    approve_automatically: bool = False,
):
    # not happy with that but we will keep it for the MVP lifecycle
    model_order_proposal = OrderProposal.objects.get(id=model_order_proposal_id)
    trade_date = model_order_proposal.trade_date
    user = User.objects.get(id=user_id)
    from wbportfolio.models.rebalancing import RebalancingModel

    model_rebalancing = RebalancingModel.objects.get(
        class_path="wbportfolio.rebalancing.models.model_portfolio.ModelPortfolioRebalancing"
    )
    product_html_list = "<ul>\n"
    for rel in model_order_proposal.portfolio.get_model_portfolio_relationships(trade_date):
        if not only_for_portfolio_ids or rel.portfolio.id in only_for_portfolio_ids:
            order_proposal, _ = OrderProposal.objects.update_or_create(
                portfolio=rel.portfolio, trade_date=trade_date, defaults={"rebalancing_model": model_rebalancing}
            )
            order_proposal.reset_orders()
            product_html_list += f"<li>{rel.portfolio}</li>\n"
            if approve_automatically:
                order_proposal.submit()
                order_proposal.approve(by=user)
                order_proposal.save()
    product_html_list += "</ul>"

    send_notification(
        code="wbportfolio.order_proposal.push_model_changes",
        title="Portfolio Model changes are pushed to dependant portfolios",
        body=f"""
<p>The latest updates to the portfolio model <strong>{model_order_proposal.portfolio}</strong> have been successfully applied to the associated portfolios, and corresponding orders have been created.</p>
<p>To proceed with executing these orders, please review the following related portfolios: </p>
        {product_html_list}
        """,
        user=user,
    )
