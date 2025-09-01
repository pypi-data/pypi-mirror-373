from typing import List, Optional

import funcy
from pydantic import AliasPath, Field
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel


class LTSWorkgroup(RhinoBaseModel):
    """
    @autoapi False
    """

    uid: str
    """@autoapi True The unique ID of the Workgroup"""
    name: str
    """@autoapi True The name of the Workgroup"""
    org_name: str
    """@autoapi True The organization name of the Workgroup"""
    image_repo_name: Optional[str]
    """@autoapi True The image repository name suffix of the Workgroup"""
    storage_bucket_name_part: Optional[str]
    """@autoapi True The storage bucket name part of the Workgroup"""


class Workgroup(LTSWorkgroup):
    """
    @autoapi True
    @hide_parent_class
    """

    org_name: Annotated[str, Field(validation_alias=AliasPath("organization", "name"))]
    _all_users: "Optional[List[User]]" = None
    _users: "Optional[List[User]]" = None
    _admins: "Optional[List[User]]" = None

    def _fetch_users(self):
        from rhino_health.lib.endpoints.user.user_dataclass import UserWorkgroupRole

        if self._all_users is None:
            self._all_users = self.session.user._search_for_users_by_name(
                name="", workgroup_uid=self.uid
            )
            self._users = [
                user
                for user in self._all_users
                if UserWorkgroupRole.is_non_admin_member(
                    user.primary_workgroup_role, is_primary_workgroup=True
                )
            ]
            self._admins = [
                user
                for user in self._all_users
                if UserWorkgroupRole.is_admin_member(user.primary_workgroup_role)
            ]
        return self._users

    @property
    def users(self):
        """
        Returns the normal users of this workgroup
        """
        if self._users is None:
            self._fetch_users()
        return self._users

    @property
    def admins(self):
        """
        Returns the admins of this workgroup
        """
        if self._admins is None:
            self._fetch_users()
        return self._admins

    def list_external_storage_file_paths(self):
        """
        Returns a list of all external storage file paths
        """
        return self.session.workgroup.list_external_storage_file_paths(self.uid)


from rhino_health.lib.endpoints.user.user_dataclass import User

LTSWorkgroup.model_rebuild()
Workgroup.model_rebuild()
