from rhino_health.lib.endpoints.endpoint import Endpoint
from rhino_health.lib.endpoints.sql_query.sql_query_dataclass import (
    SQLQuery,
    SQLQueryImportInput,
    SQLQueryInput,
)
from rhino_health.lib.utils import rhino_error_wrapper

BUFFER_TIME_IN_SEC = 300


class SQLQueryEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints to interact with a remote SQL server on the FCP
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "sql_query"

    @property
    def sql_query_dataclass(self):
        """
        @autoapi False
        :return:
        """
        return SQLQuery

    @rhino_error_wrapper
    def get_sql_query(self, sql_query_uid: str):
        """
        @autoapi True
        Returns a SQL dataclass

        Parameters
        ----------
        sql_query_uid: str
            UID for the SQL query

        Returns
        -------
        dataset: SQLQuery
            SQLQuery dataclass

        Examples
        --------
        >>> session.sql_query_input.get_sql_query(my_query_uid)
        Dataset()
        """
        return self.session.get(f"/sql_queries/{sql_query_uid}").to_dataclass(
            self.sql_query_dataclass
        )

    @rhino_error_wrapper
    def import_dataset_from_sql_query(self, sql_query_input: SQLQueryImportInput):
        """
        Returns a SQLQuery dataclass

        Parameters
        ----------
        sql_query_input: SQLQueryImportInput
            SQLQueryImportInput dataclass

        Returns
        -------
        sql_query_input: SQLQuery
            SQLQuery dataclass

        Examples
        --------
        >>> session.sql_query.import_dataset_from_sql_query(sql_query_input)
        SQLQuery()
        """

        data = sql_query_input.dict(by_alias=True)
        data["command_type"] = "import_dataset"
        data["command_params"] = {
            "dataset_name": data["dataset_name"],
            "contains_sensitive_data": not data["is_data_deidentified"],
            "data_schema_uid": data.get("data_schema", None),
            "timeout_seconds": data["timeout_seconds"],
        }

        result = self.session.post(
            f"/sql_queries",
            data=data,
        )
        return result.to_dataclass(self.sql_query_dataclass).wait_for_completion(
            timeout_seconds=data["timeout_seconds"] + BUFFER_TIME_IN_SEC
        )

    @rhino_error_wrapper
    def run_sql_query(self, sql_query_input: SQLQueryInput):
        """
        Returns a SQLQuery dataclass

        Parameters
        ----------
        sql_query_input: SQLQueryImportInput
            SQLQueryImportInput dataclass

        Returns
        -------
        sql_query_input: SQLQuery
            SQLQuery dataclass

        Examples
        --------
        >>> session.sql_query.run_sql_query(sql_query_input)
        SQLQuery()
        """
        data = sql_query_input.dict(by_alias=True)
        data["command_type"] = "metrics"
        data["command_params"] = {
            "metric_definitions": [metric.data() for metric in sql_query_input.metric_definitions],
            "timeout_seconds": data["timeout_seconds"],
        }
        del data["metric_definitions"]

        result = self.session.post(
            f"/sql_queries",
            data=data,
        )
        return result.to_dataclass(self.sql_query_dataclass).wait_for_completion(
            timeout_seconds=data["timeout_seconds"] + BUFFER_TIME_IN_SEC
        )
