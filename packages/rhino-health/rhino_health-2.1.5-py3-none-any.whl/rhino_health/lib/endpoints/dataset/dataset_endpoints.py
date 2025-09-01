from typing import Optional, Union
from warnings import warn

import arrow

from rhino_health.lib.endpoints.dataset.dataset_dataclass import (
    BaseDataset,
    Dataset,
    DatasetCreateInput,
)
from rhino_health.lib.endpoints.endpoint import Endpoint, NameFilterMode, VersionMode
from rhino_health.lib.metrics.base_metric import AggregatableMetric, MetricResponse
from rhino_health.lib.utils import rhino_error_wrapper


class DatasetEndpoints(Endpoint):
    """
    @autoapi False

    Long term supported endpoints for datasets that are not likely to change
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "dataset"

    @property
    def dataset_dataclass(self):
        return Dataset

    @rhino_error_wrapper
    def get_dataset(self, dataset_uid: str):
        """
        @autoapi True
        Returns a Dataset dataclass

        Parameters
        ----------
        dataset_uid: str
            UID for the Dataset

        Returns
        -------
        dataset: Dataset
            Dataset dataclass

        Examples
        --------
        >>> session.dataset.get_dataset(my_dataset_uid)
        Dataset()
        """
        return self.session.get(f"/datasets/{dataset_uid}").to_dataclass(self.dataset_dataclass)

    @rhino_error_wrapper
    def get_dataset_metric(self, dataset_uid: str, metric_configuration) -> MetricResponse:
        """
        @autoapi True
        Queries the Dataset with DATASET_UID on-prem and returns the result based on the METRIC_CONFIGURATION

        Parameters
        ----------
        dataset_uid: str
            UID for the Dataset to query metrics against
        metric_configuration:
            Configuration for the query to run

        Returns
        -------
        metric_response: MetricResponse
            A response object containing the result of the query

        See Also
        --------
        rhino_health.lib.metrics : Dataclasses specifying possible metric configurations to send
        rhino_health.lib.metrics.base_metric.MetricResponse : Response object
        """
        if isinstance(metric_configuration, AggregatableMetric):
            return self.session.project.aggregate_dataset_metric(
                [dataset_uid], metric_configuration
            )
        return self.session.post(
            f"/datasets/{dataset_uid}/metric/",
            metric_configuration.data(),
        ).to_dataclass(MetricResponse)

    @rhino_error_wrapper
    def get_dataset_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None
    ) -> Optional[Dataset]:
        """
        Returns the latest or a specific Dataset dataclass

        .. warning:: VersionMode.ALL will return the same as VersionMode.LATEST

        Parameters
        ----------
        name: str
            Full name for the Dataset
        version: Optional[Union[int, VersionMode]]
            Version of the Dataset, latest by default, for an earlier version pass in an integer

        project_uid: Optional[str]
            Project UID to search under

        Returns
        -------
        dataset: Optional[Dataset]
            Dataset with the name or None if not found

        Examples
        --------
        >>> session.dataset.get_dataset_by_name("My Dataset")
        Dataset(name="My Dataset")
        """
        if version == VersionMode.ALL:
            warn(
                "VersionMode.ALL behaves the same as VersionMode.LATEST for get_dataset_by_name(), did you mean to use search_for_datasets_by_name()?",
                RuntimeWarning,
            )
        results = self.search_for_datasets_by_name(name, version, project_uid, NameFilterMode.EXACT)
        return max(results, key=lambda x: arrow.get(x.created_at)) if results else None

    @rhino_error_wrapper
    def search_for_datasets_by_name(
        self,
        name: str,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
        project_uid: Optional[str] = None,
        name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS,
    ):
        """
        Returns Dataset dataclasses

        Parameters
        ----------
        name: str
            Full or partial name for the Dataset
        version: Optional[Union[int, VersionMode]]
            Version of the Dataset, latest by default
        project_uid: Optional[str]
            Project UID to search under
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified filter mode, By default uses CONTAINS

        Returns
        -------
        datasets: List[Dataset]
            Dataset dataclasses that match the name

        Examples
        --------
        >>> session.dataset.search_for_datasets_by_name("My Dataset")
        [Dataset(name="My Dataset")]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        rhino_health.lib.endpoints.endpoint.VersionMode : Which version to return
        """
        query_params = self._get_filter_query_params(
            {"name": name, "object_version": version, "project_uid": project_uid},
            name_filter_mode=name_filter_mode,
        )
        result = self.session.get("/datasets", params=query_params)
        return result.to_dataclasses(self.dataset_dataclass)

    @rhino_error_wrapper
    def add_dataset(
        self, dataset: DatasetCreateInput, return_existing=True, add_version_if_exists=False
    ) -> Dataset:
        """
        Adds a new Dataset on the remote instance.

        Parameters
        ----------
        dataset: DatasetCreateInput
            DatasetCreateInput data class
        return_existing: bool
            If a Dataset with the name already exists, return it instead of creating one.
            Takes precedence over add_version_if_exists
        add_version_if_exists
            If a Dataset with the name already exists, create a new version.

        Returns
        -------
        dataset: Dataset
            Dataset dataclass

        Examples
        --------
        >>> session.dataset.add_dataset(add_dataset_input)
        Dataset()
        """
        if return_existing or add_version_if_exists:
            try:
                existing_dataset = self.search_for_datasets_by_name(
                    dataset.name,
                    project_uid=dataset.project_uid,
                    name_filter_mode=NameFilterMode.EXACT,
                )[0]
                if return_existing:
                    return existing_dataset
                else:
                    dataset.base_version_uid = (
                        existing_dataset.base_version_uid or existing_dataset.uid
                    )
                    dataset.model_fields_set.discard("version")
            except Exception:
                # If no existing CodeObject exists do nothing
                pass
        newly_created_dataset = self._create_dataset(dataset)
        return self.get_dataset(newly_created_dataset.uid)

    @rhino_error_wrapper
    def _create_dataset(self, dataset: DatasetCreateInput) -> Dataset:
        """
        Creates a new Dataset on the remote instance.

        This function is intended for internal use only
        """
        args = dataset.create_args()
        args["import_params"] = dataset.import_args()
        args["contains_sensitive_data"] = not args["import_params"].pop("is_data_deidentified")
        return self.session.post(
            "/datasets/",
            args,
        ).to_dataclass(self.dataset_dataclass)


class DatasetEndpoints(DatasetEndpoints):
    """
    @autoapi True
    @base_class False

    Endpoints available to interact with Datasets on the Rhino Platform

    Notes
    -----
    You should access these endpoints from the RhinoSession object
    """

    @property
    def dataset_dataclass(self):
        """
        @autoapi False
        Dataclass to return for a Dataset endpoint for backwards compatibility
        """
        return Dataset

    @rhino_error_wrapper
    def export_dataset(self, dataset_uid: str, output_location: str, output_format: str):
        """
        Sends an export dataset request to the ON-PREM instance holding the specified DATASET_UID.
        The file will be exported to OUTPUT_LOCATION on the on-prem instance in OUTPUT_FORMAT

        .. warning:: This feature is under development and the interface may change

        Parameters
        ----------
        dataset_uid: str
            UID for the Dataset to export information on
        output_location: str
            Path to output the exported data to on the remote on-prem instance
        output_format: str
            The format to export the Dataset data in
        """
        return self.session.post(
            f"/datasets/{dataset_uid}/export",
            data={"output_location": output_location, "output_format": output_format},
        )

    @rhino_error_wrapper
    def sync_dataset_info(self, dataset_uid: str):
        """
        Initializes a data sync from the relevant on-prem instance for the provided DATASET_UID

        .. warning:: This feature is under development and the interface may change

        Parameters
        ----------
        dataset_uid: str
            UID for the Dataset to sync info
        """
        # TODO: what should this return value be?
        return self.session.get(f"/datasets/{dataset_uid}/info").no_dataclass_response()

    @rhino_error_wrapper
    def remove_dataset(self, dataset_or_uid: Union[str, Dataset]):
        """
        Remove a Dataset with DATASET_OR_UID from the system
        """
        return self.session.delete(
            f"/datasets/{dataset_or_uid if isinstance(dataset_or_uid, str) else dataset_or_uid.uid}/"
        ).no_dataclass_response()
