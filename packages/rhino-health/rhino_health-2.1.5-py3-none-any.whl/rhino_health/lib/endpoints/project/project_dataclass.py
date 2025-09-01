from typing import Dict, List, Optional

from pydantic import Field
from typing_extensions import Annotated, Literal

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField
from rhino_health.lib.endpoints.endpoint import VersionMode
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel
from rhino_health.lib.endpoints.user.user_dataclass import User
from rhino_health.lib.endpoints.workgroup.workgroup_baseclass import PrimaryWorkgroupModel
from rhino_health.lib.utils import alias


class ProjectBase(RhinoBaseModel):
    """
    Base class for a project
    @autoapi False
    """

    name: str
    """@autoapi True The name of the Project"""
    description: str
    """@autoapi True The description of the Project"""
    type: Literal["Validation", "Refinement"]
    """@autoapi True The type of the Project"""
    primary_workgroup_uid: Annotated[str, Field(alias="primary_workgroup")]
    """@autoapi True The unique ID of the Project's Primary Workgroup"""


class ProjectCreateInput(ProjectBase):
    """
    Input arguments for adding a new project
    @autoapi True
    """

    permissions: Optional[Dict] = None
    """@autoapi True JSON-encoded project-level permissions"""


class Project(PrimaryWorkgroupModel, ProjectBase, UserCreatedModel):
    """
    @hide_parent_class
    Dataclass representing a Project on the Rhino platform.
    """

    uid: str
    """@autoapi True The unique ID of the Project"""
    slack_channel: str
    """@autoapi True Slack Channel URL for communications for the Project"""
    collaborating_workgroup_uids: Annotated[
        List[str],
        UIDField(
            alias="collaborating_workgroups",
            is_list=True,
            model_fetcher=lambda session, uids: session.workgroup.get_workgroups(uids),
            model_property_name="collaborating_workgroups",
            model_property_type="Workgroup",
        ),
    ]
    """@autoapi True A list of unique IDs of the Project's collaborating Workgroups"""
    _users: Optional[List[User]] = None
    """@autoapi False"""

    @property
    def permissions(self):
        """
        On read these are not included in the initial response
        """
        return self.session.project.get_project_permissions(self)

    @property
    def stats(self):
        """
        Returns metadata for this project
        """
        return self.session.project.get_project_stats(self.uid)

    @property
    def status(self):
        """
        @autoapi False
        """
        return alias(
            self.stats,
            old_function_name="status",
            new_function_name="stats",
            base_object="Project",
            is_property=True,
        )()

    def add_collaborator(self, collaborator_or_uid):
        """
        Adds COLLABORATOR_OR_UID as a collaborator to this project

        .. warning:: This feature is under development and the interface may change
        """
        from ..workgroup.workgroup_dataclass import LTSWorkgroup

        if isinstance(collaborator_or_uid, LTSWorkgroup):
            collaborator_or_uid = collaborator_or_uid.uid
        self.session.project.add_collaborator(
            project_uid=self.uid, collaborating_workgroup_uid=collaborator_or_uid
        )
        self._collaborating_workgroups = None
        self.collaborating_workgroup_uids.append(collaborator_or_uid)
        return self

    def remove_collaborator(self, collaborator_or_uid):
        """
        Removes COLLABORATOR_OR_UID as a collaborator from this project

        .. warning:: This feature is under development and the interface may change
        """
        from ..workgroup.workgroup_dataclass import LTSWorkgroup

        if isinstance(collaborator_or_uid, LTSWorkgroup):
            collaborator_or_uid = collaborator_or_uid.uid
        self.session.project.remove_collaborator(
            project_uid=self.uid, collaborating_workgroup_uid=collaborator_or_uid
        )
        self._collaborating_workgroups = None
        self.collaborating_workgroup_uids.remove(collaborator_or_uid)
        return self

    @property
    def datasets(self):
        """
        Get Datasets associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.get_datasets : Full documentation
        """
        return self.session.project.get_datasets(self.uid)

    def get_dataset_by_name(self, name, version=VersionMode.LATEST, **_kwargs):
        """
        Get Dataset associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.get_dataset_by_name : Full documentation
        """
        return self.session.project.get_dataset_by_name(name, project_uid=self.uid, version=version)

    def search_for_datasets_by_name(
        self, name, version=VersionMode.LATEST, name_filter_mode=None, **_kwargs
    ):
        """
        Get Datasets associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.search_for_datasets_by_name : Full documentation
        """
        return self.session.project.search_for_datasets_by_name(
            name, project_uid=self.uid, version=version, name_filter_mode=name_filter_mode
        )

    @property
    def data_schemas(self):
        """
        Get Data Schemas associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.get_data_schemas : Full documentation
        """
        return self.session.project.get_data_schemas(self.uid)

    def get_data_schema_by_name(self, name, version=VersionMode.LATEST, **_kwargs):
        """
        Get DataSchema associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.get_data_schema_by_name : Full documentation
        """
        return self.session.project.get_data_schema_by_name(
            name, project_uid=self.uid, version=version
        )

    def search_for_data_schemas_by_name(
        self, name, version=VersionMode.LATEST, name_filter_mode=None, **_kwargs
    ):
        """
        Get Data Schemas associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.search_for_data_schemas_by_name : Full documentation
        """
        return self.session.project.search_for_data_schemas_by_name(
            name, project_uid=self.uid, version=version, name_filter_mode=name_filter_mode
        )

    @property
    def code_objects(self):
        """
        Get CodeObjects associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.get_code_objects : Full documentation
        """
        return self.session.project.get_code_objects(self.uid)

    def get_code_object_by_name(self, name, version=VersionMode.LATEST, **_kwargs):
        """
        Get CodeObject associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.get_code_object_by_name : Full documentation
        """
        return self.session.project.get_code_object_by_name(
            name, project_uid=self.uid, version=version
        )

    def search_for_code_objects_by_name(
        self, name, version=VersionMode.LATEST, name_filter_mode=None, **_kwargs
    ):
        """
        Get CodeObjects associated with this project

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.search_for_code_objects_by_name : Full documentation
        """
        return self.session.project.search_for_code_objects_by_name(
            name, project_uid=self.uid, version=version, name_filter_mode=name_filter_mode
        )

    @property
    def users(self):
        """
        Return users of this project
        """
        if self._users is None:
            self._users = self.session.user._search_for_users_by_name(name="", project_uid=self.uid)
        return self._users

    def aggregate_dataset_metric(self, *args, **kwargs):
        """
        Performs an aggregate dataset metric

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.aggregate_dataset_metric : Full documentation
        """
        return self.session.project.aggregate_dataset_metric(*args, **kwargs)

    def joined_dataset_metric(self, *args, **kwargs):
        """
        Performs a federated join dataset metric

        See Also
        --------
        rhino_health.lib.endpoints.project.project_endpoints.ProjectEndpoints.joined_dataset_metric : Full documentation
        """
        return self.session.project.joined_dataset_metric(*args, **kwargs)

    # Add Schema
    # Local Schema from CSV

    def get_agent_resources_for_workgroup(self, *args, **kwargs):
        return self.session.project.get_system_resources_for_workgroup(*args, **kwargs)


class SystemResources(RhinoBaseModel):
    """
    Output when calling system resources.
    """

    filesystem_storage: Dict
    """@autoapi True filesystem storage in bytes (free, used, total)"""
    cpu_percent_used: float
    """@autoapi True used cpu percent"""
    memory: Dict
    """@autoapi True Memory data in bytes (free, used, total)"""
    gpu: Dict
    """@autoapi True The GPU usage data per gpu"""
