import logging
from datetime import datetime

from django.conf import settings
from requests import HTTPError

from wbportfolio.api_clients.ubs import UBSNeoAPIClient
from wbportfolio.pms.typing import Order

from .. import ExecutionStatus, RoutingException
from . import BaseCustodianAdapter

ASSET_CLASS_MAP = {Order.AssetType.EQUITY: "EQUITY"}  # API can support BOND, FUTURE, OPTION, and DYNAMIC_STRATEGY
ASSET_CLASS_MAP_INV = {
    v: k for k, v in ASSET_CLASS_MAP.items()
}  # API can support BOND, FUTURE, OPTION, and DYNAMIC_STRATEGY

STATUS_MAP = {
    "Amend Pending": ExecutionStatus.PENDING,
    "Cancel Pending": ExecutionStatus.PENDING,
    "Cancelled": ExecutionStatus.PENDING,
    "Complete": ExecutionStatus.PENDING,
    "Complete (Order Cancelled)": ExecutionStatus.PENDING,
    "Complete (Partial Fill)": ExecutionStatus.PENDING,
    "In Draft": ExecutionStatus.PENDING,
    "Pending Approval": ExecutionStatus.PENDING,
    "Pending Execution": ExecutionStatus.PENDING,
    "Rebalance Cancelled": ExecutionStatus.PENDING,
    "Rebalance Cancelled (Executing partially)": ExecutionStatus.PENDING,
    "Rejected": ExecutionStatus.PENDING,
    "Rejection Acknowledged": ExecutionStatus.PENDING,
    "Waiting for Response": ExecutionStatus.PENDING,
}
logger = logging.getLogger("oms")


def _serialize_orders(orders: list[Order], default_execution_instruction=None) -> list[dict[str, str]]:
    items = []
    for order in orders:
        if order.refinitiv_identifier_code:
            identifier_type, identifier = "RIC", order.refinitiv_identifier_code
        elif order.bloomberg_ticker:
            identifier_type, identifier = "BBTICKER", order.bloomberg_ticker
        else:
            identifier_type, identifier = "SEDOL", order.sedol
        item = {
            "assetClass": ASSET_CLASS_MAP[order.asset_class],
            "identifierType": identifier_type,
            "identifier": identifier,
            "executionInstruction": order.execution_instruction
            if order.execution_instruction
            else default_execution_instruction,
            "userElementId": str(order.id),
            "tradeDate": order.trade_date.strftime("%Y-%m-%d"),
        }
        if order.shares:
            item["sharesToTrade"] = str(order.shares)
        else:
            item["targetWeight"] = str(order.target_weight)
        items.append(item)
    return items


def _deserialize_items(items: list[dict[str, str]]):
    orders = []
    for item in items:
        orders.append(
            Order(
                id=item.get("userElementId"),
                asset_class=ASSET_CLASS_MAP_INV[item.get("assetClass")],
                refinitiv_identifier_code=item.get(
                    "ric", item["identifier"] if item.get("identifierType") == "RIC" else None
                ),
                bloomberg_ticker=item["identifier"] if item.get("identifierType") == "BBTICKER" else None,
                sedol=item["identifier"] if item.get("identifierType") == "SEDOL" else None,
                trade_date=datetime.strptime(item.get("tradeDate"), "%Y-%m-%d"),
                target_weight=float(item["targetWeight"]) if "targetWeight" in item else None,
                shares=float(item["sharesToTrade"]) if "sharesToTrade" in item else None,
                execution_instruction=item.get("executionInstruction"),
            )
        )
    return orders


class CustodianAdapter(BaseCustodianAdapter):
    client: UBSNeoAPIClient

    def __init__(self, *args, raise_exception: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.raise_exception = raise_exception

    def _handle_response(self, res):
        logger.info(res["message"])
        if errors := res.get("errors"):
            logger.warning(errors)
            if self.raise_exception:
                raise RoutingException(errors)

    def authenticate(self) -> bool:
        """
        Authenticate or renew tokens with the custodian API.
        Raises an exception if authentication fails.
        """
        self.client = UBSNeoAPIClient(settings.UBS_NEO_API_TOKEN)
        return True

    def get_rebalance_status(self) -> tuple[ExecutionStatus, str]:
        res = self.client.get_rebalance_status_for_isin(self.isin)
        self._handle_response(res)
        status = res["rebalanceStatus"]
        return STATUS_MAP.get(status, ExecutionStatus.UNKNOWN), status

    def is_valid(self) -> bool:
        """
        Check whether the given isin is valid and can be rebalanced
        """

        try:
            status_res = self.client.get_rebalance_service_status()

            isin_res = self.client.get_rebalance_status_for_isin(self.isin)
            self._handle_response(status_res)
            self._handle_response(isin_res)
            return (
                status_res["status"] == UBSNeoAPIClient.SUCCESS_VALUE
                and isin_res["status"] == UBSNeoAPIClient.SUCCESS_VALUE
            )
        except (HTTPError, KeyError) as e:
            logger.warning(f"Couldn't validate adapter: {str(e)}")
            return False

    def submit_rebalancing(self, orders: list[Order], as_draft: bool = True) -> tuple[list[Order], str]:
        """
        Submit a rebalance order for the certificate.
        """
        items = _serialize_orders(orders, default_execution_instruction="MARKET_ON_CLOSE")
        if not as_draft:
            res = self.client.submit_rebalance(self.isin, items)
        else:
            res = self.client.save_draft(self.isin, items)
        self._handle_response(res)
        return _deserialize_items(res["rebalanceItems"]), res["message"]

    def cancel_current_rebalancing(self) -> bool:
        """
        Cancel an existing rebalance order identified by ISIN.
        """
        try:
            res = self.client.cancel_rebalance(self.isin)
            self._handle_response(res)
            return res["status"] == UBSNeoAPIClient.SUCCESS_VALUE
        except (HTTPError, KeyError):
            return False

    def get_current_rebalancing(self) -> list[Order]:
        """
        Fetch the current rebalance request details for a certificate.
        """
        res = self.client.get_current_rebalance_request(self.isin)
        self._handle_response(res)
        return _deserialize_items(res["rebalanceItems"])
