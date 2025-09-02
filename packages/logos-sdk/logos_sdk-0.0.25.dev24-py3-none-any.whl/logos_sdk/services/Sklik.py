from typing import List, Dict, Union
from logos_sdk.services import get_retry_session, get_headers
from http import HTTPStatus

import logging
from pytz import timezone
from datetime import timedelta, datetime
from dotenv import load_dotenv
from functools import wraps
import json
import os


class SklikServiceException(Exception):
    pass


class DataStatus:
    ERROR = "error"
    COMPLETE = "complete"
    PENDING = "preparing"


DATA_NOT_READY_MESSAGE = (
    "The job could not be run properly - data for yesterday was not yet ready in the Sklik API "
    "at the time of its execution. Set the job to run at a later time to avoid this. "
)

DATA_ALMOST_READY_MESSAGE = (
    "The job run properly but data for yesterday was not yet all ready in the Sklik API "
    "at the time of its execution. Set the job to run at a later time to avoid this. "
)


def get_session_if_malformed(wrapped_function):
    @wraps(wrapped_function)
    def inner(*args, **kwargs):
        try:
            return wrapped_function(*args, **kwargs)
        except SklikServiceException as err:
            if (
                json.loads(err.args[0].decode("utf8")).get("detail")
                == "Session has expired or is malformed."
            ):
                args[0].get_session(args[0]._secret_id, args[0]._account_email)
                return wrapped_function(*args, **kwargs)
            else:
                raise err

    return inner


def get_report_results_if_expired(wrapped_function):
    @wraps(wrapped_function)
    def inner(*args, **kwargs):
        try:
            return wrapped_function(*args, **kwargs)
        except SklikServiceException as err:
            if (
                json.loads(err.args[0].decode("utf8")).get("detail")
                == "Requested report has expired. Please create a new report by calling createReport endpoint."
            ):
                print("Report expired, creating new report")
                args[0].get_session(args[0]._secret_id, args[0]._account_email)
                return wrapped_function(*args, **kwargs)
            else:
                raise err

    return inner


class SklikService:
    def __init__(self, url=None):
        load_dotenv()
        self.request_session = get_retry_session()
        self._URL = url or os.environ.get("SKLIK_SERVICE_PATH")
        self._CREATE_REPORT = self._URL + "/create-report"
        self._READ_REPORT = self._URL + "/read-report"
        self._API = self._URL + "/call-api"
        self._GET_CLIENT = self._URL + "/get-client"
        self._CHECK_DATA_READY = self._URL + "/check-data-ready"
        self._LOGOUT = self._URL + "/logout"
        self._API_LIMITS = self._URL + "/api-limits"
        self._GET_SESSION = self._URL + "/get-session"
        self._GET_SESSION_WITHOUT_ACCOUNT = self._URL + "/get-session-without-account"
        self.session = None  # dict {"sklik_session": "", "user_id": ""}
        self._secret_id = None
        self._account_email = None

    def get_session(self, secret_id: str, account_email: str) -> None:
        """
        Manages initial login of the sessions, returns dict with sklik session string and user id int
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :return: Dict
        """
        body = {"account_email": account_email, "secret_id": secret_id}
        header = get_headers(self._GET_SESSION)
        response = self.request_session.request(
            "post", url=self._GET_SESSION, json=body, timeout=70, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            self.session = {
                "sklik_session": service_response["data"]["sklik_session"],
                "user_id": service_response["data"]["user_id"],
            }
            self._secret_id = secret_id
            self._account_email = account_email
        else:
            raise SklikServiceException(response.content)

    def get_session_without_account(self, secret_id: str) -> None:
        """
        Manages initial login of the sessions, returns dict with sklik session string without user id int
        :param secret_id: The ID of the secret in secret manager
        :return: Dict
        """
        body = {"secret_id": secret_id}
        header = get_headers(self._GET_SESSION_WITHOUT_ACCOUNT)
        response = self.request_session.request(
            "post",
            url=self._GET_SESSION_WITHOUT_ACCOUNT,
            json=body,
            timeout=70,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            self.session = {
                "sklik_session": service_response["data"]["sklik_session"],
                "user_id": None,
            }
            self._secret_id = secret_id
        else:
            raise SklikServiceException(response.content)

    def logout_of_current_session(self) -> None:
        """
        Attempts to log out of the current session, nothing happens if not ok
        :return:
        """
        try:
            if self.session is not None:
                header = get_headers(self._LOGOUT)
                self.request_session.request(
                    "post",
                    url=self._LOGOUT,
                    json=self.session,
                    timeout=70,
                    headers=header,
                )

        except:
            pass

    @get_session_if_malformed
    @get_report_results_if_expired
    def get_report_results(
        self,
        secret_id: str,
        account_email: str,
        report_type: str,
        date_from: str,
        date_to: str,
        columns: List[str],
        create_params: Dict[str, Union[int, str]] = None,
        read_params: Dict[str, Union[int, str]] = None,
    ) -> List[Dict]:
        """
        It creates sklik report with /create-report call in sklik service and reads sklik report with pagination
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :param report_type: Types for report from sklik api
        :param date_from: Start date in format yyyy-mm-dd
        :param date_to: End date in format yyyy-mm-dd
        :param columns: list of strings which names columns
        :param create_params: additional params from sklik api for creating report
        :param read_params: additional params from sklik api for reading report
        :return:
        """
        if self.session is None:
            self.get_session(secret_id, account_email)

        report_data = self._create_report(
            secret_id, account_email, report_type, date_from, date_to, create_params
        )
        result = []
        for page in range(report_data["count"]):
            body = {
                "report_type": report_type,
                "report_id": report_data["report_id"],
                "offset": page,
                "columns": columns,
            }
            if read_params:
                body.update({"params": read_params})

            header = get_headers(self._READ_REPORT)
            response = self.request_session.request(
                "post", url=self._READ_REPORT, json=body | self.session,
                timeout=70,
                headers=header,
            )


            if response.status_code == HTTPStatus.OK:
                service_response = response.json()
                result.extend(service_response["data"])
            else:
                raise SklikServiceException(response.content)

        return result

    @get_session_if_malformed
    def get_streamed_report_results(
        self,
        secret_id: str,
        account_email: str,
        report_type: str,
        date_from: str,
        date_to: str,
        columns: List[str],
        create_params: Dict[str, Union[int, str]] = None,
    ) -> List[Dict]:
        """
        It creates sklik report with /create-report call in sklik service and reads sklik report with pagination
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :param report_type: Types for report from sklik api
        :param date_from: Start date in format yyyy-mm-dd
        :param date_to: End date in format yyyy-mm-dd
        :param columns: list of strings which names columns
        :param create_params: additional params from sklik api for creating report
        :return:
        """

        if self.session is None:
            self.get_session(secret_id, account_email)

        report_data = self._create_report(
            secret_id, account_email, report_type, date_from, date_to, create_params
        )

        for page in range(report_data["count"]):
            body = {
                "report_type": report_type,
                "report_id": report_data["report_id"],
                "offset": page,
                "columns": columns,
            }

            header = get_headers(self._READ_REPORT)
            response = self.request_session.request(
                "post", url=self._READ_REPORT, json=body | self.session,
                timeout=70,
                headers=header,
            )

            if response.status_code == HTTPStatus.OK:
                service_response = response.json()
                yield service_response["data"]
            else:
                raise SklikServiceException(response.content)

    def _create_report(
        self,
        secret_id: str,
        account_email: str,
        report_type: str,
        date_from: str,
        date_to: str,
        params: Dict[str, Union[int, str]] = None,
    ) -> Dict:
        """
         Function creates sklik report with /create-report call
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :param report_type: Types for report from sklik api
        :param report_type: Types for report from sklik api
        :param date_from: Start date
        :param date_to: End date
        :param params: additional params from sklik api.
        :return: {report_id, count, sklik_session, user_id}
        """

        if self.session is None:
            self.get_session(secret_id, account_email)

        self.params_ = {
            "report_type": report_type,
            "date_from": date_from,
            "date_to": date_to,
            "params": params,
        }
        body = self.params_

        header = get_headers(self._CREATE_REPORT)
        response = self.request_session.request(
            "post", url=self._CREATE_REPORT, json=body | self.session,
            timeout=70,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise SklikServiceException(response.content)

    @get_session_if_malformed
    def call_api(
        self, secret_id: str, account_email: str, method: str, params: List[Dict]
    ) -> Union[List, Dict]:
        """
        Function to call SklikService get-api route
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :param method: Any method with sklik api
        :param params: [{"name": "`parameter name`" "value": "`given parameters value`"}]
        :return:
        """

        if self.session is None:
            self.get_session(secret_id, account_email)

        body = {
            "method": method,
            "params": params,
        }

        header = get_headers(self._API)
        response = self.request_session.request(
            "post", url=self._API, json=body | self.session,
            timeout=70,
            headers=header,
        )


        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise SklikServiceException(response.content)

    @get_session_if_malformed
    def get_client(
        self,
        secret_id: str,
        account_email: str,
    ) -> Union[List, Dict]:
        """
        Function to call SklikService get-client route
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :return:
        """

        if self.session is None:
            self.get_session(secret_id, account_email)

        header = get_headers(self._GET_CLIENT)
        response = self.request_session.request(
            "post",
            url=self._GET_CLIENT,
            json={"sklik_session": self.session["sklik_session"]},
            timeout=70,
            headers=header,
        )


        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise SklikServiceException(response.content)

    @get_session_if_malformed
    def get_accessible_accounts(
        self,
        secret_id: str,
    ) -> Union[List, Dict]:
        """
        Function to retrieve accessible accounts
        :param secret_id: The ID of the secret in secret manager
        :return:
        """

        if self.session is None:
            self.get_session_without_account(secret_id)

        header = get_headers(self._GET_CLIENT)
        response = self.request_session.request(
            "post",
            url=self._GET_CLIENT,
            json={
                "sklik_session": self.session["sklik_session"],
                "filters": {"hide_inactive": True},
            },
            timeout=70,
            headers=header,
        )


        if response.status_code == HTTPStatus.OK:
            accounts = []
            service_response = response.json()
            data = service_response["data"]
            for account in data["foreignAccounts"]:
                accounts.append(
                    {
                        "id": account["userId"],
                        "name": account["username"],
                        "active": account["relationStatus"] == "live",
                    }
                )
            return accounts
        else:
            raise SklikServiceException(response.content)

    @get_session_if_malformed
    def check_data_ready(
        self,
        secret_id: str,
        account_email: str,
        date: str = None,
    ) -> int:
        """
        Checks if data on server are ready
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :param date: Day for check. Implicit date is yesterday.
        :return: raise exception if dada are not ready. Returns severity of a log
        """

        if self.session is None:
            self.get_session(secret_id, account_email)

        date = date or (
            datetime.now(timezone("UTC")).astimezone(timezone("Europe/Prague"))
            - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        body = {"date": date}

        header = get_headers(self._CHECK_DATA_READY)
        response = self.request_session.request(
            "post", url=self._CHECK_DATA_READY, json=body | self.session,
            timeout=70,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            if service_response["data"] == DataStatus.PENDING:
                raise Exception(DATA_NOT_READY_MESSAGE)
            elif service_response["data"] == DataStatus.ERROR:
                return logging.WARNING
            else:
                return logging.INFO
        else:
            raise SklikServiceException(response.content)

    @get_session_if_malformed
    def fetch_api_limits(
        self,
        secret_id: str,
        account_email: str,
    ) -> Union[List, Dict]:
        """
        Function to call SklikService api/limits route
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :return:
        """

        if self.session is None:
            self.get_session(secret_id, account_email)

        header = get_headers(self._API_LIMITS)
        response = self.request_session.request(
            "post", url=self._API_LIMITS, json=self.session,
            timeout=70,
            headers=header,
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise SklikServiceException(response.content)

    def get_account_accessibility(self, secret_id: str, account_email: str) -> bool:
        """
        Gets account accessibility
        :param secret_id: The ID of the secret in secret manager
        :param account_email: Account email to refers to Sklik accountId
        :return: True if account has access
        """
        body = {"account_email": account_email, "secret_id": secret_id}
        header = get_headers(self._GET_SESSION)
        response = self.request_session.request(
            "post", url=self._GET_SESSION, json=body,
            timeout=70,
            headers=header,
        )

        if response.status_code == 200:
            return True
        if (
            response.status_code == 401
            or response.status_code == 403
            or response.status_code == 404
        ):
            return False
        raise SklikServiceException(response.content)
