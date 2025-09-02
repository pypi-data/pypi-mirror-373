from __future__ import annotations

import enum
import os
import typing
from pathlib import Path

import jsonpickle
import rich
import rich.console
from loguru import logger
from pydantic import BaseModel, field_validator, Field
from pydantic.dataclasses import dataclass
from devtools import pformat


DISABLE_PROGRESS = False


class StudyColumns(str, enum.Enum):
    """ Options for StudyColumns """
    INDEX = 'Index'
    """ Index """
    STUDY_UID = 'StudyInstanceUID'
    """ StudyInstanceUID """
    STUDY_DESCRIPTION = 'StudyDescription'
    """ StudyDescription """
    STUDY_DATE = 'StudyDate'
    """ StudyDate """
    PATIENT_ID = 'PatientID'
    """ PatientID """
    PATIENT_SEX = 'PatientSex'
    """ PatientSex """
    PATIENT_NAME = 'PatientName'
    """ PatientName """
    PATIENT_BIRTHDATE = 'PatientBirthDate'
    """ PatientBirthDate """
    ACCESSION_NUMBER = 'AccessionNumber'
    """ AccessionNumber """
    MODALITIES = 'ModalitiesInStudy'
    """ ModalitiesInStudy """
    BODYPARTEXAMINED = 'BodyPartExamined'
    """ BodyPartExamined """


class SeriesColumns(str, enum.Enum):
    """ Options for SeriesColumns """
    INDEX = 'Index'
    """ Index """
    STUDYINSTANCEUID = 'StudyInstanceUID'
    """ StudyInstanceUID """
    SERIESINSTANCEUID = 'SeriesInstanceUID'
    """ SeriesInstanceUID """
    MODALITY = 'Modality'
    """ Modality """
    SERIESNUMBER = 'SeriesNumber'
    """ SeriesNumber """
    SERIESDESCRIPTION = 'SeriesDescription'
    """ SeriesDescription """
    PROTOCOLNAME = 'ProtocolName'
    """ ProtocolName """


@dataclass
class ColumnLayout:
    """ Options for ColumnLayout """
    name: StudyColumns | SeriesColumns
    """ Column name """
    justify: rich.console.JustifyMethod = 'right'
    """ justify method """
    no_wrap: bool = False
    """ wrapping """


class DicomTransferMethod(enum.Enum):
    """ DICOM transfer method (C-MOVE or C-GET)"""
    GET = 'get'
    """ C-GET """
    MOVE = 'move'
    """ C-MOVE """


class PacsConfig(BaseModel):
    """ Config for PACS communication """
    server_ae_title: str = 'ANY-SCP'
    """ Server (called) Application Entity Title (AET) """
    server_ae_ip: str = 'localhost'
    """ Server IP/hostname """
    server_ae_port: int = 8000
    """ Server (called) port """
    client_ae_title: str = ''
    """ Client (caller) Application Entity Title (AET) """
    client_ae_port: int = 0
    """ Client port """
    transfer_method: DicomTransferMethod = DicomTransferMethod.MOVE
    """ Transfer method """
    base_folder: Path = Path('dumpdir')
    """ Base folder for download """
    folder_template: str = '${PatientID}/${StudyDate}/${StudyDescription}/${Modality}/${FolderUID}_${SeriesDescription}'
    """ Relative path to base_folder for download."""
    study_columns: list[ColumnLayout] | None = Field(default=None)
    """ Study columms to print/display """
    series_columns: list[ColumnLayout] | None = Field(default=None)
    """ Series columms to print/display """

    # noinspection PyMethodParameters
    @field_validator('server_ae_port', 'client_ae_port', mode='before')
    def set_port(cls, value: object) -> int:  # type: ignore # pylint: disable=no-self-argument
        """ Validator to check the port is of type int """
        if not isinstance(value, int):
            raise TypeError('Port number is not an int.')
        return value

    @classmethod
    def load(cls, _filename: Path | str) -> typing.Self:
        """ Load PACS configuration from file """
        if not Path(_filename).exists():
            raise RuntimeError(f'Settings file "{Path(_filename).absolute().resolve()}" does not exist.')

        with Path(_filename).open('r', encoding='utf-8') as settings_file:
            setting = cls(**jsonpickle.decode(settings_file.read()))

        assert isinstance(setting.server_ae_port, int)
        assert isinstance(setting.client_ae_port, int)

        return setting


def get_settings_filename(filename: Path) -> Path:
    """ Determine path of settings file.

    Search strategy:

    1. *'DICOM_QR_SETTINGS'* environment value
    2. *'settings.json'* in current directory
    3. *'~/.config/dicom_qr/settings.json'*
    """
    if 'DICOM_QR_SETTINGS' in os.environ:
        filename = Path(os.environ['DICOM_QR_SETTINGS'])
        if filename.exists():
            return filename

        logger.warning(f'File "{filename}", specified by environment variable, could not be found.')

    if filename.exists():
        return filename

    filename = Path.home() / '.config/dicom_qr/settings.json'
    if filename.exists():
        return filename

    raise RuntimeError('Settings file could not be found. ')


def get_settings(filename: Path = Path('settings.json')) -> PacsConfig:
    """ Get the settings object, uses ['get_settings_filename'][dicom_qr.settings.get_settings_filename]
    to determine final filename used. """
    filename = get_settings_filename(filename)

    logger.debug(f'Loading settings from "{filename.absolute()}".')
    _config = PacsConfig.load(filename)
    assert _config
    logger.debug(pformat(_config))
    return _config
