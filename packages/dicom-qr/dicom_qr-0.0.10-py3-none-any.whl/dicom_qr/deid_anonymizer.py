from __future__ import annotations

import dataclasses
import datetime
import hashlib
import typing
import pprint
from typing import cast

from deid.config import DeidRecipe
from deid.dicom import DicomCleaner
from deid.dicom.parser import DicomParser
from deid.logger import bot
from deid.logger.message import ERROR
from loguru import logger
import pydicom

import pydicom.valuerep

from dicom_qr.deident_tools import PatientDeident, UidDeident, PatientComments, DeindentError

if typing.TYPE_CHECKING:
    from pathlib import Path
    from deid.dicom.fields import DicomField


VR_MAX_LENGTH = {
    pydicom.valuerep.VR.IS: 12,
    pydicom.valuerep.VR.SH: 16,
    pydicom.valuerep.VR.CS: 16,
    pydicom.valuerep.VR.DS: 16,
    pydicom.valuerep.VR.LO: 64,
    pydicom.valuerep.VR.UI: 64,
    pydicom.valuerep.VR.ST: 1024,
}
CODE_MEANING = {
    '113100': 'Basic Application Confidentiality Profile',
    '113101': 'Clean Pixel Data Option',
    '113102': 'Clean Recognizable Visual Features Option',
    '113103': 'Clean Graphics Option',
    '113104': 'Clean Structured Content Option',
    '113105': 'Clean Descriptors Option',
    '113106': 'Retain Longitudinal Temporal Information Full Dates Option',
    '113107': 'Retain Longitudinal Temporal Information Modified Dates Option',
    '113108': 'Retain Patient Characteristics Option',
    '113109': 'Retain Device Identity Option',
    '113110': 'Retain UIDs Option',
    '113111': 'Retain Safe Private Option',
}
DEFAULT_DATE_OFFSET = -1764  # Days
DEFAULT_TIME_OFFSET = 42  # Minutes


@dataclasses.dataclass
class Options:  # pylint: disable=too-many-instance-attributes
    """ Deidentification options """
    recipe_path: Path
    """ recipe path """
    secret_salt: str | None = None
    """ salt applied to SHA512 hash """
    date_offset: int = DEFAULT_DATE_OFFSET  # Days
    """ date offset """
    time_offset: int = DEFAULT_TIME_OFFSET  # Minutes
    """ time offset """
    verbose: bool = False
    """ verbose """
    very_verbose: bool = False
    """ very verbose """
    xnat_project: str | None = None
    """ XNAT project"""
    xnat_prefix: str | None = None
    """ XNAT subject prefix """
    patient_deident: PatientDeident | None = None
    """ Patien ID lookup """
    uid_deident: UidDeident | None = None
    """ UID lookup """
    patient_comments: PatientComments | None = None
    """ Patient comments callback """
    pixel_anonymize: bool = False
    """ pixel anonymization """


class DeidAnonymizer:
    """This class allows to pseudonymize an instance of pydicom.Dataset with our custom recipe and functions. """
    def __init__(self, options: Options) -> None:
        bot.level = ERROR
        self.options = options

        if not self.options.recipe_path.exists():
            raise FileNotFoundError(f"Recipe path {self.options.recipe_path} does not exist")

        self.recipe = DeidRecipe(self.options.recipe_path)

        has_filter = 'filter' in self.recipe.deid and len(self.recipe.deid['filter']) > 0
        has_header = 'header' in self.recipe.deid and len(self.recipe.deid['header']) > 0

        if not (has_filter or has_header):
            raise DeindentError('Empty recipe.')

        self.uid_map: dict[str, str] = {}

        if self.options.very_verbose:
            logger.debug(pprint.pformat(self.recipe.deid))

    def __str__(self) -> str:
        return pprint.pformat(self.recipe.deid)

    # noinspection PyPep8Naming
    def pseudonymize(self, dataset: pydicom.Dataset, *, strip_sequences: bool = False, remove_private: bool = True
                     ) -> pydicom.Dataset:
        """Pseudonymize a single dicom dataset. """
        parser = DicomParser(dataset, self.recipe)

        # Functions
        parser.define('patient_id_lookup', self.patient_id_lookup)
        parser.define('hash_func', self.hash_func)
        parser.define('generate_uid', self.generate_uid)
        parser.define('date_time_jitter', self.date_time_jitter)
        if self.options.patient_comments:
            parser.define('patient_comments', self.options.patient_comments)
        # Values
        parser.define('date_offset', self.options.date_offset)
        parser.define('deident_code_seq', '113100/113107/113108/113109')
        # parse the dataset and apply the deidentification
        parser.parse(strip_sequences=strip_sequences, remove_private=remove_private)

        ds = cast('pydicom.Dataset', parser.dicom)

        ds.DeidentificationMethodCodeSequence = pydicom.Sequence()
        codes = parser.lookup['deident_code_seq'].split('/')
        for code in codes:
            codeseq = pydicom.Dataset()
            codeseq.CodeValue = code
            codeseq.CodingSchemeDesignator = 'DCM'
            codeseq.CodeMeaning = CODE_MEANING[code]

            ds.DeidentificationMethodCodeSequence.append(codeseq)

        return ds

    def pixel_anonymize(self, dataset: pydicom.Dataset) -> pydicom.Dataset:
        """
        Perform pixel anonymization on a single dicom dataset.
        :param dataset: DICOM dataset
        :return: anonymized DICOM dataset
        """
        client = DicomCleaner(deid=self.options.recipe_path)
        results = client.detect(dataset)
        if 'flagged' in results and results['flagged']:
            client.clean()

            cleaned = dataset.copy()
            if cleaned.file_meta.TransferSyntaxUID.is_compressed:
                cleaned.decompress()
            cleaned.PixelData = client.cleaned.tobytes()

            return cleaned

        return dataset

    # pylint: disable=unused-argument
    # All registered functions that are used in the recipe must
    # receive the arguments: `item`, `value`, `field`, `dicom` as keyword arguments
    # noinspection PyUnusedLocal
    def hash_func(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:  # noqa: ARG002
        """ Applies SHA512 to the value and truncates it to the maximum length allowed for the VR type. """
        msg = field.element.value
        assert isinstance(msg, str), f'value is not of type str, {type(msg)}'
        h = hashlib.sha512()
        if self.options.secret_salt:
            bytes_str = bytes(f'{self.options.secret_salt}{msg}', 'utf-8')
        else:
            bytes_str = bytes(msg, 'utf-8')
        h.update(bytes_str)
        try:
            max_length = VR_MAX_LENGTH[pydicom.valuerep.VR(field.element.VR)]
            return str(h.hexdigest())[:max_length]
        except KeyError:
            return str(h.hexdigest())

    # noinspection PyUnusedLocal
    def date_time_jitter(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:  # noqa: ARG002
        """ Apply date/time offsets. """
        vr = pydicom.valuerep.VR[field.element.VR]
        if vr == pydicom.valuerep.VR.DA:
            if field.element.value == '':
                return '19700101'

            date = datetime.datetime.strptime(field.element.value, '%Y%m%d')
            date = date + datetime.timedelta(days=self.options.date_offset)
            return date.strftime('%Y%m%d')

        if vr == pydicom.valuerep.VR.TM:
            if field.element.value == '':
                return '000000'

            try:
                time = datetime.datetime.strptime(field.element.value, '%H%M%S.%f')
            except ValueError:
                time = datetime.datetime.strptime(field.element.value, '%H%M%S')
            time = time + datetime.timedelta(minutes=self.options.time_offset)
            return time.strftime('%H%M%S.%f')

        if vr == pydicom.valuerep.VR.DT:
            dt = datetime.datetime.strptime(field.element.value, '%Y%m%d%H%M%S.%f')
            dt = dt + datetime.timedelta(days=self.options.date_offset, minutes=self.options.time_offset)
            return dt.strftime('%Y%m%d%H%M%S.%f')

        # skip all other VR types
        return cast('str', field.element.value)

    # noinspection PyUnusedLocal
    def patient_id_lookup(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:
        """ Calls the Patient de-identification method provided in the constructor options variable. """
        if not self.options.patient_deident:
            return cast('str', field.element.value)

        return self.options.patient_deident(item, value, field, dicom)

    # noinspection PyUnusedLocal
    def generate_uid(self, item: dict, value: str, field: DicomField, dicom: pydicom.Dataset) -> str:
        """ Calls the UID de-identification method provided in the constructor options variable. """
        if not self.options.uid_deident:
            raise DeindentError('no uid_deindent defined')
        return self.options.uid_deident(item, value, field, dicom)
    # pylint: enable=unused-argument
