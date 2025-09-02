from logos_sdk.services import get_headers, get_retry_session
from http import HTTPStatus
from time import sleep
from random import randint
import os
from urllib.request import urlopen
from contextlib import closing
from pandas import read_csv
from dotenv import load_dotenv


class DV360ServiceException(Exception):
    pass


class DV360Service:
    def __init__(self, url=None):
        load_dotenv()
        self.session = get_retry_session()
        self._URL = url or os.environ.get("DV360_SERVICE_PATH")
        self._LIST_LINE_ITEMS = self._URL + "/line-items"
        self._BULK_LIST_LINE_ITEM_ASSIGNED_TARGETING_OPTIONS = (
                self._URL + "/bulk-list-line-item-assigned-targeting-options"
        )
        self._BULK_EDIT_LINE_ITEM_ASSIGNED_TARGETING_OPTIONS = (
                self._URL + "/bulk-edit-line-item-assigned-targeting-options"
        )
        self._CREATE_CHANNEL = self._URL + "/create-channel"
        self._LIST_CHANNELS = self._URL + "/list-channels"
        self._LIST_INSERTION_ORDERS = self._URL + "/list-insertion-orders"
        self._LIST_CHANNEL_SITES = self._URL + "/list-channel-sites"
        self._BULK_EDIT_CHANNEL_SITES = self._URL + "/bulk-edit-channel-sites"

        self._CREATE_QUERY = self._URL + "/create-query"
        self._GET_QUERY_METADATA = self._URL + "/get-query-metadata"
        self._RUN_QUERY = self._URL + "/run-query"
        self._DELETE_QUERY = self._URL + "/delete-query"
        self._GET_ACCESSIBLE_PARTNERS = self._URL + "/get-accessible-partners"
        self._GET_ACCESSIBLE_ADVERTISERS = self._URL + "/get-accessible-advertisers"
        self._GET_ACCOUNT_ACCESSIBILITY = self._URL + "/get-account-accessibility"

    def list_line_items(self, advertiser_id, secret_id, filter_string=None):
        """
        Lists line items in an advertiser
        :param advertiser_id: The ID of the advertiser to list line items for
        :param secret_id: The ID (name) of the Logos Secret in Secret Manager to be used to access the account specified by account email
        :param filter_string: Allows filtering by line item fields
        :return List[Sites]
        """
        header = get_headers(self._LIST_LINE_ITEMS)
        body = {"advertiser_id": advertiser_id, "secret_id": secret_id}

        if filter_string is not None:
            body["filter"] = filter_string

        response = self.session.request("post", url=self._LIST_LINE_ITEMS, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def bulk_list_line_item_assigned_targeting_options(
            self,
            advertiser_id,
            secret_id,
            line_item_ids,
            filter_string,
    ):
        """
        Bulk lists targeting options under multiple line items
        :param advertiser_id: The ID of the advertiser the line items belong to
        :param secret_id: The ID (name) of the Logos Secret in Secret Manager to be used to access the account specified by account email
        :param line_item_ids: The ID of the line items whose targeting is being updated
        :param filter_string: Allows filtering by line item fields
        :return List of AssignedTargetingOption objects
        """
        header = get_headers(self._BULK_LIST_LINE_ITEM_ASSIGNED_TARGETING_OPTIONS)
        body = {
            "advertiser_id": advertiser_id,
            "secret_id": secret_id,
            "line_item_ids": line_item_ids,
            "filter": filter_string,
        }

        response = self.session.request(
            "post",
            url=self._BULK_LIST_LINE_ITEM_ASSIGNED_TARGETING_OPTIONS,
            json=body,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def bulk_edit_line_item_assigned_targeting_options(
            self,
            advertiser_id,
            secret_id,
            line_item_ids,
            delete_requests=None,
            create_requests=None,
    ):
        """
        Bulk edits targeting options under multiple line items
        :param advertiser_id: The ID of the advertiser the line items belong to
        :param secret_id: The ID (name) of the Logos Secret in Secret Manager to be used to access the account specified by account email
        :param line_item_ids: The ID of the line items whose targeting is being updated
        :param delete_requests: The assigned targeting options to delete in batch, specified as a list of
        DeleteAssignedTargetingOptionsRequest
        :param create_requests: The assigned targeting options to create in batch, specified as a list of
        CreateAssignedTargetingOptionsRequest
        :return None
        """
        header = get_headers(self._BULK_EDIT_LINE_ITEM_ASSIGNED_TARGETING_OPTIONS)
        body = {
            "advertiser_id": advertiser_id,
            "secret_id": secret_id,
            "line_item_ids": line_item_ids,
        }

        if delete_requests is not None:
            body["delete_requests"] = delete_requests

        if create_requests is not None:
            body["create_requests"] = create_requests

        response = self.session.request(
            "post",
            url=self._BULK_EDIT_LINE_ITEM_ASSIGNED_TARGETING_OPTIONS,
            json=body,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def create_channel(self, advertiser_id, secret_id, name):
        """
        Lists channels for advertiser
        :param advertiser_id: The ID of the advertiser that owns the channels
        :param secret_id: The ID (name) of the Logos Secret in Secret Manager to be used to access the account specified by account email
        :param name: The display name of the channel. Must be UTF-8 encoded with a maximum length of 240 bytes
        :return Channel
        """
        header = get_headers(self._CREATE_CHANNEL)
        body = {"advertiser_id": advertiser_id, "secret_id": secret_id, "name": name}

        response = self.session.request("post", url=self._CREATE_CHANNEL, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def list_channels(self, advertiser_id, secret_id, filter_string=None):
        """
        Lists channels for advertiser
        :param advertiser_id: The ID of the advertiser that owns the channels
        :param secret_id: The ID (name) of the Logos Secret in Secret Manager to be used to access the account specified by account email
        :param filter_string: Allows filtering by channel fields
        :return List[Channels]
        """
        header = get_headers(self._LIST_CHANNELS)
        body = {"advertiser_id": advertiser_id, "secret_id": secret_id}

        if filter_string is not None:
            body["filter"] = filter_string

        response = self.session.request("post", url=self._LIST_CHANNELS, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def list_insertion_orders(self, advertiser_id, secret_id, filter_string=None):
        """
        Lists insertion orders for advertiser
        :param advertiser_id: The ID of the advertiser that owns the insertion orders
        :param secret_id: The ID (name) of the Logos Secret in Secret Manager to be used to access the account specified by account email
        :param filter_string: Allows filtering by insertion order fields
        :return List[InsertionOrders]
        """
        header = get_headers(self._LIST_INSERTION_ORDERS)
        body = {"advertiser_id": advertiser_id, "secret_id": secret_id}

        if filter_string is not None:
            body["filter"] = filter_string

        response = self.session.request("post", url=self._LIST_INSERTION_ORDERS, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def list_channel_sites(
            self, advertiser_id, secret_id, channel_id, filter_string=None
    ):
        """
        Lists channels for advertiser
        :param advertiser_id: The ID of the advertiser that owns the channels
        :param secret_id: The ID (name) of the Logos Secret in Secret Manager to be used to access the account specified by account email
        :param channel_id: The ID of the parent channel to which the sites belong
        :param filter_string: Allows filtering by channel fields
        :return List[Sites]
        """
        header = get_headers(self._LIST_CHANNEL_SITES)
        body = {
            "advertiser_id": advertiser_id,
            "secret_id": secret_id,
            "channel_id": channel_id,
        }

        if filter_string is not None:
            body["filter"] = filter_string

        response = self.session.request(
            "post", url=self._LIST_CHANNEL_SITES, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def bulk_edit_channels_sites(
            self,
            advertiser_id,
            secret_id,
            channel_id,
            deleted_sites=None,
            created_sites=None,
    ):
        """
        Bulk edits sites under a single channel
        :param advertiser_id: The ID of the advertiser that owns the parent channel
        :param secret_id: The ID (name) of the Logos Secret in Secret Manager to be used to access the account specified by account email
        :param channel_id: The ID of the parent channel to which the sites belong
        :param deleted_sites: The sites to delete in batch
        :param created_sites: The sites to create in batch
        :return None
        """
        header = get_headers(self._BULK_EDIT_CHANNEL_SITES)
        body = {
            "advertiser_id": advertiser_id,
            "secret_id": secret_id,
            "channel_id": channel_id,
        }

        if deleted_sites is not None:
            body["deleted_sites"] = deleted_sites

        if created_sites is not None:
            body["created_sites"] = created_sites

        response = self.session.request(
            "post",
            url=self._BULK_EDIT_CHANNEL_SITES,
            json=body,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def create_query(self, secret_id, date_range, group_bys, filters, metrics_names):
        """
        Create a query in DoubleClick Bid Manager
        https://github.com/googleads/googleads-bidmanager-examples/blob/96cd16cf338aa1f175f080ccbd9e8e793bac20bb/python/v2/create_and_run_query.py
        https://developers.google.com/bid-manager/reference/rest/v2/queries/create
        :param secret_id: The ID of the secret in secret manager
        :param date_range: The date range for the query {startDate: "YYYY-MM-DD", endDate: "YYYY-MM-DD"}
        :param group_bys: The group bys for the query
        :param filters: The filters for the query
        :param metrics_names: The metrics for the query
        :return: The query ID
        """
        header = get_headers(self._CREATE_QUERY)
        body = {
            "secret_id": secret_id,
            "date_range": date_range,
            "group_bys": group_bys,
            "filters": filters,
            "metrics_names": metrics_names,
        }

        response = self.session.request("post", url=self._CREATE_QUERY, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def run_query(self, secret_id, query_id):
        """
        Run a query in DoubleClick Bid Manager
        :param secret_id: The ID of the secret in secret manager
        :param query_id: The ID of the query to run
        :return: The report ID
        """

        header = get_headers(self._RUN_QUERY)
        body = {"secret_id": secret_id, "query_id": query_id}

        response = self.session.request("post", url=self._RUN_QUERY, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def get_accessible_partners(self, secret_id):
        """
        Returns accessible partners
        :param secret_id: The ID of the secret in secret manager
        :return: list of partners
        """

        header = get_headers(self._GET_ACCESSIBLE_PARTNERS)
        body = {
            "secret_id": secret_id,
            "filters": {
                "hide_inactive": True,
            },
        }

        response = self.session.request(
            "post", url=self._GET_ACCESSIBLE_PARTNERS, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def get_accessible_advertisers(self, secret_id):
        """
        Returns accessible advertisers
        :param secret_id: The ID of the secret in secret manager
        :return: list of advertisers
        """

        header = get_headers(self._GET_ACCESSIBLE_ADVERTISERS)
        body = {
            "secret_id": secret_id,
            "filters": {
                "hide_inactive": True,
            },
        }

        response = self.session.request(
            "post", url=self._GET_ACCESSIBLE_ADVERTISERS, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def get_account_accessibility(self, secret_id: str, advertiser_id: str) -> bool:
        """
        Gets account accessibility
        :param secret_id: The ID of the secret in secret manager
        :param advertiser_id: The ID of the advertiser.
        :return: True if account has access
        """
        body = {
            "secret_id": secret_id,
            "advertiser_id": advertiser_id
        }
        header = get_headers(self._GET_ACCOUNT_ACCESSIBILITY)
        response = self.session.request(
            "post", url=self._GET_ACCOUNT_ACCESSIBILITY, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def _check_report_ready_with_exponential_backoff(
            self, secret_id: str, query_id: str, report_id: str, backoff_attempts: int = 10
    ) -> bool:
        """
        Implements exponential backoff for pooling the API for readiness of the report, suggested in
        algorithm suggested by https://developers.google.com/doubleclick-advertisers/upload#exp-backoff

        """
        for attempt in range(0, backoff_attempts):
            state = self._get_query_metadata(secret_id, query_id, report_id)["status"][
                "state"
            ]
            if state == "DONE":
                return True
            elif state == "FAILED":
                raise DV360ServiceException("Report failed to generate")
            else:
                sleep((2 ** attempt) + randint(1, 20))

        return False

    def _get_query_metadata(self, secret_id, query_id, report_id):
        """
        Get the metadata for a query in DoubleClick Bid Manager
        :param secret_id: The ID of the secret in secret manager
        :param query_id: The ID of the query to get metadata for
        :param report_id: The ID of the report to get metadata for
        :return: The metadata
        """
        header = get_headers(self._GET_QUERY_METADATA)
        body = {"secret_id": secret_id, "query_id": query_id, "report_id": report_id}

        response = self.session.request(
            "post", url=self._GET_QUERY_METADATA, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise DV360ServiceException(response.content)

    def get_query_results(self, secret_id, query_id, report_id):
        """
        Get the results for a query in DoubleClick Bid Manager
        :param secret_id: The ID of the secret in secret manager
        :param query_id: The ID of the query to get results for
        :param report_id: The ID of the report to get results for
        :return: The results
        """
        if not self._check_report_ready_with_exponential_backoff(
                secret_id, query_id, report_id
        ):
            raise DV360ServiceException("Report did not generate in time")

        metadata = self._get_query_metadata(secret_id, query_id, report_id)
        cloud_storage_path = metadata["googleCloudStoragePath"]

        if not os.path.exists("tmp"):
            os.makedirs("tmp")

        result_temp_file_location = os.path.join("tmp", "report-result-temp.csv")

        with open(result_temp_file_location, "wb") as output:
            with closing(urlopen(cloud_storage_path)) as url:
                output.write(url.read())

        results = read_csv(
            result_temp_file_location,
            on_bad_lines="skip",
            engine="python",  # otherwise warning that skipfooter arg does not exist
        )
        results = results.to_dict(orient="records")

        # get rid of the tmp file
        os.remove(result_temp_file_location)
        return results

    def delete_query(self, secret_id, query_id):
        """
        Delete a query in DoubleClick Bid Manager
        :param secret_id: The ID of the secret in secret manager
        :param query_id: The ID of the query to delete
        :return: True if the query was deleted, False otherwise
        """
        header = get_headers(self._DELETE_QUERY)
        body = {"secret_id": secret_id, "query_id": query_id}

        response = self.session.request("post", url=self._DELETE_QUERY, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            return True

        return False
