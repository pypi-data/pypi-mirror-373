"""
@autoapi False
"""
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField


class UserCreatedModel(RhinoBaseModel):
    """
    @autoapi False

    Mixin for models that are created by a user
    """

    creator_uid: Annotated[
        str,
        UIDField(
            alias="creator",
            model_fetcher=lambda session, uid: session.user.get_users([uid])[0],
            model_property_type="User",
        ),
    ]
    """
    @autoapi True
    The UID of the creator of this dataclass on the system
    """
    created_at: str
    """
    @autoapi True
    When this dataclass was created on the system
    """
