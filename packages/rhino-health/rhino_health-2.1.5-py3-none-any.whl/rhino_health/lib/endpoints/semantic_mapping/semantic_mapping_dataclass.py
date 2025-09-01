from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel
from rhino_health.lib.endpoints.project.project_baseclass import WithinProjectModel
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel
from rhino_health.lib.endpoints.workgroup.workgroup_baseclass import PrimaryWorkgroupModel


class VocabularyType(str, Enum):
    """
    Type of vocabulary
    """

    STANDARD = "standard"
    CUSTOM = "custom"


class VocabularyTerm(BaseModel):
    """
    A vocabulary term
    """

    term_display_name: Optional[str] = None
    term_identifier: Optional[str] = None


class VocabularyInput(RhinoBaseModel):
    """
    Input for creating a vocabulary
    """

    name: str
    description: Optional[str] = ""
    primary_workgroup_uid: Annotated[str, Field(alias="primary_workgroup")]
    project_uid: Annotated[str, Field(alias="project")]
    base_version_uid: Optional[str] = None
    terms: str = None


class Vocabulary(PrimaryWorkgroupModel, WithinProjectModel, UserCreatedModel, VocabularyInput):
    """
    @hide_parent_class
    Vocabulary object
    """

    uid: str
    prefiltering_service_table: Optional[str] = None
    version: Optional[int] = 0
    type: VocabularyType
    possible_domain_names: Optional[List[str]] = None
    terms: Optional[List[VocabularyTerm]] = None


class SearchMode(str, Enum):
    """
    @autoapi False
    Internal use only
    A class to represent the search mode for the vocabulary search
    The search mode determines the query that is used to search the OpenSearch DB.
    The possible values are:
    - closest: The search term is matched against the term_display_name using the custom ngram predefined in
    the index (which is a table in the DB) creation. See more details about ngram here https://opensearch.org/docs/latest/analyzers/tokenizers/index/.
    - contains_display_name: The search term is matched against the term_display_name, and matches values that starts with or contains the search term.
    - contains_identifier: The search term is matched against the term_identifier, and matches values that starts with or contains the search term.
    """

    CLOSEST = "closest"
    CONTAINS_DISPLAY_NAME = "contains_display_name"
    CONTAINS_IDENTIFIER = "contains_identifier"


class VocabularySearch(RhinoBaseModel):
    """
    @autoapi False
    Internal use only
    A request to search for a vocabulary
    """

    search_term: str
    vocabulary_categories: Optional[List[str]] = None
    num_matches: Optional[int] = 100
    search_mode: Optional[SearchMode] = SearchMode.CLOSEST


# The name of the custom ngram analyzer used for the vocabulary indexing in opensearch
CUSTOM_NGRAM_ANALYZER = "custom_ngram_analyzer"
"""
@autoapi False
"""


class DatasetColumn(BaseModel):
    """
    The dataset column to read from
    """

    dataset_uid: str
    field_name: str


class SemanticMappingCreateInput(RhinoBaseModel):
    """
    Input to create a SemanticMapping
    """

    name: str
    description: Optional[str] = ""
    primary_workgroup_uid: Annotated[str, Field(alias="primary_workgroup")]
    base_version_uid: Optional[str] = None
    version: Optional[int] = 0
    input_vocabulary_uid: Annotated[str, Field(alias="input_vocabulary")]
    output_vocabulary_uid: Annotated[str, Field(alias="output_vocabulary")]
    output_vocabulary_categories: Optional[List[str]] = None
    project_uid: Annotated[str, Field(alias="project")]
    source_dataset_columns: List[DatasetColumn]


class SemanticMappingProcessingStatus(str, Enum):
    """
    Status of the SemanticMapping
    """

    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    NEEDS_REVIEW = "Needs Review"
    APPROVED = "Approved"
    ERROR = "Error"


class SemanticMappingDataclass(
    PrimaryWorkgroupModel, WithinProjectModel, UserCreatedModel, SemanticMappingCreateInput
):
    """
    @objname SemanticMapping
    @hide_parent_class
    A SemanticMapping object
    """

    processing_status: SemanticMappingProcessingStatus
    processing_error_message: Optional[List[str]] = []
    input_vocabulary_uid: Annotated[Any, Field(alias="input_vocabulary")]
    output_vocabulary_uid: Annotated[Any, Field(alias="output_vocabulary")]
    semantic_mapping_info: Optional[Dict[str, Any]] = {}
    # input_vocabulary_uid: Annotated[Vocabulary, UIDField(alias="input_vocabulary")]
    # output_vocabulary_uid: Annotated[Vocabulary, UIDField(alias="output_vocabulary")]
    uid: str

    def wait_for_completion(
        self,
        timeout_seconds: int = 6000,
        poll_frequency: int = 10,
        print_progress: bool = True,
    ):
        from rhino_health.lib.endpoints.semantic_mapping.semantic_mapping_endpoints import (
            SemanticMappingEndpoints,
        )

        semantic_mapping_endpoints = SemanticMappingEndpoints(self.session)
        return self._wait_for_completion(
            name="semantic mapping processing",
            is_complete=self._finished_processing,
            query_function=lambda semantic_mapping: semantic_mapping_endpoints.get_semantic_mapping(
                self.uid
            ),
            validation_function=lambda old, new: (new._finished_processing),
            timeout_seconds=timeout_seconds,
            poll_frequency=poll_frequency,
            print_progress=print_progress,
        )

    @property
    def _finished_processing(self):
        """
        @autoapi False
        """
        return self.processing_status not in {
            SemanticMappingProcessingStatus.NOT_STARTED,
            SemanticMappingProcessingStatus.IN_PROGRESS,
        }


class SemanticMappingApproveEntry(BaseModel):
    """
    @autoapi False
    Internal use only
    """

    source_term_name: str
    target_term_name: str
    target_identifier: str
    is_approved: bool


class SemanticMappingApproveList(RhinoBaseModel):
    """
    @autoapi False
    Internal use only
    """

    entries: List[SemanticMappingApproveEntry]


class SemanticMappingEntry(BaseModel):
    """
    An entry in a SemanticMapping
    """

    entry_uid: str
    source_term_name: str
    target_term_name: str
    recommendation_data: List[Dict[str, Any]]
    num_appearances: int
    created_at: str
    status: Literal["calculating", "failed", "needs_review", "approved"]
    is_approved: bool
    approved_at: str
    approved_by: Dict[str, str]
    index: int


SemanticMapping = SemanticMappingDataclass
"""
@autoapi False
"""
