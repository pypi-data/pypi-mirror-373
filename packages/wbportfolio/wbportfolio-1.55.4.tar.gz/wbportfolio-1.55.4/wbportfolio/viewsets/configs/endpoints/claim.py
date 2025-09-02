from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbportfolio.models.transactions.claim import Claim


class ClaimEndpointConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        if self.request.user.has_perm("wbportfolio.change_claim"):
            try:
                obj = self.view.get_object()
                if obj.status == Claim.Status.DRAFT:
                    return reverse("wbportfolio:claim-detail", args=[obj.id], request=self.request)
            except AssertionError:
                return reverse("wbportfolio:claim-list", request=self.request)
        return None

    def get_delete_endpoint(self, **kwargs):
        if self.request.user.has_perm("wbportfolio.change_claim"):
            try:
                obj = self.view.get_object()
                if obj.status == Claim.Status.WITHDRAWN:
                    return reverse("wbportfolio:claim-detail", args=[obj.id], request=self.request)
            except AssertionError:
                pass
        return None

    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:claim-list", request=self.request)


class ClaimProductEndpointConfig(ClaimEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:product-claim-list",
            args=[self.view.kwargs["product_id"]],
            request=self.request,
        )


class ClaimAccountEndpointConfig(ClaimEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:account-claim-list",
            args=[self.view.kwargs["account_id"]],
            request=self.request,
        )


class ClaimEntryEndpointConfig(ClaimEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:entry-claim-list",
            args=[self.view.kwargs["entry_id"]],
            request=self.request,
        )


class ClaimTradeEndpointConfig(ClaimEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:trade-claim-list",
            args=[self.view.kwargs["trade_id"]],
            request=self.request,
        )


class ConsolidatedTradeSummaryEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class ConsolidatedTradeSummaryDistributionChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:consolidatedtradesummarydistributionchart-list", request=self.request)


class CumulativeNNMChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbportfolio:cumulativennmchart-list", request=self.request)


class ProfitAndLossPandasEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class NegativeTermimalAccountPerProductEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        return None

    def _get_instance_endpoint(self, **kwargs):
        return (
            reverse("wbportfolio:claim-list", request=self.request) + "?account={{account_id}}&product={{product_id}}"
        )
