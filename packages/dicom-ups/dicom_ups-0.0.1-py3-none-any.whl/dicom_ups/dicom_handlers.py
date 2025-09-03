from __future__ import annotations

import typing
from typing import Any, Self

import pydicom
import pynetdicom.dimse_primitives
from pydicom import Dataset
from pydicom.uid import generate_uid
from pynetdicom.ae import ApplicationEntity
from pynetdicom.sop_class import (
    ModalityPerformedProcedureStep,  # type: ignore
    PatientRootQueryRetrieveInformationModelFind,  # type: ignore
    UnifiedProcedureStepEvent,  # type: ignore
    UnifiedProcedureStepPull,  # type: ignore
    UnifiedProcedureStepPush,  # type: ignore
    UnifiedProcedureStepQuery,  # type: ignore
    UnifiedProcedureStepWatch  # type: ignore
)

from dicom_ups.options import ActionType, get_servers

if typing.TYPE_CHECKING:
    from collections.abc import Generator
    import types
    from pynetdicom.events import Event
    from dicom_ups.options import Server


class DbProtocol(typing.Protocol):
    def add_job(self, ds: Dataset) -> None:
        ...

    def get_job(self, uid: str) -> Dataset:
        ...

    def update_job(self, ds: Dataset) -> None:
        ...

    def remove_job(self, uid: str) -> None:
        ...

    def get_uids(self) -> list[str]:
        ...

    def get_all_jobs(self) -> list[Dataset]:
        ...


class DicomAssociation:
    def __init__(self, node_name: str = 'conductor') -> None:
        self._server = get_servers()[node_name]

        application_entity = ApplicationEntity()
        application_entity.add_requested_context(ModalityPerformedProcedureStep)
        application_entity.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
        application_entity.add_requested_context(UnifiedProcedureStepPush)
        application_entity.add_requested_context(UnifiedProcedureStepWatch)
        application_entity.add_requested_context(UnifiedProcedureStepPull)
        application_entity.add_requested_context(UnifiedProcedureStepEvent)
        application_entity.add_requested_context(UnifiedProcedureStepQuery)
        self.assoc = application_entity.associate(self._server.host, self._server.port)

    @property
    def server(self) -> Server:
        return self._server

    def __enter__(self) -> Self:
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_val: BaseException | None,
                 exc_tb: types.TracebackType | None) -> None:
        if self.assoc:
            self.assoc.release()


def n_action(event: Event, database: DbProtocol) -> tuple[int, pydicom.Dataset | None]:
    assert isinstance(event.request, pynetdicom.dimse_primitives.N_ACTION)

    match ActionType(event.action_type):  # type: ignore
        case ActionType.DELETE:
            try:
                uid = event.request.RequestedSOPInstanceUID
                assert uid is not None
                database.remove_job(uid)
                # SUCCESS
                return 0x0000, pydicom.Dataset()
            except KeyError:
                # Specified SOP Instance UID does not exist or is not a UPS Instance managed by this SCP
                return 0xC307, pydicom.Dataset()
        case _:
            pass

    # Processing Failure
    return 0x0110, pydicom.Dataset()


def n_create(event: Event, database: DbProtocol) -> tuple[int, pydicom.Dataset | None]:
    assert isinstance(event.request, pynetdicom.dimse_primitives.N_CREATE)

    req = event.request

    if req.AffectedSOPInstanceUID is None:
        # Failed - invalid attribute value
        return 0x0106, None

    uids = database.get_uids()

    # Can't create a duplicate SOP Instance
    if req.AffectedSOPInstanceUID in uids:
        # Failed - duplicate SOP Instance
        return 0x0111, None

    # The N-CREATE request's *Attribute List* dataset
    attr_list = event.attribute_list

    # Performed Procedure Step Status must be 'IN PROGRESS'
    if "PerformedProcedureStepStatus" not in attr_list:
        # Failed - missing attribute
        return 0x0120, None

    if attr_list.PerformedProcedureStepStatus.upper() != 'SCHEDULED':
        return 0x0106, None

    # Skip other tests...

    # Create a Modality Performed Procedure Step SOP Class Instance
    #   DICOM Standard, Part 3, Annex B.17
    ds = pydicom.Dataset()

    # Add the SOP Common module elements (Annex C.12.1)
    # ds.SOPClassUID = ModalityPerformedProcedureStep
    ds.SOPInstanceUID = req.AffectedSOPInstanceUID

    # Update with the requested attributes
    ds.update(attr_list)

    # Add the dataset to the managed SOP Instances
    database.add_job(ds)

    # Return status, dataset
    return 0x0000, ds


def c_find(event: Event, database: DbProtocol) -> Generator[tuple[int, Any] | tuple[int, None]]:
    """
    Event handler for C-FIND events.
    This function is called when the SCP receives a C-FIND request.
    """
    assert isinstance(event.request, pynetdicom.dimse_primitives.C_FIND)

    request_ds = event.identifier

    # Extract query keys from the request_ds
    # For a C-FIND, keys typically contain wildcards or specific values.
    # We'll use a simple matching logic for demonstration.
    query_patient_id = request_ds.get("PatientID", None)
    query_patient_name = request_ds.get("PatientName", None)
    query_procedure_state = request_ds.get("ProcedureStepState", None)
    query_req_proc_desc = request_ds.get("RequestedProcedureDescription", None)

    found_matches = []
    for ups_data in database.get_all_jobs():
        match = True
        if (query_patient_id and query_patient_id != '*' and
                query_patient_id != ups_data.get("PatientID")):
            match = False
        if (query_patient_name and query_patient_name != '*' and
                query_patient_name.upper() not in ups_data.get("PatientName", "").upper()):
            match = False
        if (query_procedure_state and query_procedure_state != '*' and
                query_procedure_state != ups_data.get("ProcedureStepState")):
            match = False
        if (query_req_proc_desc and query_req_proc_desc != '*' and
                query_req_proc_desc.upper() not in ups_data.get("RequestedProcedureDescription", "").upper()):
            match = False

        if match:
            # Construct the response dataset for each matching UPS instance
            # The response dataset should contain the requested return keys
            # and the values from the matching instance.
            response_ds = pydicom.Dataset()
            response_ds.SOPClassUID = UnifiedProcedureStepPush  # This is the SOP Class for UPS Instances
            response_ds.SOPInstanceUID = generate_uid()
            # response_ds.ProcedureStepState = ups_data["ProcedureStepState"]
            # response_ds.ScheduledProcedureStepPriority = ups_data["ScheduledProcedureStepPriority"]
            response_ds.PatientName = ups_data.get("PatientName", "")
            response_ds.PatientID = ups_data.get("PatientID", "")
            # response_ds.RequestedProcedureDescription = ups_data["RequestedProcedureDescription"]
            # response_ds.ScheduledStationAETitle = ups_data["ScheduledStationAETitle"]

            found_matches.append(response_ds)

    # Yield each match with a 'Pending' status (0xFF00)
    for match_ds in found_matches:
        yield 0xFF00, match_ds  # 0xFF00: Pending

    # After yielding all matches, yield a 'Success' status (0x0000)
    yield 0x0000, None  # 0x0000: Success, Identifier is not returned for success


def n_get(event: Event, database: DbProtocol) -> tuple[int, pydicom.Dataset | None]:
    assert isinstance(event.request, pynetdicom.dimse_primitives.N_GET)
    uid = event.request.RequestedSOPInstanceUID
    assert uid is not None

    ds = database.get_job(uid)

    if ds is None:
        # Failure - SOP Instance not recognised
        return 0x0112, None

    # Return status, dataset
    return 0x0000, ds


def n_set(event: Event, database: DbProtocol) -> tuple[int, pydicom.Dataset | None]:
    assert isinstance(event.request, pynetdicom.dimse_primitives.N_SET)

    uid = event.request.RequestedSOPInstanceUID
    assert uid is not None

    ds = database.get_job(uid)

    if ds is None:
        # Failure - SOP Instance not recognised
        return 0x0112, None

    # The N-SET request's *Modification List* dataset
    mod_list = event.attribute_list

    # Skip other tests...
    ds.update(mod_list)

    database.update_job(ds)

    # Return status, dataset
    return 0x0000, ds
