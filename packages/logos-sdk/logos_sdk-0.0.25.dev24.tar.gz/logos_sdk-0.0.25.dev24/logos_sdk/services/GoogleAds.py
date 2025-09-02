from requests.exceptions import Timeout
from typing import List, Union, Dict
from logos_sdk.services import get_headers, get_retry_session
from http import HTTPStatus
from dotenv import load_dotenv
import os
import time
import random


class GoogleAdsServiceException(Exception):
    pass


class GoogleAdsService:
    def __init__(self, url=None):
        load_dotenv()
        self.session = get_retry_session()
        self._URL = url or os.environ.get("GOOGLE_ADS_SERVICE_PATH")
        self._SEARCH_STREAM = self._URL + "/search-stream"
        self._SEARCH = self._URL + "/search"
        self._EXCLUDE_FOR_ACCOUNT = self._URL + "/exclude-for-account"
        self._EXCLUDE_FOR_AD_GROUP = self._URL + "/exclude-for-ad-group"
        self._GET_ACCESSIBLE_ACCOUNTS = self._URL + "/list-accessible-accounts"
        self._GET_ACCOUNT_ACCESSIBILITY = self._URL + "/get-account-accessibility"
        self._MUTATE_BIDDING_SEASONALITY_ADJUSTMENT = self._URL + "/mutate-bidding-seasonality-adjustment"

    def fetch_with_retry_on_timeout(self, url, json, headers):
        for attempt in range(5):
            try:
                return self.session.request("post", url, json=json, headers=headers, timeout=25)
            except Timeout:
                delay = 2 * (2 ** attempt) + random.randint(0, 9)
                print(
                    f"there was a timeout when contacting the service, going to sleep for {delay} seconds"
                )
                time.sleep(delay)

        raise Exception("The service is not able to reply within 30 seconds.")

    def search_stream(
            self,
            query: str,
            queried_account_id: str,
            secret_id: str,
    ) -> List[Union[List, Dict]]:
        """
        :param query Sql query for google ads. Best way to build it is https://developers.google.com/google-ads/api/fields/v14/accessible_bidding_strategy_query_builder
        :param queried_account_id Google ads id of queried account
        :param secret_id The ID of the secret in secret manager
        :return: List(List)
        """
        body = {
            "query": query,
            "queried_account_id": queried_account_id,
            "secret_id": secret_id,
        }

        header = get_headers(self._SEARCH_STREAM)
        response = self.fetch_with_retry_on_timeout(
            url=self._SEARCH_STREAM, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise GoogleAdsServiceException(response.content)

    def search(
            self,
            query: str,
            queried_account_id: str,
            secret_id: str,
            page_size: int,
    ) -> List[Dict]:
        """
        :param query Sql query for google ads. Best way to build it is https://developers.google.com/google-ads/api/fields/v14/accessible_bidding_strategy_query_builder
        :param queried_account_id Google ads id of queried account
        :param secret_id The ID of the secret in secret manager
        :param page_size Size of page for results
        :return {"next_page_token": token, results: list of dict where key for each dict is "metrics" and then metric type from query}
        """
        body = {
            "query": query,
            "queried_account_id": queried_account_id,
            "secret_id": secret_id,
            "page_token": None,
            "page_size": page_size,
        }

        header = get_headers(self._SEARCH)
        response = self.fetch_with_retry_on_timeout(
            url=self._SEARCH, json=body, headers=header
        )

        if response.status_code != HTTPStatus.OK:
            raise GoogleAdsServiceException(response.content)

        service_response = response.json()
        yield service_response["data"]["results"]

        # if there was a last page response is empty string
        while service_response["data"]["next_page_token"]:
            body["page_token"] = service_response["data"]["next_page_token"]
            response = self.session.request("post", url=self._SEARCH, json=body, headers=header)

            if response.status_code != HTTPStatus.OK:
                raise GoogleAdsServiceException(response.content)

            service_response = response.json()
            yield service_response["data"]["results"]

    def exclude_criterion_for_account(
            self, account_id: str, placements: List[Dict], secret_id: str = None
    ) -> List[Dict]:
        """
        Excludes list of unwanted urls/YouTube channels for account with client_id
        :param account_id: Google Ads id without -
        :param placements: list of  records {value :negative urls/YouTube channels, type: placement type}
        :param secret_id: id of the secret
        :return: list of resource names
        """
        body = {
            "account_id": account_id,
            "placements": placements,
            "secret_id": secret_id,
        }

        header = get_headers(self._EXCLUDE_FOR_ACCOUNT)
        response = self.session.request(
            "post", url=self._EXCLUDE_FOR_ACCOUNT, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise GoogleAdsServiceException(response.content)

    def exclude_criterion_for_ad_group(
            self,
            client_id: str,
            ad_group_id: str,
            exclusion_raw: List[str],
            secret_id: str = None,
    ) -> None:
        """
        Excludes list of unwanted urls/YouTube channels for given ad_group with client_id
        :param client_id: Google Ads id without -
        :param ad_group_id: given ad group id for which urls should be excluded
        :param exclusion_raw: list of negative urls/YouTube channels
        :param secret_id: id of the secret
        :return:None
        """
        body = {
            "client_id": client_id,
            "exclusion_raw": exclusion_raw,
            "ad_group_id": ad_group_id,
            "secret_id": secret_id,
        }

        header = get_headers(self._EXCLUDE_FOR_AD_GROUP)
        response = self.session.request(
            "post", url=self._EXCLUDE_FOR_AD_GROUP, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            return
        else:
            raise GoogleAdsServiceException(response.content)

    def get_accessible_accounts(
            self,
            secret_id: str,
            page_size: int = 1000,
    ) -> List[Dict]:
        body = {
            "secret_id": secret_id,
            "filters": {
                "hide_inactive": True,
            },
            "page_token": None,
            "page_size": page_size,
        }

        header = get_headers(self._GET_ACCESSIBLE_ACCOUNTS)
        response = self.fetch_with_retry_on_timeout(
            url=self._GET_ACCESSIBLE_ACCOUNTS, json=body, headers=header
        )

        if response.status_code != HTTPStatus.OK:
            raise GoogleAdsServiceException(response.content)

        service_response = response.json()
        all_results = service_response["data"]["results"]

        while service_response["data"]["next_page_token"]:
            body["page_token"] = service_response["data"]["next_page_token"]
            response = self.session.request(
                "post", url=self._GET_ACCESSIBLE_ACCOUNTS, json=body, headers=header
            )

            if response.status_code != HTTPStatus.OK:
                raise GoogleAdsServiceException(response.content)

            service_response = response.json()
            all_results.extend(service_response["data"]["results"])

        return all_results

    def mutate_bidding_seasonality_adjustment(
            self,
            client_id: str,
            create: List[Dict],
            delete: List[str],
            secret_id: str = None,
    ) -> None:
        """
        Mutate bidding seasonality of given account
        :param client_id: Google Ads id without -
        :param create: list of bidding seasonality adjustments to create
        :param delete: list of bidding seasonality adjustments to delete
        :param secret_id: id of the secret
        :return:None
        """
        body = {
            "account_id": client_id,
            "create": create,
            "delete": delete,
            "secret_id": secret_id,
        }

        header = get_headers(self._MUTATE_BIDDING_SEASONALITY_ADJUSTMENT)
        response = self.session.request(
            "post", url=self._MUTATE_BIDDING_SEASONALITY_ADJUSTMENT, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            return
        else:
            raise GoogleAdsServiceException(response.content)

    def get_account_accessibility(self, secret_id: str, account_id: str) -> bool:
        """
        Gets account accessibility
        :param secret_id: The ID of the secret in secret manager
        :param account_id: The ID of the account.
        :return: True if account has access
        """
        body = {
            "secret_id": secret_id,
            "account_id": account_id
        }
        header = get_headers(self._GET_ACCOUNT_ACCESSIBILITY)
        response = self.session.request(
            "post", url=self._GET_ACCOUNT_ACCESSIBILITY, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise GoogleAdsServiceException(response.content)
