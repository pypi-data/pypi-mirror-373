import functools
import json
from abc import ABC
from collections import OrderedDict
from typing import Dict, Optional
from warnings import warn

from pydantic import field_validator

from rhino_health.lib.metrics.aggregate_metrics.aggregation_service import (
    get_cloud_aggregated_metric_data,
)
from rhino_health.lib.metrics.base_metric import AggregatableMetric, MetricResponse
from rhino_health.lib.metrics.filter_variable import FilterVariableTypeOrColumnName


class TwoByTwoTableBasedMetric(AggregatableMetric, ABC):
    """
    Abstract class for metrics that are based on a two by two table
    """

    variable: Optional[
        FilterVariableTypeOrColumnName
    ] = None  # TODO: Deprecated, to be removed in the next breaking changes version
    detected_column_name: FilterVariableTypeOrColumnName
    exposed_column_name: FilterVariableTypeOrColumnName

    @field_validator("variable")
    @classmethod
    def warn_if_variable_used(cls, value):
        if value is not None:
            warn(
                "The field `variable` is deprecated, please use only the fields `detected_column_name` and `exposed_column_name`.",
                RuntimeWarning,
                stacklevel=2,
            )
        return value

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.group_by:
            if (
                self.detected_column_name in self.group_by.groupings
                or self.exposed_column_name in self.group_by.groupings
            ):
                raise ValueError(
                    "Can not group by the detected or exposed columns: "
                    f'"{self.detected_column_name}", "{self.exposed_column_name}"'
                )

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return False


class TwoByTwoTable(TwoByTwoTableBasedMetric):
    """
    Returns the two by two table of entries for a specified VARIABLE
    """

    @field_validator("variable")
    @classmethod
    def warn_if_variable_used(cls, value):
        if value is not None:
            warn(
                "The field `variable` is deprecated, please use only the fields `detected_column_name` and `exposed_column_name`.",
                RuntimeWarning,
                stacklevel=2,
            )
        return value

    @classmethod
    def metric_name(cls):
        return "two_by_two_table"

    @property
    def metric_response(self):
        """
        Returns the response class for the metric
        """
        return TwoByTwoTableMetricResponse


class OddsRatio(TwoByTwoTableBasedMetric):
    """
    Returns the odds ratio of entries for a specified VARIABLE
    """

    @classmethod
    def metric_name(cls):
        return "odds_ratio"


class Odds(AggregatableMetric):
    """
    Returns the odds of entries for a specified VARIABLE where the odd is calculated by the ratio of the number of true
     occurrences to the number of false occurrences.
    """

    variable: Optional[
        FilterVariableTypeOrColumnName
    ] = None  # TODO: Deprecated, to be removed in the next breaking changes version
    column_name: FilterVariableTypeOrColumnName

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @field_validator("variable")
    @classmethod
    def warn_if_variable_used(cls, value):
        if value:
            warn(
                "The field `variable` is deprecated, please use only the fields `detected_column_name` and `exposed_column_name`.",
                RuntimeWarning,
                stacklevel=2,
            )
        return value

    @classmethod
    def metric_name(cls):
        return "odds"

    @property
    def supports_custom_aggregation(self):
        """
        @autoapi False
        """
        return False


class Risk(TwoByTwoTableBasedMetric):
    """
    Returns the risk of entries for a specified VARIABLE
    """

    @classmethod
    def metric_name(cls):
        return "risk"


class RiskRatio(TwoByTwoTableBasedMetric):
    """
    Returns the risk ratio of entries for a specified VARIABLE
    """

    @classmethod
    def metric_name(cls):
        return "risk_ratio"


class TwoByTwoTableMetricResponse(MetricResponse):
    @functools.cached_property
    def _metric_configuration_dict_arguments(self):
        return json.loads(self.metric_configuration_dict["arguments"])

    def as_table(self):
        """
        Display the 2X2 table metric response as a dict representing a table. Use pd.DataFrame(as_table_result)
        to visualize the table.
        The data provided should represent a 2X2 table meaning the
        dict is of length 4, the keys should be tuples of length 2 representing the possible combination of values.
        The "detected" values are the columns and the "exposed" values are the rows.
        If the data is boolean, the table order is (true, false) for both columns and rows.
        If not, the order is alphabetical.
        """
        table_data = self.output.get("two_by_two_table")
        if not table_data:
            # As grouped two by two tables are a less common use case, and as it results in an unkNown number of tables,
            # we do not support the multiple tables output - the user can manually access the output and
            # create the desired table.
            raise ValueError(
                "Can not visualize table for grouped results. To solve this, "
                "remove the group_by argument from the metric configuration or manually access "
                "MetricResponse.output for retrieving the table data."
            )
        if not any(
            isinstance(key, str) and isinstance(value, (int, dict))
            for key, value in table_data.items()
        ):
            raise ValueError("MetricResponse is not representing a table")

        table_as_dict = TwoByTwoTableMetricResponse._get_ordered_dict_table(table_data)

        return table_as_dict

    @staticmethod
    def _get_ordered_dict_table(table_data: Dict):
        """
        Returns the table data as an ordered dict representing a table.
        The data provided should represent a 2X2 table meaning the
        dict is of length 4, the keys should be tuples of length 2 representing the possible combination of values.
        The "detected" values are the columns and the "exposed" values are the rows.
        If the data is boolean, the table order is (true, false) for both columns and rows.
        If not, the order is alphabetical.
        """

        def get_table_headers_from_data():
            col_values, row_values = set(), set()
            for key in table_data:
                col_value, row_value = eval(key)
                col_values.add(col_value)
                row_values.add(row_value)

            return sorted(col_values, reverse=all(isinstance(v, bool) for v in col_values)), sorted(
                row_values, reverse=all(isinstance(v, bool) for v in row_values)
            )

        col_headers, row_headers = get_table_headers_from_data()
        table_as_dict: OrderedDict = OrderedDict(
            [(str(col), OrderedDict({str(row): 0 for row in row_headers})) for col in col_headers]
        )

        for key, value in table_data.items():
            col_value, row_value = eval(key)
            table_as_dict[str(col_value)][str(row_value)] = value.get("count")

        return table_as_dict

    def as_dataframe(self):
        """
        Display the 2X2 table metric response as a pandas DataFrame.
        """
        try:
            import pandas as pd

            return pd.DataFrame(self.as_table())
        except ImportError:
            raise ImportError("Can not return table as dataframe, package pandas is not installed.")

    def risk(self, detected_column_name=None, exposed_column_name=None):
        detected_column_name = (
            detected_column_name
            or self._metric_configuration_dict_arguments["detected_column_name"]
        )
        exposed_column_name = (
            exposed_column_name or self._metric_configuration_dict_arguments["exposed_column_name"]
        )
        risk_config = Risk(
            detected_column_name=detected_column_name,
            exposed_column_name=exposed_column_name,
            group_by=self._metric_configuration_dict_arguments.get("group_by"),
            data_filters=self._metric_configuration_dict_arguments.get("data_filters"),
        )
        return get_cloud_aggregated_metric_data(self.session, self.dataset_uids, risk_config)

    def risk_ratio(self, detected_column_name=None, exposed_column_name=None):
        detected_column_name = (
            detected_column_name
            or self._metric_configuration_dict_arguments["detected_column_name"]
        )
        exposed_column_name = (
            exposed_column_name or self._metric_configuration_dict_arguments["exposed_column_name"]
        )
        risk_ratio_config = RiskRatio(
            detected_column_name=detected_column_name,
            exposed_column_name=exposed_column_name,
            group_by=self._metric_configuration_dict_arguments.get("group_by"),
            data_filters=self._metric_configuration_dict_arguments.get("data_filters"),
        )
        return get_cloud_aggregated_metric_data(self.session, self.dataset_uids, risk_ratio_config)

    def odds(self, column_name):
        odds_config = Odds(
            column_name=column_name,
            group_by=self._metric_configuration_dict_arguments.get("group_by"),
            data_filters=self._metric_configuration_dict_arguments.get("data_filters"),
        )
        return get_cloud_aggregated_metric_data(self.session, self.dataset_uids, odds_config)

    def odds_ratio(self, detected_column_name=None, exposed_column_name=None):
        detected_column_name = (
            detected_column_name
            or self._metric_configuration_dict_arguments["detected_column_name"]
        )
        exposed_column_name = (
            exposed_column_name or self._metric_configuration_dict_arguments["exposed_column_name"]
        )
        odds_config = OddsRatio(
            detected_column_name=detected_column_name,
            exposed_column_name=exposed_column_name,
            group_by=self._metric_configuration_dict_arguments.get("group_by"),
            data_filters=self._metric_configuration_dict_arguments.get("data_filters"),
        )
        return get_cloud_aggregated_metric_data(self.session, self.dataset_uids, odds_config)
