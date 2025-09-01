from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, field_validator


class FilterType(Enum):
    """
    Enum/Constants to specify the type of filtering to perform. Supported filtering methods are listed below
    """

    EQUAL = "="
    IN = "in"
    """
    Filter data

    Notes
    -----
    filter_value should be a list which can be checked against using `pd.Series.isin() <https://pandas.pydata.org/docs/reference/api/pandas.Series.isin.html>`_
    """
    NOT_IN = "not in"
    """
    Filter data

    Notes
    -----
    filter_value should be a list which can be checked against using `pd.Series.isin() <https://pandas.pydata.org/docs/reference/api/pandas.Series.isin.html>`_
    """
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_EQUAL = ">="
    LESS_THAN_EQUAL = "<="
    BETWEEN = "between"  # 2 conditions are specified and checked against


class FilterRangePair(BaseModel):
    """
    Specifies the upper or lower range to check against when using ranges instead of a fixed number
    """

    filter_value: Any
    filter_type: FilterType
    """
    .. warning:: FilterType.BETWEEN and FilterType.IN are not supported in FilterRangePair
    """

    @field_validator("filter_type")
    @classmethod
    def only_base_operator_types(cls, value):
        """
        @autoapi False
        """
        if value not in [
            FilterType.EQUAL,
            FilterType.GREATER_THAN,
            FilterType.GREATER_THAN_EQUAL,
            FilterType.LESS_THAN,
            FilterType.LESS_THAN_EQUAL,
        ]:
            raise ValueError("Only base types are supported for ranges")


class FilterBetweenRange(BaseModel):
    """
    Specifies the upper and lower range to check against when using ranges instead of a fixed number
    """

    lower: FilterRangePair  # A dict that defines the filter variable for the lower range
    upper: FilterRangePair  # A dict that defines the filter variable for the upper range


class FilterVariable(BaseModel):
    """
    Defines filter logic to compare data against.
    """

    data_column: str
    """The column in the remote Dataset df to get data from after filtering"""
    filter_column: str
    """The column in the remote Dataset df to check against"""
    filter_value: Union[Any, FilterBetweenRange]
    """The value to match against or a FilterBetweenRange if filter_type is FilterType.BETWEEN"""
    filter_type: Optional[FilterType] = FilterType.EQUAL
    """The type of filtering to perform. Defaults to FilterType.EQUAL"""


FilterVariableTypeOrColumnName = Union[str, FilterVariable]
"""
Either a string or a FilterVariable. Union[str, FilterVariable]

See Also
--------
rhino_health.lib.metrics.filter_variable.FilterVariable
"""
