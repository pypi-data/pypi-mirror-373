import logging
from enum import Enum
from typing import Dict, Optional, Union

import arrow
import requests
from typing_extensions import TypeAliasType, TypedDict

from rhino_health.lib.rest_api.api_request import APIRequest
from rhino_health.lib.rest_api.api_response import APIResponse
from rhino_health.lib.rest_api.request_adapter import RequestAdapter
from rhino_health.lib.utils import url_for


class OauthProvider(Enum):
    """
    @autoapi True

    Which Oauth Provider are you logging in with
    """

    GOOGLE = "google"
    OKTA = "okta"


class SSOAuthenticationDetails(TypedDict):
    """
    @autoapi True

    Dictionary configuration for logging in with SSO
    """

    sso_access_token: str
    """The SSO Access Token, required for most SSO Flows"""
    sso_id_token: Optional[str]
    """The ID Token, optional for certain flows"""
    sso_provider: OauthProvider
    """Which SSO Provider are you logging in with"""
    sso_client: Optional[str]
    """Which SSO Client are you logging in with for client provided SSO Integrations"""


class UsernamePasswordAuthenticationDetail(TypedDict):
    """
    @autoapi True

    Dictionary configuration for logging into the platform
    """

    email: str
    """The email of the account you are logging in with"""
    password: str
    """The password of the account you are logging in with, if using password"""


class SessionAuthenticationDetail(TypedDict):
    """
    @autoapi True

    Configuration to resume an existing session
    """

    session_token: str
    """The session token"""
    session_timeout: str
    """When the session is valid until"""


AuthenticationDetailType = TypeAliasType(
    "AuthenticationDetailType",
    Union[
        SSOAuthenticationDetails, UsernamePasswordAuthenticationDetail, SessionAuthenticationDetail
    ],
)
"""
Union[SSOAuthenticationDetails, UsernamePasswordAuthenticationDetail, SessionAuthenticationDetail]
"""


class RhinoAuthenticator(RequestAdapter):
    """
    @autoapi False
    Keeps track of authenticating with our backend API
    """

    AUTHORIZATION_KEY = "authorization"
    UNAUTHENTICATED_STATUS_CODE = 401
    DEFAULT_MAX_RETRY_COUNT = 2

    def __init__(
        self,
        base_url: str,
        authentication_details: Optional[AuthenticationDetailType] = None,
        otp_code: Optional[str] = None,
        accept_nonstandard_ssl_certs: bool = False,
        max_retry_count: int = DEFAULT_MAX_RETRY_COUNT,
    ):
        # TODO: Include active_workgroup in the future
        self.base_url = base_url
        self.authentication_details = authentication_details or {}
        self.otp_code = otp_code
        self.accept_nonstandard_ssl_certs: bool = accept_nonstandard_ssl_certs
        self.max_retry_count = max_retry_count
        self.login_token: Optional[str] = None
        self.login_timeout: Optional[arrow.Arrow] = None
        self.refresh_token: Optional[str] = None
        self.refresh_timeout: Optional[arrow.Arrow] = None

    @property
    def email(self) -> Union[str, None]:
        """@autoapi False"""
        return self.authentication_details.get("email", None)

    @property
    def password(self) -> Union[str, None]:
        """@autoapi False"""
        return self.authentication_details.get("password", None)

    @property
    def session_token(self) -> Union[str, None]:
        """@autoapi False"""
        return self.authentication_details.get("session_token", None)

    @property
    def session_timeout(self) -> Union[str, None]:
        """@autoapi False"""
        return self.authentication_details.get("session_timeout", None)

    def session_info(self):
        """@autoapi False"""
        try:
            return {
                "session_token": self.refresh_token,
                "session_timeout": str(self.refresh_timeout.timestamp()),
            }
        except:
            raise RuntimeError("No session available")

    @property
    def sso_access_token(self) -> Union[str, None]:
        """@autoapi False"""
        return self.authentication_details.get("sso_access_token", None)

    @property
    def sso_id_token(self) -> Union[str, None]:
        """@autoapi False"""
        return self.authentication_details.get("sso_id_token", None)

    @property
    def sso_provider(self) -> Union[str, None]:
        """@autoapi False"""
        return self.authentication_details.get("sso_provider", None)

    @property
    def sso_client(self) -> Union[str, None]:
        """@autoapi False"""
        return self.authentication_details.get("sso_client", None)

    @property
    def _is_mock_session(self) -> bool:
        return self.authentication_details.get("__mock", False)

    @property
    def _is_using_username_and_password(self) -> bool:
        return bool(self.email and self.password)

    @property
    def _is_using_sso(self):
        return (self.sso_access_token or self.sso_id_token) and self.sso_provider

    @property
    def _is_resuming_session(self):
        return bool(self.session_token and self.session_timeout)

    def _login(self):
        if (
            not self._is_mock_session
            and not self._is_using_username_and_password
            and not self._is_using_sso
            and not self._is_resuming_session
        ):
            raise RuntimeError(
                "Must provide a valid authentication: password, sso, or session information"
            )
        if self._is_mock_session:
            return
        elif self._is_using_sso:
            self._login_via_sso()
        elif self._is_using_username_and_password:
            self._login_via_username_password()
        elif self._is_resuming_session:
            self._login_via_resuming_session()
        else:
            raise RuntimeError("Unsupported authentication method")

    def _save_rhino_auth_token(self, raw_response):
        # TODO: Parse timeout hours from the token instead of hardcode
        self.login_token = raw_response["access"]
        self.login_timeout = arrow.utcnow().shift(minutes=5)
        self.refresh_token = raw_response["refresh"]
        self.refresh_timeout = arrow.utcnow().shift(hours=10)

    def _login_via_username_password(self):
        data = {"email": self.email, "password": self.password}
        if self.otp_code:
            data["otp_code"] = self.otp_code
        request_params = {"url": url_for(self.base_url, "auth/obtain_token"), "data": data}
        if self.accept_nonstandard_ssl_certs:
            request_params["verify"] = False
        raw_response = requests.post(**request_params)
        response = raw_response.json()
        if "access" in response:
            self._save_rhino_auth_token(response)
        else:
            errors = response.get("errors", [])
            error_message = errors[0].get("message", None) if errors else None
            if error_message:
                raise Exception(f"Failed to authenticate: {error_message}")
            elif isinstance(raw_response, str):
                raise Exception(raw_response)
            else:
                raise Exception(f"Error occurred trying to authenticate: {raw_response.text}")

    def _login_via_sso(self):
        data = {"response": {"token": self.sso_access_token}, "provider": self.sso_provider}
        if self.email:
            data["response"]["email"] = self.email
        if self.sso_id_token:
            data["response"]["id_token"] = self.sso_id_token
        if self.sso_client:
            data["client"] = self.sso_client
        try:
            request_params = {"url": url_for(self.base_url, "auth/oauth_token"), "json": data}
            if self.accept_nonstandard_ssl_certs:
                request_params["verify"] = False
            raw_response = requests.post(**request_params).json()
            if "access" in raw_response:
                self._save_rhino_auth_token(raw_response)
            else:
                raise Exception(raw_response.get("detail", "Error occurred trying to connect"))
        except:
            raise Exception("Unable to authenticate, please check your credentials")

    def _login_via_resuming_session(self):
        self.refresh_token = self.session_token
        self.refresh_timeout = arrow.Arrow.utcfromtimestamp(float(self.session_timeout))
        self._refresh_token()

    def _refresh_token(self):
        request_params = {
            "url": url_for(self.base_url, "auth/refresh_token"),
            "data": {"refresh": self.refresh_token},
        }
        if self.accept_nonstandard_ssl_certs:
            request_params["verify"] = False
        raw_response = requests.post(**request_params).json()
        self.login_token = raw_response.get("access")
        if not self.login_token:
            raise ValueError(
                "Invalid authentication information. Please reauthenticate to continue."
            )
        self.login_timeout = arrow.utcnow().shift(minutes=5)

    def _should_reauthenticate(self):
        return (self.login_token is None) or (arrow.utcnow() > self.login_timeout)

    def _can_refresh(self):
        refresh_expired = (self.refresh_timeout is None) or (arrow.utcnow() > self.refresh_timeout)
        return self._refresh_token is not None and not refresh_expired

    def authenticate(self):
        if self._can_refresh():
            self._refresh_token()
        else:
            self._login()

    def before_request(self, api_request: APIRequest, adapter_kwargs: Dict):
        if self._should_reauthenticate():
            self.authenticate()
        api_request.headers[self.AUTHORIZATION_KEY] = f"Bearer {self.login_token}"

    def after_request(
        self, api_request: APIRequest, api_response: APIResponse, adapter_kwargs: Dict
    ):
        unauthenticated = api_response.status_code == self.UNAUTHENTICATED_STATUS_CODE
        retry_allowed = api_request.request_count <= self.max_retry_count
        if unauthenticated and retry_allowed:
            api_request.request_status = APIRequest.RequestStatus.RETRY
            logging.debug("Refreshing login token")
            self.authenticate()
            api_request.request_count += 1
        return
