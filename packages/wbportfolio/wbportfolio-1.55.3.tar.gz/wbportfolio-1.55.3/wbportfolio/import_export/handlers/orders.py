from decimal import Decimal
from typing import Any, Dict

from django.db import models
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler, ImportState
from wbcore.contrib.io.utils import nest_row
from wbfdm.import_export.handlers.instrument import InstrumentImportHandler

from wbportfolio.pms.typing import Portfolio, Position


class OrderImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbportfolio.Order"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)
        self.order_proposal = None

    def process_object(
        self,
        data: Dict[str, Any],
        **kwargs,
    ):
        from wbportfolio.models import OrderProposal

        data = nest_row(data)
        underlying_instrument = self.instrument_handler.process_object(
            data["underlying_instrument"], only_security=False, read_only=True
        )[0]
        self.order_proposal = OrderProposal.objects.get(id=data.pop("order_proposal_id"))
        weighting = data.get("target_weight", data.get("weighting"))
        shares = data.get("target_shares", data.get("shares", 0))
        if weighting is None:
            raise DeserializationError("We couldn't figure out the target weight column")
        position_dto = Position(
            underlying_instrument=underlying_instrument.id,
            instrument_type=underlying_instrument.instrument_type.id,
            weighting=Decimal(weighting),
            shares=Decimal(shares),
            currency=underlying_instrument.currency,
            date=self.order_proposal.trade_date,
            is_cash=underlying_instrument.is_cash,
        )
        return position_dto, ImportState.CREATED

    def _get_history(self, history: Dict[str, Any]) -> models.QuerySet:
        from wbportfolio.models.orders.order_proposals import OrderProposal

        if order_proposal_id := history.get("order_proposal_id"):
            # if a order proposal is provided, we delete the existing history first as otherwise, it would mess with the target weight computation
            order_proposal = OrderProposal.objects.get(id=order_proposal_id)
            order_proposal.orders.all().delete()
        return self.model.objects.none()

    def _post_processing_objects(self, positions: list[Position], *args, **kwargs):
        total_weight = sum(map(lambda p: p.weighting, positions))
        if cash_weight := Decimal("1") - total_weight:
            cash_component = self.order_proposal.cash_component
            positions.append(
                Position(
                    underlying_instrument=cash_component.id,
                    instrument_type=cash_component.instrument_type.id,
                    weighting=cash_weight,
                    currency=cash_component.currency,
                    date=self.order_proposal.trade_date,
                    is_cash=cash_component.is_cash,
                )
            )
        self.order_proposal.reset_orders(target_portfolio=Portfolio(positions))
