from wbcore.metadata.configs.titles import TitleViewConfig
from wbfdm.models import Instrument

from wbportfolio.models import Portfolio


class AssetPositionTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Asset Position"


class AssetPositionPortfolioTitleConfig(TitleViewConfig):
    def get_list_title(self):
        portfolio = Portfolio.objects.get(id=self.view.kwargs["portfolio_id"])
        return f"Asset Positions for Portfolio: {str(portfolio)}"


class AssetPositionInstrumentTitleConfig(TitleViewConfig):
    def get_list_title(self):
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"Implemented Portfolios for Instrument: {instrument.computed_str}"


class ContributorPortfolioChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        portfolio = Portfolio.objects.get(id=self.view.kwargs["portfolio_id"])
        return f"Contributors: {str(portfolio)}"


class AssetPositionUnderlyingInstrumentChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Allocation charts"


class CashPositionPortfolioTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Cash Positions per Portfolio"


class DistributionChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        portfolio = Portfolio.objects.get(id=self.view.kwargs["portfolio_id"])
        return f"Distribution Chart - {str(portfolio)}"


class DistributionTableTitleConfig(TitleViewConfig):
    def get_list_title(self):
        portfolio = Portfolio.objects.get(id=self.view.kwargs["portfolio_id"])
        return f"Distribution Table - {str(portfolio)}"


class CompositionModelPortfolioPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        portfolio = Portfolio.objects.get(id=self.view.kwargs["portfolio_id"])
        if instrument_id := self.request.GET.get("portfolio_instrument"):
            instrument = Instrument.objects.get(id=instrument_id)
            return f"Composition between {str(portfolio)} and instrument portfolio {str(instrument)}"
        return f"Composition between {str(portfolio)} and related portfolios"
