from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional


class NameFilterMode(Enum):
    """
    The mode to filter the objects name in
    """

    EXACT = "iexact"
    CONTAINS = "icontains"


class VersionMode(str, Enum):
    """
    The version of the object to filter on
    """

    LATEST = "latest"
    ALL = "all"


class Endpoint(ABC):
    def __init__(self, session):
        self.session = session

    def _get_filter_query_params(
        self, direct_arguments: Dict[str, Any], name_filter_mode: Optional[NameFilterMode] = None
    ):
        query_params = {k: v for k, v in direct_arguments.items() if v is not None}
        if name_filter_mode is not None and query_params:
            query_params["name_filter_mode"] = name_filter_mode.value
        return query_params

    @classmethod
    @abstractmethod
    def _endpoint_name(cls):
        """
        @autoapi False
        """
        raise NotImplementedError
