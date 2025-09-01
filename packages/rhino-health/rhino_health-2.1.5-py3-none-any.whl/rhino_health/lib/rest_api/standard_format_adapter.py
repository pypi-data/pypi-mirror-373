import logging
from typing import Dict

from rhino_health.lib.rest_api.api_request import APIRequest
from rhino_health.lib.rest_api.api_response import APIResponse
from rhino_health.lib.rest_api.request_adapter import RequestAdapter


class StandardFormatAdapter(RequestAdapter):
    """
    Handles the new standard response format from the BE
    """

    def after_request(
        self, api_request: APIRequest, api_response: APIResponse, adapter_kwargs: Dict
    ):
        try:
            json_response = api_response.parsed_response
            if "data" in json_response:
                api_response.parsed_response = json_response["data"]
            if "errors" in json_response:
                api_response.parsed_errors = json_response["errors"]
        except Exception:
            # Assume direct dataclass assignment downstream
            logging.warning(
                "Response is not in the new standard response format, falling back to legacy API handling"
            )
