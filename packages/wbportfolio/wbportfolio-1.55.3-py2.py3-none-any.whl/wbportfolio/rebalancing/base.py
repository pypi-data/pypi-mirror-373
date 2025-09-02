from datetime import date

from wbportfolio.pms.typing import Portfolio as PortfolioDTO


class AbstractRebalancingModel:
    @property
    def validation_errors(self) -> str:
        return getattr(self, "_validation_errors", "Rebalacing cannot applied for these parameters")

    def __init__(
        self,
        portfolio,
        trade_date: date,
        last_effective_date: date,
        effective_portfolio: PortfolioDTO | None = None,
        **kwargs,
    ):
        self.portfolio = portfolio
        self.trade_date = trade_date
        self.last_effective_date = last_effective_date
        self.effective_portfolio = effective_portfolio
        # we try to get the portfolio at the trade date
        if not self.effective_portfolio:
            self.effective_portfolio = self.portfolio._build_dto(self.last_effective_date)

    def is_valid(self) -> bool:
        return True

    def get_target_portfolio(self) -> PortfolioDTO:
        raise NotImplementedError()
