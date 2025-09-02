import string
from pathlib import Path
from collections.abc import Callable, Iterable

from loguru import logger
import pydicom
from pathvalidate import sanitize_filename
from pynetdicom.events import Event

from dicom_qr.retrieve_utils import RetrieveResult
from dicom_qr.storage_classes import SOP_CLASS_UID_TO_PREFIX


Anonymizer = Callable[[pydicom.Dataset], pydicom.Dataset]
""" Anonymizer function. """


def dummy_filename_callback(_: Path) -> None:
    """ Dummy implementation """


def dummy_mapping(val: str) -> str:
    """ Dummy implementation, return input value """
    return val


def dummy_anonymize(_data: pydicom.Dataset) -> pydicom.Dataset:
    """ Dummy implementation, return input value """
    return _data


def dummy_retrieve_progress(_data: RetrieveResult) -> None:
    """ Dummy implementation """


# See https://github.com/pydicom/pynetdicom/issues/487

def _get_value_safe(dataset: pydicom.Dataset, tag: str) -> str:
    def sanitize_fn(data: str) -> str:
        return str(sanitize_filename(data))

    if hasattr(dataset, tag):
        val = getattr(dataset, tag)
        if tag == 'PatientName' and val.original_string is not None:
            return sanitize_fn(val.original_string.decode('utf-8'))
        return sanitize_fn(str(getattr(dataset, tag)))

    return sanitize_fn(f'No{tag}')


def dataset_to_filename_template_dict(dataset: pydicom.Dataset) -> dict[str, str]:
    """ Create a dictionary from a pydicom.Dataset instance of selected tags. """
    patient_name = _get_value_safe(dataset, 'PatientName')
    patient_id = _get_value_safe(dataset, 'PatientID')
    study_description = _get_value_safe(dataset, 'StudyDescription').replace(' ', '_').replace('_-_', '-')
    study_date = _get_value_safe(dataset, 'StudyDate')
    study_time = _get_value_safe(dataset, 'StudyTime')
    modality = _get_value_safe(dataset, 'Modality')
    series_description = _get_value_safe(dataset, 'SeriesDescription').replace(' ', '_').replace('_-_', '-')
    series_number = _get_value_safe(dataset, 'SeriesNumber')
    series_instance_uid = _get_value_safe(dataset, 'SeriesInstanceUID')
    study_instance_uid = _get_value_safe(dataset, 'StudyInstanceUID')
    accession_number = _get_value_safe(dataset, 'AccessionNumber')

    return {
        'PatientName': patient_name,
        'PatientID': patient_id,
        'StudyDescription': study_description,
        'StudyDate': study_date,
        'StudyTime': study_time,
        'Modality': modality,
        'SeriesDescription': series_description,
        'SeriesNumber': series_number,
        'SeriesInstanceUID': series_instance_uid,
        'StudyInstanceUID': study_instance_uid,
        'AccessionNumber': accession_number,
    }


def get_prefix(dataset: pydicom.Dataset) -> str:
    """ Get the filename prefix based on SOPClassUID. """
    if not hasattr(dataset, 'SOPClassUID'):
        logger.warning(f'No SOPClassUID found ({dataset}).')
        return ''

    sop_class_uid = dataset.SOPClassUID

    if sop_class_uid not in SOP_CLASS_UID_TO_PREFIX:
        logger.warning(f'Unknown SOPClassUID found ({sop_class_uid}).')
        return ''

    return SOP_CLASS_UID_TO_PREFIX[sop_class_uid]


def handle_store(
        event: Event,
        base_folder: Path,
        folder_template: str,
        anonimyzer: Anonymizer,
        uid_mapping: Callable[[str], str],
        folder_callback: Callable[[Path], None],
        sop_class_uid: Iterable[str] | None) -> int:
    """ Callback function for storing a DICOM dataset.
    :param event: The dataset to store.
    :param base_folder: Base folder for storing files.
    :param folder_template: Template for creating folders inside the base_folder.
    :param anonimyzer: Anonymizer to anonymize the dataset.
    :param uid_mapping: Mapping from UID to series index.
    :param folder_callback: Callback function for returning the final path.
    :param sop_class_uid: Optional SOPClassUIDs to process, others will be ignored.
    :return: DICOM status code.
    """
    dataset: pydicom.Dataset = event.dataset
    dataset.file_meta = event.file_meta

    dataset = anonimyzer(dataset)

    try:
        ds_dict = dataset_to_filename_template_dict(dataset)

        if sop_class_uid is not None and 'SOPClassUID' in ds_dict and ds_dict['SOPClassUID'] not in sop_class_uid:
            return 0x0000

        if 'FolderUID' in folder_template:
            try:
                ds_dict['FolderUID'] = uid_mapping(ds_dict['SeriesInstanceUID'])
            except KeyError:
                logger.warning(f'SeriesInstanceUID {ds_dict["SeriesInstanceUID"]} not found in mapping.')
                ds_dict['FolderUID'] = 'NA'

        folder_name = base_folder / string.Template(folder_template).substitute(ds_dict)
        folder_name.mkdir(parents=True, exist_ok=True)
        folder_callback(folder_name)

        filename = Path(get_prefix(dataset) + dataset.SOPInstanceUID + '.dcm')

        dataset.save_as(folder_name / filename, write_like_original=False)
    except TypeError as e:
        logger.error(e)
        return 0xA700

    return 0x0000
