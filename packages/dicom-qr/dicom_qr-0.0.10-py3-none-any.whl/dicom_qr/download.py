import time
import typing
from datetime import datetime
from pathlib import Path
from collections.abc import Callable, Iterable, Sequence

import pandas as pd
from lkeb_progress import RichProgressObject
from loguru import logger

from dicom_qr.console_output import create_series_table, create_studies_table
from dicom_qr.database import ExportInfo, SeriesData, SeriesUidMap, Status
from dicom_qr.logger import console
from dicom_qr.query import QueryPacs
from dicom_qr.retrieve import get_retrieve
from dicom_qr.retrieve_utils import RetrieveError, RetrieveResult
from dicom_qr.scp import Anonymizer, dummy_anonymize, dummy_filename_callback
from dicom_qr.search import SearchTerms
from dicom_qr.settings import DISABLE_PROGRESS, PacsConfig, get_settings

if typing.TYPE_CHECKING:
    import rich.progress


class FoldernameCallback:  # pylint: disable=too-few-public-methods
    """ Store the folder name from the scp.handle_store callback"""

    def __init__(self) -> None:
        self.folder = Path()

    def filename_callback(self, folder: Path) -> None:
        """ Store the filename """
        self.folder = folder


class RetrieveProgress:  # pylint: disable=too-few-public-methods
    """ Pass progress from scp.handle_store callback to RichProgressObject. """

    def __init__(self, progress: RichProgressObject) -> None:
        self.progress_object = progress
        self.task_id: rich.progress.TaskID | None = None

    def progress(self, result: RetrieveResult) -> None:
        """ progress callback """
        assert result.completed is not None
        assert result.remaining is not None

        self.progress_object.set_progress_count(result.completed, result.completed + result.remaining, self.task_id)


def _process_serie(retrieve: Callable[[SeriesData], None], serie: SeriesData) -> ExportInfo:
    data = ExportInfo.convert(serie)
    data.start = datetime.now()
    try:
        time.sleep(2)
        retrieve(serie)
    except RetrieveError:
        data.status = Status.ERROR
    else:
        data.status = Status.OK
    data.end = datetime.now()
    return data


def from_accession_number(
        accession_number: str,
        modalities: Sequence[str] | None,
        retrieve_callback: Callable[[RetrieveResult], None],
        settings: PacsConfig,
        sop_class_uid: Iterable[str] | None,
        verbose: bool) -> list[SeriesData]:
    """ Download all series from accession number.
    :param accession_number: the accession number to process.
    :param modalities: optional list of modalities to filter series by.
    :param retrieve_callback: progress callback.
    :param settings: settings
    :param sop_class_uid: optional list of SOPClassUIDs to filter series by.
    :param verbose: more debugging.
    :return: list of downloaded series.
    """
    series: list[SeriesData] = []
    with RichProgressObject(disable=DISABLE_PROGRESS, console=console) as progress:
        with QueryPacs(settings) as query:
            studies = query.get_studies(SearchTerms(accession_number=accession_number, modalities=modalities))
            studies_task = progress.add_task('[red]Studies...', total=len(studies))

            if verbose:
                create_studies_table(studies, columns=settings.study_columns)

            for study in studies:
                progress.update(studies_task, description=f'[green]StudyID: {study.StudyID}')
                progress.advance(studies_task)
                series.extend(query.get_series_for_study(study.StudyInstanceUID, modalities=modalities))
            progress.stop_task(studies_task)
            progress.remove_task(studies_task)

            if verbose:
                progress.print(create_series_table(series))

        if len(series) == 0:
            return series

        prog_obj = RetrieveProgress(progress)

        with get_retrieve(settings, SeriesUidMap(series).uid_map, dummy_filename_callback, retrieve_callback,
                          dummy_anonymize,
                          sop_class_uid=sop_class_uid) as retrieve:
            series_task = progress.add_task('[green]Series...')
            progress.update(series_task, total=len(series))
            for serie in series:
                prog_obj.task_id = progress.add_task('[yellow]Files...')
                progress.advance(series_task)
                retrieve.retrieve_images_for_a_series(serie)
                progress.stop(prog_obj.task_id)

            progress.stop(series_task)

    return series


def from_study_uid_list(
        study_uids: Sequence[str],
        output_filename: Path | None,
        modalities: Sequence[str] | None,
        sop_class_uid: Iterable[str] | None,
        settings: PacsConfig) -> None:
    """ Download all series from accession number.
    :param study_uids: the study UIDs to process.
    :param output_filename: CVS output of downloaded series.
    :param modalities: optional list of modalities to filter series by.
    :param sop_class_uid: ptional list of SOPClassUIDs to filter series by.
    :param settings: settings
    :return: None
    """
    processed = pd.DataFrame(columns=ExportInfo.column_names())

    callback = FoldernameCallback()

    with RichProgressObject(disable=DISABLE_PROGRESS) as progress:
        progress.set_progress_count(0, len(study_uids))
        study_uid: str
        for idx, study_uid in enumerate(study_uids):
            progress.set_progress_text(f'[red]Study: {study_uid}')
            with QueryPacs(settings) as query:
                series = query.get_series_for_study(study_uid, modalities=modalities)

            if len(series) == 0:
                processed.loc[len(processed)] = ExportInfo(  # type: ignore
                    study_uid=study_uid, start=datetime.now(), end=datetime.now(), status=Status.NO_DATA).to_dict()
                processed.to_csv(output_filename, index=False)
                continue

            prog_obj = RetrieveProgress(progress)

            with get_retrieve(
                    settings,
                    SeriesUidMap(series).uid_map,
                    callback.filename_callback,
                    prog_obj.progress,
                    dummy_anonymize,
                    sop_class_uid=sop_class_uid) as retrieve:
                task_id = progress.add_task('[green]Series...', total=len(series))
                for serie in series:
                    prog_obj.task_id = progress.add_task('[yellow]Files...')

                    logger.debug(f'Processing {serie}')
                    data = _process_serie(retrieve.retrieve_images_for_a_series, serie)
                    data.destination = callback.folder
                    processed.loc[len(processed)] = data.to_dict()  # type: ignore
                    progress.advance(task_id)
                    progress.stop(prog_obj.task_id)
                progress.stop(task_id)

            processed.to_csv(output_filename, index=False)
            progress.set_progress_count(idx, len(study_uids))


def from_search(
        search_terms: SearchTerms,
        anonymizer: Anonymizer,
        folder_callback: Callable[[Path], None],
        dumpdir: Path | None,
        sop_class_uid: Iterable[str] | None = None) -> list[SeriesData]:
    """ Download all series specified by search terms.
    :param search_terms: the search terms to process.
    :param anonymizer: Anonymizer to anonymize the dataset.
    :param folder_callback: Callback function for returning the final path.
    :param dumpdir: optional list of SOPClassUIDs to filter series by.
    :param sop_class_uid: optional alternative output directory. if not provided, use default specified in the settings.
    :return: list of series
    """
    settings = get_settings()
    if dumpdir is not None:
        settings.base_folder = dumpdir

    with RichProgressObject(console=console) as progress:
        with QueryPacs(settings) as query:
            studies = query.get_studies(search_terms)

            series = []
            for study in studies:
                series.extend(query.get_series_for_study(study.StudyInstanceUID, modalities=None))

        prog_obj = RetrieveProgress(progress)

        with get_retrieve(
                settings,
                SeriesUidMap(series).uid_map,
                folder_callback,
                prog_obj.progress,
                anonymizer,
                sop_class_uid=sop_class_uid) as retrieve:
            progress.set_progress_count(0, len(series))
            progress.set_progress_text('[green]Series...')
            for serie in series:
                prog_obj.task_id = progress.add_task('[yellow]Files...')
                progress.set_progress_text(f'[green]Series: {serie.SeriesNumber}')
                retrieve.retrieve_images_for_a_series(serie)
                progress.stop(prog_obj.task_id)

        return series
