from abc import ABC
from typing import Optional

from rhino_health.lib.metrics.base_metric import AggregatableMetric
from rhino_health.lib.metrics.filter_variable import FilterVariableTypeOrColumnName


class TimeRangeBasedMetric(AggregatableMetric, ABC):
    """
    Abstract class for metrics that are based on a time range
    """

    variable: Optional[
        FilterVariableTypeOrColumnName
    ] = None  # TODO: Deprecated, to be removed in the next breaking changes version
    detected_column_name: FilterVariableTypeOrColumnName
    time_column_name: FilterVariableTypeOrColumnName
    start_time: str
    end_time: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by:
            if (
                self.detected_column_name in self.group_by.groupings
                or self.time_column_name in self.group_by.groupings
            ):
                raise ValueError(
                    "Can not group by the detected or time columns: "
                    f'"{self.detected_column_name}", "{self.time_column_name}"'
                )

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return False


class Prevalence(TimeRangeBasedMetric):
    """
    Returns the prevalence of entries for a specified VARIABLE
    """

    @classmethod
    def metric_name(cls):
        return "prevalence"


class Incidence(TimeRangeBasedMetric):
    """
    Returns the incidence of entries for a specified VARIABLE
    """

    @classmethod
    def metric_name(cls):
        return "incidence"
