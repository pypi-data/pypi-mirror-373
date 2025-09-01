from typing import List, Optional, Union
from warnings import warn

import arrow

from rhino_health.lib.endpoints.data_schema.data_schema_dataclass import DataSchema
from rhino_health.lib.endpoints.endpoint import Endpoint, NameFilterMode, VersionMode
from rhino_health.lib.utils import alias, rhino_error_wrapper


class DataSchemaEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints for interacting with DataSchemas
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "data_schema"

    @property
    def data_schema_dataclass(self):
        """
        @autoapi False
        """
        return DataSchema

    @rhino_error_wrapper
    def get_data_schemas(self, data_schema_uids: Optional[List[str]] = None) -> List[DataSchema]:
        """
        @autoapi True
        Gets the Data Schemas with the specified DATA_SCHEMA_UIDS

        .. warning:: This feature is under development and the interface may change
        """
        if not data_schema_uids:
            return self.session.get("/data_schemas/").to_dataclasses(self.data_schema_dataclass)
        else:
            return [
                self.session.get(f"/data_schemas/{data_schema_uid}/").to_dataclass(
                    self.data_schema_dataclass
                )
                for data_schema_uid in data_schema_uids
            ]

    @rhino_error_wrapper
    def get_data_schema_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None
    ) -> Optional[DataSchema]:
        """
        Returns the latest or a specific DataSchema dataclass

        .. warning:: This feature is under development and the interface may change
        .. warning:: There is no uniqueness constraint on the name for data_schemas so you may not get the correct result
        .. warning:: VersionMode.ALL will return the same as VersionMode.LATEST

        Parameters
        ----------
        name: str
            Full name for the DataSchema
        version: Optional[Union[int, VersionMode]]
            Version of the DataSchema, latest by default, for an earlier version pass in an integer
        project_uid: Optional[str]
            Project UID to search under

        Returns
        -------
        data_schema: Optional[DataSchema]
            DataSchema with the name or None if not found

        Examples
        --------
        >>> session.data_schema.get_data_schema_by_name("My DataSchema")
        DataSchema("My DataSchema")
        """
        if version == VersionMode.ALL:
            warn(
                "VersionMode.ALL behaves the same as VersionMode.LATEST for get_data_schema_by_name(), did you mean to use search_for_data_schemas_by_name()?",
                RuntimeWarning,
            )
        results = self.search_for_data_schemas_by_name(
            name, version, project_uid, NameFilterMode.EXACT
        )
        if len(results) > 1:
            warn(
                "More than one data schema was found with the name for the provided project,"
                "please verify the schema is correct. This function returns the last created schema",
                RuntimeWarning,
            )
        return max(results, key=lambda x: arrow.get(x.created_at)) if results else None

    @rhino_error_wrapper
    def search_for_data_schemas_by_name(
        self,
        name: str,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
        project_uid: Optional[str] = None,
        name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS,
    ):
        """
        Returns DataSchema dataclasses

        .. warning:: This feature is under development and the interface may change

        Parameters
        ----------
        name: str
            Full or partial name for the DataSchema
        version: Optional[Union[int, VersionMode]]
            Version of the DataSchema, latest by default
        project_uid: Optional[str]
            Project UID to search under
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified filter mode. By default uses CONTAINS

        Returns
        -------
        data_schemas: List[DataSchema]
            DataSchema dataclasses that match the name

        Examples
        --------
        >>> session.data_schema.search_for_data_schemas_by_name("My DataSchema")
        [DataSchema(name="My DataSchema")]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        rhino_health.lib.endpoints.endpoint.VersionMode : Return specific versions


        """
        query_params = self._get_filter_query_params(
            {"name": name, "object_version": version, "project_uid": project_uid},
            name_filter_mode=name_filter_mode,
        )
        results = self.session.get("/data_schemas", params=query_params)
        return results.to_dataclasses(self.data_schema_dataclass)

    @rhino_error_wrapper
    def create_data_schema(self, data_schema, return_existing=True, add_version_if_exists=False):
        """
        @autoapi False

        Adds a new data_schema

        Parameters
        ----------
        data_schema: DataSchemaCreateInput
            DataSchemaCreateInput data class
        return_existing: bool
            If a DataSchema with the name already exists, return it instead of creating one.
            Takes precedence over add_version_if_exists
        add_version_if_exists
            If a DataSchema with the name already exists, create a new version.

        Returns
        -------
        data_schema: DataSchema
            DataSchema dataclass

        Examples
        --------
        >>> session.data_schema.create_data_schema(create_data_schema_input)
        DataSchema()
        """
        if return_existing or add_version_if_exists:
            # We need to iterate through the different project_uids because the user may not have permission to get from the first one
            try:
                existing_data_schema = self.search_for_data_schemas_by_name(
                    data_schema.name,
                    project_uid=data_schema.project_uid or data_schema.project_uids[0],
                    name_filter_mode=NameFilterMode.EXACT,
                )[0]
                if return_existing:
                    return existing_data_schema
                else:
                    data_schema.base_version_uid = (
                        existing_data_schema.base_version_uid or existing_data_schema.uid
                    )
                    data_schema.model_fields_set.discard("version")
            except Exception:
                # If no existing DataSchema exists do nothing
                pass
        result = self.session.post(
            "/data_schemas",
            data_schema.dict(by_alias=True, exclude_unset=True),
        )
        return result.to_dataclass(self.data_schema_dataclass)

    # @rhino_error_wrapper
    # def get_data_schema_csv(self, data_schema_uid: str):
    #     """
    #     @autoapi False
    #
    #     .. warning:: This feature is under development and incomplete
    #     """
    #     # TODO: What does this actually do do we need this?
    #     raise NotImplementedError()
    #     # return self.session.get(f"/data_schemas/{data_schema_uid}/export_to_csv")

    @rhino_error_wrapper
    def remove_data_schema(self, data_schema_or_uid: Union[str, DataSchema]):
        """
        Removes a DataSchema with the DATA_SCHEMA_OR_UID from the system
        """
        return self.session.delete(
            f"/data_schemas/{data_schema_or_uid if isinstance(data_schema_or_uid, str) else data_schema_or_uid.uid}"
        ).no_dataclass_response()
