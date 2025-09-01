"""
Constants that are used in the rest of the system
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ApiEnvironment:
    """
    The Rhino Cloud API you are working with. You should usually be using PROD_AWS_URL or PROD_GCP_URL.

    Examples
    --------
    >>> from rhino_health import ApiEnvironment.PROD_AWS_URL
    """

    LOCALHOST_API_URL = "http://localhost:8080/api/"
    LOCALHOST_INTEGRATION_TESTS_URL = "http://web-service:8080/api/"  # Backwards Compat
    QA_AWS_URL = "https://qa-cloud.rhinohealth.com/api/"
    QA_URL = QA_AWS_URL  # Backwards Compat
    QA_GCP_URL = "https://qa-cloud.rhinofcp.com/api/"
    DEV1_AWS_URL = "https://dev1.rhinohealth.com/api/"
    DEV2_AWS_URL = "https://dev2.rhinohealth.com/api/"
    DEV3_AWS_URL = "https://dev3.rhinohealth.com/api/"
    DEV1_GCP_URL = "https://dev1.rhinofcp.com/api/"
    DEMO_DEV_URL = "https://demo-dev.rhinohealth.com/api/"
    DEMO_URL = "https://demo-prod.rhinohealth.com/api/"
    STAGING_AWS_URL = "https://staging.rhinohealth.com/api/"
    STAGING_GCP_URL = "https://staging.rhinofcp.com/api/"
    PROD_AWS_URL = "https://prod.rhinohealth.com/api/"
    PROD_API_URL = PROD_AWS_URL  # Backwards Compat
    PROD_GCP_URL = "https://prod.rhinofcp.com/api/"


class Dashboard:
    """
    @autoapi False Deprecated
    """

    LOCALHOST_URL = "http://localhost:3000"
    DEV_URL = "https://dev-dashboard.rhinohealth.com"
    DEV4_URL = "https://dev4-dashboard.rhinofcp.com"
    DEMO_DEV_URL = "https://demo-dev-dashboard.rhinohealth.com"
    DEMO_URL = "https://demo.rhinohealth.com"
    PROD_URL = "https://dashboard.rhinohealth.com"
    PROD_GCP_URL = "https://dashboard.rhinofcp.com"


class ECRService:
    """
    @autoapi False Deprecated
    """

    TEST_URL = "localhost:5201"
    LOCALHOST_URL = "localhost:5001"
    DEV_URL = "913123821419.dkr.ecr.us-east-1.amazonaws.com"
    DEMO_DEV_URL = "913123821419.dkr.ecr.us-east-1.amazonaws.com"
    DEMO_URL = "913123821419.dkr.ecr.us-east-1.amazonaws.com"
    PROD_URL = "913123821419.dkr.ecr.us-east-1.amazonaws.com"


class CloudProvider(str, Enum):
    """
    @autoapi False Internal dataclass
    """

    AWS = "aws"
    GCP = "gcp"


class EnvironmentData(BaseModel):
    """
    @autoapi False Internal dataclass
    """

    api: str
    dashboard: Optional[str] = None
    container_registry: str
    cloud_provider: str = CloudProvider.AWS


RHINO_CLOUD_ENVIRONMENTS_DATA = {
    ApiEnvironment.LOCALHOST_API_URL: EnvironmentData(
        api=ApiEnvironment.LOCALHOST_API_URL,
        dashboard="http://localhost:3000",
        container_registry="localhost:5001",
    ),
    ApiEnvironment.LOCALHOST_INTEGRATION_TESTS_URL: EnvironmentData(
        api=ApiEnvironment.LOCALHOST_INTEGRATION_TESTS_URL,
        dashboard="http://localhost:8080",
        container_registry="localhost:5201",
    ),
    ApiEnvironment.DEV1_AWS_URL: EnvironmentData(
        api=ApiEnvironment.DEV1_AWS_URL,
        dashboard="https://dev1-dashboard.rhinohealth.com",
        container_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com",
    ),
    ApiEnvironment.DEV2_AWS_URL: EnvironmentData(
        api=ApiEnvironment.DEV2_AWS_URL,
        dashboard="https://dev2-dashboard.rhinohealth.com",
        container_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com",
    ),
    ApiEnvironment.DEV3_AWS_URL: EnvironmentData(
        api=ApiEnvironment.DEV3_AWS_URL,
        dashboard="https://dev3-dashboard.rhinohealth.com",
        container_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com",
    ),
    ApiEnvironment.DEV1_GCP_URL: EnvironmentData(
        api=ApiEnvironment.DEV1_GCP_URL,
        dashboard="https://dev1-dashboard.rhinofcp.com",
        container_registry="europe-west4-docker.pkg.dev/rhino-health-dev",
        cloud_provider=CloudProvider.GCP,
    ),
    ApiEnvironment.DEMO_DEV_URL: EnvironmentData(
        api=ApiEnvironment.DEMO_DEV_URL,
        dashboard="https://demo-dev-dashboard.rhinohealth.com",
        container_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com",
    ),
    ApiEnvironment.QA_AWS_URL: EnvironmentData(
        api=ApiEnvironment.QA_AWS_URL,
        container_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com",
    ),
    ApiEnvironment.QA_GCP_URL: EnvironmentData(
        api=ApiEnvironment.QA_GCP_URL,
        container_registry="europe-west4-docker.pkg.dev/rhino-health-qa",
        cloud_provider=CloudProvider.GCP,
    ),
    ApiEnvironment.STAGING_AWS_URL: EnvironmentData(
        api=ApiEnvironment.STAGING_AWS_URL,
        dashboard="https://staging-dashboard.rhinohealth.com",
        container_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com",
    ),
    ApiEnvironment.STAGING_GCP_URL: EnvironmentData(
        api=ApiEnvironment.STAGING_GCP_URL,
        dashboard="https://staging-dashboard.rhinofcp.com",
        container_registry="europe-west4-docker.pkg.dev/rhino-health-prod",
        cloud_provider=CloudProvider.GCP,
    ),
    ApiEnvironment.PROD_AWS_URL: EnvironmentData(
        api=ApiEnvironment.PROD_AWS_URL,
        dashboard="https://dashboard.rhinohealth.com",
        container_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com",
    ),
    ApiEnvironment.PROD_GCP_URL: EnvironmentData(
        api=ApiEnvironment.PROD_GCP_URL,
        dashboard="https://dashboard.rhinofcp.com",
        container_registry="europe-west4-docker.pkg.dev/rhino-health-prod",
        cloud_provider=CloudProvider.GCP,
    ),
    ApiEnvironment.DEMO_URL: EnvironmentData(
        api=ApiEnvironment.DEMO_URL,
        dashboard="https://demo.rhinohealth.com",
        container_registry="913123821419.dkr.ecr.us-east-1.amazonaws.com",
    ),
}
"""
@autoapi False Internal dataclass
"""
