# ruff: noqa: PTH112,PTH113,PTH118,PTH208
import enum
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self
from collections.abc import Iterable

import pydicom
from loguru import logger
from pydicom import dcmread
from pydicom.errors import InvalidDicomError
from pynetdicom import AE

from dicom_qr.retrieve_utils import AssociationError
from dicom_qr.storage_classes import StoragePresentationContexts


def get_files(folders: Iterable[str], recurse: bool = False) -> list[Path]:
    """
    List all files from a list of base folders, recursively if required.
    :param folders: base folders
    :param recurse: scan recursively
    :return: list of files
    """
    files = []
    for folder in folders:
        if os.path.isfile(folder):
            files.append(folder)
            continue
        if os.path.isdir(folder):
            if not recurse:
                files += [os.path.join(folder, pp) for pp in os.listdir(folder)]
                continue
            for root, _, x in os.walk(folder):
                files += [os.path.join(root, pp) for pp in x]

    return sorted({Path(x) for x in files if os.path.isfile(x)})


@dataclass
class Settings:
    """ Store settings. """
    calling_aet: str = 'STORESCU'
    """ Calling Application Entity Title (AET) """
    called_aet: str = 'ANY-SCP'
    """ Called Application Entity Title (AET) """
    acse_timeout: int = 30
    """ Association Control Service Element (ACSE) timeout in seconds
    used for message timeouts during association negotiation """
    dimse_timeout: int = 30
    """ DICOM Message Service Element (DIMSE) timeout in seconds for receiving data.
    The SCU will try to read data from the incoming socket stream for the number of seconds configured. """
    network_timeout: int = 30
    """ The maximum amount of time (in seconds) to wait for network messages. """
    max_pdu: int = 16382
    """ The maximum Protocol Data Units (PDU) size accepted by the AE """


class DicomStatus(enum.Enum):
    """ DICOM status. """
    # Failure
    INVALID_SOP_INSTANCE = 0x0117
    SOP_CLASS_NOT_SUPPORTED = 0x0122
    NOT_AUTHORIZED = 0x0124
    DUPLICATE_INVOCATION = 0x0210
    UNRECOGNIZED_OPERATION = 0x0211
    MISTYPED_ARGUMENT = 0x0212
    OUT_OF_RESOURCES = 0xA700
    DATASET_DOES_NOT_MATCH_SOP_CLASS_ERRROR = 0xA900
    CANNOT_UNDERSTAND = 0xC000

    # Warning
    COERCION_OF_DATA_ELEMENTS = 0xB000
    ELEMENT_DISCARDED = 0xB006
    DATASET_DOES_NOT_MATCH_SOP_CLASS_WARNING = 0xB007

    # General
    CANCEL = 0xFE00
    SUCCESS = 0x0000
    PENDING_0 = 0xFF00
    PENDING_1 = 0xFF01
    UNKNOWN = 0x1234


class StorePacs:
    """ Store images in PACS.
    Based on [pynetdicom](https://pydicom.github.io/pynetdicom/stable/examples/storage.html)
    """

    def __init__(self, addr: str, port: int, settings: Settings = Settings()) -> None:
        self.settings = settings

        self.application_entity = AE(ae_title=settings.calling_aet)
        self.application_entity.acse_timeout = settings.acse_timeout
        self.application_entity.dimse_timeout = settings.dimse_timeout
        self.application_entity.network_timeout = settings.network_timeout
        self.application_entity.supported_contexts = StoragePresentationContexts

        for cx in StoragePresentationContexts:
            self.application_entity.add_requested_context(cx.abstract_syntax)  # type: ignore

        # Request association with remote
        self.assoc = self.application_entity.associate(addr, port, ae_title=settings.called_aet, max_pdu=settings.max_pdu)
        if not self.assoc.is_established:
            raise AssociationError('Association not established.')

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.assoc.release()
        self.application_entity.shutdown()

    def store(self, dataset: Path | pydicom.Dataset, index: int) -> DicomStatus | None:
        """
        Store a dataset in PACS.
        :param dataset: dataset to store
        :param index: message index
        :return: DicomStatus or None
        """
        if not self.assoc.is_established:
            logger.error('Association not established.')
            return None

        if isinstance(dataset, Path):
            try:
                dataset = dcmread(str(dataset))
            except InvalidDicomError:
                logger.error(f'Bad DICOM file: "{dataset}"')
                return None

        response = self.assoc.send_c_store(dataset, index)
        if hasattr(response, 'OffendingElement'):
            logger.error(response.OffendingElement)

        if hasattr(response, 'ErrorComment'):
            logger.error(response.ErrorComment)

        return DicomStatus(response.Status)
