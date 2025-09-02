## this is a bare bones unofficial python library for the ecocash api by Tarmica Sean Chiwara
### the library aims to makes it easier for python devs (especially newbies) to rapidly integrate with the ecocash api using pythonic idioms they are already familiar with.

__version__ = "0.0.4"

import requests
import uuid
import logging
from typing import Optional, Dict, Any

# ========================
# Logging setup
# ========================
logger = logging.getLogger("Ecocash")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class EcoCash:
    """
    Simple, intuitive Python library for Ecocash Open API.
    Supports Payments, Refunds, and Transaction Lookup.
    """

    BASE_URL = "https://developers.ecocash.co.zw/api/ecocash_pay"

    def __init__(self, app_id: str, api_key: str, merchant_code: str, app_name: str, sandbox: bool = True):
        """
        Initialize Ecocash API client.

        Args:
            app_id (str): Your application ID.
            api_key (str): Your Ecocash API key.
            merchant_code (str): Your merchant code.
            app_name (str): Name of your app.
            sandbox (bool, optional): Use sandbox or live API. Defaults to True.
        """
        self.app_id = app_id
        self.api_key = api_key
        self.merchant_code = merchant_code
        self.app_name = app_name
        self.sandbox = sandbox
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info(f"Ecocash client initialized in {'sandbox' if sandbox else 'live'} mode.")

    def _url(self, endpoint: str) -> str:
        env = "sandbox" if self.sandbox else "live"
        return f"{self.BASE_URL}{endpoint}/{env}"

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url(endpoint)
        logger.info(f"POST Request: {url} with payload {payload}")
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            try:
                # Attempt to parse JSON
                data = response.json()
            except ValueError:
                # Handle empty or non-JSON responses gracefully because last time that gave me a headache!
                logger.warning(f"Empty or non-JSON response: {response.text}")
                data = {"status_code": response.status_code, "response_text": response.text}
            logger.info(f"Response: {data}")
            return data
        except requests.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return {"error": str(e)}


    # ========================
    # Payments
    # ========================
    def payment(self, customer_msisdn: str, amount: float, reason: str,
                currency: str = "USD", source_reference: Optional[str] = None) -> Dict[str, Any]:
        """
        Initiate a C2B payment.

        Args:
            customer_msisdn (str): Customer mobile number.
            amount (float): Amount to charge.
            reason (str): Reason for payment.
            currency (str, optional): Currency. Defaults to "USD".
            source_reference (str, optional): UUID reference. Auto-generated if None.

        Returns:
            dict: API response.
        """
        if not source_reference:
            source_reference = str(uuid.uuid4())
            logger.info(f"Generated sourceReference: {source_reference}")

        payload = {
            "customerMsisdn": customer_msisdn,
            "amount": amount,
            "reason": reason,
            "currency": currency,
            "sourceReference": source_reference
        }
        return self._post("/api/v2/payment/instant/c2b", payload)

    # ========================
    # Refunds
    # ========================
    def refund(self, original_reference: str, refund_corelator: str, source_mobile: str,
               amount: float, client_name: str, currency: str, reason_for_refund: str) -> Dict[str, Any]:
        """
        Initiate a refund.

        Args:
            original_reference (str): Original transaction UUID.
            refund_corelator (str): Refund identifier.
            source_mobile (str): Customer mobile number.
            amount (float): Refund amount.
            client_name (str): Merchant/client name.
            currency (str): Currency code.
            reason_for_refund (str): Reason for refund.

        Returns:
            dict: API response.
        """
        payload = {
            "origionalEcocashTransactionReference": original_reference,
            "refundCorelator": refund_corelator,
            "sourceMobileNumber": source_mobile,
            "amount": amount,
            "clientName": client_name,
            "currency": currency,
            "reasonForRefund": reason_for_refund
        }
        return self._post("/api/v2/refund/instant/c2b", payload)

    # ========================
    # Transaction Lookup
    # ========================
    def transaction_status(self, source_mobile: str, source_reference: str) -> Dict[str, Any]:
        """
        Lookup a transaction by mobile number and source reference.

        Args:
            source_mobile (str): Customer mobile number.
            source_reference (str): Transaction UUID.

        Returns:
            dict: API response.
        """
        payload = {
            "sourceMobileNumber": source_mobile,
            "sourceReference": source_reference
        }
        return self._post("/api/v1/transaction/c2b/status", payload)


