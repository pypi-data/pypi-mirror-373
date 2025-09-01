from io import BytesIO
from typing import List, Optional, Union

from rhino_health.lib.endpoints.code_object.code_object_dataclass import ModelInferenceAsyncResponse
from rhino_health.lib.endpoints.code_run.code_run_dataclass import CodeRun, CodeRunLogs
from rhino_health.lib.endpoints.endpoint import Endpoint
from rhino_health.lib.utils import rhino_error_wrapper


class CodeRunEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints for interacting with CodeRuns
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "code_run"

    @property
    def code_run_dataclass(self):
        """
        @autoapi False
        """
        return CodeRun

    @rhino_error_wrapper
    def run_inference(
        self,
        code_run_uid: str,
        validation_dataset_uids: List[str],
        validation_datasets_suffix: str,
        timeout_seconds: int,
    ):
        """
        @autoapi True
        Start running inference on one or more datasets using a previously trained NVFlare Model.

        Parameters
        ----------
        code_run_uid: str
            UID for the code run
        validation_dataset_uids: List[str]
            List of dataset UIDs to run inference on
        validation_datasets_suffix: str
            Suffix for the validation datasets
        timeout_seconds: int
            Timeout in seconds


        Returns
        -------
        ModelInferenceAsyncResponse()

        Examples
        --------
        >>> s = session.code_run.run_inference(code_run_uid, validation_dataset_uids, validation_datasets_suffix, timeout_seconds)
        >>> s.code_run() # Get the asynchronous result
        >>> s.code_run_uid # Get the code run UID
        See Also
        --------
        rhino_health.lib.endpoints.code_object.code_object_dataclass.ModelInferenceAsyncResponse : ModelInferenceAsyncResponse Dataclass
        """
        data = {
            "validation_dataset_uids": validation_dataset_uids,
            "validation_datasets_inference_suffix": validation_datasets_suffix,
            "timeout_seconds": timeout_seconds,
        }

        res = self.session.post(
            f"/code_runs/{code_run_uid}/run_inference",
            data=data,
        )
        return res.to_dataclass(ModelInferenceAsyncResponse)

    @rhino_error_wrapper
    def publish(self, code_run_or_uid, unpublish_other_versions: bool = True):
        """
        Makes the code run dataclass or uid published and visible to users without the permission to view all versions
        UNPUBLISH_OTHER_VERSIONS if true
        """
        code_run_uid = (
            code_run_or_uid.uid if not isinstance(code_run_or_uid, str) else code_run_or_uid
        )
        return self.session.post(
            f"/code_runs/{code_run_uid}/publish",
            data={"unpublish_other_versions": unpublish_other_versions},
        ).no_dataclass_response()

    @rhino_error_wrapper
    def unpublish(self, code_run_or_uid):
        """
        Makes this code run dataclass or uid unpublished so users without the permission to view all versions no longer see this
        """
        code_run_uid = (
            code_run_or_uid.uid if not isinstance(code_run_or_uid, str) else code_run_or_uid
        )
        return self.session.post(
            f"/code_runs/{code_run_uid}/unpublish",
        ).no_dataclass_response()

    @rhino_error_wrapper
    def remove_code_run(self, code_run_or_uid: Union[str, CodeRun]):
        """
        Removes a CodeRun with the CODE_RUN_OR_UID from the system
        """
        return self.session.delete(
            f"/code_runs/{code_run_or_uid if isinstance(code_run_or_uid, str) else code_run_or_uid.uid}"
        ).no_dataclass_response()

    @rhino_error_wrapper
    def get_code_run(self, code_run_uid: str):
        """
        Returns a CodeRun dataclass

        Parameters
        ----------
        code_run_uid: str
            UID for the CodeRun

        Returns
        -------
        code_run: CodeRun
            CodeRun dataclass

        Examples
        --------
        >>> session.code_object.get_code_run(code_run_uid)
        CodeRun()
        """
        result = self.session.get(f"/code_runs/{code_run_uid}")
        return result.to_dataclass(self.code_run_dataclass)

    @rhino_error_wrapper
    def get_model_params(
        self, code_run_uid: str, model_weights_files: Optional[List[str]] = None
    ) -> BytesIO:
        """
        Returns the contents of one or more model params file(s) associated with a model result.

        The return value is an open binary file-like object, which can be read or written to a file.

        The contents are for a single file. This is either the model params file if there was only one
        available or selected, or a Zip file containing multiple model params files.

        Parameters
        ----------
        code_run_uid: str
            UID for the CodeRun
        model_weights_files: List(str)
            List of paths within S3 of model weight files to download. If multiple files are supplied, download
            as zip. If the argument is not specified, download all model weight files found for the given CodeRun.

        Returns
        -------
        model_params: BytesIO
            A Python BytesIO Buffer

        Examples
        --------
        >>> with open("my_output_file.out", "wb") as output_file:
        >>>     model_params_buffer = session.code_run.get_model_params(code_run_uid, model_weights_files)
        >>>     output_file.write(model_params_buffer.getbuffer())
        """
        result = self.session.get(
            f"/code_runs/{code_run_uid}/download_model_params",
            params={"model_weights_files": model_weights_files},
        )
        return BytesIO(result.raw_response.content)

    @rhino_error_wrapper
    def halt_code_run(self, code_run_uid: str):
        """
        @autoapi True
        Send a halting request to a Code Run.

        This triggers the halting process but does not wait for halting to complete.

        If triggering the halting process fails, a message specifying the error is returned.

        .. warning:: This feature is under development and the interface may change

        Parameters
        ----------
        code_run_uid: str
            UID of the CodeRun to halt.

        Returns
        -------
        json response in the format of:
          "status": the request's status code -
                - 200: valid request, halting innitiated.
                - 400: invalid request, the model can not be halted, or does not exist.
                - 500: error while initiating halting.
          "data":  message specifying if the halting was initiated or failed. In case the request failed,
           the error message is also displayed.

        Examples
        --------
        >>> session.code_run.halt_code_run(code_run_uid)

        """
        result = self.session.get(f"/code_runs/{code_run_uid}/halt").no_dataclass_response()
        return result

    @rhino_error_wrapper
    def get_logs(self, code_run_uid: str):
        """
        @autoapi False

        Get the logs (including errors and warning) of a specific CodeRun.
        """
        result = self.session.get(f"/code_runs/{code_run_uid}/logs")
        return result.to_dataclass(CodeRunLogs)
