from typing import Optional, Union

from rhino_health.lib.metrics.base_metric import BaseMetric
from rhino_health.lib.metrics.filter_variable import FilterVariable


class RocAuc(BaseMetric):
    """
    Performs a Receiver Operating Characteristic calculation
    """

    y_true_variable: Union[str, FilterVariable]
    y_pred_variable: Union[str, FilterVariable]
    seed: Optional[int] = None

    @classmethod
    def metric_name(cls):
        return "roc"


class RocAucWithCI(RocAuc):
    """
    Performs a Receiver Operating Characteristic calculation with Bootstrapping using Confidence Intervals
    """

    confidence_interval: int
    bootstrap_iterations: Optional[int] = None

    @classmethod
    def metric_name(cls):
        return "roc_with_ci"
