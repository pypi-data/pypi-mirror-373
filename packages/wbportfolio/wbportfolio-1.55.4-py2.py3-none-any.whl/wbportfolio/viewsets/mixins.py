from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from wbfdm.models import Instrument

from wbportfolio.models import Portfolio, PortfolioRole, Product


class UserPortfolioRequestPermissionMixin:
    @cached_property
    def instrument(self) -> Instrument:
        return get_object_or_404(Instrument, pk=self.kwargs["instrument_id"])

    @cached_property
    def product(self) -> Instrument:
        return get_object_or_404(Product, pk=self.kwargs["product_id"])

    @cached_property
    def portfolio(self) -> Portfolio:
        return get_object_or_404(Portfolio, id=self.kwargs["portfolio_id"])

    @cached_property
    def instrument_or_none(self) -> Instrument | None:
        try:
            return get_object_or_404(Instrument, pk=self.kwargs["instrument_id"])
        except Exception:
            return None

    @cached_property
    def portfolio_or_none(self) -> Portfolio | None:
        try:
            return get_object_or_404(Portfolio, id=self.kwargs["portfolio_id"])
        except Exception:
            return None

    @cached_property
    def is_manager(self) -> bool:
        return PortfolioRole.is_manager(self.request.user.profile)

    @cached_property
    def is_portfolio_manager(self) -> bool:
        return PortfolioRole.is_portfolio_manager(
            self.request.user.profile, portfolio=self.portfolio_or_none, instrument=self.instrument_or_none
        )

    @cached_property
    def is_analyst(self) -> bool:
        return PortfolioRole.is_analyst(
            self.request.user.profile, portfolio=self.portfolio_or_none, instrument=self.instrument_or_none
        )

    @cached_property
    def has_portfolio_access(self) -> bool:
        return self.is_portfolio_manager or self.is_analyst
