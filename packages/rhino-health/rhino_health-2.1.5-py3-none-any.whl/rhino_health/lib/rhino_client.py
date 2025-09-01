import sys
from typing import List, Type

from rhino_health.lib.constants import ApiEnvironment
from rhino_health.lib.endpoints.code_object.code_object_endpoints import CodeObjectEndpoints
from rhino_health.lib.endpoints.code_run.code_run_endpoints import CodeRunEndpoints
from rhino_health.lib.endpoints.data_schema.data_schema_endpoints import DataSchemaEndpoints
from rhino_health.lib.endpoints.dataset.dataset_endpoints import DatasetEndpoints
from rhino_health.lib.endpoints.endpoint import Endpoint
from rhino_health.lib.endpoints.federated_dataset.federated_dataset_endpoints import (
    FederatedDatasetEndpoints,
)
from rhino_health.lib.endpoints.project.project_endpoints import ProjectEndpoints
from rhino_health.lib.endpoints.runtime_file.runtime_file_endpoints import RuntimeFileEndpoints
from rhino_health.lib.endpoints.semantic_mapping.semantic_mapping_endpoints import (
    SemanticMappingEndpoints,
    VocabularyEndpoints,
)
from rhino_health.lib.endpoints.sql_query.sql_query_endpoints import SQLQueryEndpoints
from rhino_health.lib.endpoints.syntactic_mapping.syntactic_mapping_endpoints import (
    SyntacticMappingEndpoints,
)
from rhino_health.lib.endpoints.user.user_endpoints import UserEndpoints
from rhino_health.lib.endpoints.workgroup.workgroup_endpoints import WorkgroupEndpoints
from rhino_health.lib.utils import alias, rhino_error_wrapper, setup_traceback, url_for

__api__ = ["RhinoClient"]


class SDKVersion:
    """
    Used internally for future backwards compatibility
    """

    STABLE = "1.0"
    PREVIEW = "2.0"


VERSION_TO_CLOUD_API = {SDKVersion.STABLE: "v2", SDKVersion.PREVIEW: "v2"}
"""
@autoapi False
"""


PUBLIC_ENDPOINTS: List[Type[Endpoint]] = [
    CodeObjectEndpoints,
    CodeRunEndpoints,
    DataSchemaEndpoints,
    DatasetEndpoints,
    FederatedDatasetEndpoints,
    ProjectEndpoints,
    RuntimeFileEndpoints,
    SemanticMappingEndpoints,
    SQLQueryEndpoints,
    SyntacticMappingEndpoints,
    UserEndpoints,
    WorkgroupEndpoints,
    VocabularyEndpoints,
]
"""
@autoapi False

Add new endpoints here and make sure to define ENDPOINT_NAME on your endpoint class.
"""


class RhinoClient:
    """
    Allows access to various endpoints directly from the RhinoSession

    Attributes
    ----------
    code_object: Access endpoints at the code_object level
    code_run: Access endpoints at the code_run level
    dataset: Access endpoints at the dataset level
    data_schema: Access endpoints at the data_schema level
    federated_dataset: Access endpoints for federated_datasets
    project: Access endpoints at the project level
    sql_query: Access endpoints for sql queries
    user: Access endpoints at the user level
    workgroup: Access endpoints at the workgroup level

    Examples
    --------
    >>> session.project.get_projects()
    array[Project...]
    >>> session.dataset.get_dataset(my_dataset_uid)
    Dataset

    See Also
    --------
    rhino_health.lib.endpoints.code_object.code_object_endpoints: Available code_object endpoints
    rhino_health.lib.endpoints.code_run.code_run_endpoints: Available code_run endpoints
    rhino_health.lib.endpoints.dataset.dataset_endpoints: Available dataset endpoints
    rhino_health.lib.endpoints.data_schema.data_schema_endpoints: Available data_schema endpoints
    rhino_health.lib.endpoints.project.project_endpoints: Available project endpoints
    rhino_health.lib.endpoints.sql_query.sql_query_endpoints: Available sql_query endpoints
    rhino_health.lib.endpoints.user.user_endpoints: Available user endpoints
    rhino_health.lib.endpoints.workgroup.workgroup_endpoints: Available workgroup endpoints
    """

    @rhino_error_wrapper
    def __init__(
        self,
        rhino_api_url: str = ApiEnvironment.PROD_API_URL,
        sdk_version: str = SDKVersion.STABLE,
        show_traceback: bool = False,
    ):
        setup_traceback(sys.excepthook, show_traceback)
        self.rhino_api_url = rhino_api_url
        self.sdk_version = sdk_version
        for endpoint in PUBLIC_ENDPOINTS:
            # Dynamically assign endpoints
            setattr(self, endpoint._endpoint_name(), endpoint(self))
        self.api_url = url_for(self.rhino_api_url, VERSION_TO_CLOUD_API[sdk_version])
