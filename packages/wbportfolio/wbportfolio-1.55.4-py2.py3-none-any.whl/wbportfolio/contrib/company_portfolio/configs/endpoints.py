from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class AssetAllocationModelEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if company_id := self.view.kwargs.get("company_id", None):
            return reverse(
                "company_portfolio:companyassetallocation-list",
                kwargs={"company_id": company_id},
                request=self.request,
            )
        return reverse("company_portfolio:assetallocation-list", request=self.request)

    def get_create_endpoint(self, **kwargs):
        if company_id := self.view.kwargs.get("company_id", None):
            return f"{reverse('company_portfolio:companyassetallocation-list', kwargs={'company_id': company_id}, request=self.request)}?company={company_id}"
        return super().get_create_endpoint(**kwargs)


class GeographicFocusModelEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if company_id := self.view.kwargs.get("company_id", None):
            return reverse(
                "company_portfolio:companygeographicfocus-list",
                kwargs={"company_id": company_id},
                request=self.request,
            )
        return reverse("company_portfolio:geographicfocus-list", request=self.request)

    def get_create_endpoint(self, **kwargs):
        if company_id := self.view.kwargs.get("company_id", None):
            return f"{reverse('company_portfolio:companygeographicfocus-list', kwargs={'company_id': company_id}, request=self.request)}?company={company_id}"
        return super().get_create_endpoint(**kwargs)
