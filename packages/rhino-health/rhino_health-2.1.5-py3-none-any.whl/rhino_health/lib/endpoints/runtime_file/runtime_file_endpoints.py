from rhino_health.lib.endpoints.endpoint import Endpoint
from rhino_health.lib.endpoints.runtime_file.runtime_file_dataclass import (
    RuntimeFileNodeResponse,
    RuntimeFilePublishInput,
)
from rhino_health.lib.utils import rhino_error_wrapper


class RuntimeFileEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints to interact with runtime files
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "runtime_file"

    @rhino_error_wrapper
    def publish(self, runtime_file_publish_params: RuntimeFilePublishInput):
        """
        Makes the runtime file published in the desired project, and visible to users within the project.
        """
        return self.session.post(
            f"/runtime_files/publish",
            runtime_file_publish_params.model_dump(by_alias=True),
        ).no_dataclass_response()

    @rhino_error_wrapper
    def unpublish_runtime_file(self, runtime_file_publish_params: RuntimeFilePublishInput):
        """
        Makes this runtime file unpublished so users from other workgroups no longer see it.
        """
        return self.session.post(
            f"/runtime_files/unpublish", runtime_file_publish_params.model_dump(by_alias=True)
        ).no_dataclass_response()

    @rhino_error_wrapper
    def get_runtime_files(self, project_uid: str, include_collaborator_files: bool = False):
        """
        Get the runtime files of the project, includes the user's workgroup files,
        and if include_collaborator_files then published files from other workgroups as well.
        """
        result = self.session.get(
            "/runtime_files/get_runtime_files",
            params={
                "project_uid": project_uid,
                "include_collaborator_files": include_collaborator_files,
            },
        )
        return result.to_dataclass(RuntimeFileNodeResponse)
