from http import HTTPStatus
from logos_sdk.services import get_headers, get_retry_session
from dotenv import load_dotenv
import os


class MerchantServiceException(Exception):
    pass


class MerchantCenterService:
    def __init__(self, url=None):
        load_dotenv()
        self.session = get_retry_session()
        self._URL = url or os.environ.get("MERCHANT_CENTER_SERVICE_PATH")
        self._LIST_ACCOUNTS = self._URL + "/account-service/accounts"
        self._LIST_ACCESSIBLE_ACCOUNTS = self._URL + "/account-service/list-accessible-accounts"
        self._GET_ACCOUNT_ACCESSIBILITY = self._URL + "/account-service/get-account-accessibility"
        self._LIST_ACCOUNT_STATUSES = self._URL + "/account-service/account-statuses"
        self._LIST_PRODUCTS = self._URL + "/product-service/products"
        self._LIST_PRODUCT_STATUSES = self._URL + "/product-service/product-statuses"
        self._REPORTS_SEARCH = self._URL + "/reports-search"
        self._GET_SUPPLEMENTAL_FEEDS = self._URL + "/feed-service/supplemental-feeds"
        self._PRIMARY_FEED = self._URL + "/feed-service/feeds"


    def list_accounts(self, merchant_account_id: str, secret_id: str):
        """
        Lists the sub-accounts in your Merchant Center account
        :param merchant_account_id: The ID of the managing account. This must be a multi-client account
        :param secret_id: The ID of the secret in secret manager
        :return: List[Dict]
        """
        body = {"merchant_account_id": merchant_account_id, "secret_id": secret_id}
        header = get_headers(self._LIST_ACCOUNTS)
        response = self.session.request("post", url=self._LIST_ACCOUNTS, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def list_accessible_accounts(self, secret_id: str):
        """
        Lists accessible accounts in Merchant Center
        :param secret_id: The ID of the secret in secret manager
        :return: List[Dict]
        """
        body = {"secret_id": secret_id}
        header = get_headers(self._LIST_ACCESSIBLE_ACCOUNTS)
        response = self.session.request("post", url=self._LIST_ACCESSIBLE_ACCOUNTS, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def list_account_statuses(
            self, merchant_account_id: str, account_id: str, secret_id: str
    ):
        """
        Retrieves the statuses of a Merchant Center account.
        :param merchant_account_id: The ID of the managing account. This must be a multi-client account.
        :param account_id: The ID of the account.
        :param secret_id: The ID of the secret in secret manager
        :return: List[Dict]
        """
        body = {
            "merchant_account_id": merchant_account_id,
            "account_id": account_id,
            "secret_id": secret_id,
        }
        header = get_headers(self._LIST_ACCOUNT_STATUSES)
        response = self.session.request(
            "post", url=self._LIST_ACCOUNT_STATUSES, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def list_products(self, merchant_account_id: str, secret_id: str, page_size: int = 250):
        """
        Lists the products in your Merchant Center account
        :param merchant_account_id: The ID of the managing account. This account cannot be a multi-client account
        :param secret_id: The ID of the secret in secret manager
        :param page_size: size of the page
        :return: List[Dict]
        """
        body = {"merchant_account_id": merchant_account_id, "secret_id": secret_id, "page_size": page_size}
        header = get_headers(self._LIST_PRODUCTS)
        response = self.session.request("post", url=self._LIST_PRODUCTS, json=body, headers=header)

        if response.status_code != HTTPStatus.OK:
            raise MerchantServiceException(response.content)

        service_response = response.json()
        yield service_response["data"]["results"]

        while service_response["data"]["nextPageToken"] is not None:
            body["page_token"] = service_response["data"]["nextPageToken"]
            response = self.session.request(
                "post", url=self._LIST_PRODUCTS, json=body, headers=header
            )

            if response.status_code != HTTPStatus.OK:
                raise MerchantServiceException(response.content)

            service_response = response.json()
            yield service_response["data"]["results"]

    def list_products_statuses(self, merchant_account_id: str, secret_id: str, page_size: int = 250):
        """
        Lists the statuses of the products in your Merchant Center account
        :param merchant_account_id: The ID of the
        account that contains the products. This account cannot be a multi-client account
        :param secret_id: The ID of the secret in secret manager
        :param page_size: size of the page
        :return: List[Dict]
        """
        body = {"merchant_account_id": merchant_account_id, "secret_id": secret_id, "page_size": page_size}
        header = get_headers(self._LIST_PRODUCT_STATUSES)
        response = self.session.request(
            "post", url=self._LIST_PRODUCT_STATUSES, json=body, headers=header
        )

        if response.status_code != HTTPStatus.OK:
            raise MerchantServiceException(response.content)

        service_response = response.json()
        yield service_response["data"]["results"]

        while service_response["data"]["nextPageToken"] is not None:
            body["page_token"] = service_response["data"]["nextPageToken"]
            response = self.session.request(
                "post", url=self._LIST_PRODUCT_STATUSES, json=body, headers=header
            )

            if response.status_code != HTTPStatus.OK:
                raise MerchantServiceException(response.content)

            service_response = response.json()
            yield service_response["data"]["results"]

    def reports_search(
            self,
            merchant_account_id: str,
            secret_id: str,
            query: str,
            page_token: str = None,
            page_size: int = 1000,
    ):
        body = {
            "merchant_account_id": merchant_account_id,
            "secret_id": secret_id,
            "query": query,
            "page_token": page_token,
            "page_size": page_size,
        }
        header = get_headers(self._REPORTS_SEARCH)
        response = self.session.request("post", url=self._REPORTS_SEARCH, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def reports_search_generator(
            self,
            merchant_account_id: str,
            secret_id: str,
            query: str,
            page_size: int = 1000,
    ):
        body = {
            "merchant_account_id": merchant_account_id,
            "secret_id": secret_id,
            "query": query,
            "page_size": page_size,
        }
        header = get_headers(self._REPORTS_SEARCH)
        response = self.session.request("post", url=self._REPORTS_SEARCH, json=body, headers=header)

        if response.status_code != HTTPStatus.OK:
            raise MerchantServiceException(response.content)

        service_response = response.json()
        yield service_response["data"]["results"]

        while service_response["data"]["nextPageToken"] is not None:
            body["page_token"] = service_response["data"]["nextPageToken"]
            response = self.session.request(
                "post", url=self._REPORTS_SEARCH, json=body, headers=header
            )

            if response.status_code != HTTPStatus.OK:
                raise MerchantServiceException(response.content)

            service_response = response.json()
            yield service_response["data"]["results"]

    def get_account_accessibility(self, secret_id: str,merchant_account_id:str, account_id: str) -> bool:
        """
        Gets account accessibility
        :param secret_id: The ID of the secret in secret manager
        :param merchant_account_id: The ID of the managing account. This must be a multi-client account.
        :param account_id: The ID of the account.
        :return: True if account has access
        """
        body = {
            "secret_id": secret_id,
            "merchant_account_id": merchant_account_id,
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
            raise MerchantServiceException(response.content)

    def get_primary_feed(self, secret_id: str, merchant_account_id: str):
        body = {"secret_id": secret_id, "merchant_account_id": merchant_account_id}
        header = get_headers(self._PRIMARY_FEED)
        response = self.session.request(
            "post", url=self._PRIMARY_FEED, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def attach_supplemental_feed_to_primary_feed(
        self,
        secret_id: str,
        merchant_account_id: str,
        primary_feed_id: str,
        supplemental_feed_id: str
    ):
        body = {
            "secret_id": secret_id,
            "merchant_account_id": merchant_account_id,
            "primary_feed_id": primary_feed_id,
            "supplemental_feed_id": supplemental_feed_id,
            "action": "attach"
        }
        header = get_headers(self._PRIMARY_FEED)
        response = self.session.request(
            "patch", url=self._PRIMARY_FEED, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def detach_supplemental_feed_from_primary_feed(
        self,
        secret_id: str,
        merchant_account_id: str,
        primary_feed_id: str,
        supplemental_feed_id: str
    ):
        body = {
            "secret_id": secret_id,
            "merchant_account_id": merchant_account_id,
            "primary_feed_id": primary_feed_id,
            "supplemental_feed_id": supplemental_feed_id,
            "action": "detach"
        }
        header = get_headers(self._PRIMARY_FEED)
        response = self.session.request(
            "patch", url=self._PRIMARY_FEED, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def get_supplemental_feeds(self, secret_id: str, merchant_account_id: str) -> bool:
        """
        Gets list of supplemental feeds
        :param secret_id: The ID of the secret in secret manager
        :param merchant_account_id: The ID of the account in Microsoft Advertising
        :return: List of supplemental feeds
        """
        body = {"secret_id": secret_id, "merchant_account_id": merchant_account_id}
        header = get_headers(self._GET_SUPPLEMENTAL_FEEDS)
        response = self.session.request(
            "post", url=self._GET_SUPPLEMENTAL_FEEDS, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def create_supplemental_feed(
        self, secret_id: str, merchant_account_id: str, display_name: str
    ) -> bool:
        """
        Creates a supplemental feed
        :param secret_id: The ID of the secret in secret manager
        :param merchant_account_id: The ID of the account in Microsoft Advertising
        :param display_name: The display name of the feed to be created
        :return: The newly created supplemental feed
        """
        body = {
            "secret_id": secret_id,
            "merchant_account_id": merchant_account_id,
            "display_name": display_name,
        }
        header = get_headers(self._GET_SUPPLEMENTAL_FEEDS)
        response = self.session.request(
            "post", url=self._GET_SUPPLEMENTAL_FEEDS, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def delete_supplemental_feed(
        self, secret_id: str, merchant_account_id: str, feed_id: str
    ) -> bool:
        """
        Deletes a supplemental feed by it id
        :param secret_id: The ID of the secret in secret manager
        :param merchant_account_id: The ID of the account in Microsoft Advertising
        :param feed_id: The ID of the supplemental feed to be deleted
        :return: Status of the operation
        """
        body = {
            "secret_id": secret_id,
            "merchant_account_id": merchant_account_id,
            "feed_id": feed_id,
        }
        header = get_headers(self._GET_SUPPLEMENTAL_FEEDS)
        response = self.session.request(
            "delete", url=self._GET_SUPPLEMENTAL_FEEDS, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)

    def batch_update_products_in_supplemental_feeds(
        self, secret_id: str, merchant_account_id: str, products
    ) -> bool:
        """
        Creates a batch for update of products via supplemental feeds
        :param secret_id: The ID of the secret in secret manager
        :param merchant_account_id: The ID of the account in Microsoft Advertising
        :param products: The products to be updated
        :return: The result of each batch operation
        """
        body = {
            "secret_id": secret_id,
            "merchant_account_id": merchant_account_id,
            "products": products,
        }
        header = get_headers(self._GET_SUPPLEMENTAL_FEEDS)
        response = self.session.request(
            "put", url=self._GET_SUPPLEMENTAL_FEEDS, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MerchantServiceException(response.content)
