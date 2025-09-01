from .constants import RHINO_CLOUD_ENVIRONMENTS_DATA, CloudProvider


class RhinoCloud:
    def __init__(self, rhino_api_url):
        if rhino_api_url not in RHINO_CLOUD_ENVIRONMENTS_DATA:
            raise ValueError(f"Invalid Rhino API URL: {rhino_api_url}")
        self.rhino_cloud_data = RHINO_CLOUD_ENVIRONMENTS_DATA[rhino_api_url]

    def get_api_url(self):
        return self.rhino_cloud_data.api

    def get_dashboard_url(self):
        return self.rhino_cloud_data.dashboard

    def get_container_image_uri(self, workgroup_repo_name, image_tag):
        if self.rhino_cloud_data.cloud_provider == CloudProvider.AWS:
            return f"{self.rhino_cloud_data.container_registry}/{workgroup_repo_name}:{image_tag}"
        elif self.rhino_cloud_data.cloud_provider == CloudProvider.GCP:
            return f"{self.rhino_cloud_data.container_registry}/{workgroup_repo_name}/images:{image_tag}"
        else:
            raise ValueError(f"Unsupported cloud provider: {self.rhino_cloud_data.cloud_provider}")
