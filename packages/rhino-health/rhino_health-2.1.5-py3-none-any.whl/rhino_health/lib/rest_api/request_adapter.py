from typing import Dict

from rhino_health.lib.rest_api.api_request import APIRequest
from rhino_health.lib.rest_api.api_response import APIResponse


class RequestAdapter:
    """
    Base class for a request adapter that handles custom logic before or after a request is made
    """

    def before_request(self, api_request: APIRequest, adapter_kwargs: Dict):
        return None

    def after_request(
        self, api_request: APIRequest, api_response: APIResponse, adapter_kwargs: Dict
    ):
        return None
