from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel
from rhino_health.lib.endpoints.project.project_baseclass import WithinProjectModel
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel
from rhino_health.lib.endpoints.workgroup.workgroup_baseclass import WithinWorkgroupModel
from rhino_health.lib.metrics.base_metric import BaseMetric


class QueryResultStatus(str, Enum):
    """
    The status of the SQLQuery
    """

    INITIALIZING = "Initializing"
    STARTED = "Started"
    COMPLETED = "Completed"
    FAILED = "Failed"


class SQLServerTypes(str, Enum):
    """
    Supported sql server Types
    """

    POSTGRESQL = "postgresql"
    MARIADB = "mariadb"
    MYSQL = "mysql"
    ORACLE = "oracle"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    IRIS = "iris"


class ConnectionDetails(BaseModel):
    """
    @autoapi True
    Defines the connection details for an external SQL DB
    """

    server_url: str
    """@autoapi True URL of the SQL server to query eg. myserverurl:5432"""
    server_user: str
    """@autoapi True The user to connect to the target SQL server"""
    server_type: SQLServerTypes
    """@autoapi True The type of the SQL server to query"""
    db_name: str
    """@autoapi True The name of the database to query"""
    password: str
    """@autoapi True The user password to connect to the target SQL server"""


class SQLQueryBase(RhinoBaseModel):
    """
    @autoapi False
    """

    project_uid: Annotated[str, Field(alias="project")]
    """@autoapi True The unique ID of the project in whose context this query is done"""
    workgroup_uid: Annotated[str, Field(alias="workgroup")]
    """@autoapi True The unique ID of the Workgroup in whose context this query is done"""
    sql_query: str
    """@autoapi True Sql query to run"""


class SQLQueryInput(SQLQueryBase):
    """
    @autoapi True
    Input parameters for running a metrics on a query in an external SQL DB

    See Also
    --------
    rhino_health.lib.endpoints.sql_query.sql_query_endpoints.SQLQueryEndpoints.run_sql_query
    """

    metric_definitions: List[BaseMetric]
    """@autoapi True The metric definitions to run on the SQL query"""
    connection_details: ConnectionDetails
    """@autoapi True The connection details to the SQL server"""
    timeout_seconds: int
    """@autoapi True The timeout in seconds for the query to run"""


class SQLQueryImportInput(SQLQueryBase):
    """
    @autoapi True
    Input parameters for importing a dataset form query run on external SQL DB

    See Also
    --------
    rhino_health.lib.endpoints.sql_query.sql_query_endpoints.SQLQueryEndpoints.run_sql_query
    """

    dataset_name: str
    """@autoapi True The name of the dataset to create"""
    is_data_deidentified: bool
    """@autoapi True Whether the data is deidentified or not"""
    connection_details: ConnectionDetails
    """@autoapi True The connection details to the SQL server"""
    data_schema_uid: Annotated[Optional[Any], Field(alias="data_schema")] = None
    """@autoapi True The unique ID of the data_schema in whose context this query is done"""
    timeout_seconds: int
    """@autoapi True The timeout in seconds for the query to run"""


class SQLQuery(WithinProjectModel, WithinWorkgroupModel, SQLQueryBase, UserCreatedModel):
    """
    @autoapi True
    An SQL query run which exists on the platform
    """

    uid: str
    """@autoapi True The Unique ID of the DICOMweb Query"""
    status: str
    """The query status"""
    ended_at: Optional[str] = None
    """@autoapi True When this query ended"""
    results: Optional[Any] = None
    """@autoapi True The results of this query"""
    errors: Optional[List[str]] = None
    """@autoapi True Errors that occurred while running this query"""
    connection_details: Dict[str, Any]
    """@autoapi True The connection details to the SQL server"""

    __hidden__ = ["command_type", "command_params"]

    @property
    def _process_finished(self):
        """
        @autoapi False
        """
        return self.status in {QueryResultStatus.COMPLETED, QueryResultStatus.FAILED}

    def wait_for_completion(
        self, timeout_seconds: int = 500, poll_frequency: int = 10, print_progress: bool = True
    ):
        """
        @autoapi True
        Wait for the asynchronous SQL query to complete

        Parameters
        ----------
        timeout_seconds: int = 500
            How many seconds to wait before timing out
        poll_frequency: int = 10
            How frequent to check the status, in seconds
        print_progress: bool = True
            Whether to print how long has elapsed since the start of the wait

        Returns
        -------
        result: SQLQuery
            Dataclasses representing the results of the run

        See Also
        --------
        rhino_health.lib.endpoints.sql_query.sql_query_dataclass.SQLQuery: Response object
        """
        result = self._wait_for_completion(
            name="SQL query",
            is_complete=self._process_finished,
            query_function=lambda sql_query: sql_query.session.sql_query.get_sql_query(
                sql_query.uid
            ),
            validation_function=lambda old, new: (new.status and new._process_finished),
            timeout_seconds=timeout_seconds,
            poll_frequency=poll_frequency,
            print_progress=print_progress,
            is_successful=lambda result: result.status == QueryResultStatus.COMPLETED,
            on_success=lambda result: print("Run finished successfully"),
            on_failure=lambda result: print("Run finished with errors"),
        )
        return result
