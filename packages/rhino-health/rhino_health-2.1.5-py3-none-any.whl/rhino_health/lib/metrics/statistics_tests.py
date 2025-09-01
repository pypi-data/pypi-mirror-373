from typing import Optional

from rhino_health.lib.metrics.base_metric import AggregatableMetric
from rhino_health.lib.metrics.filter_variable import FilterVariableTypeOrColumnName


class ChiSquare(AggregatableMetric):
    """
    A metric that calculates the Chi-Square test for multiple Datasets.
    """

    variable: Optional[
        FilterVariableTypeOrColumnName
    ] = None  # TODO: Deprecated, to be removed in the next breaking changes version
    variable_1: FilterVariableTypeOrColumnName  # TODO: better names
    variable_2: FilterVariableTypeOrColumnName

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by is not None and set(self.group_by.groupings) & {
            self.variable_1,
            self.variable_2,
        }:
            raise ValueError(
                f'Can not group by the given metric variables: "{self.variable_1}", "{self.variable_2}"'
            )

    @classmethod
    def metric_name(cls):
        return "chi_square"

    @property
    def supports_custom_aggregation(self):
        return False


class Pearson(AggregatableMetric):
    """
    A metric that calculates the Pearson Correlation Coefficient for multiple Datasets.
    """

    variable_1: FilterVariableTypeOrColumnName
    variable_2: FilterVariableTypeOrColumnName

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by is not None and set(self.group_by.groupings) & {
            self.variable_1,
            self.variable_2,
        }:
            raise ValueError(
                f'Can not group by the given metric variables: "{self.variable_1}", "{self.variable_2}"'
            )

    @classmethod
    def metric_name(cls):
        return "pearson"

    @property
    def supports_custom_aggregation(self):
        return False


class ICC(AggregatableMetric):
    """
    A metric that calculates the Intraclass Correlation Coefficient for multiple Datasets.
    """

    variable_1: FilterVariableTypeOrColumnName
    variable_2: FilterVariableTypeOrColumnName

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by is not None and set(self.group_by.groupings) & {
            self.variable_1,
            self.variable_2,
        }:
            raise ValueError(
                f'Can not group by the given metric variables: "{self.variable_1}", "{self.variable_2}"'
            )

    @classmethod
    def metric_name(cls):
        return "icc"

    @property
    def supports_custom_aggregation(self):
        return False


class Spearman(AggregatableMetric):
    """
    A metric that calculates Spearman's Rank Correlation Coefficient for multiple Datasets.
    """

    variable_1: FilterVariableTypeOrColumnName
    variable_2: FilterVariableTypeOrColumnName

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by is not None and set(self.group_by.groupings) & {
            self.variable_1,
            self.variable_2,
        }:
            raise ValueError(
                f'Can not group by the given metric variables: "{self.variable_1}", "{self.variable_2}"'
            )

    @classmethod
    def metric_name(cls):
        return "spearman"

    @property
    def supports_custom_aggregation(self):
        return False


class Wilcoxon(AggregatableMetric):
    """
    A metric that calculates the Wilcoxon signed rank test for multiple Datasets.
    """

    variable: FilterVariableTypeOrColumnName
    abs_values_variable: FilterVariableTypeOrColumnName

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by is not None and set(self.group_by.groupings) & {
            self.variable,
            self.abs_values_variable,
        }:
            raise ValueError(
                f'Can not group by the given metric variables: "{self.variable}", "{self.abs_values_variable}"'
            )

    @classmethod
    def metric_name(cls):
        return "wilcoxon"

    @property
    def supports_custom_aggregation(self):
        return False


class TTest(AggregatableMetric):
    """
    A metric that calculates the T test for multiple Datasets.
    The methods used is the Welch's t-test (equal or unequal sample sizes, unequal variances).
    """

    numeric_variable: FilterVariableTypeOrColumnName
    categorical_variable: FilterVariableTypeOrColumnName  # TODO: better names

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by is not None and set(self.group_by.groupings) & {
            self.numeric_variable,
            self.categorical_variable,
        }:
            raise ValueError(
                f'Can not group by the given metric variables: "{self.numeric_variable}", "{self.categorical_variable}"'
            )

    @classmethod
    def metric_name(cls):
        return "t_test"

    @property
    def supports_custom_aggregation(self):
        return False


class OneWayANOVA(AggregatableMetric):
    """
    A metric that calculates the T test for multiple Datasets.
    If the numeric variable data column has nans, they will be ignored.
    """

    variable: Optional[
        FilterVariableTypeOrColumnName
    ] = None  # TODO: Deprecated, to be removed in the next breaking changes version
    numeric_variable: FilterVariableTypeOrColumnName
    categorical_variable: FilterVariableTypeOrColumnName

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by is not None and set(self.group_by.groupings) & {
            self.numeric_variable,
            self.categorical_variable,
        }:
            raise ValueError(
                f'Can not group by the given metric variables: "{self.numeric_variable}", "{self.categorical_variable}"'
            )

    @classmethod
    def metric_name(cls):
        return "one_way_ANOVA"

    @property
    def supports_custom_aggregation(self):
        return False
