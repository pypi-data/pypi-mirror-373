from typing import Dict, List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel


class RuntimeFilePublishInput(RhinoBaseModel):
    """
    Input parameters for publishing runtime files in a specific project.
    """

    file_path: str
    project_uid: Annotated[str, Field(alias="project")]


class RuntimeFileNode(RhinoBaseModel):
    """
    A recursive tree node representing files and directories in a bucket.
    The root node is the bucket itself, with child nodes representing the nested file/folder structure.
    """

    uid: str
    relative_path: str
    info: Optional[Dict[str, str]] = None
    children: List["RuntimeFileNode"]
    published: Optional[bool]


class RuntimeFileNodeResponse(RhinoBaseModel):
    """
    The response from the get_runtime_files endpoints,
    holds a dict between the available bucket names, and RuntimeFileNodes of their contents.
    """

    # We use this since the bucket names are unknown, but their values should match the RuntimeFileNodes.
    __pydantic_extra__: dict[str, RuntimeFileNode]

    model_config = ConfigDict(extra="allow")
