import re
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import (  # Behavior of Union is different between different python versions, use typing_extensions for consistency
    Annotated,
    Union,
)

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField
from rhino_health.lib.endpoints.project.project_baseclass import WithinProjectModel
from rhino_health.lib.endpoints.semantic_mapping.semantic_mapping_dataclass import VocabularyType
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel
from rhino_health.lib.endpoints.workgroup.workgroup_baseclass import PrimaryWorkgroupModel

CURRENT_CONFIG_VERSION = 0
"""@autoapi False"""
SNAKE_CASE = re.compile(r"^[a-z_][a-z0-9_]*$")
"""@autoapi False"""


class TransformationType(str, Enum):
    """
    Type of transformation to perform
    """

    # SQL = "sql"
    SPECIFIC_VALUE = "specific_value"
    SOURCE_DATA_VALUE = "source_data_value"
    ROW_PYTHON = "row_python"
    TABLE_PYTHON = "table_python"
    SECURE_UUID = "secure_uuid"
    DATE = "date"
    SEMANTIC_MAPPING = "semantic_mapping"
    CUSTOM_MAPPING = "custom_mapping"
    VLOOKUP = "vlookup"
    # CHAIN = "chain"


class Transformation(BaseModel):
    """
    A transformation
    """

    transformation_type: TransformationType


class SpecificValueTransformation(Transformation):
    """
    Always use a specific value
    This transformation cannot be used for the first in a field.
    """

    transformation_type: Literal[
        TransformationType.SPECIFIC_VALUE
    ] = TransformationType.SPECIFIC_VALUE
    value: Any


class SourceValueTransformation(Transformation):
    """
    Read from source data and directly assign
    SourceValue must be the first in a given chain
    """

    transformation_type: Literal[
        TransformationType.SOURCE_DATA_VALUE
    ] = TransformationType.SOURCE_DATA_VALUE


class RowPythonCodeTransformationOnError(str, Enum):
    """
    Enum for behaviors on error
    """

    SKIP_ROW = "skip_row"
    FAIL = "fail"
    SET_TO_DEFAULT = "set_to_default"


class RowPythonCodeTransformation(Transformation):
    """
    Row level python code transformation
    """

    transformation_type: Literal[TransformationType.ROW_PYTHON] = TransformationType.ROW_PYTHON
    code: str
    on_error: RowPythonCodeTransformationOnError = RowPythonCodeTransformationOnError.SET_TO_DEFAULT
    default_value: Any = None


class TablePythonCodeTransformationOnError(str, Enum):
    """
    Enum for behaviors on error
    """

    FAIL = "fail"
    SET_TO_DEFAULT = "set_to_default"


class TablePythonCodeTransformation(Transformation):
    """
    Table level python code transformation
    """

    transformation_type: Literal[TransformationType.TABLE_PYTHON] = TransformationType.TABLE_PYTHON
    code: str
    on_error: TablePythonCodeTransformationOnError = TablePythonCodeTransformationOnError.FAIL
    default_value: Any = None


class VLookupTransformationOnMissing(str, Enum):
    """
    Enum for behaviors on missing
    """

    SKIP_ROW = "skip_row"
    FAIL = "fail"
    USE_SOURCE_VALUE = "use_source_value"
    SET_TO_DEFAULT = "set_to_default"


class VLookupTransformationOnMultiple(str, Enum):
    """
    Enum for behaviors if multiple matches are found
    """

    USE_FIRST = "use_first"
    USE_LAST = "use_last"
    FAIL = "fail"
    SET_TO_DEFAULT = "set_to_default"


class VLookupTransformation(Transformation):
    """
    Perform a VLOOKUP
    """

    transformation_type: Literal[TransformationType.VLOOKUP] = TransformationType.VLOOKUP
    source_data_source: Optional[
        str
    ] = None  # For V1 we only ever have one data source so the source table will be inferred
    lookup_data_source: str
    lookup_key_field: Optional[str] = None
    lookup_value_field: str
    on_missing: VLookupTransformationOnMissing = VLookupTransformationOnMissing.SET_TO_DEFAULT
    on_multiple: VLookupTransformationOnMultiple = VLookupTransformationOnMultiple.USE_FIRST
    default_value: Any = None


class SemanticMappingTransformationOnMissing(str, Enum):
    """
    Enum for behaviors on missing
    """

    SKIP_ROW = "skip_row"
    FAIL = "fail"
    USE_SOURCE_VALUE = "use_source_value"
    SET_TO_DEFAULT = "set_to_default"


class SemanticMappingTransformationOutput(str, Enum):
    """
    Enum for column to use for semantic mapping
    """

    TARGET_TERM_NAME = "target_term_name"
    TARGET_IDENTIFIER = "target_identifier"


class SemanticMappingTransformationOnUnapprovedValue(str, Enum):
    """
    Enum for behaviors when the mapping value is unapproved
    """

    USE_TOP_RECOMMENDATION = "use_top_recommendation"
    TREAT_AS_MISSING = "treat_as_missing"


class SemanticMappingTransformation(Transformation):
    """
    A semantic mapping
    """

    transformation_type: Literal[
        TransformationType.SEMANTIC_MAPPING
    ] = TransformationType.SEMANTIC_MAPPING
    vocabulary_name: str
    on_missing: SemanticMappingTransformationOnMissing = (
        SemanticMappingTransformationOnMissing.SET_TO_DEFAULT
    )
    output: SemanticMappingTransformationOutput
    default_value: Any = None
    on_unapproved_value: SemanticMappingTransformationOnUnapprovedValue = (
        SemanticMappingTransformationOnUnapprovedValue.USE_TOP_RECOMMENDATION
    )

    @field_validator("vocabulary_name")
    @classmethod
    def ensure_vocabulary_names_snake_case(cls, vocabulary_name: str):
        """
        @autoapi False
        """
        if not SNAKE_CASE.match(vocabulary_name):
            raise ValueError("Vocabulary names must match the pattern ^[a-z_][a-z0-9_]*")
        return vocabulary_name


CustomMappingTransformationOnMissing = SemanticMappingTransformationOnMissing
"""
@autoapi False
"""


class CustomMappingTransformationMappingFormat(str, Enum):
    """
    Enum for format the mapping is in
    """

    CSV = "csv"
    JSON = "json"


class CustomMappingTransformation(Transformation):
    """
    A custom mapping transformation
    """

    transformation_type: Literal[
        TransformationType.CUSTOM_MAPPING
    ] = TransformationType.CUSTOM_MAPPING
    on_missing: CustomMappingTransformationOnMissing = (
        CustomMappingTransformationOnMissing.SET_TO_DEFAULT
    )
    default_value: Any = None
    mappings: Union[str, Dict[str, str]] = {}
    mapping_format: CustomMappingTransformationMappingFormat = (
        CustomMappingTransformationMappingFormat.JSON
    )


class SecureUUIDTransformation(Transformation):
    """
    Performs a secure UUID Transformation
    """

    """
    Use SCRYPT to hash the value to generate a consistent pseudo-UUID to use as the reference
    value which can be calculated idempotently and in parallel without the need for a global
    tracking database
    """

    transformation_type: Literal[TransformationType.SECURE_UUID] = TransformationType.SECURE_UUID


class DateTransformation(Transformation):
    """
    Performs a date transformation
    """

    transformation_type: Literal[TransformationType.DATE] = TransformationType.DATE
    input_format: str
    output_format: str


# Important: When adding a new map entry, you will also need to update TransformationTypeAlias
TransformationTypesToDataclasses = {
    TransformationType.SEMANTIC_MAPPING: SemanticMappingTransformation,
    TransformationType.CUSTOM_MAPPING: CustomMappingTransformation,
    TransformationType.SECURE_UUID: SecureUUIDTransformation,
    TransformationType.SOURCE_DATA_VALUE: SourceValueTransformation,
    TransformationType.SPECIFIC_VALUE: SpecificValueTransformation,
    TransformationType.ROW_PYTHON: RowPythonCodeTransformation,
    TransformationType.TABLE_PYTHON: TablePythonCodeTransformation,
    TransformationType.VLOOKUP: VLookupTransformation,
    TransformationType.DATE: DateTransformation,
}
"""
@autoapi False
"""


TransformationTypeAlias = Annotated[
    Union[  # < Python 3.11 does not support dynamic typing
        SemanticMappingTransformation,
        CustomMappingTransformation,
        SecureUUIDTransformation,
        SourceValueTransformation,
        SpecificValueTransformation,
        RowPythonCodeTransformation,
        TablePythonCodeTransformation,
        VLookupTransformation,
        DateTransformation,
    ],
    Field(discriminator="transformation_type"),
]
"""
@autoapi False Autoapi crashes on dynamic types as it is a static linter
"""


class VocabularyMapping(BaseModel):
    """
    A Vocabulary Mapping
    """

    name: str
    type: VocabularyType
    uid: str
    metadata: Optional[Dict[str, Any]] = {}  # includes extra filters and identifiers ie omop domain


class SourceDataField(BaseModel):
    """
    Where to get the source data from
    """

    data_source: str  # There will be a mapping from data_source_name to data_schema_uid in the GlobalContext
    field: str  # In v1 this will be the name of the field, in v1.5 for FHIR we can interpret this as a path if needed


class FieldConfiguration(BaseModel):
    """
    Configuration for a specific field
    """

    source_fields: List[
        SourceDataField
    ]  # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.get.html
    target_field: str  # Eg column in OMOP
    transformations: List[TransformationTypeAlias]
    """
    List[Transformation]. TypeAlias is internal use by Pydantic
    If no transformations are defined, SourceValueTransformation is used
    """
    # TODO Add new autoapi extension to allow overriding the type.


class TableConfiguration(BaseModel):
    """
    Configuration for a table
    """

    table_name: str  # Used for readability of the config (e.g. OMOP table name, FHIR profile name, Dataset name). In v1 used as the output dataset name (in v1.5 it can be part of the output_dataset_naming_template)
    field_configurations: List[
        FieldConfiguration
    ]  # NOTE: There should always be at least 1 non specific value transformation

    @field_validator("table_name")
    @classmethod
    def avoid_private_table_names(cls, table_name: str):
        """
        @autoapi False
        """
        if table_name.startswith("__"):
            raise ValueError(
                "Table names cannot start with double underscore, these are used for internal purposes by the ETL"
            )
        return table_name

    @model_validator(mode="after")
    def validate_first_field_configuration(self):
        """
        @autoapi False
        """
        if not self.field_configurations:
            # The syntactic config is a work in progress state and we should not validate it
            # This is due to the FE sending in progress maps
            # We don't want to crash out on the dataclass serialization
            # Validation is done during run time
            return self
        has_valid_transformation = False
        for field_configuration in self.field_configurations:
            if (
                not field_configuration.transformations
            ):  # Default is TransformationType.SOURCE_DATA_VALUE
                has_valid_transformation = True
                break
            for transformation in field_configuration.transformations:
                transformation_type = getattr(
                    transformation, "transformation_type", TransformationType.SOURCE_DATA_VALUE
                )
                if transformation_type == TransformationType.SPECIFIC_VALUE:
                    continue
                if (
                    transformation_type == TransformationType.TABLE_PYTHON
                    and getattr(transformation, "on_error")
                    != TablePythonCodeTransformationOnError.FAIL
                ):
                    continue
                has_valid_transformation = True
        if not has_valid_transformation:
            raise ValueError(
                f"At least one field must exist with a transformation that is not {TransformationType.SPECIFIC_VALUE} or python with on_error={TablePythonCodeTransformationOnError.SET_TO_DEFAULT}"
            )
        return self


class GlobalConfiguration(BaseModel):
    """
    Configuration for a map at the global level
    """

    data_sources_to_data_schemas: List[
        Dict[str, str]
    ]  # Key is the “data source” and value is the UUID of the data_schema
    vocabulary_mapping: List[VocabularyMapping]
    version: Optional[
        int
    ] = CURRENT_CONFIG_VERSION  # Automatically created by the system to track version of the config
    output_table_names_to_data_schemas: Optional[
        List[Dict[str, str]]
    ] = []  # Used by the frontend for auto generating custom data model, optional

    @field_validator("vocabulary_mapping")
    @classmethod
    def ensure_unique_vocabulary_restriction_names(
        cls, vocabulary_mapping: List[VocabularyMapping]
    ):
        """
        @autoapi False
        """
        vocabulary_names = [vocabulary.name for vocabulary in vocabulary_mapping]
        if len(vocabulary_names) != len(set(vocabulary_names)):
            raise ValueError("Vocabulary names in the global configuration must be unique")
        if not all(SNAKE_CASE.match(vocabulary_name) for vocabulary_name in vocabulary_names):
            raise ValueError("Vocabulary names must match the pattern ^[a-z_][a-z0-9_]*")
        return vocabulary_mapping

    @field_validator("data_sources_to_data_schemas")
    @classmethod
    def ensure_valid_data_source_name(cls, data_sources_to_data_schemas):
        """
        @autoapi False
        """
        data_source_keys = [
            data_source
            for data_entry in data_sources_to_data_schemas
            for data_source in data_entry.keys()
        ]
        if not all(SNAKE_CASE.match(data_source) for data_source in data_source_keys):
            raise ValueError("Data sources must match the pattern ^[a-z_][a-z0-9_]*")
        return data_sources_to_data_schemas


class SyntacticMappingConfig(BaseModel):
    """
    Configuration for a Syntactic Mapping
    """

    global_configuration: GlobalConfiguration
    table_configurations: List[TableConfiguration]

    @model_validator(mode="after")
    def ensure_all_vocabularies_have_definitions(self):
        """
        @autoapi False
        """
        vocabulary_names = [vocab.name for vocab in self.global_configuration.vocabulary_mapping]
        missing = []
        for table_configuration in self.table_configurations:
            for field_configuration in table_configuration.field_configurations:
                for transformation in field_configuration.transformations:
                    is_semantic_map = (
                        transformation.transformation_type == TransformationType.SEMANTIC_MAPPING
                    )
                    if is_semantic_map and transformation.vocabulary_name not in vocabulary_names:
                        missing.append(transformation.vocabulary_name)
        if missing:
            raise ValueError(
                f"One or more vocabularies in semantic map are missing from the global configuration: {missing}"
            )
        return self


class SyntacticMappingDataModel(str, Enum):
    """
    What type of Syntactic Mapping are we trying to create
    """

    OMOP = "omop"
    FHIR = "fhir"
    CUSTOM = "custom"


class SyntacticMappingCreateInput(RhinoBaseModel):
    """
    The input to create a syntactic mapping
    """

    name: str
    description: Optional[str] = ""
    primary_workgroup_uid: Annotated[str, Field(alias="primary_workgroup")]
    project_uid: Annotated[str, Field(alias="project")]
    target_data_model_type: SyntacticMappingDataModel
    mapping_config: SyntacticMappingConfig
    base_version_uid: Optional[str] = None


class SyntacticMapping(
    PrimaryWorkgroupModel, WithinProjectModel, UserCreatedModel, SyntacticMappingCreateInput
):
    """
    @hide_parent_class
    A syntactic mapping object in the system
    """

    uid: str
    version: int
    code_object_uids: Annotated[
        List[str],
        UIDField(
            alias="code_objects",
            model_fetcher=lambda session, uids: [
                session.code_object.get_code_object(uid) for uid in uids
            ],
            model_property_name="code_objects",
            model_property_type="SyntacticMapping",
            is_list=True,
        ),
    ]


class DataHarmonizationRunInput(RhinoBaseModel):
    """
    Input for running data harmonization
    """

    input_dataset_uids: List[str]
    semantic_mapping_uids_by_vocabularies: Dict[str, str]
    description: Optional[str] = ""
    timeout_seconds: Optional[float] = 600.0


SyntacticMappingRun = DataHarmonizationRunInput
"""
@autoapi False For backwards compatibility, will be deprecated
"""
