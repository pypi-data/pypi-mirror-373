from typing import Any, Callable, Dict, List, Optional, Union
from warnings import warn

import arrow
from funcy import compact, flatten

from rhino_health.lib.endpoints.code_object.code_object_dataclass import CodeObject
from rhino_health.lib.endpoints.data_schema.data_schema_dataclass import DataSchema
from rhino_health.lib.endpoints.dataset.dataset_dataclass import Dataset
from rhino_health.lib.endpoints.endpoint import Endpoint, NameFilterMode, VersionMode
from rhino_health.lib.endpoints.project.project_dataclass import (
    Project,
    ProjectCreateInput,
    SystemResources,
)
from rhino_health.lib.endpoints.workgroup.workgroup_dataclass import Workgroup
from rhino_health.lib.metrics.aggregate_metrics.aggregation_service import (
    get_cloud_aggregated_metric_data,
)
from rhino_health.lib.metrics.base_metric import (
    AggregatableMetric,
    BaseMetric,
    JoinableMetric,
    MetricResponse,
)
from rhino_health.lib.utils import alias, rhino_error_wrapper


def handle_resource_management_response(json_response):
    # TODO: However we are processing errors is not being stored correctly
    return {
        "filesystem_storage": {
            "total": json_response["filesystem_total_bytes"],
            "free": json_response["filesystem_free_bytes"],
            "used": json_response["filesystem_used_bytes"],
        },
        "cpu_percent_used": json_response["cpu_percent_used"],
        "memory": {
            "total": json_response["mem_total_bytes"],
            "free": json_response["mem_free_bytes"],
            "used": json_response["mem_used_bytes"],
        },
        "gpu": {
            "gpu_percent_used": json_response["gpu_percent_used"],
            "gpu_mem_percent_used": json_response["gpu_mem_percent_used"],
        },
    }


class ProjectEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints available to interact with Projects on the Rhino Platform

    Notes
    -----
    You should access these endpoints from the RhinoSession object
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "project"

    @property
    def project_dataclass(self):
        return Project

    @property
    def workgroup_dataclass(self):
        return Workgroup

    @property
    def dataset_dataclass(self):
        return Dataset

    @property
    def data_schema_dataclass(self):
        return DataSchema

    @property
    def resource_management(self):
        """
        @autoapi False
        """
        return SystemResources

    @rhino_error_wrapper
    def get_projects(self, project_uids: Optional[List[str]] = None) -> List[Project]:
        """
        @autoapi True
        Returns projects the SESSION has access to. If uids are provided, returns only the
        project_uids that are specified.

        :param project_uids: Optional List of strings of project uids to get
        """
        if not project_uids:
            return self.session.get("/projects/").to_dataclasses(self.project_dataclass)
        else:
            return [
                self.session.get(f"/projects/{project_uid}/").to_dataclass(self.project_dataclass)
                for project_uid in project_uids
            ]

    def get_system_resources_for_workgroup(self, project_uid, workgroup_uid) -> SystemResources:
        """
        Returns agent system resources(Memory, GPU, storage) for a collaborating workgroup.

        .. warning:: This feature is under development and the return response may change

        Parameters
        ----------
        project_uid: str
            UID of the project
        workgroup_uid: str
            UID of the workgroup

        Returns
        -------
        system resources: SystemResources
            SystemResources dataclass that match the name
        """

        return self.session.get(
            f"projects/{project_uid}/get_collaborator_resources/{workgroup_uid}/"
        ).to_dataclass(self.resource_management, handle_resource_management_response)

    def get_project_permissions(self, project_or_project_uid: Union[Project, str]):
        """
        @autoapi False
        """
        return self.session.get(
            f"projects/{project_or_project_uid if isinstance(project_or_project_uid, str) else project_or_project_uid.uid}/permissions"
        ).no_dataclass_response()

    @rhino_error_wrapper
    def get_project_by_name(self, name: str):
        """
        Returns Project dataclass

        Parameters
        ----------
        name: str
            Full name for the Project

        Returns
        -------
        project: Project
            Project dataclass that match the name

        Examples
        --------
        >>> session.project.get_project_by_name(my_project_name)
        Project()
        """
        results = self.search_for_projects_by_name(name, NameFilterMode.EXACT)
        return max(results, key=lambda x: arrow.get(x.created_at)) if results else None

    @rhino_error_wrapper
    def search_for_projects_by_name(
        self, name: str, name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS
    ):
        """
        Returns Project dataclasses

        Parameters
        ----------
        name: str
            Full or partial name for the Project
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified matching mode

        Returns
        -------
        projects: List[Project]
            Project dataclasses that match the name

        Examples
        --------
        >>> session.project.search_for_projects_by_name(my_project_name)
        [Project()]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        """
        query_params = self._get_filter_query_params(
            {"name": name}, name_filter_mode=name_filter_mode
        )
        results = self.session.get("/projects", params=query_params)
        return results.to_dataclasses(self.project_dataclass)

    @rhino_error_wrapper
    def get_project_stats(self, project_uid: str) -> Dict[str, Any]:
        return self.session.get(f"/projects/{project_uid}/stats").no_dataclass_response()

    @rhino_error_wrapper
    def add_project(self, project: ProjectCreateInput) -> Project:
        """
        Adds a new project owned by the currently logged in user.

        .. warning:: This feature is under development and the interface may change
        """
        return self.session.post("/projects", data=project.dict(by_alias=True)).to_dataclass(
            self.project_dataclass
        )

    @rhino_error_wrapper
    def remove_project(self, project_or_uid: Union[str, Project]):
        """
        Remove a Project with PROJECT_OR_UID from the system
        """
        return self.session.delete(
            f"/projects/{project_or_uid if isinstance(project_or_uid, str) else project_or_uid.uid}"
        ).no_dataclass_response()

    @rhino_error_wrapper
    def get_datasets(self, project_uid: str) -> List[Dataset]:
        """
        Returns Datasets associated with the project_uid
        """
        if not project_uid:
            raise ValueError("Must provide a project id")
        return self.search_for_datasets_by_name(
            "", version=VersionMode.ALL, project_uid=project_uid
        )

    @rhino_error_wrapper
    def get_dataset_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None
    ) -> Optional[Dataset]:
        """
        Returns Dataset dataclass

        See Also
        --------
        rhino_health.lib.endpoints.dataset.dataset_endpoints.get_dataset_by_name
        """
        return self.session.dataset.get_dataset_by_name(name, version, project_uid)

    @rhino_error_wrapper
    def search_for_datasets_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None, name_filter_mode=None
    ) -> List[Dataset]:
        """
        Returns Dataset dataclasses

        See Also
        --------
        rhino_health.lib.endpoints.dataset.dataset_endpoints.search_for_datasets_by_name
        """
        return self.session.dataset.search_for_datasets_by_name(
            name, version, project_uid, name_filter_mode=name_filter_mode
        )

    @rhino_error_wrapper
    def get_data_schemas(self, project_uid: str) -> List[DataSchema]:
        """
        Returns Datashemas associated with the project_uid
        """
        if not project_uid:
            raise ValueError("Must provide a project id")
        query_params = self._get_filter_query_params({"project_uid": project_uid})
        return self.search_for_data_schemas_by_name(
            "", version=VersionMode.ALL, project_uid=project_uid
        )

    @rhino_error_wrapper
    def get_data_schema_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None
    ) -> DataSchema:
        """
        Returns DataSchema dataclass

        See Also
        --------
        rhino_health.lib.endpoints.data_schema.data_schema_endpoints.get_data_schema_by_name
        """
        return self.session.data_schema.get_data_schema_by_name(name, version, project_uid)

    @rhino_error_wrapper
    def search_for_data_schemas_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None, name_filter_mode=None
    ) -> List[DataSchema]:
        """
        Returns DataSchema dataclasses

        See Also
        --------
        rhino_health.lib.endpoints.data_schema.data_schema_endpoints.search_for_data_schemas_by_name
        """
        return self.session.data_schema.search_for_data_schemas_by_name(
            name, version, project_uid, name_filter_mode=name_filter_mode
        )

    @rhino_error_wrapper
    def get_code_objects(self, project_uid: str) -> List[CodeObject]:
        """
        Returns CodeObjects associated with the project
        """
        if not project_uid:
            raise ValueError("Must provide a project id")
        return self.search_for_code_objects_by_name(
            "", version=VersionMode.ALL, project_uid=project_uid
        )

    @rhino_error_wrapper
    def get_code_object_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None
    ) -> Optional[CodeObject]:
        """
        Returns the CodeObject

        See Also
        --------
        rhino_health.lib.endpoints.code_object.code_object_endpoints.get_code_object_by_name
        """
        return self.session.code_object.get_code_object_by_name(name, version, project_uid)

    @rhino_error_wrapper
    def search_for_code_objects_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None, name_filter_mode=None
    ) -> List[CodeObject]:
        """
        Returns CodeObject dataclasses

        See Also
        --------
        rhino_health.lib.endpoints.code_object.code_object_endpoints.search_for_code_objects_by_name
        """
        return self.session.code_object.search_for_code_objects_by_name(
            name, version, project_uid, name_filter_mode=name_filter_mode
        )

    @rhino_error_wrapper
    def get_collaborating_workgroups(self, project_uid: Union[str, Project]):
        collaborating_workgroup_uids = (
            project_uid.collaborating_workgroup_uids
            if not isinstance(project_uid, str)
            else self.session.project.get_projects([project_uid])[0].collaborating_workgroup_uids
        )
        return self.session.workgroup.get_workgroups(collaborating_workgroup_uids)

    @rhino_error_wrapper
    def add_collaborator(self, project_uid: str, collaborating_workgroup_uid: str):
        """
        Adds COLLABORATING_WORKGROUP_UID as a collaborator to PROJECT_UID

        .. warning:: This feature is under development and the interface may change
        """
        # TODO: Backend needs to return something sensible
        # TODO: Automatically generated swagger docs don't match with internal code
        self.session.post(
            f"/projects/{project_uid}/add_collaborator/{collaborating_workgroup_uid}", {}
        )
        return self.session.project.get_projects([project_uid])[0]

    @rhino_error_wrapper
    def remove_collaborator(self, project_uid: str, collaborating_workgroup_uid: str):
        """
        Removes COLLABORATING_WORKGROUP_UID as a collaborator from PROJECT_UID

        .. warning:: This feature is under development and the interface may change
        """
        # TODO: What should this return internally
        # TODO: Backend needs to return something sensible
        # TODO: Automatically generated swagger docs don't match with internal code
        self.session.post(
            f"/projects/{project_uid}/remove_collaborator/{collaborating_workgroup_uid}", {}
        )

    @rhino_error_wrapper
    def aggregate_dataset_metric(
        self,
        dataset_uids: List[str],
        metric_configuration: BaseMetric,
        aggregation_method_override: Optional[
            Callable
        ] = None,  # TODO: Deprecated - remove in the next sdk breaking changes version
    ) -> MetricResponse:
        """
        Returns the aggregate metric based on the METRIC_CONFIGURATION for a list of datasets.
        In order to override the aggregation method, use the custom_aggregation_method argument in the metric config object.
        The method signature should be: method(metric_name: str, metric_results: List[Dict[str, Any]], **kwargs),
            where the metric_results are each of the Dataset results for the metric,
            and the method should return a dict with the structure of: {metric_name: <aggregated_value>}.

        Parameters
        ----------
        dataset_uids: List[str]
            UIDS for the Datasets to query metrics against
        metric_configuration: BaseMetric
            Configuration for the metric to be run
        aggregation_method_override: Optional[Callable] DEPRECATED
            A custom function to use to aggregate the results. The method signature should be: method(metric_name: str, metric_results: List[Dict[str, Any]], **kwargs),
            where the metric_results are each of the Dataset results for the metric,
            and the method should return a dict with the structure of: {metric_name: <aggregated_value>}.

        Returns
        -------
        metric_response: MetricResponse
            A response object containing the result of the query

        See Also
        --------
        rhino_health.lib.metrics : Dataclasses specifying possible metric configurations to send
        rhino_health.lib.metrics.base_metric.MetricResponse : Response object
        rhino_health.lib.metrics.aggregate_metrics.aggregation_methods : Sample aggregation methods
        """
        if not isinstance(metric_configuration, AggregatableMetric):
            raise ValueError(
                f"The chosen metric is not aggregatable. For using this metric, please use the dataset.get_metric endpoint instead, for a specific dataset."
            )

        if aggregation_method_override:
            warn(
                f"The parameter aggregation_method_override is deprecated, for overriding the aggregation method, use the custom_aggregation_method argument in the metric config object.",
                RuntimeWarning,
            )

        return get_cloud_aggregated_metric_data(self.session, dataset_uids, metric_configuration)

    @rhino_error_wrapper
    def joined_dataset_metric(
        self,
        configuration: JoinableMetric,
        query_datasets: List[str],
        filter_datasets: Optional[List[str]] = None,
    ) -> MetricResponse:
        """
        Perform a Federated Join Dataset Metric

        Intersection Joins allow filtering against columns in that are present in the filter dataset
        and then getting metrics from a separate query dataset which do not contain those columns.

        Union Joins handles deduplication of results between multiple datasets.

        Parameters
        ----------
        configuration: JoinableMetric
            Configuration for the metric to be run
        query_datasets: List[str]
            UIDS for the dataset(s) to get the query values from.
            For INTERSECTION mode supports one dataset.
            For UNION mode supports any number of datasets.
        filter_datasets: Optional[List[str]] = None
            UIDS for the dataset(s) to perform the join query against.
            For INTERSECTION mode supports one dataset.
            For UNION mode this is ignored

        Returns
        -------
        metric_response: MetricResponse
            A response object containing the result of the query
        """
        configuration.filter_datasets = filter_datasets
        configuration.query_datasets = query_datasets
        all_dataset_uids = list(flatten(compact([filter_datasets, query_datasets])))
        return self.session.project.aggregate_dataset_metric(all_dataset_uids, configuration)
