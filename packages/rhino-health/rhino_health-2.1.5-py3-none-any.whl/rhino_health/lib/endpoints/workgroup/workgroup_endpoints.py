from typing import List, Optional, Union

from rhino_health.lib.endpoints.endpoint import Endpoint, NameFilterMode, VersionMode
from rhino_health.lib.endpoints.workgroup.workgroup_dataclass import LTSWorkgroup, Workgroup
from rhino_health.lib.utils import rhino_error_wrapper


class WorkgroupEndpoints(Endpoint):
    """
    @autoapi True
    Endpoints available to interact with Workgroups on the Rhino Platform

    Notes
    -----
    You should access these endpoints from the RhinoSession object
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "workgroup"

    @property
    def workgroup_dataclass(self):
        """
        @autoapi False
        """
        return Workgroup

    @rhino_error_wrapper
    def get_workgroups(self, workgroup_uids: List[str] = None) -> List[LTSWorkgroup]:
        """
        Returns the specified workgroup_uids

        :param workgroup_uids: List of strings of workgroup uids to get
        """
        if not workgroup_uids:
            return []
        else:
            return [
                self.session.get(f"/workgroups/{workgroup_uid}/").to_dataclass(
                    self.workgroup_dataclass
                )
                for workgroup_uid in workgroup_uids
            ]

    @rhino_error_wrapper
    def search_for_workgroups_by_name(
        self,
        name: str,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
        project_uid: Optional[str] = None,
        name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS,
    ):
        """
        @autoapi False
        Searches for Workgroup by name

        INTERNAL ONLY USE ENDPOINT

        Parameters
        ----------
        name: str
            Full or partial name for the Workgroup
        version: Optional[Union[int, VersionMode]]
            Version of the Workgroup, latest by default
        project_uid: Optional[str]
            Project UID to search under
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified filter mode, By default uses CONTAINS

        Returns
        -------
        workgroups: List[Workgroup]
            Workgroup dataclasses that match the name

        Examples
        --------
        >>> session.user.search_for_workgroups_by_name("My Workgroup")
        [Workgroup(name="My Workgroup")]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        rhino_health.lib.endpoints.endpoint.VersionMode : Which version to return
        """
        query_params = self._get_filter_query_params(
            {"name": name, "project_uid": project_uid},
            name_filter_mode=name_filter_mode,
        )
        result = self.session.get("/workgroups", params=query_params)
        raise NotImplementedError  # Backend not supported yet
        # return result.to_dataclasses(self.workgroup_dataclass)

    @rhino_error_wrapper
    def list_external_storage_file_paths(self, workgroup_uid: str):
        """
        Get all the storage bucket file paths for a workgroup

        Parameters
        ----------
        workgroup_uid: str
            UID for the Workgroup

        Returns
        -------
        Files: List[str]
            The storage bucket file paths for a workgroup

        Examples
        --------
        >>> session.workgroup.list_external_storage_file_paths("workgroup_uid")
        ["/path/to/file1", "/path/to/file2", "/path/to/file3"]
        """
        return self.session.get(
            f"/workgroups/{workgroup_uid}/get_storage_bucket_file_paths"
        ).no_dataclass_response()
