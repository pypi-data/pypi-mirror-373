from __future__ import annotations

import typing
from typing import cast, Protocol, Self

import deid.dicom
import pandas as pd

if typing.TYPE_CHECKING:
    import pydicom
    from pathlib import Path
    from deid.dicom.fields import DicomField


class DeindentError(Exception):
    """ Generic exception raised when deindent fails. """


class PatientDeident(Protocol):  # pylint: disable=too-few-public-methods
    """ Generate PatientName or PatientID. """
    def __call__(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:
        ...


class UidDeident(Protocol):  # pylint: disable=too-few-public-methods
    """ Generate new UID. """
    def __call__(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:
        ...


class PatientComments(Protocol):  # pylint: disable=too-few-public-methods
    """ Generate a PatientComments. """
    def __call__(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:
        ...


class BasicUidDeident:  # pylint: disable=too-few-public-methods
    """ Use the deid function to generate a new UID. Also stores it in a map, so it can be exported to a key file. """
    def __init__(self, dicom_uid_root: str) -> None:
        self.dicom_uid_root = dicom_uid_root
        self.uid_map: dict[str, str] = {}

    def __call__(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:  # noqa: ARG002
        uid = deid.dicom.actions.uids.pydicom_uuid(  # type: ignore
            item, value, field, extras=f'prefix={self.dicom_uid_root} stable_remapping=true')

        self.uid_map[field.element.value] = uid

        return cast('str', uid)


class PatientLookupDeident:  # pylint: disable=too-few-public-methods
    """ Lookup the new patientid/name using the provided map.
    This assumes there is a unique relation between key and value.
    No key can have more than one value and each value can only be matched to one key.
    The first part is guaranteed by the dict, we validate the other condition in the constructor.
    """
    def __init__(self, patient_id_map: dict[str, str]) -> None:
        self.patient_id_map = patient_id_map
        # check to see if a value isn't assigned to multiple keys.
        if len(self.patient_id_map.values()) != len(set(self.patient_id_map.values())):
            raise DeindentError('One or more values of the patient_id_map match to multiple keys.')

    def __call__(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:  # noqa: ARG002
        if field.name not in ('PatientName', 'PatientID'):
            raise DeindentError(f'{field.name} not supported.')

        if dicom.PatientID not in self.patient_id_map:
            # PatientID not found in lookup table keys, so maybe it got changed already.
            # Check if the PatientID is present as a value, this means it has been changed and return the value.
            # This all assumes there is a unique relation between key and value. No key can have more than one value
            # and each value can only be matched to one key
            if dicom.PatientID not in self.patient_id_map.values():
                raise DeindentError(f'{dicom.PatientID} not in present in lookup table')
            return cast('str', dicom.PatientID)

        return self.patient_id_map[dicom.PatientID]

    @classmethod
    def load_file(cls, filename: Path, original_column: str | int, new_column: str | int) -> Self:
        """ Load a CSV with patient ID mapping. """
        try:
            df = pd.read_csv(filename, dtype=str)
        except pd.errors.ParserError:
            try:
                df = pd.read_excel(filename, dtype=str)
            except pd.errors.ParserError as e:
                raise DeindentError(f'Could not parse {filename}') from e

        if isinstance(original_column, int):
            original_column = df.columns[original_column]

        if isinstance(new_column, int):
            new_column = df.columns[new_column]

        if isinstance(original_column, str) and original_column not in df.columns:
            raise DeindentError(f'Could find column {original_column}')

        if isinstance(original_column, str) and new_column not in df.columns:
            raise DeindentError(f'Could find column {new_column}')

        df = df[[original_column, new_column]]
        # https://stackoverflow.com/questions/66886081/create-a-dictionary-from-dataframe-with-first-column-as-keys-and-remaining-as-va
        data = df.set_index(original_column).aggregate(' '.join, axis=1).to_dict()
        return cls(data)
