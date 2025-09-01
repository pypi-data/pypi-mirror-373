from typing import List, Optional, Union
from warnings import warn

import arrow

from rhino_health.lib.endpoints.endpoint import Endpoint, NameFilterMode, VersionMode
from rhino_health.lib.endpoints.federated_dataset.federated_dataset_dataclass import (
    FederatedDataset,
    FederatedDatasetCreateInput,
)
from rhino_health.lib.utils import rhino_error_wrapper


class FederatedDatasetEndpoints(Endpoint):
    """
    @autoapi True
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "federated_dataset"

    @rhino_error_wrapper
    def get_federated_datasets(
        self, federated_dataset_uids: Optional[List[str]] = None
    ) -> List[FederatedDataset]:
        """
        @autoapi True
        Gets the Federated Datasets with the specified FEDERATED_DATASET_UIDS

        .. warning:: This feature is under development and the interface may change
        """
        if not federated_dataset_uids:
            results = self.session.get("/federated_datasets/")
        else:
            query_params = self._get_filter_query_params({"uid__in": [federated_dataset_uids]})
            results = self.session.get(f"/federated_datasets/", params=query_params)

        return results.to_dataclasses(FederatedDataset)

    @rhino_error_wrapper
    def get_federated_dataset_by_name(
        self,
        name,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
    ) -> Optional[FederatedDataset]:
        """
        Returns the latest or a specific Federated Dataset

        .. warning:: This feature is under development and the interface may change
        .. warning:: VersionMode.ALL will return the same as VersionMode.LATEST

        Parameters
        ----------
        name: str
            Full name for the Federated Dataset
        version: Optional[Union[int, VersionMode]]
            Version of the Federated Dataset, latest by default, for an earlier version pass in an integer
        project_uid: Optional[str]
            Project UID to search under

        Returns
        -------
        data_schema: Optional[FederatedDataset]
            Federated Dataset with the name or None if not found

        Examples
        --------
        >>> session.federated_dataset.get_federated_dataset_by_name("My Federated Dataset")
        FederatedDataset("My Federated Dataset")
        """
        if version == VersionMode.ALL:
            warn(
                "VersionMode.ALL behaves the same as VersionMode.LATEST for get_federated_dataset_by_name(), did you mean to use search_for_federated_datasets_by_name()?",
                RuntimeWarning,
            )
        results = self.search_for_federated_datasets_by_name(
            name, version, name_filter_mode=NameFilterMode.EXACT
        )
        if len(results) > 1:
            warn(
                "More than one federated dataset was found with the name for the provided project,"
                "please verify the schema is correct. This function returns the last created schema",
                RuntimeWarning,
            )
        return max(results, key=lambda x: arrow.get(x.created_at)) if results else None

    @rhino_error_wrapper
    def search_for_federated_datasets_by_name(
        self,
        name: str,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
        name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS,
    ) -> List[FederatedDataset]:
        """
        Returns DataSchema dataclasses

        .. warning:: This feature is under development and the interface may change

        Parameters
        ----------
        name: str
            Full or partial name for the Federated Dataset
        version: Optional[Union[int, VersionMode]]
            Version of the Federated Dataset, latest by default
        project_uid: Optional[str]
            Project UID to search under
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified filter mode. By default uses CONTAINS

        Returns
        -------
        data_schemas: List[FederatedDataset]
            Federated Dataset dataclasses that match the name

        Examples
        --------
        >>> session.data_schema.search_for_data_schemas_by_name("My Federated Dataset")
        [FederatedDataset(name="My Federated Dataset")]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        rhino_health.lib.endpoints.endpoint.VersionMode : Return specific versions
        """
        query_params = self._get_filter_query_params(
            {"name": name, "object_version": version},
            name_filter_mode=name_filter_mode,
        )
        results = self.session.get("/federated_datasets", params=query_params)
        return results.to_dataclasses(FederatedDataset)

    @rhino_error_wrapper
    def create_federated_dataset(
        self, federated_dataset: FederatedDatasetCreateInput, add_version_if_exists: bool = False
    ) -> FederatedDataset:
        """
        @autoapi False

        Adds a new Federated Datast

        Parameters
        ----------
        federated_dataset: FederatedDatasetCreateInput
            FederatedDatasetCreateInput data class
        add_version_if_exists: bool
            If a Federated Dataset with the name already exists, create a new version.

        Returns
        -------
        federated_dataset: FederatedDataset
            FederatedDataset dataclass

        Examples
        --------
        >>> session.federated_dataset.create_federated_dataset(FederatedDatasetCreateInput(
        ...     name="My Federated Dataset",
        ...     datasets=[dataset.uid for dataset in datasets],
        ...     datasheet=json.dumps(datasheet),
        ...     analytics_visibility="Limited",
        ...     privacy_settings=json.dumps(privacy_settings),
        ...     primary_workgroup_uid=project.primary_workgroup_uid,
        ... ))
        FederatedDataset()
        """
        if add_version_if_exists:
            existing_federated_dataset = self.get_federated_dataset_by_name(federated_dataset.name)
            if existing_federated_dataset is not None:
                federated_dataset.base_version_uid = (
                    existing_federated_dataset.base_version_uid or existing_federated_dataset.uid
                )
                federated_dataset.model_fields_set.discard("version")
        result = self.session.post(
            "/federated_datasets",
            federated_dataset.dict(by_alias=True, exclude_unset=True),
        )

        return result.to_dataclass(FederatedDataset)

    @rhino_error_wrapper
    def remove_federated_dataset(self, federated_dataset_or_uid: Union[str, FederatedDataset]):
        """
        Remove a FederatedDataset with FEDERATED_DATASET_OR_UID from the system
        """
        return self.session.delete(
            f"/projects/{federated_dataset_or_uid if isinstance(federated_dataset_or_uid, str) else federated_dataset_or_uid.uid}"
        ).no_dataclass_response()
