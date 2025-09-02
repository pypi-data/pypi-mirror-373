from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class TradeEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:trade-list", args=[], request=self.request)

    # def get_instance_endpoint(self, **kwargs):
    #     try:
    #         if self.request.user.has_perm("wbportfolio.administrate_trade"):
    #             obj = self.view.get_object()
    #             return reverse("wbportfolio:trade-detail", args=[obj.id], request=self.request)
    #     except AssertionError:
    #         pass
    #     return reverse("wbportfolio:trade-list", request=self.request)

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class TradeInstrumentEndpointConfig(TradeEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:instrument-trade-list", args=[self.view.kwargs["instrument_id"]], request=self.request
        )


class TradePortfolioEndpointConfig(TradeEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:portfolio-trade-list", args=[self.view.kwargs["portfolio_id"]], request=self.request
        )


class CustodianDistributionInstrumentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:instrument-custodiandistribution-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class SubscriptionRedemptionEndpointConfig(TradeEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:subscriptionredemption-list", args=[], request=self.request)
