from enum import Enum
from typing import List, Optional

from pydantic import BaseModel
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField
from rhino_health.lib.endpoints.workgroup.workgroup_baseclass import PrimaryWorkgroupModel
from rhino_health.lib.utils import alias


class UserWorkgroupRole(str, Enum):
    """
    The role the user has on the platform
    """

    MEMBER = "Member"
    WORKGROUP_ADMIN = "Workgroup Admin"
    ORG_ADMIN = "Org Admin"
    RHINO_ADMIN = "Rhino Admin"

    @classmethod
    def is_admin_member(cls, member_role) -> bool:
        return member_role in {cls.WORKGROUP_ADMIN, cls.ORG_ADMIN, cls.RHINO_ADMIN}

    @classmethod
    def is_non_admin_member(cls, member_role, is_primary_workgroup=False) -> bool:
        if is_primary_workgroup:
            return member_role in {None, cls.MEMBER}
        return member_role in {cls.MEMBER}


class User(PrimaryWorkgroupModel, RhinoBaseModel):
    """
    @hide_parent_class
    @autoapi True
    Dataclass representing a User on the Rhino platform.
    """

    uid: str
    """@autoapi True Unique ID of the user"""
    full_name: str
    """@autoapi True The full name of the user"""
    workgroup_uids: Annotated[
        List[str],
        UIDField(
            alias="workgroups",
            is_list=True,
            model_fetcher=lambda session, uids: session.workgroup.get_workgroups(uids),
            model_property_name="workgroups",
            model_property_type="Workgroup",
        ),
    ]
    """@autoapi True Additional workgroup unique IDs the user belongs to"""
    primary_workgroup_role: Optional[UserWorkgroupRole] = UserWorkgroupRole.MEMBER
    """@autoapi True Elevated roles the user has in their primary workgroup."""

    # API responses we do not want to surface to the user
    __hidden__ = ["first_name", "profile_pic", "otp_enabled"]

    @property
    def workgroups_uids(self) -> List[str]:
        """
        @autoapi False
        """
        return alias(
            self.stats,
            old_function_name="workgroups_uids",
            new_function_name="workgroup_uids",
            base_object="User",
            is_property=True,
        )()


class SFTPInformation(BaseModel):
    """
    The SFTP information for transferring files for the current user.
    You can use this information with Paramiko

    .. warning:: This information may not be correct if your machine is behind an institution firewall
    .. warning:: The username and password will be rotated every few hours, please make sure to get the latest value
    """

    username: str
    password: str
    url: str
