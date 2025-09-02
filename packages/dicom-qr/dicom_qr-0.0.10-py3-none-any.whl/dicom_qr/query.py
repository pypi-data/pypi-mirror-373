"""
Module for querying a DICOM SCU using the C-FIND service.
"""
from __future__ import annotations

import typing
from collections import defaultdict
from enum import Enum
from typing import Self

from loguru import logger
from pydicom.dataset import Dataset, UID
from pynetdicom import AE, Association
from pynetdicom.sop_class import (PatientRootQueryRetrieveInformationModelFind,  # type: ignore
                                  PatientStudyOnlyQueryRetrieveInformationModelFind,  # type: ignore
                                  StudyRootQueryRetrieveInformationModelFind)  # type: ignore

from dicom_qr.database import SeriesData, StudyData

if typing.TYPE_CHECKING:
    import datetime
    from collections.abc import Sequence
    from dicom_qr.search import SearchTerms
    from dicom_qr.settings import PacsConfig


class DicomStatus(Enum):
    """
    [DICOM C-FIND status codes](https://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_cc.2.8.4.html)
    """
    OUT_OF_RESOURCES = 0xA700
    """Refused Out of resources"""
    DATASET_DOES_NOT_MATCH_SOP_CLASS = 0xA900
    """Error Data Set does not match SOP Class"""
    SOP_CLASS_NOT_SUPPORTED = 0x0122
    """Refused SOP Class not supported"""
    CANCEL = 0xFE00
    """Matching terminated due to Cancel request"""
    SUCCESS = 0x0000
    """Matching is complete - No final Identifier is supplied."""
    PENDING_0 = 0xFF00
    """Matches are continuing - Current Match is supplied and any
    Optional Keys were supported in the same manner as Required Keys."""
    PENDING_1 = 0xFF01
    """Matches are continuing - Warning that one or more
    Optional Keys were not supported for existence for this Identifier."""
    UNABLE_TO_PROCESS = 0xC000
    """Failed Unable to process"""
    UNKNOWN = 0x1234
    """Unknown"""


DicomStatusFailure = [DicomStatus.OUT_OF_RESOURCES, DicomStatus.DATASET_DOES_NOT_MATCH_SOP_CLASS,
                      DicomStatus.SOP_CLASS_NOT_SUPPORTED, DicomStatus.UNABLE_TO_PROCESS]


class QueryError(Exception):
    """Query exception"""

    def __init__(self, response: Dataset) -> None:
        super().__init__('Error perfoming query')
        self.response = response


def get_date_query(date_range: datetime.date | tuple[datetime.date, datetime.date]) -> str:
    """ Convert one of two datetime.date objects to a DICOM compatible date range."""
    if date_range is None:
        return '""'

    if isinstance(date_range, tuple):
        try:
            begin_date = date_range[0].strftime('%Y%m%d')
            end_date = date_range[1].strftime('%Y%m%d')
            return f'{begin_date}-{end_date}'
        except ValueError:
            return '""'

    try:
        return date_range.strftime('%Y%m%d')
    except ValueError:
        return '""'


def _dataset_from_searchterms(search_terms: SearchTerms) -> Dataset:
    dataset = Dataset()
    dataset.StudyDescription = search_terms.study_desc if search_terms.study_desc is not None else ''
    dataset.StudyInstanceUID = search_terms.study_uid if search_terms.study_uid is not None else ''
    dataset.AccessionNumber = search_terms.accession_number if search_terms.accession_number is not None else ''
    dataset.PatientID = search_terms.patid if search_terms.patid is not None else ''
    dataset.PatientName = search_terms.pat_name if search_terms.pat_name is not None else ''
    dataset.StudyDate = get_date_query(search_terms.date_range) if search_terms.date_range is not None else ''
    dataset.PatientSex = ''
    dataset.PatientBirthDate = ''
    dataset.ModalitiesInStudy = ''

    return dataset


class QueryPacs:
    """
    Class to perform the actual query.
    """

    def __init__(self, pacs_config: PacsConfig) -> None:
        self.pacs_config = pacs_config

        self.assoc: Association | None = None
        self._check_association()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self.assoc:
            self.assoc.release()

    def _check_association(self) -> None:
        if self.assoc and self.assoc.is_established:
            return

        application_entity = AE(ae_title=self.pacs_config.client_ae_title)
        application_entity.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
        application_entity.add_requested_context(PatientStudyOnlyQueryRetrieveInformationModelFind)
        application_entity.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
        self.assoc = application_entity.associate(self.pacs_config.server_ae_ip, self.pacs_config.server_ae_port,
                                                  ae_title=self.pacs_config.server_ae_title)

        if not self.assoc.is_established:
            raise RuntimeError('Association not established.')

    def get_studies_for_patient(self, search_terms: SearchTerms) -> defaultdict[str, list[StudyData]]:
        """ Get all studies matching the 'pat_name' in the search_terms."""
        studies = self.get_studies(search_terms)

        patient_data: defaultdict[str, list[StudyData]] = defaultdict(list)
        for study_data in studies:
            assert study_data.PatientName is not None
            patient_data[study_data.PatientName].append(study_data)

        if search_terms.modalities is None or len(search_terms.modalities) == 0:
            return patient_data

        for pat_data in patient_data.values():
            for study in pat_data:
                study.series = self.get_series_for_study(study.StudyInstanceUID, modalities=search_terms.modalities)

        return patient_data

    def get_modalities_for_accession_number(self, search_terms: SearchTerms) -> list[str]:
        """ Get modalities for matching the 'accession_number' in the search_terms."""
        studies = self.get_studies(search_terms)

        modalities: set[str] = set()
        for study in studies:
            modalities = modalities | set(study.ModalitiesInStudy)

        return list(modalities)

    def get_series_for_study(self, study_uid: str | UID, modalities: Sequence[str] | None = None) -> list[SeriesData]:
        """Get the series for 'study_uid', filtered by modalities (if specified)."""
        dataset = Dataset()
        dataset.QueryRetrieveLevel = 'SERIES'
        dataset.StudyInstanceUID = str(study_uid)
        dataset.SeriesInstanceUID = ''
        dataset.SeriesDescription = ''
        dataset.SeriesNumber = ''
        dataset.Modality = ''
        dataset.ProtocolName = ''

        if modalities is None or len(modalities) == 0:
            return self._get_series_response(dataset)

        results = []
        for modality in modalities:
            dataset.Modality = modality
            results.extend(self._get_series_response(dataset))
        return results

    def get_series(self, search_terms: SearchTerms) -> list[SeriesData]:
        """Get the series matching the search_terms."""
        dataset = _dataset_from_searchterms(search_terms)
        dataset.QueryRetrieveLevel = 'SERIES'
        dataset.StudyInstanceUID = ''
        dataset.SeriesInstanceUID = ''
        dataset.StudyID = ''
        dataset.StudyTime = ''
        dataset.Modality = ''
        dataset.SeriesDescription = ''
        dataset.ProtocolName = ''

        return self._get_series_response(dataset)

    def get_study(self, study_uid: str | UID) -> StudyData:
        """Get the single study for the 'study_uid'."""
        dataset = Dataset()
        dataset.QueryRetrieveLevel = 'STUDY'
        dataset.StudyInstanceUID = str(study_uid)
        dataset.AccessionNumber = ''
        dataset.BodyPartExamined = ''
        dataset.ModalitiesInStudy = ''
        dataset.PatientBirthDate = ''
        dataset.PatientID = ''
        dataset.PatientName = ''
        dataset.PatientSex = ''
        dataset.StudyDate = ''
        dataset.StudyDescription = ''
        dataset.StudyID = ''
        dataset.StudyTime = ''

        studies = self._get_studies_response(dataset, modalities=None)
        if len(studies) != 1:
            raise RuntimeError('Study not available.')

        return studies[0]

    def get_studies(self, search_terms: SearchTerms) -> list[StudyData]:
        """Get the studies matching the search_terms."""
        dataset = _dataset_from_searchterms(search_terms)
        dataset.QueryRetrieveLevel = 'STUDY'
        dataset.StudyID = ''
        dataset.StudyTime = ''
        dataset.BodyPartExamined = ''

        return self._get_studies_response(dataset, search_terms.modalities)

    def _get_series_response(self, dataset: Dataset) -> list[SeriesData]:
        self._check_association()
        assert self.assoc

        responses = self.assoc.send_c_find(dataset, StudyRootQueryRetrieveInformationModelFind)
        series = []
        last_status = DicomStatus.UNKNOWN
        for response, response_dataset in responses:
            try:
                last_status = DicomStatus(response.Status)
            except AttributeError:
                continue

            if last_status in DicomStatusFailure:
                raise QueryError(response)

            if response_dataset is None:
                continue

            if last_status in [DicomStatus.PENDING_0, DicomStatus.PENDING_1, DicomStatus.SUCCESS]:
                series.append(SeriesData(**{x.keyword: x.value for x in response_dataset.values()}))  # type: ignore
                continue

            if last_status == DicomStatus.SUCCESS:
                logger.debug('Success')

            if last_status == DicomStatus.CANCEL:
                logger.warning('Cancelled')

        if last_status not in [DicomStatus.SUCCESS, DicomStatus.CANCEL]:
            logger.warning('Respones finished without SUCCESS or CANCEL status.')

        return series

    def _get_studies_response(self, dataset: Dataset, modalities: Sequence[str] | None) -> list[StudyData]:
        self._check_association()
        assert self.assoc

        responses = self.assoc.send_c_find(dataset, StudyRootQueryRetrieveInformationModelFind)
        studies = []
        last_status = DicomStatus.UNKNOWN
        for response, response_dataset in responses:
            try:
                last_status = DicomStatus(response.Status)
            except AttributeError:
                continue

            if last_status in DicomStatusFailure:
                raise QueryError(response)

            if response_dataset is None:
                continue

            if last_status in [DicomStatus.PENDING_0, DicomStatus.PENDING_1, DicomStatus.SUCCESS]:
                study = StudyData(**{x.keyword: x.value for x in response_dataset.values()})  # type: ignore
                if modalities is not None and len(modalities) > 0 and not set(modalities) & set(study.ModalitiesInStudy):
                    continue
                logger.debug(f'Found study: "{response_dataset.StudyDescription}"')
                studies.append(study)
                continue

            if last_status == DicomStatus.SUCCESS:
                logger.debug('Success')

            if last_status == DicomStatus.CANCEL:
                logger.warning('Cancelled')

        if last_status not in [DicomStatus.SUCCESS, DicomStatus.CANCEL]:
            logger.warning('Respones finished without SUCCESS or CANCEL status.')

        return studies
