import time
from typing import List, Optional

from rhino_health.lib.endpoints.dicomweb_query.dicomweb_query_dataclass import (
    DicomwebQuery,
    DicomwebQueryCreateInput,
)
from rhino_health.lib.endpoints.endpoint import Endpoint
from rhino_health.lib.utils import rhino_error_wrapper


class DicomwebQueryEndpoint(Endpoint):
    """
    @autoapi False

    These endpoints are for internal testing use and not surfaced to users
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "dicom"

    @property
    def dicomweb_query_dataclass(self):
        """
        @autoapi False
        :return:
        """
        return DicomwebQuery

    @rhino_error_wrapper
    def get_dicomweb_query(self, dicomweb_query_uid: str):
        """
        @autoapi True
        Returns a DicomwebQuery dataclass

        Parameters
        ----------
        dicomweb_query_uid: str
            UID for the DICOMweb query

        Returns
        -------
        dicomweb_query: DicomwebQuery
            DicomwebQuery dataclass

        Examples
        --------
        >>> DicomwebQueryEndpoint(session).get_dicomweb_query(my_query_uid)
        DicomwebQuery()
        """
        return self.session.get(f"/dicomweb_queries/{dicomweb_query_uid}").to_dataclass(
            self.dicomweb_query_data_class
        )

    @rhino_error_wrapper
    def get_dicomweb_queries(
        self, dicomweb_query_uids: Optional[List[str]] = None
    ) -> List[DicomwebQuery]:
        """
        @autoapi True
        Gets the DICOMweb queries with the specified DICOMWEB_QUERY_UIDS.

        .. warning:: This feature is under development and the interface may change.
        """
        if not dicomweb_query_uids:
            return self.session.get("/dicomweb_queries/").to_dataclasses(
                self.dicomweb_query_data_class
            )
        else:
            return [
                self.session.get(f"/dicomweb_queries/{dicomweb_query_uid}/").to_dataclass(
                    self.dicomweb_query_data_class
                )
                for dicomweb_query_uid in dicomweb_query_uids
            ]

    @rhino_error_wrapper
    def create_dicomweb_query(self, dicomweb_query_input: DicomwebQueryCreateInput):
        """
        Returns a DicomwebQuery dataclass

        Parameters
        ----------
        dicomweb_query_input: DicomwebQueryCreateInput
            DicomwebQueryCreateInput dataclass

        Returns
        -------
        dicomweb_query: DicomwebQuery
            DicomwebQuery dataclass

        Examples
        --------
        >>> DicomwebQueryEndpoint(session).create_dicomweb_query(dicomweb_query_input)
        DicomwebQuery()
        """
        # print(dicomweb_query_input)
        # print(dicomweb_query_input.dict(by_alias=True))
        result = self.session.post(
            f"/dicomweb-queries",
            data=dicomweb_query_input.model_dump(by_alias=True),
        )
        return result.to_dataclass(self.dicomweb_query_dataclass)

    def run_query(
        self,
        dicomweb_query_input: DicomwebQueryCreateInput,
        timeout_seconds: Optional[float] = None,
        query_interval_seconds: Optional[float] = 1.0,
    ) -> DicomwebQuery:
        """
        @autoapi True
        Run a DICOMweb query against an external service and get its results.

        This will create a query, wait for it to complete and retrieve
        its results.

        .. warning:: This feature is under development and the interface may change.
        """
        if query_interval_seconds <= 0:
            raise ValueError("query_interval_seconds must be greater than zero.")

        dicomweb_query = self.create_dicomweb_query(dicomweb_query_input)

        start_time = time.monotonic()
        last_status = None
        while True:
            dicomweb_query = self.get_dicomweb_query(dicomweb_query.uid)
            status = dicomweb_query.status
            if status != last_status:
                print("DICOMweb query status:", status)
                last_status = status
            if status not in {"Initialized", "Started"}:
                break
            elapsed = time.monotonic() - start_time
            if timeout_seconds is not None and elapsed >= timeout_seconds:
                raise Exception("Timeout running DICOMweb query.")
            time.sleep(query_interval_seconds - (elapsed % query_interval_seconds))

        return dicomweb_query
