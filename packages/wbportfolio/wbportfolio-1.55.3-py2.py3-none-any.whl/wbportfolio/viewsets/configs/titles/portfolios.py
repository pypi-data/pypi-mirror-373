from wbcore.metadata.configs.titles import TitleViewConfig

from wbportfolio.models.portfolio import Portfolio


class PortfolioTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Portfolios"

    def get_instance_title(self):
        return "Portfolio {{name}}"

    def get_create_title(self):
        return "New Portfolio"


class DailyPortfolioCashFlowTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if portfolio_id := self.view.kwargs.get("portfolio_id", None):
            portfolio = Portfolio.objects.get(id=portfolio_id)
            return f"{portfolio}: Daily Portfolio Cash Flow"
        return "Daily Portfolio Cash Flow"


class PortfolioTreeGraphChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        portfolio = self.view.portfolio
        return f"Tree Graph Chart for {portfolio}"


class TopDownPortfolioCompositionPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        portfolio = self.view.portfolio
        return f"Top-Down Composition for {portfolio}"
