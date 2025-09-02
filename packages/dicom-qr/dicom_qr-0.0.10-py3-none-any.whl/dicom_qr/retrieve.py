from pathlib import Path
from typing import Protocol, Self
from collections.abc import Callable, Iterable

import pydicom

from dicom_qr.database import SeriesData
from dicom_qr.retrieve_c_get import RetrievePacsGet
from dicom_qr.retrieve_c_move import RetrievePacsMove
from dicom_qr.retrieve_utils import RetrieveResult
from dicom_qr.scp import Anonymizer, dummy_anonymize, dummy_filename_callback, dummy_retrieve_progress
from dicom_qr.settings import DicomTransferMethod, PacsConfig


class RetrievePacs(Protocol):
    """ Protocol describing RetrievePacs. """

    def retrieve_images_for_a_series(self, series_data: SeriesData) -> None:
        """ Retrieve images for a series. """

    def retrieve(self, dataset: pydicom.Dataset) -> RetrieveResult | None:
        """ Retrieve images for a dataset. """

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        ...


def get_retrieve(pacs_config: PacsConfig, uid_mapping: Callable[[str], str],
                 folder_callback: Callable[[Path], None] = dummy_filename_callback,
                 retrieve_callback: Callable[[RetrieveResult], None] = dummy_retrieve_progress,
                 anonymizer: Anonymizer = dummy_anonymize,
                 sop_class_uid: Iterable[str] | None = None,
                 store_scp: bool = True) -> RetrievePacs:
    """ factory method to create RetrievePacs based on the *transfer_method* specified in *pacs_config*."""
    if pacs_config.transfer_method == DicomTransferMethod.GET:
        return RetrievePacsGet(
            pacs_config=pacs_config,
            uid_mapping=uid_mapping,
            folder_callback=folder_callback,
            anonymizer=anonymizer,
            sop_class_uid=sop_class_uid,
            retrieve_callback=retrieve_callback
        )

    if pacs_config.transfer_method == DicomTransferMethod.MOVE:
        return RetrievePacsMove(
            pacs_config=pacs_config,
            uid_mapping=uid_mapping,
            folder_callback=folder_callback,
            anonymizer=anonymizer,
            sop_class_uid=sop_class_uid,
            store_scp=store_scp,
            retrieve_callback=retrieve_callback
        )

    raise NotImplementedError
