from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pydicom.tag

from loguru import logger

import pydicom
from pynetdicom.status import UNIFIED_PROCEDURE_STEP_SERVICE_CLASS_STATUS

from pynetdicom.sop_class import (  # type: ignore
    ModalityWorklistInformationFind,  # type: ignore
)

from dicom_ups.dicom_handlers import DicomAssociation


def create_step(dataset: pydicom.Dataset, sop_class_uid: str) -> pydicom.Dataset | None:
    with DicomAssociation('conductor') as d:
        if not d.assoc.is_established:
            msg = f'Association not established. {d.server}'
            raise RuntimeError(msg)

        status, result = d.assoc.send_n_create(
            dataset,
            class_uid=sop_class_uid,
            instance_uid=dataset.SOPInstanceUID
        )

        try:
            if status.Status != 0x0000:
                logger.warning(', '.join(UNIFIED_PROCEDURE_STEP_SERVICE_CLASS_STATUS[status.Status]))
        except AttributeError:
            logger.error('Error sending create_step')
            return pydicom.Dataset()

        return result


def set_step(dataset: pydicom.Dataset, uid: str, sop_class_uid: str) -> pydicom.Dataset | None:
    with DicomAssociation('conductor') as d:
        if not d.assoc.is_established:
            msg = f'Association not established. {d.server}'
            raise RuntimeError(msg)

        status, result = d.assoc.send_n_set(
            dataset,
            class_uid=sop_class_uid,
            instance_uid=uid
        )

        if status.Status != 0x0000:
            logger.warning(', '.join(UNIFIED_PROCEDURE_STEP_SERVICE_CLASS_STATUS[status.Status]))

        return result


def get_step(uid: str, sop_class_uid: str) -> pydicom.Dataset | None:
    with DicomAssociation('conductor') as d:
        if not d.assoc.is_established:
            msg = f'Association not established. {d.server}'
            raise RuntimeError(msg)

        status, result = d.assoc.send_n_get(
            [],
            class_uid=sop_class_uid,
            instance_uid=uid
        )

        if status.Status != 0x0000:
            logger.warning(', '.join(UNIFIED_PROCEDURE_STEP_SERVICE_CLASS_STATUS[status.Status]))

        return result


def action_step(dataset: pydicom.Dataset | None, uid: str, sop_class_uid: str) -> pydicom.Dataset | None:
    with DicomAssociation('conductor') as d:
        if not d.assoc.is_established:
            msg = f'Association not established. {d.server}'
            raise RuntimeError(msg)

        status, result = d.assoc.send_n_action(
            dataset,  # type: ignore
            action_type=1,
            class_uid=sop_class_uid,
            instance_uid=uid
        )

        if status.Status != 0x0000:
            logger.warning(', '.join(UNIFIED_PROCEDURE_STEP_SERVICE_CLASS_STATUS[status.Status]))

        return result


def find_step(dataset: pydicom.Dataset) -> list[pydicom.Dataset]:
    with DicomAssociation('conductor') as d:
        if not d.assoc.is_established:
            msg = f'Association not established. {d.server}'
            raise RuntimeError(msg)

        responses = d.assoc.send_c_find(dataset, ModalityWorklistInformationFind)

        results = []
        for response, response_dataset in responses:
            try:
                last_status = response.Status
            except AttributeError:
                continue

            if response_dataset is None:
                continue

            if last_status in [0xFF00, 0xFF01, 0x0000]:
                results.append(response_dataset)
                continue

        return results
