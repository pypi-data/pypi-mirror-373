"""Entry point to using the Rhino Health Python SDK."""

__version__ = "2.1.5"

import sys
from typing import Optional

import requests

# Expose this for users to catch on
from ratelimit import RateLimitException

import rhino_health.lib.endpoints
import rhino_health.lib.metrics
from rhino_health.lib.constants import ApiEnvironment
from rhino_health.lib.rest_api.rhino_authenticator import AuthenticationDetailType
from rhino_health.lib.rhino_client import SDKVersion
from rhino_health.lib.rhino_session import RhinoSession

# Which modules to autogenerate documentation for
__api__ = [
    "rhino_health.lib.metrics",
    "rhino_health.lib.endpoints",
    "rhino_health.lib.constants",
    "rhino_health.lib.rhino_session",
    "rhino_health.lib.rest_api",
]


def _check_sdk_version():
    """
    Check the SDK is the latest version, if not let users know on login
    """
    try:
        response = requests.get("https://pypi.org/pypi/rhino_health/json")
        latest_version = response.json()["info"]["version"]
        if latest_version != __version__:
            print("You are not using the latest version of the Rhino SDK.")
            print(f"Latest version: {latest_version}")
            print(f"Current version: {__version__}")
            print("To upgrade, run: pip install --upgrade rhino_health")
    except Exception:
        # Don't pollute the user logs if PyPI fails
        pass


def _get_sdk_environment():
    """
    @autoapi False
    Returns the library versions to Rhino Health in order to know if any users are using older versions
    """
    # On purpose do not expose these as exported at the module level so users do not accidentally get wrong version
    from importlib.metadata import version

    dependencies = [  # Note this needs to be kept in sync with pyproject.toml
        "arrow",
        "backoff",
        "funcy",
        "pydantic",
        "ratelimit",
        "requests",
        "typing-extensions",
    ]
    version_report = {}
    for library in dependencies:
        try:
            version_report[library] = version(library)
        except Exception as e:
            version_report[library] = f"Unknown (error={e})"
    version_report["python"] = sys.version
    version_report["platform"] = sys.platform
    return version_report


def _report_sdk_environment(session):
    try:
        sdk_environment = _get_sdk_environment()
        session.user.report_sdk_environment(sdk_environment)
    except:
        # Don't pollute the user logs if sdk environment call fails
        pass


def login(
    username: Optional[str] = None,
    password: Optional[str] = None,
    otp_code: Optional[str] = None,
    rhino_api_url: str = ApiEnvironment.PROD_API_URL,
    sdk_version: str = SDKVersion.STABLE,
    show_traceback: bool = False,
    authentication_details: Optional[AuthenticationDetailType] = None,
    accept_nonstandard_ssl_certs: bool = False,
) -> RhinoSession:
    """
    Login to the Rhino platform and get a RhinoSession to interact with the rest of the system.

    Parameters
    ----------
    username: Optional[str]
        The email you are logging in with if logging in with username/password. You must login with either username/password or authentication_details
    password: Optional[str]
        The password you are logging in with if logging in with username/password You must login with either username/password or authentication_details
    authentication_details: Optional[AuthenticationDetailType]
        Dictionary of authentication information you are logging in with if not using username/password. Refer to Examples and See Also section
    otp_code: Optional[str]
        If 2FA is enabled for the account, the One Time Password code from your 2FA device
    rhino_api_url: str
        Which rhino environent you are working in.
    sdk_version: str
        Used internally for future backwards compatibility. Use the default
    show_traceback: bool
        Should traceback information be included if an error occurs
    accept_nonstandard_ssl_certs: bool
        If you are on a private environment behind an institution firewall that strips the SSL certificate from
        HTTPS calls and re-encrypts with your corporate SSL and you cannot get REQUESTS_CA_BUNDLE to work

    Returns
    -------
    session: RhinoSession
        A session object to interact with the cloud API

    Examples
    --------
    >>> import rhino_health
    >>> my_username = "user@example.com"  # Replace me
    >>> my_password = "Correct horse battery staple"  # Replace me (see https://xkcd.com/936/)
    >>> session = rhino_health.login(username=my_username, password=my_password, otp_code=otp_code)
    RhinoSession()

    >>> import rhino_health
    >>> session = rhino_health.login(authentication_details={"sso_access_token": "MyAccessToken", "sso_provider": "google", "sso_client": "my_hospital"})
    RhinoSession()

    >>> import rhino_health
    >>> session = rhino_health.login(authentication_details={"sso_access_token": "MyAccessToken", "sso_id_token": "MyIdToken", "sso_provider": "azure_ad"})
    RhinoSession()

    >>> session_info = my_previous_session.session_info()
    >>> session = rhino_health.login(authentication_details=session_info)
    RhinoSession()

    See Also
    --------
    rhino_health.lib.constants.ApiEnvironment : List of supported environments
    rhino_health.lib.rhino_session.RhinoSession : Session object with accessible endpoints
    rhino_health.lib.rest_api.rhino_authenticator.AuthenticationDetailType: Authentication detail dictionary for login
    """
    if username and password and not authentication_details:
        authentication_details = {"email": username, "password": password}
    _check_sdk_version()
    session = RhinoSession(
        authentication_details,
        otp_code,
        rhino_api_url,
        sdk_version,
        show_traceback,
        accept_nonstandard_ssl_certs,
    )
    _report_sdk_environment(session)
    return session
