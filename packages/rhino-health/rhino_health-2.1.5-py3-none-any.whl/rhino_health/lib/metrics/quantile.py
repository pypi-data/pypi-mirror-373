from typing import Union

from rhino_health.lib.metrics.base_metric import AggregatableMetric, BaseMetric
from rhino_health.lib.metrics.filter_variable import FilterVariableTypeOrColumnName


class Median(AggregatableMetric):
    """
    Returns the median of entries for a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName

    @classmethod
    def metric_name(cls):
        return "median"

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return False


class Percentile(AggregatableMetric):
    """
    Returns the k-percentile of entries for a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName
    percentile: Union[int, float]

    @classmethod
    def metric_name(cls):
        return "percentile"

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return False


class Min(AggregatableMetric):
    """
    Returns the minimum of entries for a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName

    @classmethod
    def metric_name(cls):
        return "min"

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return False


class Max(AggregatableMetric):
    """
    Returns the maximum of entries for a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName

    @classmethod
    def metric_name(cls):
        return "max"

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return False
