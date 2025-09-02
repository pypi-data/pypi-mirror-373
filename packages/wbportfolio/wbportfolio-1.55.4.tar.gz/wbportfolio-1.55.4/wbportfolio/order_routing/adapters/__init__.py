from abc import ABC, abstractmethod

from wbportfolio.order_routing import ExecutionStatus
from wbportfolio.pms.typing import Order

class BaseCustodianAdapter(ABC):

    def __init__(self, isin: str, **identifiers):
        self.isin = isin

    @property
    def errors(self):
        if not hasattr(self, '_errors'):
            raise ValueError("is_valid needs to call before accessing errors")
        return
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate or renew tokens with the custodian API.
        Raises an exception if authentication fails.
        """
        pass

    @abstractmethod
    def get_rebalance_status(self) -> tuple[ExecutionStatus, str]:
        """
        Return the rebalance status as a string (in the custodian format)
        """
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """
        Check whether the given isin is valid and can be rebalanced
        """
        pass

    @abstractmethod
    def submit_rebalancing(self, orders: list[Order], as_draft: bool = True) -> tuple[list[Order], str]:
        """
        Submit a rebalance order for the certificate.
        """
        pass

    @abstractmethod
    def cancel_current_rebalancing(self) -> bool:
        """
        Cancel an existing rebalance order identified by ISIN.
        """
        pass

    @abstractmethod
    def get_current_rebalancing(self) -> list[Order]:
        """
        Fetch the current rebalance request details for a certificate.
        """
        pass
