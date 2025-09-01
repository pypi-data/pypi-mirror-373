from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, NonNegativeInt
from typing_extensions import Annotated

from rhino_health.lib.dataclass import RhinoBaseModel, UIDField
from rhino_health.lib.endpoints.dataset.dataset_dataclass import Dataset
from rhino_health.lib.endpoints.user.user_baseclass import UserCreatedModel
from rhino_health.lib.endpoints.workgroup.workgroup_baseclass import PrimaryWorkgroupModel


class AnalyticsVisibility(str, Enum):
    """
    Supported values for FederatedDataset.analytics_visibility.
    """

    PUBLIC = "Public"
    LIMITED = "Limited"


class DataSheetComposition(BaseModel):
    """
    Describe the General composition of the dataset
    """

    geography: Optional[str] = None
    """Describe the geographic regions represented in this dataset"""
    data_type: Optional[str] = None
    """Describe the data types represented in this dataset"""
    modality: Optional[str] = None
    """Describe the modalities represented in this dataset"""
    disease_group: Optional[str] = None
    """Describe the disease areas represented in this dataset"""
    body_part: Optional[str] = None
    """Describe the body parts represented in this dataset"""


class DataSheet(BaseModel):
    """
    A standard description of the data to aid users of the data to understand
    your dataset.
    See https://arxiv.org/abs/1803.09010
    """

    name: Optional[str] = None
    """Name for the dataset"""
    motivation: Optional[str] = None
    """Describe the motivation for building this dataset"""
    composition: Optional[DataSheetComposition] = None
    """Describe the General composition of the dataset"""
    collection_process: Optional[str] = None
    """Describe the data collection processes used in the creation of this dataset."""
    preprocessing: Optional[str] = None
    """Describe any preprocessing/cleaning/labeling performed in the preparation of the dataset."""
    uses: Optional[str] = None
    """Has the dataset been used for any tasks already?"""
    distribution: Optional[str] = None
    """Describe distribution considerations for this dataset, if any"""
    maintenance: Optional[str] = None
    """Describe the maintenance plan for this dataset."""


class DifferentialPrivacy(int, Enum):
    """
    Differential privacy level
    """

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class PrivacySettings(RhinoBaseModel):
    """Privacy Settings for your Dataset"""

    k_anonymization_parameter: NonNegativeInt
    """@autoapi True The minimal number of data points required to provide metric response values"""
    differential_privacy_setting: DifferentialPrivacy
    """@autoapi True The level at which to enforce differential privacy"""


class FederatedDatasetBase(RhinoBaseModel):
    """
    @autoapi False
    Base DataSchema used by both return result and creation
    """

    name: str
    """@autoapi True The name of the Federated Dataset"""
    base_version_uid: Optional[str] = None
    """@autoapi True If this Federated Dataset is a new version of another Federated Dataset, the original Unique ID of the base Federated Dataset."""
    dataset_uids: Annotated[List[str], Field(alias="datasets")]
    """@autoapi True A list of UIDs of the Datasets comprising the Federated Dataset"""
    datasheet: DataSheet
    """@autoapi True Datasheet for the Federated Dataset"""
    analytics_visibility: AnalyticsVisibility
    """@autoapi True The visibility mode for Federated Dataset's Dataset' analytics ("Public" or "Limited")"""
    privacy_settings: PrivacySettings
    """@autoapi True Privacy settings for the Federated Dataset"""
    primary_workgroup_uid: Annotated[str, Field(alias="primary_workgroup")]
    """@autoapi True The unique ID of the Federated Dataset's primary Workgroup"""
    contact_email: Optional[str] = None
    """@autoapi True Email address to use to contact the owners of the Federated Dataset"""


class FederatedDatasetCreateInput(FederatedDatasetBase):
    """
    @autoapi True
    Input for creating a new Federated Dataset

    Examples
    --------
    >>> FederatedDatasetCreateInput(
    ...     name="My Federated Dataset",
    ...     datasets=datasets,
    ...     datasheet=json.dumps(datasheet),
    ...     analytics_visibility="Limited",
    ...     privacy_settings=json.dumps(privacy_settings),
    ...     primary_workgroup=project.primary_workgroup,
    ... )

    Parameters
    ----------
    datasets: Optional[List[Dataset]]
        A list of Dataset Dataclasses, use in place of dataset_uids
    primary_workgroup: Optional[Workgroup]
        A workgroup Dataclass, use in place of primary_workgroup_uid
    """

    def __init__(self, **kwargs):
        datasets = kwargs.pop("datasets", None)
        if datasets is not None:
            if "dataset_uids" in kwargs:
                raise TypeError("Cannot specify both datasets and dataset_uids")
            datasets = list(datasets)  # In case it's an iterator.
            if not all(isinstance(dataset, Dataset) for dataset in datasets):
                raise TypeError("datasets must be a collection of Dataset objects")
            dataset_uids = [dataset.uid for dataset in datasets]
            kwargs["dataset_uids"] = dataset_uids

        primary_workgroup = kwargs.pop("primary_workgroup", None)
        if primary_workgroup is not None:
            if "primary_workgroup_uid" in kwargs:
                raise TypeError("Cannot specify both primary_workgroup and primary_workgroup_uid")
            kwargs["primary_workgroup_uid"] = primary_workgroup.uid

        super().__init__(**kwargs)


class FederatedDataset(PrimaryWorkgroupModel, FederatedDatasetBase, UserCreatedModel):
    """
    @autoapi True
    @hide_parent_class
    A Federated Dataset existing on the platform
    """

    uid: str
    """@autoapi True The Unique ID of the Federated Dataset"""
    dataset_uids: Annotated[
        List[str],
        UIDField(
            alias="datasets",
            is_list=True,
            model_fetcher=lambda session, uids: [session.dataset.get_dataset(uid) for uid in uids],
            model_property_type="Dataset",
        ),
    ]
    """@autoapi True A list of Datasets comprising the Federated Dataset"""
