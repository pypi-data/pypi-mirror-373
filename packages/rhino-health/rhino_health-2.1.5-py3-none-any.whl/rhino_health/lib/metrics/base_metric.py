import json
from abc import ABC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from rhino_health.lib.metrics.filter_variable import (
    FilterBetweenRange,
    FilterType,
    FilterVariableTypeOrColumnName,
)


class DataFilter(BaseModel):
    """
    A filter to be applied on the entire Dataset
    """

    filter_column: str
    """The column in the remote dataset df to check against"""
    filter_value: Union[Any, FilterBetweenRange]
    """The value to match against or a FilterBetweenRange if filter_type is FilterType.BETWEEN"""
    filter_type: Optional[FilterType] = FilterType.EQUAL
    """The type of filtering to perform. Defaults to FilterType.EQUAL"""
    filter_dataset: Optional[str] = None
    """The dataset to perform the filter on if there are multiple datasets for Federated Join. If unspecified will be all datasets"""


class GroupingData(BaseModel):
    """
    Configuration for grouping metric results

    See Also
    --------
    pandas.groupby : Implementation used for grouping. `See documentation <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html>`_
    """

    groupings: List[str] = []
    """
    A list of columns to group metric results by
    """
    dropna: Optional[bool] = True
    """
    Should na values be dropped if in a grouping key
    """


MetricResultDataType = Dict[str, Any]
"""
Dict[str, Any]
"""


class MetricResponse(BaseModel):
    """
    Standardized response from querying metrics against a Dataset
    """

    output: MetricResultDataType  # if group_by is specified in the arguments, is a map of group: output
    metric_configuration_dict: Optional[Dict[str, Any]] = None
    dataset_uids: Optional[List[str]] = None
    session: Any = None

    def __init__(self, **data):
        if isinstance(data["output"], str):
            data["output"] = json.loads(data["output"])
        if list(data["output"].keys()) == ["null"]:
            data["output"] = data["output"]["null"]
        if "metric_configuration_dict" not in data:
            data["metric_configuration_dict"] = None
        super(MetricResponse, self).__init__(**data)


class KaplanMeierMetricResponse(MetricResponse):
    time_variable: str
    event_variable: str

    def __init__(self, **data):
        arguments = json.loads(data["metric_configuration_dict"]["arguments"])
        data["time_variable"] = arguments["time_variable"]
        data["event_variable"] = arguments["event_variable"]
        super().__init__(**data)

    def surv_func_right_model(self, group=None):
        """
        Creates a survival function model for the metric response
        """
        try:
            import statsmodels.api as sm
        except ImportError:
            raise ImportError(
                "Package statsmodels is not installed. Use the survival and time vectors in KaplanMeierMetricResponse.output "
                "to manually create a survival function model using statsmodels.SurvFuncRight."
            )
        events_vector = self.output[group] if group else self.output
        return sm.SurvfuncRight(
            events_vector[self.time_variable], events_vector[self.event_variable]
        )


class BaseMetric(BaseModel):
    """
    Parameters available for every metric
    """

    data_filters: Optional[List[DataFilter]] = []  # We will filter in the order passed in
    group_by: Optional[GroupingData] = None
    timeout_seconds: Optional[
        float
    ] = 600.0  # Metric calculations that take longer than this time will timeout
    count_variable_name: str = "variable"

    @classmethod
    def metric_name(cls):
        """
        @autoapi False
        Each metric should define this so the backend cloud knows how to handle things.
        """
        raise NotImplementedError

    def data(self):
        data = {
            "metric": self.metric_name(),
            "arguments": self.model_dump_json(
                exclude_none=True, exclude={"timeout_seconds", "custom_aggregation_method"}
            ),
        }
        if self.timeout_seconds is not None:
            data["timeout_seconds"] = self.timeout_seconds
        return data

    @property
    def metric_response(self):
        return MetricResponse


class AggregatableMetric(BaseMetric, ABC):
    """
    @autoapi False
    custom_aggregation_method: Optional[Callable] A custom function to use to aggregate the results. The method signature should be: method(metric_name: str, metric_results: List[Dict[str, Any]], **kwargs),
            where the metric_results are each of the Dataset results for the metric,
            and the method should return a dict with the structure of: {metric_name: <aggregated_value>}
    """

    custom_aggregation_method: Optional[Callable] = None

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return True

    def data(self):
        arguments = self.model_dump_json(
            exclude_none=True, exclude={"timeout_seconds", "custom_aggregation_method"}
        )
        data = {"metric": self.metric_name()}
        if self.custom_aggregation_method:
            arguments["override_aggregation_method"] = True
        data["arguments"] = arguments
        if self.timeout_seconds is not None:
            data["timeout_seconds"] = self.timeout_seconds
        return data


class JoinMode(str, Enum):
    """
    @autoapi True
    The mode we are performing the FederatedJoin
    """

    INTERSECTION = "intersection"
    """
    @autoapi True Return values where the identifiers are found in both the filter and query datasets.
    """
    UNION = "union"
    """
    @autoapi True Returns values where rows with the same identifiers are deduplicated.
    """


class JoinableMetric(AggregatableMetric, ABC):
    """
    @autoapi False
    """

    join_mode: Optional[JoinMode] = None
    """
    @autoapi True The mode to perform an optional Federated Join in. Defaults to intersection if join_field, query_datasets, or filter_datasets are defined
    """
    join_field: Optional[FilterVariableTypeOrColumnName] = None
    """
    @autoapi True A field to perform a join on if performing a Federated Join. This filter_variable will be performed on the filter_dataset(s)
    """
    query_datasets: Optional[List[str]] = None
    """
    @autoapi False A list of Datasets to get data from. Used for Federated Join. Currently only supports 1 dataset for Intersection Mode. Supports any number of datasets for Union mode. The order of datasets determines the selection order in Intersection mode. Data from earlier datasets has will be used over later datasets.
    """
    filter_datasets: Optional[List[str]] = None
    """
    @autoapi False A list of datasets to perform the join filter logic against. Used for Federated Join Intersection. Currently only supports 1 dataset.
    """

    def __init__(self, **data):
        # Handle optional join_mode fields based on user input
        join_field = data.get("join_field")
        query_datasets = data.get("query_datasets")
        filter_datasets = data.get("filter_datasets")
        join_mode = data.get("join_mode")
        if any([x is not None for x in [join_field, query_datasets, filter_datasets, join_mode]]):
            # Cannot do the following check with the desired interface alias
            # if not query_datasets:
            #     raise ValueError("data_datasets cannot be empty for a Federated Join. Either remove all Join fields or provide a dataset UID")
            # if not filter_datasets:
            #     raise ValueError("filter_datasets cannot be empty for a Federated Join. Either remove all Join fields or provide a dataset UID")
            if not join_field:
                raise ValueError(
                    "The join_field cannot be empty when attempting a Federated Join. Either remove all Join fields or provide a join field"
                )
            if not join_mode:
                data["join_mode"] = JoinMode.INTERSECTION
        super().__init__(**data)
