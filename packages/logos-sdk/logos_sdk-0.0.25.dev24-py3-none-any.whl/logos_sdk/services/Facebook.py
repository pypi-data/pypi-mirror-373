from typing import List, Dict, Optional
from logos_sdk.services import get_headers, get_retry_session
from http import HTTPStatus
from random import randint
from dotenv import load_dotenv
import os
import time


class FacebookServiceException(Exception):
    pass


class FacebookService:
    def __init__(self, url=None):
        load_dotenv()
        self.session = get_retry_session()
        self._URL = url or os.environ.get("FACEBOOK_SERVICE_PATH")
        self._ACCESSIBLE_ACCOUNTS = self._URL + "/accessible-accounts"
        self._INSIGHTS = self._URL + "/insights"
        self._LINK_URLS = self._URL + "/link-urls"
        self._ACCESSIBLE_BUSINESSES = self._URL + "/accessible-businesses"
        self._PRODUCT_CATALOGS = self._URL + "/product-catalogs"
        self._PRODUCT_CATALOG = self._URL + "/product-catalog"
        self._PRODUCTS = self._URL + "/products"
        self._FEEDS = self._URL + "/feeds"
        self._FEED_ERRORS = self._URL + "/feed-errors"
        self._FEED_ERRORS_REPORT_STATUS = self._URL + "/feed-errors-report-status"
        self._FEED_ERRORS_REPORT = self._URL + "/feed-errors-report"
        self._GET_ACCOUNT_ACCESSIBILITY = self._URL + "/get-account-accessibility"
        self._ACCOUNT_ACTIVITIES = self._URL + "/account-activities-report"
        self._BUSINESS_USERS = self._URL + "/business-users"

    def get_accessible_accounts(
        self, secret_id: str, timeout: int = None
    ) -> List[Dict]:
        """
        Get all accessible accounts
        :param secret_id The ID of the secret in secret manager
        :param timeout Cut the request if it takes too long
        :return: all accessible accounts List(Dict)
        """

        body = {
            "secret_id": secret_id,
            "filters": {
                "hide_inactive": True,
            }
        }

        header = get_headers(self._ACCESSIBLE_ACCOUNTS)

        response = self.session.request(
            "post",
            url=self._ACCESSIBLE_ACCOUNTS,
            json=body,
            headers=header,
            timeout=timeout,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

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
            raise FacebookServiceException(response.content)
    def get_insights(
        self,
        account_id: str,
        secret_id: str,
        date_from: str,
        date_to: str,
        report_columns: List[str],
        breakdowns: List[str],
        filter_columns: List[Dict],
        level: str = None,
        timeout: int = None,
    ) -> List[Dict]:
        """
        Get Facebook Ads Insights according to configuration
        :param account_id The id of the ad account
        :param secret_id The ID of the secret in secret manager
        :param date_from The date from
        :param date_to The date to
        :param report_columns Required and available fields for report
        :param breakdowns Group the Insights API results into different sets using breakdowns
        :param filter_columns Option for filtering results according to specified conditions
        :param level Set the entity level for insights report
        :param timeout Cut the request if it takes too long
        :return Facebook Ads Insights List(Dict)
        """
        body = {
            "account_id": account_id,
            "date_from": date_from,
            "secret_id": secret_id,
            "date_to": date_to,
            "report_columns": report_columns,
            "breakdowns": breakdowns,
            "filter": filter_columns,
        }
        if level is not None:
            body["level"] = level
        header = get_headers(self._INSIGHTS)

        response = self.session.request(
            "post", url=self._INSIGHTS, json=body, headers=header, timeout=timeout
        )
        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_link_urls(
        self,
        account_id: str,
        secret_id: str,
        date_from: str,
        date_to: str,
        report_columns: List[str],
        filter_columns: List[Dict],
        timeout: int = None,
    ) -> List[Dict]:
        """
        Get Facebook Ads Insights according to configuration together with ad link urls
        :param account_id The id of the ad account
        :param secret_id The ID of the secret in secret manager
        :param date_from The date from
        :param date_to The date to
        :param report_columns Required and available fields for report
        :param filter_columns Option for filtering results according to specified conditions
        :param timeout Cut the request if it takes too long
        :return Facebook Ads Insights with ad link urls List(Dict)
        """
        body = {
            "account_id": account_id,
            "date_from": date_from,
            "secret_id": secret_id,
            "date_to": date_to,
            "report_columns": report_columns,
            "filter": filter_columns,
        }

        header = get_headers(self._LINK_URLS)

        response = self.session.request(
            "post", url=self._LINK_URLS, json=body, headers=header, timeout=timeout
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_accessible_businesses(
        self, secret_id: str, report_columns: List[str], timeout: int = None
    ) -> List[Dict]:
        """
        Get all accessible business entities for the user. Business id is required parameter for requesting connected
        product catalogs
        :param secret_id The ID of the secret in secret manager
        :param report_columns Required and available fields for report
        :param timeout Cut the request if it takes too long
        :return: all accessible business entities for the user List(Dict)
        """
        body = {"secret_id": secret_id, "report_columns": report_columns}

        header = get_headers(self._ACCESSIBLE_BUSINESSES)

        response = self.session.request(
            "post",
            url=self._ACCESSIBLE_BUSINESSES,
            json=body,
            headers=header,
            timeout=timeout,
        )
        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_product_catalogs(
        self,
        secret_id: str,
        business_id: str,
        report_columns: List[str],
        filter_columns: List[Dict],
        timeout: int = None,
    ) -> List[Dict]:
        """
        Get product catalogs for the selected business
        :param secret_id The ID of the secret in secret manager
        :param business_id Business id is required parameter for requesting connected product catalogs
        :param report_columns Required and available fields for report
        :param filter_columns Option for filtering results according to specified conditions
        :param timeout Cut the request if it takes too long
        :return: product catalogs for the selected business List(Dict)
        """
        body = {
            "secret_id": secret_id,
            "report_columns": report_columns,
            "filter": filter_columns,
            "business_id": business_id,
        }

        header = get_headers(self._PRODUCT_CATALOGS)

        response = self.session.request(
            "post",
            url=self._PRODUCT_CATALOGS,
            json=body,
            headers=header,
            timeout=timeout,
        )
        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_product_catalog(
        self,
        secret_id: str,
        catalog_id: str,
        report_columns: List[str],
        timeout: int = None,
    ) -> List[Dict]:
        """
        Retrieves product catalog by catalog ID
        :param secret_id The ID of the secret in secret manager
        :param catalog_id Catalog id of catalog to retrieve
        :param report_columns Required and available fields for report
        :param timeout Cut the request if it takes too long
        :return: product catalog List(Dict)
        """
        body = {
            "secret_id": secret_id,
            "report_columns": report_columns,
            "catalog_id": catalog_id,
        }

        header = get_headers(self._PRODUCT_CATALOG)

        response = self.session.request(
            "post",
            url=self._PRODUCT_CATALOG,
            json=body,
            headers=header,
            timeout=timeout,
        )
        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def products(
        self,
        secret_id: str,
        catalog_id: str,
        report_columns: List[str],
        filter_columns: Optional[Dict[str, Dict]],
        error_priority: Optional[str] = None,
        timeout: int = None,
    ) -> List[Dict]:
        """
        Returns products for the selected product catalog
        :param secret_id: The ID of the secret in secret manager
        :param catalog_id: Catalog id is required parameter for requesting connected products
        :param report_columns: Required and available fields for report
        :param filter_columns: Option for filtering results according to specified conditions
        :param error_priority: Use for filtering product with issues. Possible values: "HIGH", "MEDIUM", "LOW"
        :param timeout Cut the request if it takes too long
        :return: List(Dict)
        """
        body = {
            "secret_id": secret_id,
            "report_columns": report_columns,
            "filter": filter_columns,
            "catalog_id": catalog_id,
            "error_priority": error_priority,
        }

        header = get_headers(self._PRODUCTS)

        response = self.session.request(
            "post", url=self._PRODUCTS, json=body, headers=header, timeout=timeout
        )
        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_feeds(
        self, secret_id: str, catalog_id: str, timeout: int = None
    ) -> List[Dict]:
        """
        Returns available feeds for selected product catalog.
        :param secret_id The ID of the secret in secret manager
        :param catalog_id Catalog id is required parameter for requesting connected products
        :param timeout Cut the request if it takes too long
        """
        body = {"secret_id": secret_id, "catalog_id": catalog_id}

        header = get_headers(self._FEEDS)
        response = self.session.request(
            "post", url=self._FEEDS, json=body, headers=header, timeout=timeout
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_feed_errors(
        self, secret_id: str, feed_id: str, timeout: int = None
    ) -> Dict:
        """
        Returns count of errors and status for detailed error report for the newest run of feed upload for selected feed.
        If the error count is greater than 0 this endpoint initiates creation of the detailed error report.
        :param secret_id The ID of the secret in secret manager
        :param feed_id ID of the selected feed
        :param timeout Cut the request if it takes too long
        """
        body = {"secret_id": secret_id, "feed_id": feed_id}

        header = get_headers(self._FEED_ERRORS)
        response = self.session.request(
            "post", url=self._FEED_ERRORS, json=body, headers=header, timeout=timeout
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_feed_errors_report_status(
        self, secret_id: str, feed_id: str, timeout: int = None
    ) -> Dict:
        """
        Returns status for detailed error report for the newest run of feed upload for selected feed.
        :param secret_id The ID of the secret in secret manager
        :param feed_id ID of the selected feed
        :param timeout Cut the request if it takes too long
        """
        body = {"secret_id": secret_id, "feed_id": feed_id}

        header = get_headers(self._FEED_ERRORS_REPORT_STATUS)
        response = self.session.request(
            "post",
            url=self._FEED_ERRORS_REPORT_STATUS,
            json=body,
            headers=header,
            timeout=timeout,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_feed_errors_report(
        self, secret_id: str, feed_id: str, timeout: int = None
    ) -> List[Dict]:
        """
        When status of the feed error report is 'WRITE_FINISHED' or 'PARTIAL_WRITE_FINISHED' returns detailed list
        of possible feed upload errors with description and hints for correction.
        Otherwise, it returns just the count of errors with the current error report status.
        :param secret_id The ID of the secret in secret manager
        :param feed_id ID of the selected feed
        :param timeout Cut the request if it takes too long
        """
        body = {"secret_id": secret_id, "feed_id": feed_id}

        header = get_headers(self._FEED_ERRORS_REPORT)
        response = self.session.request(
            "post",
            url=self._FEED_ERRORS_REPORT,
            json=body,
            headers=header,
            timeout=timeout,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def check_feed_errors_report_ready_with_exponential_backoff(
        self,
        secret_id: str,
        feed_id: str,
        backoff_attempts: int = 10,
        timeout: int = None,
    ) -> Dict:
        """
        Implements exponential backoff for pooling the API for readiness of the report, suggested in
        algorithm suggested by https://developers.google.com/doubleclick-advertisers/upload#exp-backoff
        :param secret_id: The ID of the secret in secret manager
        :param feed_id: ID of the selected feed
        :param backoff_attempts: Number of attempts in checking the report status
        :param timeout Cut the request if it takes too long
        :return Bool
        """
        for attempt in range(0, backoff_attempts):
            if (
                self.get_feed_errors_report_status(secret_id, feed_id, timeout=timeout)
                == "WRITE_FINISHED"
            ):
                return True
            else:
                time.sleep((2**attempt) + randint(1, 20))

        return False

    def get_account_activities(
        self,
        secret_id: str,
        account_id: str,
        date_from: str,
        date_to: str
    ) -> Dict:
        """
        Gets account activities
        :param secret_id: The ID of the secret in secret manager
        :param account_id: The ID of the account
        :param date_from: Start date for the activities
        :param date_to: End date for the activities
        :return List of activities
        """
        body = {
            "secret_id": secret_id,
            "account_id": account_id,
            "date_from": date_from,
            "date_to": date_to
        }

        header = get_headers(self._ACCOUNT_ACTIVITIES)
        response = self.session.request(
            "post",
            url=self._ACCOUNT_ACTIVITIES,
            json=body,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)

    def get_business_users(
        self,
        secret_id: str,
    ) -> Dict:
        """
        Gets account activities
        :param secret_id: The ID of the secret in secret manager
        :return List of users
        """
        body = {
            "secret_id": secret_id,
        }

        header = get_headers(self._BUSINESS_USERS)
        response = self.session.request(
            "post",
            url=self._BUSINESS_USERS,
            json=body,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise FacebookServiceException(response.content)
