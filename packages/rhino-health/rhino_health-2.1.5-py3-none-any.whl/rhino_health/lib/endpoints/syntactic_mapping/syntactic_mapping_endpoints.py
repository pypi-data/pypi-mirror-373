from typing import Union

from rhino_health.lib.endpoints.endpoint import Endpoint
from rhino_health.lib.endpoints.syntactic_mapping.syntactic_mapping_dataclass import (
    DataHarmonizationRunInput,
    SyntacticMapping,
    SyntacticMappingCreateInput,
)
from rhino_health.lib.utils import rhino_error_wrapper

BUFFER_TIME_IN_SEC = 300
"""
@autoapi False"""


class SyntacticMappingEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints to interact with syntactic mappings
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "syntactic_mapping"

    @property
    def syntactic_mapping_dataclass(self):
        """
        @autoapi False
        :return:
        """
        return SyntacticMapping

    @rhino_error_wrapper
    def create_syntactic_mapping(self, syntactic_mapping_input: SyntacticMappingCreateInput):
        """
        @autoapi True
        Create a SyntacticMapping on the Rhino Health Platform

        Parameters
        ----------
        syntactic_mapping_input: SyntacticMappingCreateInput
            Input arguments for the SyntacticMapping to create

        Returns
        -------
        syntactic_mapping: SyntacticMapping
            A response object containing the created SyntacticMapping
        """
        data = syntactic_mapping_input.dict(by_alias=True)
        result = self.session.post(
            "/syntactic_mappings",
            data=data,
        )
        return result.to_dataclass(self.syntactic_mapping_dataclass)

    @rhino_error_wrapper
    def get_syntactic_mapping(self, syntactic_mapping_or_uid: Union[str, SyntacticMapping]):
        """
        @autoapi True
        Get a SyntacticMapping on the Rhino Health Platform

        Parameters
        ----------
        syntactic_mapping_or_uid: Union[str, SyntacticMapping]
            The SyntacticMapping object or the UID

        Returns
        -------
        syntactic_mapping: SyntacticMapping
            A response object containing the syntactic mapping
        """
        result = self.session.get(
            f"/syntactic_mappings/{syntactic_mapping_or_uid if isinstance(syntactic_mapping_or_uid, str) else syntactic_mapping_or_uid.uid}"
        )
        return result.to_dataclass(self.syntactic_mapping_dataclass)

    def run_data_harmonization(
        self,
        syntactic_mapping_or_uid: Union[str, SyntacticMapping],
        run_params: DataHarmonizationRunInput,
    ):
        """
        @autoapi True
        Run a data harmonization code object

        Parameters
        ----------
        syntactic_mapping_or_uid: Union[str, SyntacticMapping]
            The uid of the syntactic mapping or the syntactic mapping object itself
        run_params: DataHarmonizationRunInput
            Parameters for running data harmonization for this code object

        Returns
        -------
        code_object_response: CodeObjectRunAsyncResponse
            Asynchronous run response object similar to a Promise. Call code_object_response.code_run to wait for the response.
        """
        syntactic_mapping = (
            self.get_syntactic_mapping(syntactic_mapping_or_uid)
            if isinstance(syntactic_mapping_or_uid, str)
            else syntactic_mapping_or_uid
        )
        return self.session.code_object.run_data_harmonization(
            syntactic_mapping.code_object_uids[0], run_params
        )

    @rhino_error_wrapper
    def remove_syntactic_mapping(self, syntactic_mapping_or_uid: Union[str, SyntacticMapping]):
        """
        Remove a SyntacticMapping with SYNTACTIC_MAPPING_OR_UID from the system
        """
        return self.session.delete(
            f"/syntactic_mappings/{syntactic_mapping_or_uid if isinstance(syntactic_mapping_or_uid, str) else syntactic_mapping_or_uid.uid}"
        ).no_dataclass_response()
