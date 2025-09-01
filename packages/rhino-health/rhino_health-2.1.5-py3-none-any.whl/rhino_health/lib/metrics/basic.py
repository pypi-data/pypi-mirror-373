from rhino_health.lib.metrics.base_metric import JoinableMetric
from rhino_health.lib.metrics.filter_variable import FilterVariableTypeOrColumnName


class Count(JoinableMetric):
    """
    Returns the count of entries for a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName

    @classmethod
    def metric_name(cls):
        return "count"


class Mean(JoinableMetric):
    """
    Returns the mean value of a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName

    @classmethod
    def metric_name(cls):
        return "mean"


class StandardDeviation(JoinableMetric):
    """
    Returns the standard deviation of a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName

    @classmethod
    def metric_name(cls):
        return "stddev"


class Sum(JoinableMetric):
    """
    Returns the sum of a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName

    @classmethod
    def metric_name(cls):
        return "sum"


COMMON_METRICS = [Count, Mean, StandardDeviation, Sum]
