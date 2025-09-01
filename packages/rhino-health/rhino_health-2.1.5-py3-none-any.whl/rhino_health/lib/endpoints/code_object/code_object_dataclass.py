import json
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from warnings import warn

from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField
from rhino_health.lib.endpoints.code_run.code_run_dataclass import CodeRunInputDatasets
from rhino_health.lib.endpoints.data_schema.data_schema_dataclass import DataSchema
from rhino_health.lib.endpoints.project.project_baseclass import WithinProjectModel
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel


class CodeExecutionMode(str, Enum):
    """
    A mode the CodeObject will run in
    """

    DEFAULT = "default"
    AUTO_CONTAINER_NVFLARE = "nvflare"
    AUTO_CONTAINER_SNIPPET = "snippet"
    AUTO_CONTAINER_FILE = "file"


class CodeLocation(str, Enum):
    """
    Location the code is stored and uploaded to the system
    """

    DEFAULT = "single_non_binary_file"
    S3_MULTIPART_ZIP = "s3_multipart_zip"  # TODO: For supporting backwards compatibility, remove in next breaking change version of SDK
    STORAGE_MULTIPART_ZIP = "storage_multipart_zip"


# TODO: This is a breaking change remove in next breaking change version of SDK
CodeFormat = CodeLocation
"""
@autoapi True ..warning This dataclass is deprecated, will be removed soon, please use CodeLocation
"""


class RequirementMode(str, Enum):
    """
    The format the requirements are in
    """

    PYTHON_PIP = "python_pip"
    ANACONDA_ENVIRONMENT = "anaconda_environment"
    ANACONDA_SPECFILE = "anaconda_specfile"


class CodeTypes(str, Enum):
    """
    Supported CodeObject Types
    """

    GENERALIZED_COMPUTE = "Generalized Compute"
    NVIDIA_FLARE_V2_0 = "NVIDIA FLARE v2.0"
    NVIDIA_FLARE_V2_2 = "NVIDIA FLARE v2.2"
    NVIDIA_FLARE_V2_3 = "NVIDIA FLARE v2.3"
    NVIDIA_FLARE_V2_4 = "NVIDIA FLARE v2.4"
    NVIDIA_FLARE_V2_5 = "NVIDIA FLARE v2.5"
    NVIDIA_FLARE_V2_6 = "NVIDIA FLARE v2.6"
    PYTHON_CODE = "Python Code"
    INTERACTIVE_CONTAINER = "Interactive Container"
    DATA_HARMONIZATION = "Data Harmonization"


class CodeObjectBuildStatus(str, Enum):
    """
    The build status of the CodeObject
    """

    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETE = "Complete"
    ERROR = "Error"


class CodeObjectInputConfig(BaseModel):
    """
    @autoapi True
    Configuration for a single input of a CodeObject.
    """

    data_schema_uid: Annotated[
        Optional[str],
        UIDField(
            alias="schema_uid",
            model_fetcher=lambda session, uid: session.data_schema.get_data_schema(uid),
            model_property_type="DataSchema",
        ),
    ]
    """@autoapi True The data schema UID of the input"""
    is_optional: bool = False
    """@autoapi True Whether the input is optional"""
    is_multiple: bool = False
    """@autoapi True Whether the input accepts multiple datasets"""


class CodeObjectOutputConfig(BaseModel):
    """
    @autoapi True
    Configuration for a single input of a CodeObject.
    """

    data_schema_uid: Annotated[
        Optional[str],
        UIDField(
            alias="schema_uid",
            model_fetcher=lambda session, uid: session.data_schema.get_data_schema(uid),
            model_property_type="DataSchema",
        ),
    ]
    """@autoapi True The data schema uid of the input"""
    is_optional: bool = False
    """@autoapi True Whether the input is optional"""
    is_multiple: bool = False
    """@autoapi True Whether the input accepts multiple datasets"""


class CodeObjectCreateInput(RhinoBaseModel):
    """
    @autoapi True
    Input arguments for creating CodeObject
    """

    name: str
    """@autoapi True The name of the CodeObject"""
    description: str
    """@autoapi True The description of the CodeObject"""
    input_data_schema_uids: Optional[List[Optional[str]]] = None
    """@autoapi True A list of uids of data schemas this CodeObject expects input datasets to adhere to."""
    output_data_schema_uids: Optional[List[Optional[str]]] = None
    """@autoapi True A list of uids of data schemas this CodeObject expects output datasets to adhere to."""
    inputs_config: Optional[List[Union[CodeObjectInputConfig, str, None]]] = None
    """@autoapi True A list of input configs this CodeObject expects input datasets to adhere to."""
    outputs_config: Optional[List[Union[CodeObjectOutputConfig, str, None]]] = None
    """@autoapi True A list of input configs this CodeObject expects input datasets to adhere to."""
    project_uid: Annotated[str, Field(alias="project")]
    """@autoapi True The CodeObject project"""
    code_type: Annotated[str, Field(alias="type")]
    """@autoapi True The code type which corresponds to the CodeTypes enum

    See Also
    --------
    rhino_health.lib.endpoints.code_object.code_object_dataclass.CodeTypes
    """
    base_version_uid: Optional[str] = ""
    """@autoapi True The first version of the CodeObject if multiple versions exist. You can also use add_version_if_exists=True when creating the code object in create_code_object if an existing code object with the same name exists"""
    config: Optional[Dict] = None
    """@autoapi True Additional configuration of the CodeObject. The contents will differ based on the model_type and code_run_type.
    
    Examples
    --------
    + CodeTypes.GENERALIZED_COMPUTE and CodeTypes.INTERACTIVE_CONTAINER
        - container_image_uri: URI of the container image to use for the model
    + CodeTypes.NVIDIA_FLARE_V2_X (existing image)
        - code_execution_mode: CodeExecutionMode
        - if CodeExecutionMode.DEFAULT requires the following additional parameters
            - container_image_uri: URI of the container image to use for the model
        - if CodeExecutionMode.AUTO_CONTAINER_NVFLARE, see CodeTypes.PYTHON_CODE below
    + CodeTypes.PYTHON_CODE
        - code_execution_mode: CodeExecutionMode = CodeExecutionMode.DEFAULT - The format the code is structured in
            - CodeTypes.PYTHON_CODE supports CodeExecutionMode.DEFAULT, CodeExecutionMode.AUTO_CONTAINER_SNIPPET, and CodeExecutionMode.AUTO_CONTAINER_FILE
            - CodeTypes.NVIDIA_FLARE_V2_X only supports CodeExecutionMode.AUTO_CONTAINER_NVFLARE
        - if CodeExecutionMode.DEFAULT requires the following additional parameters
            - python_code: str - the python code to run
        - CodeExecutionMode.AUTO_CONTAINER_SNIPPET requires the following additional parameters
            - code: str - the python code to run
        - CodeExecutionMode.AUTO_CONTAINER_FILE or CodeExecutionMode.AUTO_CONTAINER_NVFLARE
            - base_image: choose one of the following 
                - base_image_uri: str - the base docker image to use for the container
                or
                - python_version: str - the python version to use for the container
                - cuda_version: Optional[str] - the cuda version to use for the container
            - requirements_mode: Optional[RequirementMode] = RequirementMode.PYTHON_PIP - The format the requirements are in
            - requirements: List[str] - a list of requirements to install in the container, uses the pip/conda install format
            - code_location: CodeLocation the location the code is passed to the user
                - CodeLocation.DEFAULT
                    - code: str - A string representation of the code directly embedded in the request
                - CodeLocation.STORAGE_MULTIPART_ZIP
                    - folder_path: str | Path - the folder path to files on local disk which will be uploaded as a zip to the storage bucket  
                    - entry_point: str - name of the file to run first. Not used for auto container nvflare    

    See Also
    --------
    rhino_health.lib.endpoints.code_object.code_object_dataclass.CodeTypes
    rhino_health.lib.endpoints.code_object.code_object_dataclass.CodeExecutionMode
    """

    @model_validator(mode="after")
    def _validate_inputs_and_outputs_configs(self):
        """@autoapi False"""
        # Must provide inputs_config xor input_data_schema_uids
        if self.inputs_config is None and self.input_data_schema_uids is None:
            raise ValueError("Cannot provide both inputs_config and input_data_schema_uids")
        if self.inputs_config is not None and self.input_data_schema_uids is not None:
            raise ValueError("Must provide either inputs_config or input_data_schema_uids")

        # Must provide outputs_config xor output_data_schema_uids
        if self.outputs_config is None and self.output_data_schema_uids is None:
            raise ValueError("Cannot provide both outputs_config and output_data_schema_uids")
        if self.outputs_config is not None and self.output_data_schema_uids is not None:
            raise ValueError("Must provide either outputs_config or output_data_schema_uids")


class CodeObject(WithinProjectModel, CodeObjectCreateInput, UserCreatedModel):
    """
    @autoapi True
    @hide_parent_class
    A CodeObject which exists on the platform
    """

    uid: str
    """@autoapi True The unique ID of the CodeObject"""
    version: Optional[int] = None
    """@autoapi True The version of the CodeObject"""
    build_status: CodeObjectBuildStatus = CodeObjectBuildStatus.COMPLETE
    """@autoapi True The build status of the CodeObject"""
    inputs_config: List[CodeObjectInputConfig]
    """
    @autoapi True A list of CodeObjectInputConfig objects, describing the required inputs for running this code object.
    """
    outputs_config: List[CodeObjectOutputConfig]
    """
    @autoapi True A list of CodeObjectOutputConfig objects, describing the expected outputs of running this code object.
    """
    build_errors: Optional[List[str]] = None
    """@autoapi True Errors when building the CodeObject, if building in the cloud"""
    published: bool = False

    _input_data_schemas: Union[List[Union[DataSchema, None]], None] = None
    _output_data_schemas: Union[List[Union[DataSchema, None]], None] = None

    # API responses we do not want to surface to the user
    __hidden__ = ["container_image_build"]

    @model_validator(mode="after")
    def _validate_inputs_and_outputs_configs(self):
        """@autoapi False

        Override the parent method, since here input_data_schema_uids and
        output_data_schema_uids are provided via properties.
        """
        pass

    @property
    def build_logs(self):
        """@autoapi True Logs when building the CodeObject, if building in the cloud"""
        return self.session.code_object.get_build_logs(self.uid)

    @property
    def _code_object_built(self):
        return self.build_status in {CodeObjectBuildStatus.COMPLETE, CodeObjectBuildStatus.ERROR}

    @property
    def input_data_schema_uids(self) -> List[Union[str, None]]:
        """
        @autoapi True
        Return the UIDs of input data schemas associated with this CodeObject

        Returns
        -------
        data_schemas: List[Union[str, None]]
            List of DataSchema UIDs, or None values for "any schema" inputs
        """
        return [cfg.data_schema_uid for cfg in self.inputs_config]

    @property
    def input_data_schemas(self) -> List[Union[DataSchema, None]]:
        """
        @autoapi True
        Return the input data schemas associated with this CodeObject

        Returns
        -------
        data_schemas: List[Union[DataSchema, None]]
            List of DataSchema objects, or None values for "any schema" inputs
        """
        if self._input_data_schemas is None:
            not_none_uids = {cfg.data_schema_uid for cfg in self.inputs_config} - {None}
            if not_none_uids:
                schemas = self.session.data_schema.get_data_schemas(list(not_none_uids))
                schemas_by_uid = {schema.uid: schema for schema in schemas}
            else:
                schemas_by_uid = {}
            self._input_data_schemas = [
                schemas_by_uid[uid] if (uid := cfg.data_schema_uid) is not None else None
                for cfg in self.inputs_config
            ]
        return self._input_data_schemas

    @property
    def output_data_schema_uids(self) -> List[Union[str, None]]:
        """
        @autoapi True
        Return the UIDs of output data schemas associated with this CodeObject

        .. warning:: The result of this function is cached.
            Be careful calling this function after making changes

        Returns
        -------
        data_schemas: List[Union[str, None]]
            List of DataSchema UIDs, or None values for "inferred schema" outputs
        """
        return [cfg.data_schema_uid for cfg in self.outputs_config]

    @property
    def output_data_schemas(self) -> List[Union[DataSchema, None]]:
        """
        @autoapi True
        Return the output data schemas associated with this CodeObject

        .. warning:: The result of this function is cached.
            Be careful calling this function after making changes

        Returns
        -------
        data_schemas: List[Union[DataSchema, None]]
            List of DataSchema objects, or None values for "inferred schema" outputs
        """
        if self._output_data_schemas is None:
            not_none_uids = {cfg.data_schema_uid for cfg in self.outputs_config} - {None}
            if not_none_uids:
                schemas = self.session.data_schema.get_data_schemas(list(not_none_uids))
                schemas_by_uid = {schema.uid: schema for schema in schemas}
            else:
                schemas_by_uid = {}
            self._output_data_schemas = [
                schemas_by_uid[uid] if (uid := cfg.data_schema_uid) is not None else None
                for cfg in self.outputs_config
            ]
        return self._output_data_schemas

    def wait_for_build(
        self, timeout_seconds: int = 900, poll_frequency: int = 30, print_progress: bool = True
    ):
        """
        @autoapi True
        Wait for the asynchronous CodeObject to finish building

        Parameters
        ----------
        timeout_seconds: int = 900
            How many seconds to wait before timing out. Maximum of 1800.
        poll_frequency: int = 30
            How frequent to check the status, in seconds
        print_progress: bool = True
            Whether to print how long has elapsed since the start of the wait

        Returns
        -------
        code_object: CodeObject
            Dataclass representing the CodeObject
        """
        return self._wait_for_completion(
            name="code object build",
            is_complete=self._code_object_built,
            query_function=lambda code_object: code_object.session.code_object.get_code_object(
                code_object.uid
            ),
            validation_function=lambda old, new: (new.build_status and new._code_object_built),
            timeout_seconds=timeout_seconds,
            poll_frequency=poll_frequency,
            print_progress=print_progress,
        )

    def publish(self, unpublish_other_versions: bool = True):
        return self.session.code_object.publish(
            self, unpublish_other_versions=unpublish_other_versions
        )

    def unpublish(self):
        return self.session.code_object.unpublish(self)


class CodeObjectRunInput(RhinoBaseModel):
    """
    @autoapi True
    @hide_parent_class
    Input parameters for running generalized code with multiple input and/or output datasets per container

    See Also
    --------
    rhino_health.lib.endpoints.code_object.code_object_endpoints.CodeObjectEndpoints.run_code_object : Example Usage
    """

    def __init__(self, *args, **kwargs):
        run_params = kwargs.get("run_params", None)
        if isinstance(run_params, dict):
            kwargs["run_params"] = json.dumps(run_params)
        secret_run_params = kwargs.get("secret_run_params", None)
        if isinstance(secret_run_params, dict):
            kwargs["secret_run_params"] = json.dumps(secret_run_params)
        super().__init__(*args, **kwargs)

    description: Optional[str] = ""
    """@autoapi True The description of the code run"""
    code_object_uid: str
    """@autoapi True The unique ID of the CodeObject"""
    run_params: Optional[str] = "{}"
    """@autoapi True The run params code you want to run on the datasets"""
    timeout_seconds: int = 600
    """@autoapi True The time before a timeout is declared for the run"""
    secret_run_params: Optional[str] = None
    """The secrets for the CodeObject"""
    external_storage_file_paths: Optional[List[str]] = None
    """@autoapi True The s3 bucket paths of files to be used in the run"""
    sync: bool = False
    """@autoapi True Highly recommended to use the default parameter"""
    input_dataset_uids: Union[CodeRunInputDatasets, List[List[str]]]
    """A list of list of lists of the input dataset uids.

    [[first_dataset_for_first_run, second_dataset_for_first_run ...], [first_dataset_for_second_run, second_dataset_for_second_run ...], ...] for N runs

    Examples
    --------
    Suppose we have the following CodeObject with 2 Input Data Schemas:

    - CodeObject
        + DataSchema 1
        + DataSchema 2

    We want to run the CodeObject over two sites: Applegate and Bridgestone

    The user passes in dataset UIDs for Datasets A, B, C, and D in the following order:

    [[Dataset A, Dataset B], [Dataset C, Dataset D]]

    The model will then be run over both sites with the following datasets passed to generalized compute:

    - Site A - Applegate:
        + Dataset A - DataSchema 1
        + Dataset B - DataSchema 2
    - Site B - Bridgestone:
        + Dataset C - DataSchema 1
        + Dataset D - DataSchema 2
    """
    # TODO: Remove this after figuring out how to replicate old logic
    output_dataset_names_suffix: Optional[str] = None
    """@autoapi False ..warning This argument is deprecated, will be removed soon, and does not behave properly with multiple datasets. Please use output_dataset_naming_templates"""
    output_dataset_naming_templates: Optional[List[str]] = None
    """ A list of string naming templates used to name the output datasets at each site.
    You can use parameters in each template surrounded by double brackets ``{{parameter}}`` which will
    then be replaced by their corresponding values.

    Parameters
    ----------
    workgroup_name:
        The name of the workgroup the CodeObject belongs to.
    workgroup_uid:
        The name of the workgroup the CodeObject belongs to.
    code_object_name:
        The CodeObject name
    input_dataset_names.n:
        The name of the nth input dataset, (zero indexed)
    input_sal_names.n:
        The name of the nth input Secure Access List (if a SAL is used as an input in Interactive Containers), (zero indexed)
    input_names.n:
        The name of the nth input, whether dataset or SAL, (zero indexed)

    Examples
    --------
    Suppose we have two input datasets, named "First Dataset" and "Second Dataset"
    and our CodeObject has two outputs:

    | output_dataset_naming_templates = [
    |     "{{input_dataset_names.0}} - Train",
    |     "{{input_dataset_names.1}} - Test"
    | ]

    After running Generalized Compute, we will save the two outputs as "First Dataset - Train" and "Second Dataset - Test"
    """

    @field_validator("output_dataset_names_suffix")
    @classmethod
    def warn_on_usage_of_obsolete_arg(cls, value):
        if value is not None:
            warn(
                "output_dataset_names_suffix is deprecated and will be removed very soon, please use output_dataset_naming_templates instead",
                RuntimeWarning,
            )
        return value

    @model_validator(mode="after")
    def max_timeout_check(self):
        """
        @autoapi False
        """
        if self.sync == True and self.timeout_seconds > 600:
            raise ValueError(
                "Timeout seconds cannot be greater than 600 when run in synchronous mode"
            )
        return self

    @field_serializer("input_dataset_uids")
    def serialize_input_dataset_uids_as_triply_nested_list(
        self, input_dataset_uids
    ) -> List[List[List[str]]]:
        """
        @autoapi False
        """
        if isinstance(input_dataset_uids, list) and all(
            isinstance(index_input_uids, list)
            and all(
                isinstance(index_input_value, str) or index_input_value is None
                for index_input_value in index_input_uids
            )
            for index_input_uids in input_dataset_uids
        ):
            # Convert doubly-nested list to triply-nested list.
            return [[[uid] for uid in index_input_uids] for index_input_uids in input_dataset_uids]
        elif isinstance(input_dataset_uids, CodeRunInputDatasets):
            # Convert CodeRunInputDatasets triply-nested list.
            return [
                [[uid for uid in uids.root] for uids in index_input_dataset_uids.root]
                for index_input_dataset_uids in input_dataset_uids.root
            ]
        else:
            return input_dataset_uids


class CodeRunWaitMixin(RhinoBaseModel):
    """
    @autoapi False
    """

    code_run_uid: Optional[str] = None
    """
    @autoapi True The UID of the model result
    """
    _code_run: Any = None

    def wait_for_completion(self, *args, **kwargs):
        """
        @autoapi True
        Wait for the asynchronous Code Run to complete, convenience function call to the same function
        on the CodeRun object.

        Returns
        -------
        code_run: CodeRun
            Dataclass representing the CodeRun of the CodeObject

        See Also
        --------
        rhino_health.lib.endpoints.code_run.code_run_dataclass.CodeRun: Response object
        rhino_health.lib.endpoints.code_run.code_run_dataclass.CodeRun.wait_for_completion: Accepted parameters
        """
        if not self._code_run:
            self._code_run = self.session.code_run.get_code_run(self.code_run_uid)
        if self._code_run._process_finished:
            return self._code_run
        self._code_run = self._code_run.wait_for_completion(*args, **kwargs)
        return self._code_run


class CodeObjectRunResponse(CodeRunWaitMixin):
    """
    @autoapi False
    """

    status: str
    """
    @autoapi True The status of the run
    """

    @property
    def code_run(self):
        """
        @autoapi True
        Return the CodeRun associated with this CodeObject

        .. warning:: The result of this function is cached.
            Be careful calling this function after making changes

        Returns
        -------
        code_run: CodeRun
            Dataclass representing the CodeRun
        """
        if self._code_run:
            return self._code_run
        if self.code_run_uid:
            self._code_run = self.session.code_run.get_code_run(self.code_run_uid)
            return self._code_run
        else:
            return None


class CodeObjectRunAsyncResponse(CodeObjectRunResponse):
    """
    @autoapi True
    An asynchronous code run response
    """

    task_uids: List[str]

    @property
    def code_run(self):
        return self.wait_for_completion()


class CodeObjectRunSyncResponse(CodeObjectRunResponse):
    """
    @autoapi True
    A synchronous code run response
    """

    output_dataset_uids: Optional[List[str]] = []
    """
    @autoapi True A list of output dataset UIDs for the run
    """
    errors: Optional[List[Any]] = []
    warnings: Optional[List[Any]] = []

    def wait_for_completion(self, *args, **kwargs):
        return self.code_run


## NVFlare


class ModelTrainInput(RhinoBaseModel):
    """
    @autoapi True
    Input for training an NVFlare Model

    See Also
    --------
    rhino_health.lib.endpoints.code_object.code_object_endpoints.CodeObjectEndpoints.train_model : Example Usage
    """

    code_object_uid: str
    """The unique ID of the CodeObject"""
    input_dataset_uids: List[str]
    """A list of the input Dataset uids"""
    validation_dataset_uids: List[str]
    """A list of the Dohort uids for validation"""
    validation_datasets_inference_suffix: str
    """The suffix given to all output datasets"""
    simulate_federated_learning: Annotated[bool, Field(alias="one_fl_client_per_dataset")]
    """Run simulated federated learning on the same on-prem installation by treating each dataset as a site"""
    config_fed_server: Optional[str] = None
    """The config for the federated server"""
    config_fed_client: Optional[str] = None
    """The config for the federated client"""
    secrets_fed_server: Optional[str] = None
    """The secrets for the federated server"""
    secrets_fed_client: Optional[str] = None
    """The secrets for the federated client"""
    homomorphic_encryption_config: Optional[str] = None
    """Configuration for Homomorphic Encryption, in YAML or JSON syntax"""
    external_storage_file_paths: Optional[List[str]] = None
    """@autoapi True The s3 bucket paths of files to be used in the run"""
    timeout_seconds: int
    """The time before a timeout is declared for the run"""


class ModelInferenceAsyncResponse(CodeRunWaitMixin):
    @property
    def code_run(self):
        return self.wait_for_completion()


class ModelTrainAsyncResponse(CodeRunWaitMixin):
    """
    Response of training an NVFlare Model
    .. warning:: This feature is under development and the interface may change
    """

    status: str
    """
    @autoapi True The status of the run
    """

    @property
    def code_run(self):
        """
        @autoapi True
        Return the CodeRun associated with the NVFlare training

        .. warning:: The result of this function is cached.
            Be careful calling this function after making changes

        Returns
        -------
        code_run: CodeRun
            Dataclass representing the CodeRun
        """
        return self.wait_for_completion()
