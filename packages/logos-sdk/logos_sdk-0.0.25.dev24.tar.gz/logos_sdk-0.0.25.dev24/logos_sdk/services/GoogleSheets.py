from requests import request
from typing import List, Dict, Tuple, Union
from logos_sdk.services import get_headers
from http import HTTPStatus
from dotenv import load_dotenv
import os


class SheetServiceException(Exception):
    pass


class SheetService:

    def __init__(self, sheet_link=None, url=None):
        load_dotenv()
        self._URL = url or os.environ.get("GOOGLE_SHEETS_SERVICE_PATH")
        self.sheet_link = sheet_link
        self._UPDATE = self._URL + "/update"
        self._BATCH_UPDATE = self._URL + "/batch-update"
        self._GET_RECORDS = self._URL + "/get-records"
        self._GET_VALUES = self._URL + "/get-values"
        self._CLEAR = self._URL + "/clear"
        self._DELETE = self._URL + "/delete"
        self._FORMAT = self._URL + "/format"
        self._SORT = self._URL + "/sort"
        self._RESIZE_CLEAR = self._URL + "/resize-clear"
        self._GET_COL_VALUES = self._URL + "/get-column-values"

    def update(self, update: List[List], worksheet_name: str, a1_notation: str = None,
               create_if_not_exist: bool = False, clear: bool = False, sheet_link: str = None) -> None:
        """
        Function to call SheetService with update route
        :param update: List of lists of values to be added to worksheet
        :param worksheet_name: Name of worksheet in spreadsheet
        :param a1_notation: Range which is updated
        :param create_if_not_exist: If true new worksheet is created if the worksheet name did not exist in spreadsheet
        :param sheet_link: Url link for spreadsheet
        :param clear If true whole worksheet is cleaned before update.
        Parameters rules and ranges are only applied when new sheet is created. If you want to apply new changes
        please use set_rules/format.
        :return: None
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "update": update,
            "worksheet_name": worksheet_name,
            "range": "A1" if a1_notation is None else a1_notation,
            "create_if_not_exist": create_if_not_exist,
            "clear": clear
        }

        header = get_headers(self._UPDATE)

        response = request("post", url=self._UPDATE, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return
        
        raise SheetServiceException(service_response)

    def batch_update(self, batch_updates: List[Dict[str, Union[str, Dict[str, List[List]]]]],
                     create_if_not_exist: bool = False, sheet_link: str = None) -> None:
        """
        Function to call SheetService with batch-update route.
        :param batch_updates: List(Dict("worksheet_name": str,
                                        "batch_update": Dict("range": "a1_notation", "values": List(List(Any)))))
        :param create_if_not_exist: If true, creates every non-existing worksheet in batch updates
        :param sheet_link: Url link for spreadsheet
        :return: None
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "batch_updates": batch_updates,
            "create_if_not_exist": create_if_not_exist
        }

        header = get_headers(self._BATCH_UPDATE)

        response = request("post", url=self._BATCH_UPDATE, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return
        
        raise SheetServiceException(service_response)

    def get_records(self, worksheet_name: str, sheet_link: str = None) -> List[Dict]:
        """
        Function to call SheetService with get-records route
        :param worksheet_name:
        :param sheet_link: Url link for spreadsheet.
        :return: Dict(List(Int/Str/Float))
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "worksheet_name": worksheet_name
        }

        header = get_headers(self._GET_RECORDS)

        response = request("post", url=self._GET_RECORDS, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return service_response["data"]
        
        raise SheetServiceException(service_response)

    def get_values(self, worksheet_name: str, a1_range: str = None, row_start: int = None, col_start: int = None,
                   row_end: int = None, col_end: int = None, sheet_link: str = None) -> List[List]:
        """
        Function to call SheetService with get-values route. You can specify a1_range which you want to get. Or you can
        specify which rows/cols should be retrieved. If none of the parameters are fulfilled whole
        worksheet will be retrieved. A1_range cannot be combined with row/col start/end.
        :param worksheet_name:
        :param a1_range: A1 range to get data
        :param row_start: Row start
        :param col_start: Colum start
        :param row_end: Row end
        :param col_end: Colum end
        :param sheet_link: Url link for spreadsheet
        :return: List(List(Int/Str/Float))
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "worksheet_name": worksheet_name
        }

        if row_start is not None and col_start is not None and col_end is not None and row_end is not None:
            body = {**body, **{"row_start": row_start, "col_start": col_start, "row_end": row_end,
                               "col_end": col_end}}
        elif a1_range is not None:
            body["a1_range"] = a1_range

        header = get_headers(self._GET_VALUES)

        response = request("post", url=self._GET_VALUES, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return service_response["data"]
        
        raise SheetServiceException(service_response)

    def clear(self, worksheet_name: str, a1_range: str = None, row_clear_start: int = None,
              row_clear_end: int = None, sheet_link: str = None) -> None:
        """
         Function to call SheetService with clear route. You can specify cells which should be cleaned  with a1_range or
         starting and ending row. If none of them are filled whole worksheet will be cleaned.
         A1 range cannot be combined with row start/end
        :param worksheet_name: Name of the cleared worksheet
        :param a1_range: Range which should be cleared
        :param row_clear_start: Starting clearing row
        :param row_clear_end: Ending clearing row
        :param sheet_link: Url link for spreadsheet
        :return: None
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "worksheet_name": worksheet_name
        }

        if row_clear_start is not None and row_clear_end is not None:
            body = {**body, **{"row_clear_start": row_clear_start,
                               "row_clear_end": row_clear_end}}
        elif a1_range is not None:
            body["a1_range"] = a1_range

        header = get_headers(self._CLEAR)

        response = request("post", url=self._CLEAR, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return service_response["data"]
        
        raise SheetServiceException(service_response)

    def delete(self, worksheet_name: str, sheet_link: str = None) -> None:
        """
        Function to call SheetService with delete route
        :param worksheet_name: Name of the worksheet to be deleted
        :param sheet_link: Url link for spreadsheet
        :return: None
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "worksheet_name": worksheet_name
        }

        header = get_headers(self._DELETE)

        response = request("post", url=self._DELETE, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return
        
        raise SheetServiceException(service_response)

    def format(self, worksheet_name: str, cells_format: List[Dict], sheet_link: str = None, freeze: int = None) -> None:
        """
        Set formats for given worksheet
        :param worksheet_name: Name of the worksheet
        :param sheet_link: Url link for spreadsheet
        :param cells_format: An iterable whose elements are dict {color: hex, bold: bool}
        notation, e.g. 'A1:A5', and a ``CellFormat`` object)
        :param freeze num of rows to be frozen
        :return:
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "worksheet_name": worksheet_name,
            "cells_format": cells_format,
            "freeze": freeze
        }

        header = get_headers(self._FORMAT)

        response = request("post", url=self._FORMAT, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return
        
        raise SheetServiceException(service_response)

    def sort(self, worksheet_name: str, sort: Tuple[int, str], sheet_link: str = None, a1_range: str = None) -> None:
        """
        Sort given worksheet according to sort parameter. asc/des according to column number
        :param worksheet_name: Name of given worksheet
        :param sort: tuple (Union(asc, des), col_number)
        :param sheet_link: Url link for spreadsheet
        :param a1_range: Range which should be sorted
        :return: None
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "worksheet_name": worksheet_name,
            "sort": sort,
            "range": a1_range
        }

        header = get_headers(self._SORT)

        response = request("post", url=self._SORT, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return
        
        raise SheetServiceException(service_response)

    def resize_clear(self, worksheet_name: str, row_num: int, sheet_link: str = None) -> None:
        """
        This endpoint takes worksheet, resizes it to minimum (1, or num_of_frozen_rows + 1) which deletes data with
        formatting and then resizes it back to row_num.
        :param worksheet_name: Name of given worksheet
        :param row_num: new number of rows.
        :param sheet_link: Url link for spreadsheet
        :return:
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "worksheet_name": worksheet_name,
            "row_num": row_num
        }

        header = get_headers(self._RESIZE_CLEAR)

        response = request("post", url=self._RESIZE_CLEAR, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return
        
        raise SheetServiceException(service_response)

    def get_column_values(self, worksheet_name: str, col_num: int, sheet_link: str = None) -> List:
        """
        Returns a list of all values in column `col_num`
        :param worksheet_name: Name of given worksheet
        :param col_num: Number of column for which you want the date
        :param sheet_link: Url link for spreadsheet
        :return:
        """
        body = {
            "sheet_link": self.sheet_link if sheet_link is None else sheet_link,
            "worksheet_name": worksheet_name,
            "column": col_num
        }

        header = get_headers(self._GET_COL_VALUES)

        response = request("post", url=self._GET_COL_VALUES, json=body, headers=header)
        service_response = response.json()
        if response.status_code == HTTPStatus.OK:
            return service_response["data"]
        
        raise SheetServiceException(service_response)
