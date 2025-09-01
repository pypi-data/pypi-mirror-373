"""
@autoapi False
"""
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField


class PrimaryWorkgroupModel(RhinoBaseModel):
    """
    @autoapi False

    Mixin for models that have a primary workgroup
    """

    primary_workgroup_uid: Annotated[
        str,
        UIDField(
            alias="primary_workgroup",
            model_fetcher=lambda session, uid: session.workgroup.get_workgroups([uid])[0],
            model_property_type="Workgroup",
        ),
    ]
    """
    The UID of the primary_workgroup owning this dataclass
    """


class WithinWorkgroupModel(RhinoBaseModel):
    """
    @autoapi False

    Mixin for models that have a workgroup
    """

    workgroup_uid: Annotated[
        str,
        UIDField(
            alias="workgroup",
            model_fetcher=lambda session, uid: session.workgroup.get_workgroups([uid])[0],
            model_property_type="Workgroup",
        ),
    ]
    """
    The UID of the workgroup associated with this dataclass
    """
