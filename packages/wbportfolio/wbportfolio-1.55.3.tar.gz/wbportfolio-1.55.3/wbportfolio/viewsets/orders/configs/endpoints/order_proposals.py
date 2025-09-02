from django.shortcuts import get_object_or_404
from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbportfolio.models import OrderProposal


class OrderProposalEndpointConfig(EndpointViewConfig):
    def get_delete_endpoint(self, **kwargs):
        if pk := self.view.kwargs.get("pk", None):
            order_proposal = get_object_or_404(OrderProposal, pk=pk)
            if order_proposal.status == OrderProposal.Status.DRAFT:
                return super().get_endpoint()
        return None


class OrderProposalPortfolioEndpointConfig(OrderProposalEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbportfolio:portfolio-orderproposal-list", args=[self.view.kwargs["portfolio_id"]], request=self.request
        )
