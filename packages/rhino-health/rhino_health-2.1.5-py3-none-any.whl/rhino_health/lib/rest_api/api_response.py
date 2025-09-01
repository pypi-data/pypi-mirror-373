from typing import Callable, List, Type, TypeVar
from warnings import warn

from rhino_health.lib.rest_api.error_parsers.error_parser import ErrorParser
from rhino_health.lib.rest_api.error_parsers.eula import EULAErrorParser
from rhino_health.lib.rest_api.error_parsers.general_error import GeneralErrorParser
from rhino_health.lib.rest_api.error_parsers.reverse_rpc import ReverseRPCErrorParser

ERROR_PARSERS: List[ErrorParser] = [
    EULAErrorParser(),
    ReverseRPCErrorParser(),
    GeneralErrorParser(),
]


class APIResponse:
    """
    An internal representation of a HTTP response from the cloud API

    Attributes
    ----------
    session: RhinoSession
        The RhinoSession that triggered this request
    status_code: int
        The status code of the response
    """

    """
    Internal docs:
    raw_response: requests.Response
    A `requests.Response <https://docs.python-requests.org/en/latest/api/#requests.Response>`_ object.
    parsed_response: JSON like object
    """

    def __init__(self, session, request_response, api_request):
        self.session = session
        self.raw_response = request_response
        self.status_code = self.raw_response.status_code
        try:
            self.parsed_response = self.raw_response.json()
        except:
            self.parsed_response = self.raw_response
        self.parsed_errors = []
        self.api_request = api_request
        self.trace_id = self.raw_response.headers.get("X-Trace-Id", "")

    Dataclass = TypeVar("Dataclass")
    """
    A Type Hint representing a Dataclass in the system.
    
    Notes
    -----
    Dataclasses are how we represent input and output objects in the SDK. They provide validation,
    and convenience functions for you to interact with the objects. Example dataclasses include our metrics
    as well as various endpoint dataclasses.
    
    All SDK dataclasses extend `pydantic <https://pydantic-docs.helpmanual.io/>`_ and have access to functionality
    found within the library.

    See Also
    --------
    rhino_health.lib.endpoints.dataset.dataset_dataclass : Example Dataset dataclass
    """

    @property
    def request_status(self):
        return self.api_request.request_status

    def _accepted_fields_for(self, dataclass):
        accepted_fields = list(dataclass.__fields__.keys())
        uid_remap = {field[:-4]: field for field in accepted_fields if field.endswith("_uid")}
        accepted_fields.extend(uid_remap.keys())
        return accepted_fields, uid_remap

    def _response(self):
        """
        @autoapi False
        Convenience function that returns itself but also performs error checks
        """
        if self._request_failed():
            self.parse_and_raise_exception(None)
        return self

    def _to_dataclass(self, dataclass, data):
        dataclass = dataclass(session=self.session, **data)
        dataclass._persisted = True
        if hasattr(dataclass, "_trace_id"):
            dataclass._trace_id = self.trace_id
        return dataclass

    def no_dataclass_response(self):
        """
        Placeholder function for endpoints that need to return something with no well defined dataclass
        """
        warn(
            "The return result of the function you called will change in the future once a dataclass is defined",
            DeprecationWarning,
        )
        if self.parsed_errors:
            self.parse_and_raise_exception(None)
        else:
            return self.parsed_response

    def to_dataclass(
        self, dataclass: Type[Dataclass], format_response_function: Callable = None
    ) -> Dataclass:
        """
        Convenience class to convert the cloud API response to an expected Dataclass
        """
        try:
            json_response = self.parsed_response
            if format_response_function is not None:
                json_response = format_response_function(json_response)
            if not isinstance(json_response, dict):
                raise RuntimeError(
                    f"Response format does not match expected format for {dataclass.__name__} {self.trace_id}"
                )
            return self._to_dataclass(dataclass, json_response)
        except Exception as e:
            self.parse_and_raise_exception(e)

    def to_dataclasses(
        self, dataclass: Type[Dataclass], format_response_function: Callable = None
    ) -> List[Dataclass]:
        """
        Convenience class to convert the cloud API response to multiple expected Dataclasses
        """
        try:
            json_response = self.parsed_response
            if not isinstance(json_response, list):
                raise RuntimeError(
                    f"Response format does not match expected format for {dataclass.__name__} {self.trace_id}"
                )
            if format_response_function is not None:
                json_response = list(map(format_response_function, json_response))
            if not all(isinstance(item, dict) for item in json_response):
                raise RuntimeError(
                    f"Response format does not match expected format for {dataclass.__name__} {self.trace_id}"
                )
            return [self._to_dataclass(dataclass, data) for data in json_response]
        except Exception as e:
            self.parse_and_raise_exception(e)

    def _request_failed(self):
        from rhino_health.lib.rest_api.api_request import APIRequest

        return self.api_request.request_status == APIRequest.RequestStatus.FAILED

    def _get_error_messages(self):
        """
        Returns human readable error messages based on the error parsers for this request
        # TODO: Allow override per endpoint for additional error parsers if required
        """
        errors = []
        for error_parser in ERROR_PARSERS:
            parsed_error = error_parser.parse(self)
            if parsed_error:
                errors.extend(parsed_error)
        return ",".join(errors)

    def parse_and_raise_exception(self, e):
        """
        @autoapi False
        Parses the error message to return a more human readable exception
        """
        message = self._get_error_messages()
        raise Exception(
            f"Failed to make request\nStatus is {self.status_code}, Trace Id: {self.trace_id}, Errors: {message}, Content is {self.raw_response.content}\n{'' if e is None else 'Exception is ' + str(e)}"
        )
