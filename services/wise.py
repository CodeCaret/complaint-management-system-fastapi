import uuid

import requests
from decouple import config
from fastapi import HTTPException, status


class WiseService:

    def __init__(self):
        self.main_url = config("WISE_URL")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config('WISE_TOKEN')}",
            "Accept-Minor-Version": "1",
        }

        self.profile_id = self._get_profile_id()

    def _get_profile_id(self):
        url = self.main_url + "/2026Q3/profiles"

        resp = requests.get(url, headers=self.headers)

        # print("PROFILE STATUS:", resp.status_code)
        # print("PROFILE BODY:", resp.text)

        if resp.status_code == 200:
            profiles = resp.json()

            for profile in profiles:
                if profile["type"] == "PERSONAL":
                    return profile["id"]

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve Wise profile",
        )

    def create_quote(self, amount):
        url = self.main_url + f"/2026Q3/profiles/{self.profile_id}/quotes"

        data = {
            "sourceCurrency": "EUR",
            "targetCurrency": "EUR",
            "sourceAmount": amount,
            "targetAmount": None,
            "targetAccount": None,
            "preferredPayIn": "BALANCE",
            "payOut": "BANK_TRANSFER",
        }

        resp = requests.post(url, headers=self.headers, json=data)

        # print("QUOTE STATUS:", resp.status_code)
        # print("QUOTE BODY:", resp.text)

        if resp.status_code in (200, 201):
            return resp.json()["id"]

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create Wise quote",
        )

    def create_recipient_account(self, full_name, iban):
        url = self.main_url + "/2026Q3/accounts"

        data = {
            "currency": "EUR",
            "type": "iban",
            "profile": self.profile_id,
            "accountHolderName": full_name,
            "details": {
                "legalType": "PRIVATE",
                "iban": iban,
            },
        }

        resp = requests.post(url, headers=self.headers, json=data)

        # print("RECIPIENT STATUS:", resp.status_code)
        # print("RECIPIENT BODY:", resp.text)

        if resp.status_code in (200, 201):
            return resp.json()["id"]

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create Wise recipient",
        )

    def create_transfer(self, target_account_id, quote_id):
        url = self.main_url + "/2026Q3/transfers"

        customer_transaction_id = str(uuid.uuid4())

        data = {
            "targetAccount": target_account_id,
            "quoteUuid": quote_id,
            "customerTransactionId": customer_transaction_id,
        }

        resp = requests.post(url, headers=self.headers, json=data)

        # print("TRANSFER STATUS:", resp.status_code)
        # print("TRANSFER BODY:", resp.text)

        if resp.status_code in (200, 201):
            return resp.json()["id"]

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create Wise transfer",
        )

    def fund_transfer(self, transfer_id):
        url = (
            self.main_url
            + f"/2026Q3/profiles/{self.profile_id}"
            + f"/transfers/{transfer_id}/payments"
        )

        data = {
            "type": "BALANCE",
            "balanceId": config("WISE_EUR_BALANCE_ID", cast=int),
        }

        resp = requests.post(url, headers=self.headers, json=data)

        # print("FUND STATUS:", resp.status_code)
        # print("FUND BODY:", resp.text)

        # Successful funding
        if resp.status_code in (200, 201):
            return resp.json()

        # Wise requires SCA
        if (
            resp.status_code == 403
            and resp.headers.get("x-2fa-approval-result") == "REJECTED"
            and resp.headers.get("x-2fa-approval")
        ):
            return {
                "status": "SCA_REQUIRED",
                "message": "Wise transfer funding requires Strong Customer Authentication.",
            }

        # Other Wise errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fund Wise transfer",
        )

    def cancel_transfer(self, transfer_id):
        url = self.main_url + f"/2026Q3/transfers/{transfer_id}/cancel"

        resp = requests.put(url, headers=self.headers)

        # print("CANCEL STATUS:", resp.status_code)
        # print("CANCEL BODY:", resp.text)

        if resp.status_code == 200:
            return resp.json()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not cancel Wise transfer",
        )
