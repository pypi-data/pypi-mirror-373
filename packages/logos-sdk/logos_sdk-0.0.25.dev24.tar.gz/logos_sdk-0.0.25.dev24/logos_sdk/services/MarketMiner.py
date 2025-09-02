"""
from requests import request
from typing import List
from logos_sdk.services import get_headers
from http import HTTPStatus
from dotenv import load_dotenv
import os


class MarketMinerServiceException(Exception):
    pass


class MarketMiner:

    def __init__(self, url=None):
        load_dotenv()
        self._URL = url or os.environ.get("MARKET_MINER_SERVICE_PATH")
        self._SEARCH_VOLUME = self._URL + "/search-volume-data"

    def search_volume_data(self, lang: str, keywords: List[str]) -> List:

        Function to call mm api point
        :param lang: Language can be "cs", "sk", "us", "pl", "gb"
        :param keywords: List of keywords you want search volume
        :return:

        body = {
            "lang": lang,
            "keywords": keywords
        }

        header = get_headers(self._SEARCH_VOLUME)

        response = request("post", url=self._SEARCH_VOLUME, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return service_response["data"]
        
        raise MarketMinerServiceException(service_response)
"""