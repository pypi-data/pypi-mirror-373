"""from requests import request
from typing import List, Dict
from logos_sdk.services import get_headers
from http import HTTPStatus
from dotenv import load_dotenv
import os


class CollabimServiceException(Exception):
    pass


class CollabimService:
    def __init__(self, project_id, secret_id, url=None):
        self.project_id = project_id
        self.secret_id = secret_id
        load_dotenv()
        self._URL = url or os.environ.get("COLLABIM_SERVICE_PATH")
        self._GET_LINKS_DATA = self._URL + "/get-links"
        self._GET_PROJECT_KEYWORDS = self._URL + "/get-project-keywords"
        self._GET_KEYWORDS_ACTUAL_POSITION = self._URL + "/get-keywords-actual-position"
        self._GET_PROJECT_ACTUAL_POSITION = self._URL + "/get-project-actual-position"
        self._GET_KEYWORDS_HISTORIC_POSITION = self._URL + "/get-keywords-historic-position"
        self._GET_PROJECT_HISTORIC_POSITION = self._URL + "/get-project-historic-position"
        self._GET_PROJECT_INFO = self._URL + "/get-project-info"

    def _get_links_data(self, page: int, items_per_page: int) -> List[Dict]:
        body = {
            "secret_id": self.secret_id,
            "project_id": self.project_id,
            "page": page,
            "items_per_page": items_per_page,
        }

        header = get_headers(self._GET_LINKS_DATA)

        response = request("post", url=self._GET_LINKS_DATA, json=body, headers=header)

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CollabimServiceException(response.content)

    def get_links_data(self, items_per_page: int = 500) -> List[Dict]:
        page = 1
        while True:
            links = self._get_links_data(page, items_per_page)
            if not links:
                break
            yield links
            page += 1

    def _get_project_keywords(self, page: int, items_per_page: int) -> List[Dict]:
        body = {
            "secret_id": self.secret_id,
            "project_id": self.project_id,
            "page": page,
            "items_per_page": items_per_page,
        }

        header = get_headers(self._GET_PROJECT_KEYWORDS)

        response = request(
            "post", url=self._GET_PROJECT_KEYWORDS, json=body, headers=header
        )
        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CollabimServiceException(response.content)

    def get_project_keywords(self, items_per_page: int = 500) -> List[Dict]:
        page = 1
        while True:
            keywords = self._get_project_keywords(page, items_per_page)
            if not keywords:
                break
            yield keywords
            page += 1

    def get_keywords_actual_position(
        self, project_keyword_ids: List[List[str]]
    ) -> List[Dict]:
        body = {
            "secret_id": self.secret_id,
            "project_id": self.project_id,
            "string_keywords_ids": project_keyword_ids,
        }

        header = get_headers(self._GET_KEYWORDS_ACTUAL_POSITION)

        response = request(
            "post", url=self._GET_KEYWORDS_ACTUAL_POSITION, json=body, headers=header
        )
        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CollabimServiceException(response.content)

    def get_keywords_historic_position(
        self, project_keyword_ids: List[List[str]], date_from, date_to
    ) -> List[Dict]:
        body = {
            "secret_id": self.secret_id,
            "project_id": self.project_id,
            "string_keywords_ids": project_keyword_ids,
            "date_from": date_from,
            "date_to": date_to,
        }

        header = get_headers(self._GET_KEYWORDS_HISTORIC_POSITION)

        response = request(
            "post", url=self._GET_KEYWORDS_HISTORIC_POSITION, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CollabimServiceException(response.content)

    def _get_project_actual_position(
        self, page: int, items_per_page: int
    ) -> List[Dict]:
        body = {
            "secret_id": self.secret_id,
            "project_id": self.project_id,
            "page": page,
            "items_per_page": items_per_page,
        }

        header = get_headers(self._GET_PROJECT_ACTUAL_POSITION)

        response = request(
            "post", url=self._GET_PROJECT_ACTUAL_POSITION, json=body, headers=header
        )
        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CollabimServiceException(response.content)

    def get_project_actual_position(self, items_per_page: int = 500) -> List[Dict]:
        page = 1
        while True:
            keywords = self._get_project_actual_position(page, items_per_page)
            if not keywords:
                break
            yield keywords
            page += 1

    def _get_project_historic_position(
        self,
        page: int,
        items_per_page: int,
        date_from: str,
        date_to: str,
    ) -> List[Dict]:
        body = {
            "secret_id": self.secret_id,
            "project_id": self.project_id,
            "page": page,
            "items_per_page": items_per_page,
            "date_from": date_from,
            "date_to": date_to,
        }

        header = get_headers(self._GET_PROJECT_HISTORIC_POSITION)

        response = request(
            "post", url=self._GET_PROJECT_HISTORIC_POSITION, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise CollabimServiceException(response.content)

    def get_project_historic_position(
        self,
        date_from: str,
        date_to: str,
        items_per_page: int = 500,
    ) -> List[Dict]:
        page = 1
        while True:
            keywords = self._get_project_historic_position(
                page, items_per_page, date_from, date_to
            )
            if not keywords:
                break
            yield keywords
            page += 1

    def get_project_info(self):
        header = get_headers(self._GET_PROJECT_INFO)
        body = {"secret_id": self.secret_id, "project_id": self.project_id}

        response = request(
            "post", url=self._GET_PROJECT_INFO, json=body, headers=header
        )
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return service_response["data"]

        raise CollabimServiceException(service_response)
"""