from typing import Dict, Optional

from rhino_health.lib.constants import ApiEnvironment
from rhino_health.lib.rest_api.error_handler import ErrorHandler
from rhino_health.lib.rest_api.rhino_authenticator import (
    AuthenticationDetailType,
    RhinoAuthenticator,
)
from rhino_health.lib.rest_api.standard_format_adapter import StandardFormatAdapter
from rhino_health.lib.rest_handler import RequestDataType, RestHandler
from rhino_health.lib.rhino_client import RhinoClient, SDKVersion
from rhino_health.lib.rhino_cloud import RhinoCloud
from rhino_health.lib.utils import rhino_error_wrapper


# Class docstring in rhino_client for autodoc
class RhinoSession(RhinoClient):
    @rhino_error_wrapper
    def __init__(
        self,
        authentication_details: Optional[AuthenticationDetailType] = None,
        otp_code: Optional[str] = None,
        rhino_api_url: str = ApiEnvironment.PROD_API_URL,
        sdk_version: str = SDKVersion.STABLE,
        show_traceback: bool = False,
        accept_nonstandard_ssl_certs: bool = False,
    ):
        super().__init__(
            rhino_api_url=rhino_api_url, sdk_version=sdk_version, show_traceback=show_traceback
        )
        self.authenticator = RhinoAuthenticator(
            self.api_url, authentication_details, otp_code, accept_nonstandard_ssl_certs
        )
        self.login()
        self.rest_adapter = RestHandler(
            session=self,
            base_url=self.api_url,
            adapters={
                self.authenticator.__class__.__name__: self.authenticator,
                StandardFormatAdapter.__name__: StandardFormatAdapter(),
                ErrorHandler.__name__: ErrorHandler(),
            },
        )
        self._current_user = None
        self.rhino_cloud = RhinoCloud(rhino_api_url)
        self.accept_nonstandard_ssl_certs = accept_nonstandard_ssl_certs

    def login(self):
        """
        @autoapi False
        Login to the Rhino Cloud API. Called automatically on initialization
        """
        self.authenticator.authenticate()

    def switch_user(self, authentication_details, otp_code=None):
        """
        Switch the currently logged in user.

        Parameters
        ----------
        authentication_details: AuthenticationDetailType
            A dictionary containing authentication details
        otp_code: Optional[str]
            2FA login code if 2FA is enabled for the account

        See Also
        --------
        rhino_health.lib.rest_api.rhino_authenticator.AuthenticationDetailType: AuthenticationDetailType
        """
        new_authenticator = RhinoAuthenticator(
            self.api_url, authentication_details, otp_code, self.accept_nonstandard_ssl_certs
        )
        self.login()
        self.authenticator = new_authenticator
        self.rest_adapter.adapters[self.authenticator.__class__.__name__] = self.authenticator
        self._current_user = None

    @property
    def current_user(self):
        """
        Returns the logged in user
        """
        if not self._current_user:
            self._current_user = self.user.get_logged_in_user()
        return self._current_user

    def session_info(self):
        """
        Returns a dictionary containing session info that can be persisted and passed to a future rhino session object
        """
        return self.authenticator.session_info()

    def get_container_image_uri(self, image_tag: str, rhino_common_image: bool = False) -> str:
        """
        Get the container image URI for a specific image tag in the Workgroup's image repo or in the common Rhino image repo

        Parameters
        ----------
        image_tag: str
            The tag of the image
        rhino_common_image: bool
            Whether the image is a Rhino common image

        Returns
        -------
        container_uri: str
            The container image URI
        """
        if rhino_common_image:
            return self.rhino_cloud.get_container_image_uri(
                "rhino-gc-workgroup-rhino-health", image_tag
            )
        user = self.current_user
        workgroup = user.primary_workgroup
        if not workgroup.image_repo_name:
            raise ValueError(f"Workgroup '{workgroup.name}' does not have an image repo configured")
        workgroup_image_repo = f"rhino-gc-workgroup-{workgroup.image_repo_name}"
        return self.rhino_cloud.get_container_image_uri(workgroup_image_repo, image_tag)

    # These are just remappings for now until we need more complex stuff in future
    @rhino_error_wrapper
    def get(self, url: str, params: Optional[Dict] = None, adapter_kwargs: Optional[Dict] = None):
        """
        @autoapi False
        Low level interface for submitting a REST GET request.
        Intended For Internal Use

        Parameters
        ----------
        url: str
            The URL that you are hitting
        params: Optional[Dict]
            A dictionary of `query params <https://en.wikipedia.org/wiki/Query_string>`_ to send with the request
        adapter_kwargs: Optional[Dict]
            | (Advanced) a dictionary of additional kwargs to pass to the system
            | • accepted_status_codes List[int]: List of status codes to accept
            | • data_as_json: bool = True Pass the data attribute as a json to `requests <https://docs.python-requests.org/en/latest/>`_

        Examples
        --------
        >>> session.get("/alpha/secret/api").raw_response.json()
        { "status": "success" }

        Returns
        -------
        api_response: APIResponse
            Result of making the HTTP GET request

        See Also
        --------
        rhino_health.lib.rest_api.api_response.APIResponse: Response object
        """
        return self.rest_adapter.get(url=url, params=params, adapter_kwargs=adapter_kwargs)

    @rhino_error_wrapper
    def post(
        self,
        url: str,
        data: Optional[RequestDataType] = None,
        params: Optional[Dict] = None,
        adapter_kwargs: Dict = None,
    ):
        """
        @autoapi False
        Low level interface for submitting a REST POST request.
        Intended For Internal Use

        Parameters
        ----------
        url: str
            The URL that you are hitting
        data: Union[str, dict, list]
            The payload to include with the POST request
        params: Optional[Dict]
            A dictionary of `query params <https://en.wikipedia.org/wiki/Query_string>`_ to send with the request
        adapter_kwargs: Optional[Dict]
            | (Advanced) a dictionary of additional kwargs to pass to the system
            | • accepted_status_codes List[int]: List of status codes to accept
            | • data_as_json: bool = True Pass the data attribute as a json to `requests <https://docs.python-requests.org/en/latest/>`_


        Examples
        --------
        >>> session.post(
        ...   "/alpha/secret/api",
        ...   {"arbitrary_payload": "value"}
        ... ).raw_response.json()
        { "status": "success" }

        Returns
        -------
        api_response: APIResponse
            Result of making the HTTP Post request

        See Also
        --------
        rhino_health.lib.rest_api.api_response.APIResponse: Response object
        """
        return self.rest_adapter.post(
            url=url,
            data=data,
            params=params,
            adapter_kwargs=adapter_kwargs,
        )

    @rhino_error_wrapper
    def delete(
        self,
        url: str,
        params: Optional[Dict] = None,
        adapter_kwargs: Dict = None,
    ):
        """
        @autoapi False
        Low level interface for submitting a REST POST request.
        Intended For Internal Use

        Parameters
        ----------
        url: str
            The URL that you are hitting
        params: Optional[Dict]
            A dictionary of `query params <https://en.wikipedia.org/wiki/Query_string>`_ to send with the request
        adapter_kwargs: Optional[Dict]
            | (Advanced) a dictionary of additional kwargs to pass to the system
            | • accepted_status_codes List[int]: List of status codes to accept
            | • data_as_json: bool = True Pass the data attribute as a json to `requests <https://docs.python-requests.org/en/latest/>`_


        Examples
        --------
        >>> session.delete(
        ...   "/alpha/secret/api",
        ... ).raw_response.json()
        { "status": "success" }

        Returns
        -------
        api_response: APIResponse
            Result of making the HTTP Post request

        See Also
        --------
        rhino_health.lib.rest_api.api_response.APIResponse: Response object
        """
        return self.rest_adapter.delete(
            url=url,
            params=params,
            adapter_kwargs=adapter_kwargs,
        )
