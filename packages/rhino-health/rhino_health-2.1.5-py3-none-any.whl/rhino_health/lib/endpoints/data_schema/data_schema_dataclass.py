from typing import Any, Dict, List, Optional
from warnings import warn

from pydantic import BaseModel, Field, RootModel
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel
from rhino_health.lib.endpoints.project.project_baseclass import WithinProjectModel
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel
from rhino_health.lib.endpoints.workgroup.workgroup_baseclass import PrimaryWorkgroupModel
from rhino_health.lib.utils import alias


class SchemaField(BaseModel):
    """
    A schema field
    """

    # TODO: Better type checks
    name: str
    identifier: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
    type_params: Any = None
    units: Optional[str] = None
    may_contain_phi: Optional[bool] = None
    permissions: Optional[str] = None


class SchemaFields(RootModel):
    """
    List-like dataclass that provides some convenience functions
    Pydantic v2 uses RootModel to handle internal things required for serialization
    """

    root: List[Any]  # The actual type

    def __init__(self, schema_fields: List[Dict]):
        schema_fields = self._parse_data(schema_fields)
        super(SchemaFields, self).__init__(schema_fields)

    def __iter__(self):
        for schema_field in self.root:
            yield schema_field

    @property
    def field_names(self):
        return [variable.name for variable in self.root]

    def _parse_data(self, schema_fields: List[Dict]):
        return [SchemaField(**schema_field) for schema_field in schema_fields]

    def dict(self, *args, **kwargs):
        return [schema_field.model_dump(*args, **kwargs) for schema_field in self]

    def to_csv(self, output_file):
        """
        @autoai False
        """
        # TODO: RH-1871 Ability to write to CSV again
        raise NotImplementedError


class BaseDataSchema(RhinoBaseModel):
    """
    @autoapi False
    Base DataSchema used by both return result and creation
    """

    name: str
    """@autoapi True The name of the DataSchema"""
    description: str
    """@autoapi True The description of the DataSchema"""
    base_version_uid: Optional[str] = None
    """@autoapi True If this DataSchema is a new version of another DataSchema, the original Unique ID of the base DataSchema."""
    version: Optional[int] = 0
    """@autoapi True The revision of this DataSchema"""


class DataSchemaCreateInput(BaseDataSchema):
    """
    @autoapi True
    Input for creating a new DataSchema

    Examples
    --------
    >>> DataSchemaCreateInput(
    >>>     name="My DataSchema",
    >>>     description="A Sample DataSchema",
    >>>     primary_workgroup_uid=project.primary_workgroup_uid,
    >>>     project=project.uid,
    >>>     file_path="/absolute/path/to/my_schema_file.csv"
    >>> )
    """

    schema_fields: List[str] = []
    """ A list of rows representing the schema fields from a csv file.

    Users are recommended to use file_path instead of directly setting this value
    
    The first row should be the field names in the schema. Each list string should have a newline at the end.
    Each row should have columns separated by commas.
    """
    file_path: Optional[str] = None
    """ Path to a `CSV <https://en.wikipedia.org/wiki/Comma-separated_values>`_ File 
    that can be opened with python's built in `open() <https://docs.python.org/3/library/functions.html#open>`_ command.
    """
    primary_workgroup_uid: Annotated[str, Field(alias="primary_workgroup")]
    """@autoapi True The UID of the primary workgroup for this data schema"""
    project_uid: Annotated[Optional[str], Field(alias="project")] = None
    """@autoapi True The UID of the project for this data schema"""
    project_uids: Annotated[Optional[List[str]], Field(alias="projects")] = None
    """@autoapi False The UID of the project for this data schema"""

    def __init__(self, **data):
        if "projects" in data:
            warn(
                "The projects field is deprecated. Please use project instead.",
                DeprecationWarning,
            )

        self._load_csv_file(data)
        super(BaseDataSchema, self).__init__(**data)
        if self.project_uid and self.project_uids:
            raise ValueError("Can't use both project_uid and project_uids please use project_uid")

    def _load_csv_file(self, data):
        file_path = data.get("file_path", None)
        if file_path:
            data["schema_fields"] = [
                x for x in open(file_path, "r", encoding="utf-8", newline=None).readlines()
            ]
            # TODO: Verify the schema file is correct
            del data["file_path"]


class DataSchema(WithinProjectModel, PrimaryWorkgroupModel, BaseDataSchema, UserCreatedModel):
    """
    @autoapi True
    @hide_parent_class

    A DataSchema in the system used by Datasets
    """

    uid: Optional[str] = None
    """@autoapi True The Unique ID of the DataSchema"""
    schema_fields: SchemaFields
    """@autoapi True A list of schema fields in this data schema"""

    def __init__(self, **data):
        self._handle_schema_fields(data)
        super().__init__(**data)

    def _handle_schema_fields(self, data):
        raw_schema_field = data["schema_fields"]
        data["schema_fields"] = SchemaFields(raw_schema_field)

    def delete(self):
        if not self._persisted or not self.uid:
            raise RuntimeError("DataSchema has already been deleted")

        self.session.data_schema.remove_data_schema(self.uid)
        self._persisted = False
        self.uid = None
        return self

    @property
    def project_uids(self):
        """
        @autoapi False
        """
        return [
            alias(
                self.project_uid,
                "project_uids",
                is_property=True,
                new_function_name="project_uid",
                base_object="data_schema",
            )()
        ]

    @property
    def projects(self):
        """
        @autoapi False
        """
        return [
            alias(
                self.project,
                "projects",
                is_property=True,
                new_function_name="project",
                base_object="data_schema",
            )()
        ]

    @property
    def project_names(self):
        """
        @autoapi False
        """
        return [
            alias(
                self.project_name,
                "project_names",
                is_property=True,
                new_function_name="project_name",
                base_object="data_schema",
            )()
        ]


DataSchema.model_rebuild()
