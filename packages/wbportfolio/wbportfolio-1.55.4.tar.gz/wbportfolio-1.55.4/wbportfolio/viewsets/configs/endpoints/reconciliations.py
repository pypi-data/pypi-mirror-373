from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbportfolio.models.reconciliations.account_reconciliations import (
    AccountReconciliation,
)


class AccountReconciliationEndpointViewConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        if self.view.kwargs.get("pk"):
            return None
        return super().get_instance_endpoint(**kwargs)

    def get_delete_endpoint(self, **kwargs):
        return None


class AccountReconciliationLineEndpointViewConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return None

    def get_update_endpoint(self, **kwargs):
        if accountreconciliation_id := self.view.kwargs.get("accountreconciliation_id"):
            if AccountReconciliation.objects.filter(id=accountreconciliation_id, approved_dt__isnull=False).exists():
                return None
        return super().get_endpoint()
