import io
import json
import httplib2
import os
import time

from random import randint
from logos_sdk.services import get_headers, get_retry_session
from typing import Dict, List
from http import HTTPStatus
from googleapiclient.http import MediaIoBaseDownload, HttpRequest
from pandas import read_csv
from dotenv import load_dotenv


class CampaignManagerServiceException(Exception):
    pass


class CampaignManagerService:
    def __init__(self, url: str = None):
        load_dotenv()
        self.session = get_retry_session()
        self._URL = url or os.environ.get("CM360_SERVICE_PATH")
        self._CREATE_REPORT = self._URL + "/create-report"
        self._GET_REPORT = self._URL + "/get-report"
        self._RUN_REPORT = self._URL + "/run-report"
        self._PATCH_REPORT = self._URL + "/patch-report"
        self._DELETE_REPORT = self._URL + "/delete-report"
        self._GET_FILE = self._URL + "/get-file"
        self._GET_FILE_MEDIA_REQUEST = self._URL + "/get-file-media-request"
        self._QUERY_DIMENSION_VALUES = self._URL + "/query-dimension-values"
        self._GET_ACCESSIBLE_PARENT_ACCOUNTS = self._URL + "/get-parent-accounts"
        self._GET_ACCESSIBLE_ADVERTISERS = self._URL + "/get-advertisers"
        self._GET_ACCOUNT_ACCESSIBILITY = self._URL + "/get-account-accessibility"

    def create_report(
            self,
            account_id: str,
            name: str,
            start_date: str,
            end_date: str,
            dimensions: list,
            metrics_names: list,
            dimension_filters: list,
            secret_id: str,
    ) -> Dict:
        """
        Method for creating a report in API and returning a dict containing its ID for further use
        :param account_id: the Campaign Manager 360 account ID
        :param name: the name for the report
        :param start_date: start date for the report, in yyyy-mm-dd format
        :param end_date: end date for the report, in yyyy-mm-dd format
        :param dimensions: a list containing dimensions for the report
        :param metrics_names: a list containing metrics for the report
        :param dimension_filters: a list containing filters for the dimensions
        :param secret_id: ID of the secret in Secret Manager to be used to access Campaign Manager 360
        :return Dict
        """
        body = {
            "account_id": account_id,
            "name": name,
            "date_range": {"startDate": start_date, "endDate": end_date},
            "dimensions": dimensions,
            "metrics_names": metrics_names,
            "dimension_filters": dimension_filters,
            "secret_id": secret_id,
        }
        header = get_headers(self._CREATE_REPORT)
        response = self.session.request(
            method="post", url=self._CREATE_REPORT, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CampaignManagerServiceException(response.content)

    def get_report(self, account_id: str, report_id: str, secret_id: str) -> Dict:
        """
        Method to return report
        :param account_id: The ID of the account to fetch the report from
        :param report_id: The ID of the report
        :param secret_id: ID of the secret in Secret Manager to be used to access Campaign Manager 360
        :return Dict
        """
        body = {
            "account_id": account_id,
            "report_id": report_id,
            "secret_id": secret_id,
        }

        header = get_headers(self._GET_REPORT)
        response = self.session.request("post", url=self._GET_REPORT, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CampaignManagerServiceException(response.content)

    def run_report(self, account_id: str, report_id: str, secret_id: str) -> Dict:
        """
        Method to run report
        :param account_id: The ID of the account to run the report for
        :param report_id: The ID of the report
        :param secret_id: ID of the secret in Secret Manager to be used to access Campaign Manager 360
        :return Dict
        """
        body = {
            "account_id": account_id,
            "report_id": report_id,
            "secret_id": secret_id,
        }
        header = get_headers(self._RUN_REPORT)
        response = self.session.request("post", url=self._RUN_REPORT, json=body, headers=header)
        service_response = response.json()

        if response.status_code == HTTPStatus.OK:
            return service_response["data"]
        else:
            raise CampaignManagerServiceException(service_response)

    # def patch_report(
    #     self,
    #     report_id: str,
    #     advertiser_name: str,
    #     start_date: str,
    #     end_date: str,
    #     dimensions: list,
    #     metrics_names: list,
    #     dimension_filters: list,
    #     secret_id: str,
    # ) -> bool:
    #     """
    #     Method to patch report
    #     :param report_id: The ID of the report.
    #     :param advertiser_name: advertiser name of advertiser dimension filter.
    #     :param start_date: The start date for which this report should be run.
    #     :param end_date: The end date for which this report should be run.
    #     :param dimensions: The list of standard dimensions. Valid dimensions: dv360InsertionOrder, dv360LineItem, dv360Site.
    #     :param metrics_names: The list of names of metrics. Valid metric names: clickRate, impressions, totalConversions.
    #     :param dimension_filters: The list of filters on which dimensions are filtered.
    #     :param secret_id: ID of the secret in Secret Manager to be used to access Campaign Manager 360
    #     :return Boolean
    #     """
    #     body = {
    #         "report_id": report_id,
    #         "advertiser_name": advertiser_name,
    #         "date_range": {"startDate": start_date, "endDate": end_date},
    #         "dimensions": dimensions,
    #         "metrics_names": metrics_names,
    #         "dimension_filters": dimension_filters,
    #         "secret_id": secret_id,
    #     }
    #
    #     header = get_headers(self._PATCH_REPORT)
    #     response = request("patch", url=self._PATCH_REPORT, json=body, headers=header)
    #     service_response = response.json()
    #     if response.status_code == HTTPStatus.OK:
    #         return True
    #     else:
    #         raise CampaignManagerServiceException(service_response)

    def check_report_ready(self, report_id: str, file_id: str, secret_id: str) -> Dict:
        """
        Method to check weather the report is already available for download
        :param report_id: The ID of the report
        :param file_id: The ID of the report file to be downloaded
        :param secret_id: ID of the secret in Secret Manager to be used to access Campaign Manager 360
        :return Dict
        """
        body = {"report_id": report_id, "file_id": file_id, "secret_id": secret_id}
        header = get_headers(self._GET_FILE)
        response = self.session.request("post", url=self._GET_FILE, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]["status"] == "REPORT_AVAILABLE"
        else:
            raise CampaignManagerServiceException(response.content)

    def check_report_ready_with_exponential_backoff(
            self, report_id: str, file_id: str, secret_id: str, backoff_attempts: int = 10
    ) -> bool:
        """
        Implements exponential backoff for pooling the API for readiness of the report, suggested in
        algorithm suggested by https://developers.google.com/doubleclick-advertisers/upload#exp-backoff
        :param report_id: The ID of the report
        :param file_id: The ID of the report file to be downloaded
        :param secret_id: ID of the secret in Secret Manager to be used to access Campaign Manager 360
        :param backoff_attempts: number of attempts
        :return Bool
        """
        for attempt in range(0, backoff_attempts):
            if self.check_report_ready(report_id, file_id, secret_id):
                return True
            else:
                time.sleep((2 ** attempt) + randint(1, 20))

        return False

    def get_report_results(self, report_id: str, file_id: str, secret_id: str) -> Dict:
        """
        Method to fetch report, based on https://developers.google.com/doubleclick-advertisers/guides/download_reports
        and https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaIoBaseDownload-class.html
        :param account_id: The ID of the account to check for the report
        :param report_id: The ID of the report
        :param file_id: The ID of the report file to be downloaded
        :param secret_id: ID of the secret in Secret Manager to be used to access Campaign Manager 360
        :return Dict
        """
        body = {"report_id": report_id, "file_id": file_id, "secret_id": secret_id}
        header = get_headers(self._GET_FILE_MEDIA_REQUEST)

        # fetch the authorized request from our service for downloading the report from API
        response = self.session.request(
            "post", url=self._GET_FILE_MEDIA_REQUEST, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            authorised_request = HttpRequest.from_json(
                json.dumps(service_response["data"]),
                http=httplib2.Http(),
                postproc=None,
            )

            # crete tmp directory if not exist
            if not os.path.exists("tmp"):
                os.makedirs("tmp")
            result_temp_file_location = os.path.join("tmp", "report-result-temp.csv")
            # prepare a local file to download the report contents to
            result_temp_file = io.FileIO(result_temp_file_location, mode="wb")
            # 1024 * 1024 * 10 = 10 MB, based on best practices described in CM360 API documentation, default would be 1 MB
            chunk_size = 10485760
            # create a media downloader instance
            media_downloader = MediaIoBaseDownload(
                result_temp_file, authorised_request, chunksize=chunk_size
            )
            # execute the get request and download the file.
            download_finished = False
            while download_finished is False:
                _, download_finished = media_downloader.next_chunk()

            result_temp_file.close()

            skip = 0
            with open(result_temp_file_location, "r") as file:
                for line in file:
                    skip += 1
                    if "Report Fields" == line.strip():
                        break

            results = read_csv(
                result_temp_file_location,
                on_bad_lines="skip",
                skiprows=skip,  # skip metadata
                skipfooter=1,  # last row contains "grand total"
                engine="python",  # otherwise warning that skipfooter arg does not exist
            )
            results = results.to_dict(orient="records")

            # get rid of the tmp file
            os.remove(result_temp_file_location)
            return results

        else:
            raise CampaignManagerServiceException(response.content)

    def delete_report(self, account_id: str, report_id: str, secret_id: str) -> bool:
        """
        Method to delete report
        :param account_id: The ID of the account to check for the report
        :param report_id: The ID of the report
        :param secret_id: ID of the secret in Secret Manager to be used to access Campaign Manager 360
        :return Boolean
        """
        body = {
            "account_id": account_id,
            "report_id": report_id,
            "secret_id": secret_id,
        }
        header = get_headers(self._DELETE_REPORT)
        response = self.session.request("post", url=self._DELETE_REPORT, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            return True
        else:
            raise CampaignManagerServiceException(response.content)

    def query_dimension_values(
            self,
            account_id: str,
            secret_id: str,
            dimension_name: str,
            filters: List,
            start_date: str,
            end_date: int,
            max_results: int = 100,
    ) -> List[Dict]:
        """
        Retrieves values of selected dimensions for data filtered according to rules set in list of filters
        :param account_id: Account ID
        :param dimension_name: The name of the dimension for which values should be requested
        :param secret_id: The ID of the secret in secret manager
        :param filters: The list of filters by which to filter values
        :param start_date: The start date of the date range for which to retrieve dimension values
        :param end_date: The end date of the date range for which to retrieve dimension values
        :param max_results: Maximum number of results to return


        return {"next_page_token": token, items: values of selected dimensions}
        """
        body = {
            "account_id": account_id,
            "dimension_name": dimension_name,
            "secret_id": secret_id,
            "filters": filters,
            "start_date": start_date,
            "end_date": end_date,
            "page_token": None,
            "max_results": max_results,
        }

        header = get_headers(self._QUERY_DIMENSION_VALUES)
        response = self.session.request(
            "post", url=self._QUERY_DIMENSION_VALUES, json=body, headers=header
        )

        if response.status_code != HTTPStatus.OK:
            raise CampaignManagerServiceException(response.content)

        service_response = response.json()
        yield service_response["data"]["items"]

        # if there was a last page response is empty string
        while service_response["data"]["nextPageToken"]:
            body["page_token"] = service_response["data"]["nextPageToken"]
            response = self.session.request(
                "post", url=self._QUERY_DIMENSION_VALUES, json=body, headers=header
            )

            if response.status_code != HTTPStatus.OK:
                raise CampaignManagerServiceException(response.content)

            service_response = response.json()
            yield service_response["data"]["items"]

    def create_and_get_report_results(
            self,
            account_id: str,
            name: str,
            start_date: str,
            end_date: str,
            dimensions: list,
            metrics_names: list,
            dimension_filters: list,
            secret_id: str,
            backoff_attempts: int,
    ) -> Dict:
        """
        Method to create report, run it and fetch results in one go
        """
        report = {}
        try:
            report = self.create_report(
                account_id=account_id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                dimensions=dimensions,
                metrics_names=metrics_names,
                dimension_filters=dimension_filters,
                secret_id=secret_id,
            )
            run_report = self.run_report(
                account_id=account_id,
                report_id=report["id"],
                secret_id=secret_id,
            )
            if self.check_report_ready_with_exponential_backoff(
                    report_id=report["id"],
                    file_id=run_report["id"],
                    secret_id=secret_id,
                    backoff_attempts=backoff_attempts,
            ):
                return self.get_report_results(
                    report_id=report["id"],
                    file_id=run_report["id"],
                    secret_id=secret_id,
                )
        except CampaignManagerServiceException as err:
            raise err
        finally:
            if report:
                self.delete_report(
                    account_id=account_id,
                    report_id=report["id"],
                    secret_id=secret_id,
                )

    def get_accessible_parent_accounts(self, secret_id):
        """
        Returns accessible parent accounts
        :param secret_id: The ID of the secret in secret manager
        :return: list of parent accounts
        """

        header = get_headers(self._GET_ACCESSIBLE_PARENT_ACCOUNTS)
        body = {"secret_id": secret_id}

        response = self.session.request(
            "post", url=self._GET_ACCESSIBLE_PARENT_ACCOUNTS, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CampaignManagerServiceException(response.content)

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
            raise CampaignManagerServiceException(response.content)

    def get_account_accessibility(self, secret_id: str,account_id, advertiser_id: str) -> bool:
        """
        Gets account accessibility
        :param secret_id: The ID of the secret in secret manager
        :param account_id: Account ID
        :param advertiser_id: The ID of the advertiser.
        :return: True if account has access
        """
        body = {
            "secret_id": secret_id,
            "account_id": account_id,
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
            raise CampaignManagerServiceException(response.content)
