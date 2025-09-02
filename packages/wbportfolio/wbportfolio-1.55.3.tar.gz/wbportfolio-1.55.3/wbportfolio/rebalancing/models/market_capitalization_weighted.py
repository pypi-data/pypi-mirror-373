from decimal import Decimal

import numpy as np
import pandas as pd
from django.db.models import QuerySet
from pandas._libs.tslibs.offsets import BDay
from wbfdm.enums import MarketData
from wbfdm.models import (
    Classification,
    Exchange,
    Instrument,
    InstrumentListThroughModel,
)

from wbportfolio.pms.analytics.utils import fix_quantization_error
from wbportfolio.pms.typing import Portfolio, Position
from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.rebalancing.base import AbstractRebalancingModel
from wbportfolio.rebalancing.decorators import register


@register("Market Capitalization Rebalancing")
class MarketCapitalizationRebalancing(AbstractRebalancingModel):
    TARGET_CURRENCY: str = "USD"
    MIN_WEIGHT: float = 1e-5  # we allow only weight of minimum 0.01%

    def __init__(
        self,
        *args,
        bypass_exchange_check: bool = False,
        ffill_market_cap_limit: int = 5,
        effective_portfolio: PortfolioDTO | None = None,
        **kwargs,
    ):
        super().__init__(*args, effective_portfolio=effective_portfolio, **kwargs)
        self.bypass_exchange_check = bypass_exchange_check
        instruments = self._get_instruments(**kwargs)
        self.market_cap_df = pd.DataFrame(
            instruments.dl.market_data(
                values=[MarketData.MARKET_CAPITALIZATION],
                from_date=self.trade_date - BDay(ffill_market_cap_limit),
                to_date=self.trade_date,
                target_currency=self.TARGET_CURRENCY,
            )
        )
        self.exchange_df = (
            pd.DataFrame(instruments.values_list("id", "exchange"), columns=["id", "exchange"])
            .set_index("id")
            .replace({np.nan: None})
        )
        instrument_ids = list(instruments.values_list("id", flat=True))
        try:
            self.market_cap_df = (
                self.market_cap_df.sort_values(by="valuation_date")
                .groupby("instrument_id")
                .last()["market_capitalization"]
            )
            self.market_cap_df = self.market_cap_df.reindex(instrument_ids)
        except (IndexError, KeyError):
            self.market_cap_df = pd.Series(dtype="float64", index=instrument_ids)

    def _get_instruments(
        self,
        classification_ids: list[int] | None = None,
        instrument_ids: list[int] | None = None,
        instrument_list_id: int | None = None,
    ) -> QuerySet[Instrument]:
        """
        Use the provided kwargs to return a list of instruments as universe.
        - If classifications are given, we returns all the instrument linked to these classifications
        - Or directly from a static list of instrument ids
        - fallback to the last effective portfolio underlying instruments list
        """
        if not instrument_ids:
            instrument_ids = []
        if classification_ids:
            for classification in Classification.objects.filter(id__in=classification_ids):
                for children in classification.get_descendants(include_self=True):
                    for company in children.instruments.all():
                        instrument_ids.append(company.get_primary_quote().id)
        if instrument_list_id:
            instrument_ids.extend(
                list(
                    InstrumentListThroughModel.objects.filter(instrument_list_id=instrument_list_id).values_list(
                        "instrument", flat=True
                    )
                )
            )

        if not instrument_ids:
            instrument_ids = list(self.effective_portfolio.positions_map.keys())

        return (
            Instrument.objects.filter(id__in=instrument_ids)
            .filter(exchange__isnull=False)
            .filter_active_at_date(self.trade_date)
        )

    def is_valid(self) -> bool:
        if not self.market_cap_df.empty:
            df = pd.concat(
                [self.market_cap_df, self.exchange_df], axis=1
            )  # if we are missing any market cap for not-delisted instrument, we consider the rebalancing not valid
            df = df.groupby("exchange", dropna=False)["market_capitalization"].any()
            missing_exchanges = Exchange.objects.filter(id__in=df[~df].index.to_list())
            # if bypass exchange check is true, we do not care whether an exchange is closed we just care if there are at least one exchange open
            if self.bypass_exchange_check:
                return df.any()
            else:
                if missing_exchanges.exists():
                    setattr(
                        self,
                        "_validation_errors",
                        f"Couldn't find any market capitalization for exchanges {', '.join([str(e) for e in missing_exchanges])}",
                    )
                return df.all()
        return False

    def get_target_portfolio(self) -> Portfolio:
        positions = []
        df = self.market_cap_df / self.market_cap_df.dropna().sum()
        df = df[df > self.MIN_WEIGHT]
        df = df / df.sum()
        df = fix_quantization_error(df, 8)
        for underlying_instrument, weighting in df.to_dict().items():
            if np.isnan(weighting):
                weighting = Decimal(0)
            else:
                weighting = round(Decimal(weighting), 8)
            positions.append(
                Position(
                    underlying_instrument=underlying_instrument,
                    weighting=weighting,
                    date=self.trade_date,
                )
            )
        return Portfolio(positions=tuple(positions))
