"""
@autoapi False
"""
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField


class WithinProjectModel(RhinoBaseModel):
    """
    @autoapi False

    Mixin for models that are within a project
    """

    project_uid: Annotated[
        str,
        UIDField(
            alias="project",
            model_fetcher=lambda session, uid: session.project.get_projects([uid])[0],
            model_property_type="Project",
        ),
    ]
    """
    The UID of the project this dataclass is part of
    """
