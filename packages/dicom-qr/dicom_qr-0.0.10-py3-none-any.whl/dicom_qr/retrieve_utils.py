""" Utilities used by the RetrievePacs classes. """

from __future__ import annotations

import dataclasses
import enum
import typing

from loguru import logger


if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    import pydicom
    from pydicom import Dataset


class DicomStatus(enum.Enum):
    """
    [DICOM C-MOVE status codes](https://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_c.4.2.html)
    """
    OUT_OF_RESOURCES_UNABLE_TO_CALCULATE_NUMBER_OF_MATCHES = 0xA701
    """ Out of resources - Unable to calculate number of matches. """
    OUT_OF_RESOURCES_UNABLE_TO_PERFORM_SUB_OPERATIONS = 0xA702
    """ Out of resources - Unable to perform sub-operations. """
    MOVE_DESTINATION_UNKNOWN = 0xA801
    """ Move Destination unknown. """
    DATASET_DOESNT_MATCH_SOP_CLASS = 0xA900
    """ Data Set does not match SOP Class. """
    SUB_OPERATIONS_COMPLETE_ONE_OR_MORE_FAILURES = 0xB000
    """ Sub-operations Complete - One or more Failures. """
    FAILED_UNABLE_TO_PROCESS = 0xC000
    """ Unable to process. """
    CANCEL = 0xFE00
    """ Cancel. """
    SUCCESS = 0x0000
    """ Sub-operations Complete - No Failures. """
    PENDING = 0xFF00
    """ Sub-operations are continuing. """
    UNKNOWN = 0x1234
    """ Unknown. """


DicomStatusFailure = [
    DicomStatus.OUT_OF_RESOURCES_UNABLE_TO_CALCULATE_NUMBER_OF_MATCHES,
    DicomStatus.OUT_OF_RESOURCES_UNABLE_TO_PERFORM_SUB_OPERATIONS,
    DicomStatus.MOVE_DESTINATION_UNKNOWN,
    DicomStatus.DATASET_DOESNT_MATCH_SOP_CLASS,
    DicomStatus.SUB_OPERATIONS_COMPLETE_ONE_OR_MORE_FAILURES,
    DicomStatus.CANCEL
]


def process_responses(responses: Iterator[tuple[Dataset, Dataset | None]],
                      retrieve_callback: Callable[[RetrieveResult], None]) -> RetrieveResult:
    """ Process the retrieve responses. """
    result = RetrieveResult()
    for response, response_dataset in responses:
        try:
            result.status = DicomStatus(response.Status)
        except AttributeError:
            continue
        except ValueError as e:
            logger.warning(f'Unknown status: {e}')

        result.update(response)
        retrieve_callback(result)

        if response_dataset is None:
            continue

        if result.status in DicomStatusFailure:
            raise RetrieveError(response)

        if result.status == DicomStatus.SUCCESS:
            logger.debug('Success')

        if result.status == DicomStatus.CANCEL:
            logger.warning('Cancelled')

    if result.status not in [DicomStatus.SUCCESS, DicomStatus.CANCEL]:
        logger.warning(f'Responses finished without SUCCESS or CANCEL status. Last status: "{result.status.name}".')

    return result


@dataclasses.dataclass
class RetrieveResult:
    """ The result of a retrieve operation. """
    status: DicomStatus = DicomStatus.UNKNOWN
    """ Status of the retrieve operation. """
    completed: int | None = None
    """ Completed sub-operations. """
    failed: int | None = None
    """ Failed sub-operations. """
    remaining: int | None = None
    """ Remaining sub-operations. """
    warning: int | None = None
    """ Warnings. """

    def update(self, dataset: pydicom.Dataset) -> None:
        """ Update. """
        if hasattr(dataset, 'NumberOfCompletedSuboperations'):
            self.completed = dataset.NumberOfCompletedSuboperations
        if hasattr(dataset, 'NumberOfFailedSuboperations'):
            self.failed = dataset.NumberOfFailedSuboperations
        if hasattr(dataset, 'NumberOfRemainingSuboperations'):
            self.remaining = dataset.NumberOfRemainingSuboperations
        if hasattr(dataset, 'NumberOfWarningSuboperations'):
            self.warning = dataset.NumberOfWarningSuboperations


class RetrieveError(Exception):
    """ Exception raised when a retrieve operation fails. """
    def __init__(self, response: pydicom.Dataset) -> None:
        super().__init__('Error performing retrieve')
        self.response = response


class AssociationError(Exception):
    """ Exception raised when an association operation fails. """
