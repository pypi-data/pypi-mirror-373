from datetime import date, datetime, timedelta
from json import JSONDecodeError

import requests
from django.conf import settings
from django.utils import timezone
from requests import HTTPError


class UBSNeoAPIClient:
    BASE_URL = "https://neo.ubs.com/api"
    SUCCESS_VALUE = "SUCCESS"
    VIRTUAL_AMC_ISIN = "TEST_API_001"

    def __init__(
        self,
        initial_jwt_token: str,
        jwt_token_expiry_timestamp: datetime | None = None,
        default_execution_instruction: str = "MARKET_ON_CLOSE",
    ):
        """
        :param service_account_id: Identifier for your UBS service account (for reference).
        :param initial_jwt_token: JWT token string initially provided to authenticate API calls.
        :param jwt_token_expiry_timestamp: UNIX timestamp when the token expires - to manage renewal.
        """
        self.jwt_token = initial_jwt_token
        self.jwt_token_expiry = (
            jwt_token_expiry_timestamp if jwt_token_expiry_timestamp else timezone.now() + timedelta(days=1)
        )
        self.default_execution_instruction = default_execution_instruction

    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or near expiry (e.g. within 5 minutes)."""
        return timezone.now() > self.jwt_token_expiry - timedelta(minutes=5)

    def _renew_token(self):
        """
        Placeholder: Implement token renewal logic here.
        This usually involves interacting with UBS Neo application or token service
        before expiry to obtain a new token. This must be customized per your process.
        """
        raise ValueError("Token has expired. Please go to https://neo.ubs.com/ and renew it.")

    def _get_headers(self) -> dict[str, str]:
        """Prepare HTTP headers including Authorization bearer token."""
        if self._is_token_expired():
            self._renew_token()
        return {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}

    def _get_json(self, response) -> dict:
        try:
            return response.json()
        except JSONDecodeError:
            return dict()

    def _validate_isin(self, isin: str, test: bool = False) -> str:
        # ensure the given isin can be used for rebalancing (e.g. debug or dev mode)
        if test or settings.DEBUG:
            return self.VIRTUAL_AMC_ISIN
        return isin

    def _raise_for_status(self, response):
        try:
            response.raise_for_status()
        except HTTPError:
            json_response = response.json()
            raise HTTPError(json_response.get("errors", json_response.get("message")))

    def get_rebalance_service_status(self) -> dict:
        """Check API connection status."""
        url = f"{self.BASE_URL}/ged-amc/external/rebalance/v1/status"
        response = requests.get(url, headers=self._get_headers())
        self._raise_for_status(response)
        return self._get_json(response)

    def get_rebalance_status_for_isin(self, isin: str) -> dict:
        """Check certificate accessibility and workflow status for given ISIN."""
        url = f"{self.BASE_URL}/ged-amc/external/rebalance/v1/status/{isin}"
        response = requests.get(url, headers=self._get_headers())
        self._raise_for_status(response)
        return self._get_json(response)

    def submit_rebalance(self, isin: str, items: list[dict[str, str]], test: bool = False) -> dict:
        """
        Submit a rebalance request.
        :param isin: Certificate ISIN string.
        :param orders: List of dto representing order instructions.
        :param test: If True, submits to test endpoint to validate syntax only (no persistence).
        """
        isin = self._validate_isin(isin, test=test)
        url = f"{self.BASE_URL}/ged-amc/external/rebalance/v1/submit/{isin}"
        payload = {"items": items}
        response = requests.post(url, json=payload, headers=self._get_headers())
        self._raise_for_status(response)
        return self._get_json(response)

    def save_draft(self, isin: str, items: list[dict[str, str]]) -> dict:
        """Save a rebalance draft."""
        isin = self._validate_isin(isin)
        url = f"{self.BASE_URL}/ged-amc/external/rebalance/v1/savedraft/{isin}"
        payload = {"items": items}
        response = requests.post(url, json=payload, headers=self._get_headers())
        self._raise_for_status(response)
        return self._get_json(response)

    def cancel_rebalance(self, isin: str) -> dict:
        """Cancel a rebalance request."""
        isin = self._validate_isin(isin)
        url = f"{self.BASE_URL}/ged-amc/external/rebalance/v1/cancel/{isin}"
        response = requests.delete(url, headers=self._get_headers())
        self._raise_for_status(response)
        return self._get_json(response)

    def get_current_rebalance_request(self, isin: str) -> dict:
        """Fetch the current rebalance request for a certificate."""
        url = f"{self.BASE_URL}/ged-amc/external/rebalance/v1/currentRebalanceRequest/{isin}"
        response = requests.get(url, headers=self._get_headers())
        self._raise_for_status(response)
        return self._get_json(response)

    def get_portfolio_at_date(self, isin: str, val_date: date) -> dict:
        url = f"https://neo.ubs.com/api/ged-amc/external/report/v1/valuation/{isin}/{val_date:%Y-%m-%d}"
        response = requests.get(url, headers=self._get_headers())
        self._raise_for_status(response)
        return self._get_json(response)

    def get_management_fees(self, isin: str, from_date: date, to_date: date) -> dict:
        url = f"https://neo.ubs.com/api/ged-amc/external/fee/v1/management/{isin}"
        response = requests.get(
            url,
            headers=self._get_headers(),
            params={"fromDate": from_date.strftime("%Y-%m-%d"), "toDate": to_date.strftime("%Y-%m-%d")},
        )
        self._raise_for_status(response)
        return self._get_json(response)

    def get_performance_fees(self, isin: str, from_date: date, to_date: date) -> dict:
        url = f"https://neo.ubs.com/api/ged-amc/external/fee/v1/performance/{isin}"
        response = requests.get(
            url,
            headers=self._get_headers(),
            params={"fromDate": from_date.strftime("%Y-%m-%d"), "toDate": to_date.strftime("%Y-%m-%d")},
        )
        self._raise_for_status(response)
        return self._get_json(response)

    def validate_response(self, response: dict) -> dict:
        if response.get("status", "") == self.SUCCESS_VALUE:
            return response
        return dict()
