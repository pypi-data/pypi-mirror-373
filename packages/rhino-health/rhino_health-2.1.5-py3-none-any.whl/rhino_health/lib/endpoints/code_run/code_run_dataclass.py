from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Union

import funcy
from pydantic import BaseModel, Field, RootModel
from typing_extensions import Annotated

from rhino_health.lib.dataclass import UIDField
from rhino_health.lib.endpoints.dataset.dataset_dataclass import Dataset
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel


class CodeRunStatus(str, Enum):
    """
    Status of the code run
    """

    INITIALIZING = "Initializing"
    STARTED = "Started"
    COMPLETED = "Completed"
    FAILED = "Failed"
    HALTING = "Halting"
    HALTED_SUCCESS = "Halted: Success"
    HALTED_FAILURE = "Halted: Failure"  # Indicating the halting failed


class CodeRunInputWorkgroupInputDatasets(RootModel):
    """
    See CodeRunInputDatasets
    """

    root: List[str]


class CodeRunInputWorkgroupDatasets(RootModel):
    """
    See CodeRunInputDatasets
    """

    root: List[CodeRunInputWorkgroupInputDatasets]


class CodeRunInputDatasets(RootModel):
    """
    A triply-nested list of dataset uids. Each entry is a list of lists of datasets corresponding to a single workgroup within the code run.
    [[[first_dataset_for_first_run], [second_dataset_for_first_run] ...], [[first_dataset_for_second_run], [second_dataset_for_second_run] ...], ...]
    """

    root: List[CodeRunInputWorkgroupDatasets]


class CodeRunWorkgroupOutputDatasets(RootModel):
    """
    See CodeRunOutputDatasets
    """

    root: List[str]


class CodeRunWorkgroupDatasets(RootModel):
    """
    See CodeRunOutputDatasets
    """

    root: List[CodeRunWorkgroupOutputDatasets]


class CodeRunOutputDatasets(RootModel):
    """
    A triply-nested list of dataset uids. Each entry is a list of lists of datasets corresponding to a single workgroup within the code run.
    [[[first_dataset_for_first_run], [second_dataset_for_first_run] ...], [[first_dataset_for_second_run], [second_dataset_for_second_run] ...], ...]
    """

    root: List[CodeRunWorkgroupDatasets]


class CodeRunLogs(BaseModel):
    """
    Logs for a code run
    """

    logs: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]


class CodeRun(UserCreatedModel):
    """
    @autoapi True
    @hide_parent_class
    Result of a code run
    """

    uid: str
    """The unique ID of the CodeRun"""
    description: Optional[str] = None
    """The description of the code run"""
    action_type: str
    """The type of code run performed"""
    status: CodeRunStatus
    """The code run status"""
    start_time: str
    """The code run start time"""
    end_time: Any = None
    """The code run end time"""
    _code_object: Any = None
    _input_datasets: Any = None
    _output_datasets: Any = None
    input_dataset_uids: Optional[CodeRunInputDatasets]
    """
    A triply-nested list of dataset uids. Each entry is a list of lists of datasets corresponding to a single workgroup within the code run.
    [[[first_dataset_for_first_run], [second_dataset_for_first_run] ...], [[first_dataset_for_second_run], [second_dataset_for_second_run] ...], ...]
    """
    output_dataset_uids: Optional[CodeRunOutputDatasets]
    """
    A triply-nested list of dataset uids. Each entry is a list of lists of datasets corresponding to a single workgroup within the code run.
    [[[first_dataset_for_first_run], [second_dataset_for_first_run] ...], [[first_dataset_for_second_run], [second_dataset_for_second_run] ...], ...]
    """
    code_object_uid: Annotated[
        str,
        UIDField(
            alias="code_object",
            model_fetcher=lambda session, uid: session.code_object.get_code_object(uid),
            model_property_type="CodeObject",
        ),
    ]
    _logs: Optional[CodeRunLogs] = None
    """The run result info"""
    results_report: Optional[Union[str, dict]] = None
    """The run result report"""
    # Note: pydantic field names cannot start with "model".
    paths_to_model_params: Annotated[
        Optional[List[str]], Field(alias="model_params_external_storage_paths")
    ] = None
    """The external paths where model param results are stored, if any"""
    created_at: Annotated[str, Field(alias="start_time")]
    published: bool = False
    """Whether this code run is published"""

    # API responses we do not want to surface to the user
    __hidden__ = [
        "config_info",  # Internal Task UID data
        "input_sal_uids",  # Internal usage no SAL object in SDK
    ]

    @property
    def input_datasets(self):
        """
        @autoapi True
        Return the Input Datasets that were used for this CodeRun

        .. warning:: The result of this function is cached.
            Be careful calling this function after making changes

        Returns
        -------
        datasets: List[Dataset]
            Dataclasses representing the Datasets
        """
        if self._input_datasets is not None:
            return self._input_datasets

        dataset_uids: Iterable[str]
        if isinstance(self.input_dataset_uids, RootModel):
            dataset_uids = funcy.flatten(self.input_dataset_uids.model_dump())
        else:
            dataset_uids = funcy.flatten(self.input_dataset_uids)

        results: List[Dataset] = []
        for dataset_uid in dataset_uids:
            results.append(self.session.dataset.get_dataset(dataset_uid))

        self._input_datasets = results
        return results

    @property
    def output_datasets(self):
        """
        @autoapi True
        Return the Output Datasets that were used for this CodeRun

        .. warning:: The result of this function is cached.
            Be careful calling this function after making changes

        Returns
        -------
        datasets: List[Dataset]
            Dataclasses representing the Datasets
        """
        if self.output_dataset_uids is None:
            return None
        if self._output_datasets is not None:
            return self._output_datasets

        dataset_uids: Iterable[str]
        if isinstance(self.output_dataset_uids, RootModel):
            dataset_uids = funcy.flatten(self.output_dataset_uids.model_dump())
        else:
            dataset_uids = funcy.flatten(self.output_dataset_uids)

        results: List[Dataset] = []
        for dataset_uid in dataset_uids:
            results.append(self.session.dataset.get_dataset(dataset_uid))

        self._output_datasets = results
        return results

    def save_model_params(self, file_name):
        """
        Saves the model params to a file.

        .. warning:: This feature is under development and the interface may change

        Parameters
        ----------
        file_name: str
            Name of the file to save to
        """
        model_params = self.session.code_run.get_model_params()
        with open(file_name, "wb") as output_file:
            output_file.write(model_params.getbuffer())

    @property
    def _process_finished(self):
        """
        @autoapi False
        """
        return self.status in {
            CodeRunStatus.COMPLETED,
            CodeRunStatus.FAILED,
            CodeRunStatus.HALTED_SUCCESS,
            CodeRunStatus.HALTED_FAILURE,
        }

    def wait_for_completion(
        self, timeout_seconds: int = 500, poll_frequency: int = 10, print_progress: bool = True
    ):
        """
        @autoapi True
        Wait for the asynchronous CodeRun to complete

        Parameters
        ----------
        timeout_seconds: int = 500
            How many seconds to wait before timing out
        poll_frequency: int = 10
            How frequent to check the status, in seconds
        print_progress: bool = True
            Whether to print how long has elapsed since the start of the wait

        Returns
        -------
        code_run: CodeRun
            Dataclass representing the CodeRun of the run

        See Also
        --------
        rhino_health.lib.endpoints.code_run.code_run_dataclass.CodeRun: Response object
        """
        return self._wait_for_completion(
            name="code run",
            is_complete=self._process_finished,
            query_function=lambda code_run: code_run.session.code_run.get_code_run(code_run.uid),
            validation_function=lambda old, new: (new.status and new._process_finished),
            timeout_seconds=timeout_seconds,
            poll_frequency=poll_frequency,
            print_progress=print_progress,
        )

    # def __logs(self):
    #     return self.session.code_run.__logs(self.uid)

    @property
    def warnings(self):
        """
        Returns any warnings that occurred during this run
        """
        if self._logs is None:
            self._logs = self.session.code_run.get_logs(self.uid)
        warnings = self._logs.warnings or []
        warnings += funcy.flatten([x.get("warnings") or [] for x in self._logs.logs])

        return warnings

    @property
    def errors(self):
        """
        Returns any errors that occurred during this run
        """
        if self._logs is None:
            self._logs = self.session.code_run.get_logs(self.uid)
        errors = self._logs.errors or []
        errors += funcy.flatten([x.get("errors") or [] for x in self._logs.logs])

        return errors

    def publish(self, unpublish_other_versions: bool = True):
        return self.session.code_run.publish(
            self, unpublish_other_versions=unpublish_other_versions
        )

    def unpublish(self):
        return self.session.code_run.unpublish(self)
