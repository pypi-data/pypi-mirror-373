from typing import Dict, Optional, Union

from backoff import expo, on_exception
from ratelimit import RateLimitException, limits

from rhino_health.lib.constants import ApiEnvironment
from rhino_health.lib.rest_api.api_request import APIRequest
from rhino_health.lib.rest_api.api_response import APIResponse
from rhino_health.lib.rest_api.request_adapter import RequestAdapter

RequestDataType = Union[str, dict, list]
AdapterTableType = Dict[str, RequestAdapter]


class RestHandler:
    """
    @autoapi False
    """

    def __init__(
        self,
        session,
        base_url: str = ApiEnvironment.LOCALHOST_API_URL,
        adapters: AdapterTableType = None,
    ):
        self.session = session
        self.adapters: AdapterTableType = adapters
        self.base_url = base_url

    def get(
        self, url: str, params: Optional[Dict] = None, adapter_kwargs: Optional[Dict] = None
    ) -> APIResponse:
        return self._make_request(
            method="get",
            base_url=self.base_url,
            url=url,
            params=params,
            data=None,
            adapter_kwargs=adapter_kwargs,
        )

    # Note the ordering is different from get as data is more often used in post requests.
    def post(
        self,
        url: str,
        data: Optional[RequestDataType] = None,
        params: Optional[Dict] = None,
        adapter_kwargs: Optional[Dict] = None,
    ) -> APIResponse:
        return self._make_request(
            method="post",
            base_url=self.base_url,
            url=url,
            params=params,
            data=data,
            adapter_kwargs=adapter_kwargs,
        )

    def delete(
        self, url: str, params: Optional[Dict] = None, adapter_kwargs: Optional[Dict] = None
    ) -> APIResponse:
        return self._make_request(
            method="delete",
            base_url=self.base_url,
            url=url,
            params=params,
            data=None,
            adapter_kwargs=adapter_kwargs,
        )

    # def _ensure_json(self, payload: Union[str, dict, list]) -> str:
    #     if isinstance(payload, (dict, list)):
    #         return json.dumps(payload)
    #     return payload

    @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=15, period=2)
    def _make_request(
        self,
        method: str,
        base_url: str,
        url: str,
        params: Optional[Dict],
        data: Optional[RequestDataType],
        adapter_kwargs: Optional[Dict],
    ) -> APIResponse:
        # TODO: Automatic retry and backoff
        request = APIRequest(
            session=self.session,
            method=method,
            base_url=base_url,
            url=url,
            params=params,
            data=data,
        )
        adapter_kwargs = adapter_kwargs or {}
        response = None
        # TODO: Max request count prevent endless loops
        while request.pending:
            for adapter in self.adapters.values():
                adapter.before_request(request, adapter_kwargs)
            request.request_status = APIRequest.RequestStatus.PENDING
            response = request.make_request(adapter_kwargs)
            for adapter in self.adapters.values():
                adapter.after_request(request, response, adapter_kwargs)
        return response._response()
