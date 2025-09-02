from wbcore.metadata.configs.titles import TitleViewConfig
from wbfdm.models import Instrument

from wbportfolio.models import Portfolio


class TradeTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if self.request.GET.get("is_customer_trade", "False") == "True":
            return "Subscription / Redemption"
        return "Trade"

    def get_instance_title(self):
        return "Trade: {{shares}} {{bank}} - {{transaction_date}} ({{_product.name}})"

    def get_create_title(self):
        return "New Trade"


class TradeInstrumentTitleConfig(TradeTitleConfig):
    def get_list_title(self):
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"Trades of Instrument {instrument.name} ({instrument.isin})"


class TradePortfolioTitleConfig(TradeTitleConfig):
    def get_list_title(self):
        portfolio = Portfolio.objects.get(id=self.view.kwargs["portfolio_id"])
        return f"Trades within Portfolio {str(portfolio)})"


class CustodianDistributionInstrumentTitleConfig(TitleViewConfig):
    def get_list_title(self):
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"Custodians Distribution {instrument.computed_str}"


class CustomerDistributionInstrumentTitleConfig(TitleViewConfig):
    def get_list_title(self):
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"Customer Distribution {instrument.computed_str}"


class SubscriptionRedemptionTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if instrument_id := self.view.kwargs.get("instrument_id", None):
            instrument = Instrument.objects.get(id=instrument_id)
            return f"Subscription / Redemption of {instrument.computed_str}"
        return "Subscription / Redemption"

    def get_instance_title(self):
        return "Subscription / Redemption: {{shares}} {{bank}} - {{transaction_date}} ({{_product.name}})"
