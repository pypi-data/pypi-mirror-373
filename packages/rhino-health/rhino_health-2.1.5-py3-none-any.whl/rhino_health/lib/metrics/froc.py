from typing import Optional

from rhino_health.lib.metrics.base_metric import BaseMetric
from rhino_health.lib.metrics.filter_variable import FilterVariable


class FRoc(BaseMetric):
    """
    Performs a Free-response Receiver Operating Characteristic calculation
    """

    y_true_variable: FilterVariable
    y_pred_variable: FilterVariable
    specimen_variable: FilterVariable
    seed: Optional[int] = None

    @classmethod
    def metric_name(cls):
        return "froc"


class FRocWithCI(FRoc):
    """
    Performs a Free-response Receiver Operating Characteristic calculation with Bootstrapping using Confidence Intervals
    """

    confidence_interval: int
    bootstrap_iterations: Optional[int] = None

    @classmethod
    def metric_name(cls):
        return "froc_with_ci"
