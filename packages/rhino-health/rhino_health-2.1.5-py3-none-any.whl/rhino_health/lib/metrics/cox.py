from enum import Enum
from typing import List, Optional

from rhino_health.lib.metrics.base_metric import AggregatableMetric
from rhino_health.lib.metrics.filter_variable import FilterVariableTypeOrColumnName


class InitialBeta(Enum):
    """
    The initial beta value for the Cox metric.
    """

    ZERO = "zero"
    MEAN = "mean"


class Cox(AggregatableMetric):
    """
    A metric that calculates the Cox proportional hazard metric for a dataset.
    """

    time_variable: FilterVariableTypeOrColumnName
    event_variable: FilterVariableTypeOrColumnName
    covariates: Optional[List[FilterVariableTypeOrColumnName]] = None
    initial_beta: Optional[InitialBeta] = InitialBeta.MEAN
    max_iterations: int = 100
    accuracy: float = 1e-6

    @classmethod
    def metric_name(cls):
        return "cox"

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return False
