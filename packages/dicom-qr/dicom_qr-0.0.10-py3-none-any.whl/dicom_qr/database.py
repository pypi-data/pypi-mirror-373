""" Datatypes and objects. """
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import typing
from typing import Any

from pydantic import BaseModel, field_validator, Field
from pydicom.valuerep import PersonName

if typing.TYPE_CHECKING:
    from datetime import datetime, timedelta


# pylint: disable=too-few-public-methods
class SeriesData(BaseModel):
    """ Info for DICOM series. """
    StudyInstanceUID: str = 'NA'
    """ StudyInstanceUID """
    SeriesInstanceUID: str = 'NA'
    """ SeriesInstanceUID """
    Modality: str = 'NA'
    """ Modality """
    SeriesNumber: int | None = None
    """ SeriesNumber """
    SeriesDescription: str = 'NA'
    """ SeriesDescription """
    ProtocolName: str = 'NA'
    """ ProtocolName """

    def __str__(self) -> str:
        return f'{self.Modality}, "{self.SeriesDescription}"'

    def __repr__(self) -> str:
        return self.SeriesInstanceUID


# noinspection PyNestedDecorators
class StudyData(BaseModel):
    """ Info for DICOM studies. """
    StudyInstanceUID: str = 'NA'
    """ StudyInstanceUID """
    PatientID: str = 'NA'
    """ PatientID """
    PatientName: str = 'NA'
    """ PatientName """
    PatientSex: str = 'NA'
    """ PatientSex """
    PatientBirthDate: str = 'NA'
    """ PatientBirthDate """
    StudyID: str = 'NA'
    """ StudyID """
    StudyDate: str = 'NA'
    """ StudyDate """
    StudyDescription: str = 'NA'
    """ StudyDescription """
    StudyTime: str = 'NA'
    """ StudyTime """
    AccessionNumber: str = 'NA'
    """ AccessionNumber """
    BodyPartExamined: str = 'NA'
    """ BodyPartExamined """
    ModalitiesInStudy: list[str] = Field(default_factory=list)
    """ ModalitiesInStudy """
    series: list[SeriesData] = Field(default_factory=list)
    """ series """

    def __str__(self) -> str:
        return f'{self.PatientID}, "{self.StudyID}", {self.StudyDescription}'

    def __repr__(self) -> str:
        return f'{self.StudyDate}, {self.StudyDescription}, {self.StudyInstanceUID}'

    @field_validator('PatientName', mode='before')
    @classmethod
    def set_patient_name(cls, value: PersonName | str) -> str:
        """ Validator to decode the patient name from PersonName. """
        if isinstance(value, PersonName):
            if value.original_string is None:
                return ''
            return value.original_string.decode('utf-8')
        return str(value)

    @field_validator('ModalitiesInStudy', mode='before')
    @classmethod
    def modalities_in_study_is_list(cls, value: str | list) -> list[str]:
        """ Validator to make sure the ModalitiesInStudy is a list. """
        if isinstance(value, str):
            return [value]
        return list(value)


class SeriesUidMap:
    """ Map a SeriesInstanceUID to an index. """
    def __init__(self, series: list[SeriesData]) -> None:
        num_series = len(series) + 1
        num_digits = 1 if num_series == 0 else math.ceil(math.log10(num_series))
        self.series_uid_map = {serie.SeriesInstanceUID: f'{index:0{num_digits}}' for index, serie in enumerate(series, 1)}

    def uid_map(self, series_uid: str) -> str:
        """
        Get the index for an UID.
        :param series_uid: SeriesInstanceUID
        :return: index
        """
        return self.series_uid_map[series_uid]


class Status(Enum):
    """ Download status codes. """
    OK = auto()
    """ Everything went ok. """
    ERROR = auto()
    """ An error occured. """
    NO_DATA = auto()
    """ No data found. """
    UNKNOWN = auto()
    """ Unknown error. """


@dataclass(order=True)
class ExportInfo:
    """ The results of a download action. """
    series_uid: str = 'NA'
    """ SeriesInstanceUID downloaded. """
    study_uid: str = 'NA'
    """ StudyInstanceUID downloaded. """
    status: Status = Status.UNKNOWN
    """ Download status."""
    destination: Path = Path()
    """ Download location. """
    start: datetime | None = None
    """ Start of download action. """
    end: datetime | None = None
    """ End of download action. """

    def __post_init__(self) -> None:
        assert ('.' in self.series_uid or self.series_uid == 'NA')

    def to_dict(self) -> dict[str, Any]:
        """ Convert to dictionary. """
        return {
            'StudyInstanceUID': self.study_uid,
            'SeriesInstanceUID': self.series_uid,
            'Start': self.start,
            'End': self.end,
            'Destination': self.destination,
            'Status': self.status,
        }

    @classmethod
    def convert(cls, data: SeriesData) -> ExportInfo:
        """ Convert a SeriesData to an ExportInfo. """
        return cls(study_uid=data.StudyInstanceUID, series_uid=data.SeriesInstanceUID)

    @staticmethod
    def column_names() -> list[str]:
        """ Get the column names. """
        return list(ExportInfo().to_dict().keys())

    def duration(self) -> timedelta | None:
        """ Get the duration of the export. """
        if self.start is None or self.end is None:
            return None
        return self.end - self.start
