import base64
import json
from typing import Any, Dict, Optional

from pydantic import Field
from typing_extensions import Annotated, Literal

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField
from rhino_health.lib.endpoints.project.project_baseclass import WithinProjectModel
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel
from rhino_health.lib.endpoints.workgroup.workgroup_baseclass import WithinWorkgroupModel
from rhino_health.lib.metrics.base_metric import BaseMetric
from rhino_health.lib.utils import alias


class BaseDataset(RhinoBaseModel):
    """
    @autoapi False
    Used for GET/CREATE of a Dataset
    """

    name: str
    """
    @autoapi True The name of the Dataset
    """
    description: str
    """
    @autoapi True The description of the Dataset
    """
    base_version_uid: Optional[str] = None
    """
    @autoapi True The original Dataset this Dataset is a new version of, if applicable
    """
    project_uid: Annotated[str, Field(alias="project")]
    """
    @autoapi True The unique ID of the Project this Dataset belongs to.
    """
    workgroup_uid: Annotated[str, Field(alias="workgroup")]
    """
    @autoapi True
    The unique ID of the Workgroup this Dataset belongs to
    .. warning workgroup_uid may change to primary_workgroup_uid in the future
    """
    data_schema_uid: Annotated[Any, Field(alias="data_schema")]
    """
    @autoapi True The unique ID of the DataSchema this Dataset follows
    """
    contains_sensitive_data: Optional[bool] = True

    @property
    def primary_workgroup_uid(self):
        # TODO: Standardize workgroup_uid -> primary_workgroup_uid to be consistent with the other objects
        return self.workgroup_uid

    def create_args(self):
        return self.dict(
            by_alias=True,
            include={
                "name",
                "description",
                "base_version_uid",
                "project_uid",
                "workgroup_uid",
                "data_schema_uid",
            },
        )


class DatasetCreateInput(BaseDataset):
    """
    Input arguments for adding a new Dataset
    """

    csv_filesystem_location: Optional[str] = None
    """@autoapi True The location the Dataset data is located on-prem. The file should be a CSV."""
    method: Literal["DICOM", "filesystem"] = "filesystem"
    """@autoapi True What source are we importing imaging data from. Either a DICOM server, or the local file system"""
    is_data_deidentified: Optional[bool] = False
    """@autoapi True Is the data already deidentified?"""

    image_dicom_server: Optional[str] = None
    """@autoapi True The DICOM Server URL to import DICOM images from"""
    image_filesystem_location: Optional[str] = None
    """@autoapi True The on-prem Location to import DICOM images from"""

    file_base_path: Optional[str] = None
    """@autoapi True The location of non DICOM files listed in the dataset data CSV on-prem"""
    sync: Optional[bool] = True
    """@autoapi True Should we perform this import request synchronously."""

    def import_args(self):
        return self.dict(
            by_alias=True,
            include={
                "csv_filesystem_location",
                "method",
                "is_data_deidentified",
                "image_dicom_server",
                "image_filesystem_location",
                "file_base_path",
                "sync",
            },
        )


class Dataset(WithinProjectModel, WithinWorkgroupModel, BaseDataset, UserCreatedModel):
    """
    @autoapi True
    @hide_parent_class
    """

    uid: str
    """
    @autoapi True The unique ID of the Dataset
    """
    version: Optional[int] = 0
    """
    @autoapi True Which revision this Dataset is
    """
    num_cases: int
    """
    @autoapi True The number of cases in the Dataset
    """
    _dataset_info: Optional[Dict] = None
    import_status: str
    """
    @autoapi True The import status of the Dataset
    """
    data_schema_uid: Annotated[
        Any,
        UIDField(
            alias="data_schema",
            model_fetcher=lambda session, uid: session.data_schema.get_data_schemas([uid])[0],
            model_property_type="DataSchema",
        ),
    ]

    # API responses we do not want to surface to the user
    __hidden__ = ["import_details"]

    @property
    def primary_workgroup(self):
        # TODO: Standardize workgroup -> primary_workgroup to be consistent with the other objects
        return self.workgroup

    def run_code(self, run_code, print_progress=True, **kwargs):
        """
        @autoapi True

        Create and run code on this dataset using defaults that can be overridden

        .. warning:: This function relies on a dataset's metadata so make sure to create the input dataset first
        .. warning:: This feature is under development and the interface may change

        run_code: str
            The code that will run in the container
        print_progress: bool = True
            Whether to print how long has elapsed since the start of the wait
        name: Optional[str] = "{dataset.name} (v.{dataset.version}) containerless code"
            Model name - Uses the dataset name and version as part of the default
            (eg: when using a the first version of dataset named dataset_one the name will be dataset_one (v.1) containerless code)
        description: Optional[str] = "Python code run"
            Model description
        container_image_uri: Optional[str] = {ENV_URL}/rhino-gc-workgroup-rhino-health:generic-python-runner"
            Uri to container that should be run - ENV_URL is the environment ecr repo url
        input_data_schema_uid: Optional[str] = dataset.data_schema_uid
            The data_schema used for the input dataset - By default uses the data_schema used to import the dataset
        output_data_schema_uid: Optional[str] = None (Auto generate data schema)
            The data_schema used for the output dataset - By default generates a schema from the dataset_csv
        output_dataset_names_suffix: Optional[str] = "containerless code"
            String that will be added to output dataset name
        timeout_seconds: Optional[int] = 600
            Amount of time before timeout in seconds

        Examples
        --------
        dataset.run_code(run_code = <df['BMI'] = df.Weight / (df.Height ** 2)>)

        Returns
        -------
        Tuple: (output_datasets, code_run)
            output_datasets: List of Dataset Dataclasses
            code_run: A CodeRun object containing the run outcome
        """
        from rhino_health.lib.endpoints.code_object.code_object_dataclass import (
            CodeObjectCreateInput,
            CodeObjectRunInput,
            CodeTypes,
        )

        param_dict = {
            "name": f"{self.name} (v.{self.version}) containerless code",
            "description": f"Python code run",
            "container_image_uri": self.session.get_container_image_uri(
                "generic-python-runner", rhino_common_image=True
            ),
            "input_data_schema_uid": str(self.data_schema_uid),
            "output_data_schema_uid": None,
            "output_dataset_names_suffix": " containerless code",
            "timeout_seconds": 600,
        }
        unrecognized_kwarg_keys = set(kwargs.keys()) - set(param_dict.keys())
        if unrecognized_kwarg_keys:
            raise ValueError(
                f"Unrecognized keyword arguments: {', '.join(unrecognized_kwarg_keys)}"
            )
        param_dict.update(kwargs)
        code_object_creation_params = {
            "name": param_dict["name"],
            "description": param_dict["description"],
            "code_type": CodeTypes.GENERALIZED_COMPUTE,
            "config": {"container_image_uri": param_dict["container_image_uri"]},
            "project_uid": self.project_uid,
            "output_dataset_naming_templates": [
                f"{{{{input_dataset_names.0}}}}{param_dict['output_dataset_names_suffix']}"
            ],
            "input_data_schema_uids": [param_dict["input_data_schema_uid"]],
            "output_data_schema_uids": [param_dict["output_data_schema_uid"]],
        }
        create_model_params = CodeObjectCreateInput(**code_object_creation_params)
        code_object_response = self.session.code_object.create_code_object(
            create_model_params, return_existing=False, add_version_if_exists=True
        )

        run_code_object_params = CodeObjectRunInput(
            code_object_uid=code_object_response.uid,
            input_dataset_uids=[[self.uid]],
            output_dataset_naming_templates=code_object_creation_params[
                "output_dataset_naming_templates"
            ],
            run_params=json.dumps(
                {"code64": base64.b64encode(run_code.encode("utf-8")).decode("utf-8")}
            ),
            timeout_seconds=param_dict["timeout_seconds"],
            sync=False,
        )
        async_run_response = self.session.code_object.run_code_object(run_code_object_params)
        code_run = async_run_response.wait_for_completion(
            timeout_seconds=param_dict["timeout_seconds"] + 10,
            print_progress=print_progress,
        )
        output_datasets = code_run.output_datasets
        return output_datasets, code_run

    def get_metric(self, metric_configuration: BaseMetric):
        """
        Queries on-prem and returns the result based on the METRIC_CONFIGURATION for this Dataset.

        See Also
        --------
        rhino_health.lib.endpoints.dataset.dataset_endpoints.DatasetEndpoints.get_dataset_metric : Full documentation
        """
        """
        Then Cloud API use gRPC -> on-prem where the Dataset raw data exists
        On on-prem we will run the sklearn metric function with the provided arguments on the raw Dataset data
        on-prem will perform k-anonymization, and return data to Cloud API
        # TODO: Way to exclude internal docs from autoapi
        """
        return self.session.dataset.get_dataset_metric(self.uid, metric_configuration)

    @property
    def dataset_info(self):
        """
        @autoapi True Sanitized metadata information about the Dataset.
        """
        if not self._dataset_info:
            result = self.session.dataset.sync_dataset_info(self.uid)
            self._dataset_info = result
        return self._dataset_info
