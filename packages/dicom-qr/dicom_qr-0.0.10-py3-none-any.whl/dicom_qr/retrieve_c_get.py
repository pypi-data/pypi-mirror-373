""" Perform C_GET action. """
from __future__ import annotations

import functools
import typing
from typing import Self

import pydicom
from loguru import logger
from pynetdicom import AE, evt, build_role
from pynetdicom.sop_class import (PatientRootQueryRetrieveInformationModelGet,  # type: ignore
                                  PatientStudyOnlyQueryRetrieveInformationModelGet,  # type: ignore
                                  StudyRootQueryRetrieveInformationModelGet,  # type: ignore
                                  EncapsulatedSTLStorage,  # type: ignore
                                  EncapsulatedOBJStorage,  # type: ignore
                                  EncapsulatedMTLStorage)  # type: ignore
from dicom_qr.scp import handle_store, Anonymizer, dummy_anonymize
from dicom_qr.storage_classes import StoragePresentationContexts
from dicom_qr.retrieve_utils import AssociationError, RetrieveResult, process_responses

if typing.TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Iterable, Callable
    from dicom_qr.database import SeriesData
    from dicom_qr.settings import PacsConfig


class RetrievePacsGet:
    """ Retrieve images from PACS using C-GET.
    Based on [getscu.py](https://github.com/pydicom/pynetdicom/blob/main/pynetdicom/apps/getscu/getscu.py)
    """
    def __init__(self,
                 pacs_config: PacsConfig,
                 uid_mapping: Callable[[str], str],
                 folder_callback: Callable[[Path], None],
                 retrieve_callback: Callable[[RetrieveResult], None],
                 anonymizer: Anonymizer = dummy_anonymize,
                 sop_class_uid: Iterable[str] | None = None) -> None:
        self.pacs_config = pacs_config
        self._retrieve_callback = retrieve_callback

        # Exclude these SOP Classes
        _exclusion = [
            EncapsulatedSTLStorage,
            EncapsulatedOBJStorage,
            EncapsulatedMTLStorage,
        ]
        store_contexts = [
            cx for cx in StoragePresentationContexts if cx.abstract_syntax not in _exclusion
        ]

        self.application_entity = AE(ae_title=pacs_config.client_ae_title)
        self.application_entity.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
        self.application_entity.add_requested_context(PatientStudyOnlyQueryRetrieveInformationModelGet)
        self.application_entity.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
        self.application_entity.supported_contexts = StoragePresentationContexts

        ext_neg = []
        for cx in store_contexts:
            self.application_entity.add_requested_context(cx.abstract_syntax)  # type: ignore
            # Add SCP/SCU Role Selection Negotiation to the extended negotiation. We want to act as a Storage SCP
            ext_neg.append(build_role(cx.abstract_syntax, scp_role=True))  # type: ignore

        handler_func = functools.partial(
            handle_store,
            base_folder=self.pacs_config.base_folder,
            folder_template=self.pacs_config.folder_template,
            anonimyzer=anonymizer,
            uid_mapping=uid_mapping,
            folder_callback=folder_callback,
            sop_class_uid=sop_class_uid
        )

        self.assoc = self.application_entity.associate(addr=pacs_config.server_ae_ip, port=pacs_config.server_ae_port,
                                                       ae_title=pacs_config.server_ae_title,
                                                       evt_handlers=[(evt.EVT_C_STORE, handler_func)],
                                                       ext_neg=ext_neg)  # type: ignore

        if not self.assoc.is_established:
            raise AssociationError('Association not established.')

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.assoc.release()
        self.application_entity.shutdown()

    def retrieve(self, dataset: pydicom.Dataset) -> RetrieveResult | None:
        """ Retrieve images for a dataset. """
        if not self.assoc.is_established:
            logger.error('Association not established.')
            return None

        responses = self.assoc.send_c_get(dataset, StudyRootQueryRetrieveInformationModelGet)

        return process_responses(responses, self._retrieve_callback)

    def retrieve_images_for_a_series(self, series_data: SeriesData) -> None:
        """ Retrieve images for a series. """
        dataset = pydicom.Dataset()
        dataset.QueryRetrieveLevel = 'SERIES'
        dataset.StudyInstanceUID = series_data.StudyInstanceUID
        dataset.SeriesInstanceUID = series_data.SeriesInstanceUID
        self.retrieve(dataset)
