from enum import Enum

import requests

from rhino_health.lib.rest_api.api_response import APIResponse
from rhino_health.lib.utils import url_for


class APIRequest:
    class RequestStatus(Enum):
        PENDING = "pending"
        SUCCESS = "success"
        FAILED = "failed"
        RETRY = "retry"

    def __init__(self, session, method, base_url, url, params, data):
        self.session = session
        self.method = method
        self.base_url = base_url
        self.url = url
        self.params = params or {}
        self.data = data
        self.headers = {"RHINO-REQUEST-SOURCE-SUBSYSTEM": "RHINO-SDK", "Referer": "rhino_sdk"}
        self.request_status = self.__class__.RequestStatus.PENDING
        self.request_count = 0

    def make_request(self, adapter_kwargs) -> APIResponse:
        url = url_for(self.base_url, self.url)
        request_args = {
            "method": self.method,
            "url": url,
            "params": self.params,
            "headers": self.headers,
        }
        if adapter_kwargs.get("data_as_json", True):
            request_args["json"] = self.data
        else:
            request_args["data"] = self.data
        if self.session.accept_nonstandard_ssl_certs:
            request_args["verify"] = False
        raw_response = requests.request(**request_args)
        self.request_count += 1
        return APIResponse(self.session, raw_response, self)

    @property
    def pending(self):
        return self.request_status in [
            self.__class__.RequestStatus.PENDING,
            self.__class__.RequestStatus.RETRY,
        ]
