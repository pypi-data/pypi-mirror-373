from collections import defaultdict
from contextlib import suppress
from datetime import datetime
from decimal import Decimal
from itertools import chain
from typing import Any, Dict, List, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from wbcore.contrib.authentication.authentication import User
from wbcore.contrib.currency.import_export.handlers import CurrencyImportHandler
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler
from wbcore.contrib.notifications.dispatch import send_notification
from wbfdm.import_export.handlers.instrument import InstrumentImportHandler
from wbfdm.import_export.handlers.instrument_price import InstrumentPriceImportHandler
from wbfdm.models.exchanges import Exchange

from wbportfolio.models.roles import PortfolioRole


class AssetPositionImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbportfolio.AssetPosition"
    PRICE_DATE_TIMEDELTA: int = 7
    MAX_PRICE_DATE_TIMEDELTA: int = 360

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)
        self.instrument_price_handler = InstrumentPriceImportHandler(self.import_source)
        self.currency_handler = CurrencyImportHandler(self.import_source)

    def _deserialize(self, data: Dict[str, Any]):
        from wbportfolio.models import Portfolio

        portfolio_data = data.pop("portfolio", None)
        underlying_quote_data = data.pop("underlying_quote", data.pop("underlying_instrument", None))
        if "currency" in data:
            data["currency"] = self.currency_handler.process_object(
                data["currency"], read_only=True, raise_exception=False
            )[0]
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()
        if data.get("asset_valuation_date", None):
            data["asset_valuation_date"] = datetime.strptime(data["asset_valuation_date"], "%Y-%m-%d").date()
        else:
            data["asset_valuation_date"] = data["date"]

        if exchange_data := data.pop("exchange", None):
            sanitized_dict = {k: v for k, v in exchange_data.items() if v is not None}
            if sanitized_dict:
                data["exchange"] = Exchange.dict_to_model(sanitized_dict)

        data["portfolio"] = Portfolio._get_or_create_portfolio(self.instrument_handler, portfolio_data)
        data["underlying_quote"] = self.instrument_handler.process_object(
            underlying_quote_data, only_security=False, read_only=True
        )[0]

        # Ensure that for shares and weighting, a None value default to 0
        if "initial_shares" in data and data["initial_shares"] is None:
            data["initial_shares"] = Decimal(0)
        if "weighting" in data and data["weighting"] is None:
            data["weighting"] = Decimal(0)

        # if the initial price is not provided, we try to get it directly from the dataloader
        if data.get("initial_price") is None:
            try:
                data["initial_price"] = data["underlying_quote"].get_price(
                    data["date"], price_date_timedelta=self.PRICE_DATE_TIMEDELTA
                )
            except ValueError:
                # If we cannot find a price with the default timedelta, we try with a bigger range (in case the instrument stopped trading for some time for instance)
                try:
                    data["initial_price"] = data["underlying_quote"].get_price(
                        data["date"], price_date_timedelta=self.MAX_PRICE_DATE_TIMEDELTA
                    )
                except ValueError:
                    raise DeserializationError("Price not provided but can not be found automatically")

        # number type deserialization and sanitization
        # ensure the provided Decimal field are of type Decimal
        decimal_fields = ["initial_currency_fx_rate", "initial_price", "initial_shares", "weighting"]
        for field in decimal_fields:
            if not (value := data.get(field, None)) is None:
                data[field] = Decimal(value)

    def _process_raw_data(self, data: Dict[str, Any]):
        if prices := data.get("prices", None):
            self.import_source.log += "Instrument Prices found: Importing"
            self.instrument_price_handler.process({"data": prices})

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        self.import_source.log += "\nTrying to get asset position instance"
        position = data["portfolio"].assets.filter(date=data["date"], underlying_quote=data["underlying_quote"])
        if position.exists():
            self.import_source.log += "\nAsset Position found."
            if position.count() > 1:
                position = position.filter(is_estimated=False)
            if position.count() > 1:
                raise ValueError(f'We should find only one Assetposition:{position.values_list("id", flat=True)}')
            return position.first()
        self.import_source.log += "\nAsset Position not found. A new one will be created"
        return None

    def _create_instance(self, data: Dict[str, Any], **kwargs) -> models.Model:
        instance = self.model(
            portfolio=data["portfolio"],
            underlying_quote=data["underlying_quote"],
            date=data["date"],
            asset_valuation_date=data["asset_valuation_date"],
            weighting=data.get("weighting", None),
            initial_price=data["initial_price"],
            initial_shares=data.get("initial_shares", None),
            initial_currency_fx_rate=data.get("initial_currency_fx_rate", 1),
            import_source=self.import_source,
            currency=data.get("currency", None),
        )

        return self._save_object(instance, **kwargs)

    def _save_object(self, _object, **kwargs):
        _object.underlying_quote_price = (
            None  # detech possibly already attached instrument price to retrigger the save mechanism
        )
        _object.save(create_underlying_quote_price_if_missing=True)
        return _object

    def _post_processing_objects(
        self,
        created_objs: List[models.Model],
        modified_objs: List[models.Model],
        unmodified_objs: List[models.Model],
    ):
        from wbportfolio.models.portfolio import trigger_portfolio_change_as_task

        portfolio_to_resynch = defaultdict(set)
        imported_ids = defaultdict(set)
        for obj in chain(created_objs, modified_objs, unmodified_objs):
            portfolio_to_resynch[obj.portfolio].add(obj.date)
            imported_ids[obj.portfolio].add(obj.id)

        for portfolio, dates in portfolio_to_resynch.items():
            # We remove leftovers positions from wrongly imported file
            leftovers_positions = self.model.objects.filter(portfolio=portfolio, date__in=dates)
            for obj_id in imported_ids[portfolio]:
                leftovers_positions = leftovers_positions.exclude(id=obj_id)
            for position in leftovers_positions:
                position.delete()
            for val_date in sorted(dates):
                trigger_portfolio_change_as_task.delay(portfolio.id, val_date, fix_quantization=True)

            # check if portfolio as custodian
            latest_date = max(dates)
            with suppress(ObjectDoesNotExist):
                if (custodian_rel := portfolio.dependency_through.get(type="CUSTODIAN")) and portfolio.assets.latest(
                    "date"
                ).date >= latest_date:
                    custodian_portfolio = custodian_rel.dependency_portfolio
                    differences = portfolio.check_related_portfolio_at_date(latest_date, custodian_portfolio)
                    if differences.exists():
                        for user in User.objects.filter(
                            profile_id__in=PortfolioRole.portfolio_managers().values_list("person", flat=True)
                        ):
                            send_notification(
                                code="wbportfolio.portfolio.check_custodian_portfolio",
                                title="There is a discrepency between two portfolios",
                                body=f"There has been a discrepency between two portfolios: {portfolio} and {custodian_portfolio}.",
                                user=user,
                                reverse_name="wbportfolio:portfolio-modelcompositionpandas-list",
                                reverse_args=[portfolio.id],
                            )
