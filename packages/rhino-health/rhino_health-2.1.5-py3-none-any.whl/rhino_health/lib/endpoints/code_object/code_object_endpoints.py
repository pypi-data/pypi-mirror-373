from typing import Optional, Union
from warnings import warn

import arrow

from rhino_health.lib.constants import CloudProvider
from rhino_health.lib.endpoints.code_object.code_object_dataclass import (
    CodeExecutionMode,
    CodeObject,
    CodeObjectCreateInput,
    CodeObjectRunAsyncResponse,
    CodeObjectRunInput,
    CodeObjectRunSyncResponse,
    ModelTrainAsyncResponse,
    ModelTrainInput,
)
from rhino_health.lib.endpoints.endpoint import Endpoint, NameFilterMode, VersionMode
from rhino_health.lib.endpoints.syntactic_mapping.syntactic_mapping_dataclass import (
    DataHarmonizationRunInput,
)
from rhino_health.lib.services.cloud_storage_upload_file_service import (
    GCSUploadFileService,
    S3UploadFileService,
)
from rhino_health.lib.utils import rhino_error_wrapper


class CodeObjectEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints for interacting with CodeObjects
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "code_object"

    @property
    def code_object_dataclass(self):
        """
        @autoapi False
        """
        return CodeObject

    @rhino_error_wrapper
    def get_code_object(self, code_object_uid: str):
        """
        @autoapi True
        Returns a CodeObject dataclass

        Parameters
        ----------
        code_object_uid: str
            UID for the CodeObject

        Returns
        -------
        code_object: CodeObject
            CodeObject dataclass

        Examples
        --------
        >>> session.code_object.get_code_object(my_code_object_uid)
        CodeObject()
        """
        result = self.session.get(f"/code_objects/{code_object_uid}")
        return result.to_dataclass(self.code_object_dataclass)

    @rhino_error_wrapper
    def get_code_object_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None
    ) -> Optional[CodeObject]:
        """
        @autoapi True
        Returns the latest or a specific CodeObject dataclass

        .. warning:: VersionMode.ALL will return the same as VersionMode.LATEST

        Parameters
        ----------
        name: str
            Full name for the CodeObject
        version: Optional[Union[int, VersionMode]]
            Version of the CodeObject, latest by default, for an earlier version pass in an integer
        project_uid: Optional[str]
            Project UID to search under

        Returns
        -------
        code_object: Optional[CodeObject]
            CodeObject with the name or None if not found

        Examples
        --------
        >>> session.code_object.get_code_object_by_name("My CodeObject")
        CodeObject(name="My CodeObject")
        """
        if version == VersionMode.ALL:
            warn(
                "VersionMode.ALL behaves the same as VersionMode.LATEST for get_code_object_by_name(), did you mean to use search_for_code_objects_by_name()?",
                RuntimeWarning,
            )
        results = self.search_for_code_objects_by_name(
            name, version, project_uid, NameFilterMode.EXACT
        )
        return max(results, key=lambda x: arrow.get(x.created_at)) if results else None

    def search_for_code_objects_by_name(
        self,
        name,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
        project_uid: Optional[str] = None,
        name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS,
    ):
        """
        @autoapi True
        Returns CodeObject dataclasses

        Parameters
        ----------
        name: str
            Full or partial name for the CodeObject
        version: Optional[Union[int, VersionMode]]
            Version of the CodeObject, latest by default
        project_uid: Optional[str]
            Project UID to search under
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified filter mode. By default uses CONTAINS

        Returns
        -------
        code_objects: List[CodeObject]
            CodeObject dataclasses that match the name

        Examples
        --------
        >>> session.code_object.search_for_code_objects_by_name("My CodeObject")
        [CodeObject(name="My CodeObject)]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        rhino_health.lib.endpoints.endpoint.VersionMode : Which version to return
        """
        query_params = self._get_filter_query_params(
            {"name": name, "object_version": version, "project_uid": project_uid},
            name_filter_mode=name_filter_mode,
        )
        results = self.session.get("/code_objects", params=query_params)
        return results.to_dataclasses(self.code_object_dataclass)

    @rhino_error_wrapper
    def get_build_logs(self, code_object_uid: str):
        """
        @autoapi True
        Returns logs for building the CodeObject

        Parameters
        ----------
        code_object_uid: str
            UID for the CodeObject

        Returns
        -------
        build_logs: str

        Examples
        --------
        >>> session.code_object.get_build_logs(my_code_object_uid)
        "Starting to build..."
        """
        return self.session.get(
            f"/code_objects/{code_object_uid}/build_logs"
        ).no_dataclass_response()

    @rhino_error_wrapper
    def publish(self, code_object_or_uid, unpublish_other_versions: bool = True):
        """
        Makes the code object dataclass or uid published and visible to users without the permission to view all versions
        UNPUBLISH_OTHER_VERSIONS if true
        """
        code_object_uid = (
            code_object_or_uid.uid
            if not isinstance(code_object_or_uid, str)
            else code_object_or_uid
        )
        return self.session.post(
            f"/code_objects/{code_object_uid}/publish",
            data={"unpublish_other_versions": unpublish_other_versions},
        ).no_dataclass_response()

    @rhino_error_wrapper
    def unpublish(self, code_object_or_uid):
        """
        Makes this code object dataclass or uid unpublished so users without the permission to view all versions no longer see this
        """
        code_object_uid = (
            code_object_or_uid.uid
            if not isinstance(code_object_or_uid, str)
            else code_object_or_uid
        )
        return self.session.post(
            f"/code_objects/{code_object_uid}/unpublish",
        ).no_dataclass_response()

    @rhino_error_wrapper
    def remove_code_object(self, code_object_or_uid: Union[str, CodeObject]):
        """
        Removes a CodeObject with the CODE_OBJECT_UID from the system
        """
        return self.session.delete(
            f"/code_objects/{code_object_or_uid if isinstance(code_object_or_uid, str) else code_object_or_uid.uid }"
        ).no_dataclass_response()

    @rhino_error_wrapper
    def run_code_object(
        self, code_object: CodeObjectRunInput
    ) -> Union[CodeObjectRunSyncResponse, CodeObjectRunAsyncResponse]:
        """
        @autoapi True
        Returns the result of starting a CodeRun

        .. warning:: This feature is under development and the return response may change

        Parameters
        ----------
        code_object: CodeObjectRunInput
            CodeObjectRunInput data class

        Returns
        -------
        run_response: Union[CodeObjectRunSyncResponse, CodeObjectRunAsyncResponse]
            Response dataclass depending on if the request was run synchronously

        Examples
        --------
        >>> run_response = session.code_object.code_object(run_code_object_input)
        CodeObjectRunSyncResponse()
        >>> run_response.code_run
        CodeRun()

        See Also
        --------
        rhino_health.lib.endpoints.code_object.code_object_dataclass.CodeObjectRunSyncResponse : CodeObjectRunSyncResponse Dataclass
        rhino_health.lib.endpoints.code_object.code_object_dataclass.CodeObjectRunAsyncResponse : CodeObjectRunAsyncResponse Dataclass
        """
        output_dataclass = (
            CodeObjectRunSyncResponse if code_object.sync else CodeObjectRunAsyncResponse
        )
        return self.session.post(
            f"/code_objects/{code_object.code_object_uid}/run",
            data=code_object.dict(by_alias=True, exclude_unset=True),
        ).to_dataclass(output_dataclass)

    @rhino_error_wrapper
    def train_model(self, model: ModelTrainInput):
        """
        @autoapi True
        Starts training a NVFlare Model

        .. warning:: This feature is under development and the return response may change

        Parameters
        ----------
        model: ModelTrainInput
            ModelTrainInput data class

        Returns
        -------
        run_response: ModelTrainAsyncResponse
            Response dataclass

        Examples
        --------
        >>> session.code_object.train_model(model_train_input)
        ModelTrainAsyncResponse()

        See Also
        --------
        rhino_health.lib.endpoints.code_object.code_object_dataclass.ModelTrainAsyncResponse : ModelTrainAsyncResponse Dataclass
        """
        return self.session.post(
            f"/code_objects/{model.code_object_uid}/train",
            data=model.dict(by_alias=True, exclude_unset=True),
        ).to_dataclass(ModelTrainAsyncResponse)

    def run_data_harmonization(
        self, code_object_uid: Union[str, CodeObject], run_params: DataHarmonizationRunInput
    ):
        """
        Run a data harmonization code object

        Parameters
        ----------
        code_object_or_uid: Union[str, CodeObject]
            The uid of the code object or the code object itself
        run_params: DataHarmonizationRunInput
            Parameters for running data harmonization for this code object

        Returns
        -------
        code_object_response: CodeObjectRunAsyncResponse
            Asynchronous run response object similar to a Promise. Call code_object_response.code_run to wait for the response.
        """
        code_object_uid = (
            code_object_uid if isinstance(code_object_uid, str) else code_object_uid.uid
        )
        data = run_params.dict(by_alias=True)
        result = self.session.post(
            f"/code_objects/{code_object_uid}/run_data_harmonization", data=data
        )
        return result.to_dataclass(CodeObjectRunAsyncResponse)

    # Likely change how the config will work very soon
    @rhino_error_wrapper
    def create_code_object(
        self, code_object: CodeObjectCreateInput, return_existing=True, add_version_if_exists=False
    ):
        """
        Starts the creation of a new CodeObject on the platform.

        .. warning:: This feature is under development and the interface may change

        Parameters
        ----------
        code_object: CodeObjectCreateInput
            CodeObjectCreateInput data class
        return_existing: bool
            If a CodeObject with the name already exists, return it instead of creating one.
            Takes precedence over add_version_if_exists
        add_version_if_exists
            If a CodeObject with the name already exists, create a new version.

        Returns
        -------
        code_object: CodeObject
            CodeObject dataclass

        Examples
        --------
        >>> session.code_object.create_code_object(create_code_object_input)
        CodeObject()
        """

        if return_existing or add_version_if_exists:
            try:
                existing_code_object = self.search_for_code_objects_by_name(
                    code_object.name,
                    project_uid=code_object.project_uid,
                    name_filter_mode=NameFilterMode.EXACT,
                )[0]
                if return_existing:
                    return existing_code_object
                else:
                    code_object.base_version_uid = (
                        existing_code_object.base_version_uid or existing_code_object.uid
                    )
                    code_object.model_fields_set.discard("version")
            except Exception:
                # If no existing CodeObject exists do nothing
                pass
        folder_path = code_object.config.get("folder_path")
        code_execution_mode = code_object.config.get("code_execution_mode")
        if (
            code_execution_mode
            in {CodeExecutionMode.AUTO_CONTAINER_FILE, CodeExecutionMode.AUTO_CONTAINER_NVFLARE}
            and folder_path
        ):
            cloud_provider = self.session.get("/system/cloud_provider").parsed_response

            if cloud_provider == CloudProvider.AWS:
                storage_folder_path = S3UploadFileService(
                    self.session, code_object.project_uid
                ).upload_folder_into_s3(folder_path)
            elif cloud_provider == CloudProvider.GCP:
                storage_folder_path = GCSUploadFileService(
                    self.session, code_object.project_uid
                ).upload_folder_into_gcs(folder_path)
            else:
                raise ValueError(f"Cloud provider {cloud_provider} is not supported")
            code_object.config["folder"] = storage_folder_path
            code_object.config.pop("folder_path", None)
        result = self.session.post(
            f"/code_objects",
            data=code_object.dict(by_alias=True, exclude_unset=True),
        )
        return result.to_dataclass(self.code_object_dataclass)
