from typing import List, Optional, Union

from rhino_health.lib.endpoints.endpoint import Endpoint, NameFilterMode, VersionMode
from rhino_health.lib.endpoints.user.user_dataclass import SFTPInformation, User
from rhino_health.lib.utils import rhino_error_wrapper


class UserEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints available to interact with Users on the Rhino Platform

    Notes
    -----
    You should access these endpoints from the RhinoSession object
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "user"

    @property
    def user_dataclass(self):
        return User

    """
    @autoapi False
    """

    @rhino_error_wrapper
    def get_logged_in_user(self):
        """
        Returns the currently logged in user
        """
        result = self.session.get("/users/self")
        return result.to_dataclass(self.user_dataclass)

    @rhino_error_wrapper
    def get_users(self, user_uids: List[str]) -> List[User]:
        """
        @autoapi True
        Gets the users with the specified USER_UIDS

        .. warning:: This feature is under development and the interface may change
        """
        query_params = self._get_filter_query_params({"uid__in": [user_uids]})
        results = self.session.get(f"/users/", params=query_params)

        return results.to_dataclasses(self.user_dataclass)

    @rhino_error_wrapper
    def report_sdk_environment(self, environment_info):
        """
        @autoapi False
        Reports the SDK environment to rhino
        """
        return self.session.post(
            f"/users/report_sdk_environment", environment_info
        ).no_dataclass_response()

    @rhino_error_wrapper
    def _search_for_users_by_name(
        self,
        name: str,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
        workgroup_uid: Optional[str] = None,
        project_uid: Optional[str] = None,
        name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS,
    ):
        """
        @autoapi False
        Searches for User by name

        INTERNAL ONLY USE ENDPOINT

        Parameters
        ----------
        name: str
            Full or partial name for the User
        version: Optional[Union[int, VersionMode]]
            Version of the User, latest by default
        workgroup_uid: Optional[str]
            Workgroup UID to search under
        project_uid: Optional[str]
            Project UID to search under
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified filter mode, By default uses CONTAINS

        Returns
        -------
        users: List[User]
            User dataclasses that match the name

        Examples
        --------
        >>> session.user._search_for_users_by_name("My User")
        [User(name="My User")]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        rhino_health.lib.endpoints.endpoint.VersionMode : Which version to return
        """
        query_params = self._get_filter_query_params(
            {"name": name, "primary_workgroup_uid": workgroup_uid, "project_uid": project_uid},
            name_filter_mode=name_filter_mode,
        )
        result = self.session.get("/users", params=query_params)
        return result.to_dataclasses(self.user_dataclass)

    @rhino_error_wrapper
    def sftp_info(self) -> SFTPInformation:
        """
        Returns the SFTP information for transferring files for the current user.
        You can use this information with Paramiko

        .. warning:: This information may not be correct if your machine is behind an institution firewall
        """
        user = self.session.current_user
        credentials = self.session.get("/users/self/credentials/sftp").raw_response.json()["data"]
        ip_address = self.session.get(
            f"/workgroups/{user.primary_workgroup_uid}/client_ip_address"
        ).raw_response.json()["data"]
        return SFTPInformation(
            username=credentials["sftp_username"],
            password=credentials["sftp_password"],
            url=ip_address,
        )
