import os
from datetime import datetime

import google.auth.exceptions
from typing import List, Dict, Union, Optional

from google.api_core.exceptions import NotFound
from google.cloud.logging import Client as LoggerClient
from google.auth.exceptions import DefaultCredentialsError
from google.cloud.bigquery import Table
from google.cloud import bigquery
import numpy as np
import time

from google.api_core.retry import Retry

from logos_sdk.big_query import retry_on_not_found
from dotenv import load_dotenv


class BigQueryException(Exception):
    def __init__(self, messages):
        self.messages = messages


class BigQuery:
    BQ_ROWS_LIMIT = 10000
    _service = None

    def __init__(self):
        load_dotenv()
        self.project_id = os.environ.get("PROJECT_ID")
        self._service = bigquery.Client(project=self.project_id)
        try:
            self.logger = LoggerClient(_use_grpc=False).logger(name="logos-logging")
        except DefaultCredentialsError:
            self.logger = None

    def parse_fields(self, fields):
        result = []
        for row in fields:
            result.append(
                bigquery.schema.SchemaField(
                    row["name"],
                    row["col_type"],
                    mode=row["mode"],
                    fields=self.parse_fields(row["fields"]) if "fields" in row else [],
                )
            )
        return result

    def get_dataset(self, dataset_id: str):
        return self._service.get_dataset(dataset_id)

    def create_dataset(self, dataset_id: str):
        return self._service.create_dataset(dataset_id)

    def delete_dataset(self, dataset_id: str):
        self._service.delete_dataset(dataset_id, not_found_ok=True)

    def _get_table_id_sql_format(self, dataset_id: str, table_id: str):
        return f"{self.project_id}.{dataset_id}.{table_id}"

    def run_query(self, query: str) -> List[Dict]:
        df = self._service.query(query).result().to_dataframe().fillna(np.nan)
        return df.replace([np.nan], [None]).to_dict("records")

    def get_table(self, dataset_id: str, table_id: str) -> Table:
        sql_format = self._get_table_id_sql_format(dataset_id, table_id)
        return self._service.get_table(sql_format)

    def insert_into_table(
        self, dataset_id: str, table_id: str, records: List[Dict]
    ) -> None:
        bq_table = self.get_table(dataset_id, table_id)
        self._insert_into_table(bq_table, records)

    def insert_create_table(
        self,
        dataset_id: str,
        table_id: str,
        records: List[Dict],
        schema_columns: List[Dict],
    ) -> None:
        bq_table = self.check_table_exists(dataset_id, table_id)
        if bq_table is None:
            bq_table = self.create_table(dataset_id, table_id, schema_columns)

        self._insert_into_table(bq_table, records)

    def insert_create_partitioned_table(
        self,
        dataset_id: str,
        table_id: str,
        records: List[Dict],
        schema_columns: List[Dict],
        partitioning_column_name: str,
        partition_type=bigquery.TimePartitioningType.DAY,
    ):
        bq_table = self.check_table_exists(dataset_id, table_id)
        if bq_table is None:
            bq_table = self.create_partitioned_table(
                dataset_id,
                table_id,
                schema_columns,
                partitioning_column_name,
                partition_type,
            )

        self._insert_into_table(bq_table, records)

    def delete_table(self, dataset_id: str, table_id: str) -> None:
        if self.check_table_exists(dataset_id, table_id):
            sql_format = self._get_table_id_sql_format(dataset_id, table_id)
            self._service.delete_table(sql_format)

    def check_table_exists(self, dataset_id: str, table_id: str) -> Optional[Table]:
        try:
            return self.get_table(dataset_id, table_id)
        except google.cloud.exceptions.NotFound:
            return None

    def create_partitioned_table(
        self,
        dataset_id: str,
        table_id: str,
        schema_columns: List[Dict],
        partitioning_column_name: str,
        partition_type=bigquery.TimePartitioningType.DAY,
    ):
        table_schema = [
            bigquery.schema.SchemaField(
                row["name"],
                row["col_type"],
                mode=row["mode"],
                fields=self.parse_fields(row["fields"]) if "fields" in row else [],
            )
            for row in schema_columns
        ]
        try:
            sql_format = self._get_table_id_sql_format(dataset_id, table_id)
            table_object = bigquery.Table(sql_format, schema=table_schema)
            # Set partitioning on the "report_date" column
            table_object.time_partitioning = bigquery.TimePartitioning(
                type_=partition_type,
                field=partitioning_column_name,  # The column to use for partitioning
            )
            return self._service.create_table(table_object)
        except google.cloud.exceptions.Conflict:
            return False

    def create_table(
        self, dataset_id: str, table_id: str, schema_columns: List[Dict]
    ) -> Union[bool, Table]:
        table_schema = [
            bigquery.schema.SchemaField(
                row["name"],
                row["col_type"],
                mode=row["mode"],
                fields=self.parse_fields(row["fields"]) if "fields" in row else [],
            )
            for row in schema_columns
        ]
        try:
            sql_format = self._get_table_id_sql_format(dataset_id, table_id)
            table_object = bigquery.Table(sql_format, schema=table_schema)
            return self._service.create_table(table_object)
        except google.cloud.exceptions.Conflict:
            return False

    def create_view(self, dataset_id, view_id, sql_string):
        try:
            sql_format = self._get_table_id_sql_format(dataset_id, view_id)
            view = bigquery.Table(sql_format)
            view.view_query = sql_string
            return self._service.create_table(view)
        except google.cloud.exceptions.Conflict:
            return False

    def get_table_last_modified_date(self, dataset_id: str, table_id: str):
        last_modified_timestamp = (
            self._service.query(
                f"SELECT TIMESTAMP_MILLIS(last_modified_time) as time_stamp "
                f"FROM `{self.project_id}.{dataset_id}.__TABLES__` "
                f"WHERE table_id = '{table_id}'"
            )
            .result()
            .to_dataframe()
        )

        if last_modified_timestamp.empty:
            raise NotFound("Table does not exist!")

        last_modified_timestamp = last_modified_timestamp["time_stamp"].iloc[0]
        last_modified_date = datetime.strptime(
            str(last_modified_timestamp), "%Y-%m-%d %H:%M:%S.%f+00:00"
        )

        return last_modified_date

    @retry_on_not_found
    def _insert_into_table(
        self, bq_table: Table, records: List[Dict], attempts: int
    ) -> None:
        if len(records) > self.BQ_ROWS_LIMIT:
            for index in range(0, len(records), self.BQ_ROWS_LIMIT):
                errors = self._service.insert_rows(
                    bq_table,
                    records[index : (index + self.BQ_ROWS_LIMIT)],
                    retry=Retry(
                        total=2, connect=4, backoff_factor=2, allowed_methods=None
                    ),
                )
                time.sleep(2)
                if errors:
                    raise BigQueryException(errors)
        else:
            errors = self._service.insert_rows(bq_table, records)
            if errors:
                raise BigQueryException(errors)
