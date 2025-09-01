from typing import List, Optional, Union

from rhino_health.lib.metrics.base_metric import AggregatableMetric, BaseMetric
from rhino_health.lib.metrics.filter_variable import FilterVariableTypeOrColumnName


class AccuracyScore(AggregatableMetric):
    """
    Calculates the `Accuracy Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html#sklearn.metrics.accuracy_score>`_

    Examples
    --------
    >>> accuracy_score_configuration = AccuracyScore(
    ...   y_true = 'first_binary_column',
    ...   y_pred = 'second_binary_column',
    ...   normalize = False,
    ...   sample_weight = [ 0.1, 0.2, 1, 0, ..... ],
    ... )
    >>> my_dataset.get_metric(accuracy_score_configuration)
    """

    y_true: FilterVariableTypeOrColumnName
    y_pred: FilterVariableTypeOrColumnName
    normalize: Optional[bool] = True
    sample_weight: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "accuracy_score"


class AveragePrecisionScore(AggregatableMetric):
    """
    Calculates the `Average Precision Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html#sklearn.metrics.average_precision_score>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_score: FilterVariableTypeOrColumnName
    average: Optional[str] = "macro"
    pos_label: Optional[Union[int, str]] = 1
    sample_weight: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "average_precision_score"


class BalancedAccuracyScore(AggregatableMetric):
    """
    Calculates the `Balanced Accuracy Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html#sklearn.metrics.balanced_accuracy_score>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_pred: FilterVariableTypeOrColumnName
    sample_weight: Optional[List] = None
    adjusted: Optional[bool] = False

    @classmethod
    def metric_name(cls):
        return "balanced_accuracy_score"


class BrierScoreLoss(AggregatableMetric):
    """
    Calculates the `Brier Score Loss <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html#sklearn.metrics.brier_score_loss>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_prob: FilterVariableTypeOrColumnName
    sample_weight: Optional[List] = None
    pos_label: Optional[Union[int, str]] = None

    @classmethod
    def metric_name(cls):
        return "brier_score_loss"


class CohenKappaScore(AggregatableMetric):
    """
    Calculates the `Cohen Kappa Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html#sklearn.metrics.cohen_kappa_score>`_
    """

    y1: FilterVariableTypeOrColumnName
    y2: FilterVariableTypeOrColumnName
    labels: Optional[List] = None
    weights: Optional[str] = None
    sample_weight: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "cohen_kappa_score"


class ConfusionMatrix(AggregatableMetric):
    """
    Calculates the `Confusion Matrix <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html#sklearn.metrics.confusion_matrix>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_pred: FilterVariableTypeOrColumnName
    labels: Optional[List] = None
    sample_weight: Optional[List] = None
    normalize: Optional[bool] = True

    @classmethod
    def metric_name(cls):
        return "confusion_matrix"


class DCGScore(AggregatableMetric):
    """
    Calculates the `DCG Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.dcg_score.html#sklearn.metrics.dcg_score>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_score: FilterVariableTypeOrColumnName
    k: Optional[int] = None
    log_base: Optional[int] = 2
    sample_weight: Optional[List] = None
    ignore_ties: Optional[bool] = False

    @classmethod
    def metric_name(cls):
        return "dcg_score"


class WeightedScore(AggregatableMetric):
    """@autoapi False"""

    y_true: FilterVariableTypeOrColumnName
    """@autoapi True """
    y_pred: FilterVariableTypeOrColumnName
    """@autoapi True"""
    average: Optional[str] = "binary"
    """@autoapi True"""
    labels: Optional[List] = None
    """@autoapi True"""
    pos_label: Optional[Union[int, str]] = 1
    """@autoapi True"""
    sample_weight: Optional[List] = None
    """@autoapi True"""


class F1Score(WeightedScore):
    """
    Calculates the `F1 Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html#sklearn.metrics.f1_score>`_
    """

    @classmethod
    def metric_name(cls):
        return "f1_score"


class FBetaScore(WeightedScore):
    """
    Calculates the `F Beta Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.fbeta_score.html#sklearn.metrics.fbeta_score>`_
    """

    @classmethod
    def metric_name(cls):
        return "fbeta_score"


class HammingLossMetric(AggregatableMetric):
    """
    Calculates the `Hamming Loss Metric <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.hamming_loss.html#sklearn.metrics.hamming_loss>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_pred: FilterVariableTypeOrColumnName
    sample_weight: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "hamming_loss"


class HingeLossMetric(AggregatableMetric):
    """
    Calculates the `Hinge Loss Metric <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.hinge_loss.html#sklearn.metrics.hinge_loss>`_
    """

    y_true: FilterVariableTypeOrColumnName
    pred_decision: FilterVariableTypeOrColumnName
    labels: Optional[List] = None
    sample_weight: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "hinge_loss"


class JaccardScore(AggregatableMetric):
    """
    Calculates the `Jaccard Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.jaccard_score.html#sklearn.metrics.jaccard_score>`_
    """

    @classmethod
    def metric_name(cls):
        return "jaccard_score"


class LogLoss(AggregatableMetric):
    """
    Calculates the `Log Loss <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.jaccard_score.html#sklearn.metrics.log_loss>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_pred: FilterVariableTypeOrColumnName
    eps: Optional[float] = None
    normalize: Optional[bool] = True
    sample_weight: Optional[List] = None
    labels: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "log_loss"


class MatthewsCorrelationCoefficient(AggregatableMetric):
    """
    Calculates the `Matthews Correlation Coefficient <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html#sklearn.metrics.matthews_corrcoef>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_pred: FilterVariableTypeOrColumnName
    sample_weight: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "matthews_corrcoef"


class NDCGScore(AggregatableMetric):
    """
    Calculates the `NDCG Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html#sklearn.metrics.ndcg_score>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_score: FilterVariableTypeOrColumnName
    k: Optional[int] = None
    sample_weight: Optional[List] = None
    ignore_ties: Optional[bool] = False

    @classmethod
    def metric_name(cls):
        return "ndcg_score"


class PrecisionScore(WeightedScore):
    """
    Calculates the `Precision Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html#sklearn.metrics.precision_score>`_
    """

    @classmethod
    def metric_name(cls):
        return "precision_score"


class RecallScore(WeightedScore):
    """
    Calculates the `Recall Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html#sklearn.metrics.recall_score>`_
    """

    @classmethod
    def metric_name(cls):
        return "recall_score"


class TopKAccuracyScore(AggregatableMetric):
    """
    Calculates the `Top K Accuracy Score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.top_k_accuracy_score.html#sklearn.metrics.top_k_accuracy_score>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_score: FilterVariableTypeOrColumnName
    k: Optional[int] = 2
    normalize: Optional[bool] = True
    sample_weight: Optional[List] = None
    labels: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "top_k_accuracy_score"


class ZeroOneLoss(AggregatableMetric):
    """
    Calculates the `Zero One Loss <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.zero_one_loss.html#sklearn.metrics.zero_one_loss>`_
    """

    y_true: FilterVariableTypeOrColumnName
    y_score: FilterVariableTypeOrColumnName
    normalize: Optional[bool] = True
    sample_weight: Optional[List] = None

    @classmethod
    def metric_name(cls):
        return "zero_one_loss"
