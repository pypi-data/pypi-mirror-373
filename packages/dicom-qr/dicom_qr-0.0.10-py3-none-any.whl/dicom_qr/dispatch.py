import logging
from collections import defaultdict
from contextlib import nullcontext
from datetime import datetime
from importlib import metadata
from pathlib import Path

import pandas as pd
import pydicom
import pydicom.errors
import rich
import rich.box
import rich.progress
import rich.traceback
import typer
from loguru import logger
from rich.table import Table

from lkeb_progress import RichProgressObject

import dicom_qr.store
import dicom_qr.echo
import dicom_qr.download as dl
from dicom_qr.retrieve_utils import RetrieveError
from dicom_qr.tui.pacs_app import PacsApp
from dicom_qr.deident_tools import BasicUidDeident, DeindentError, PatientLookupDeident
from dicom_qr.retrieve import get_retrieve
from dicom_qr.store import StorePacs
from dicom_qr.settings import get_settings_filename, get_settings, DISABLE_PROGRESS
from dicom_qr.logger import setup_logging, console
from dicom_qr.search import SearchTerms
from dicom_qr.database import StudyData, SeriesData, SeriesUidMap
from dicom_qr.query import QueryPacs
from dicom_qr.scp import dummy_anonymize, dummy_filename_callback, dummy_retrieve_progress, get_prefix
from dicom_qr.console_output import create_series_table, create_studies_table
from dicom_qr.deident import DeidFilter
from dicom_qr.deid_anonymizer import DEFAULT_DATE_OFFSET, DEFAULT_TIME_OFFSET, Options, DeidAnonymizer

app = typer.Typer(add_completion=False, no_args_is_help=True, help='DICOM Query & Retrieve tool.')

CURRENT_DATE = datetime.now().date().strftime("%Y-%m-%d")

ORG_ROOT = "1.2.840.113654.2.70.1."  # must end with .


def validate_accession_number(accession_number: str) -> str:
    """ Make sure the accession number has 16 characters. Pad or crop if necessary. Required for LUMC Sectra PACS. """
    if len(accession_number) < 16:
        return accession_number.zfill(16)

    if len(accession_number) > 16:
        return accession_number[-16:]

    return accession_number


def get_accession_numbers(filename: Path) -> list[str]:
    """ Read the accession numbers from CSV file, look for column named 'AccessionNumber' or 'Accessionnummer'. """
    df = pd.read_csv(filename, dtype=str)
    df_keys = ['AccessionNumber', 'Accessionnummer']
    accession_numbers: list[str] = []
    for key in df_keys:
        if key in df:
            accession_numbers = df[key].to_list()
            break
    else:
        logger.error(f'Could not find accession_number in file, supported column names: {df_keys}')

    return [validate_accession_number(x) for x in accession_numbers]


@app.command(rich_help_panel='UI')
def tui(settings_file: Path = typer.Argument('settings.json', exists=False, file_okay=True, dir_okay=False,
                                             readable=True) ) -> None:
    """ Start the TUI."""
    PacsApp(settings_file).run()


@app.command(rich_help_panel='Query')
def list_series_for_study(
        study_uid: str = typer.Argument(..., help='StudyInstanceUID'),
        modalities: list[str] | None = typer.Argument(None),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> list[SeriesData]:
    """ Get the series for a study. """
    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    settings = get_settings()
    with QueryPacs(settings) as query:
        series = query.get_series_for_study(study_uid, modalities)

    if len(series) == 0:
        logger.warning('No series found.')
        return []

    rich.print(create_series_table(series, title=f'{len(series)} series found for StudyUID: {study_uid}',
                                   columns=settings.series_columns))
    return series


@app.command(rich_help_panel='Query')
def list_studies_name(
        patient_name: str = typer.Argument(..., help='Patient name to query'),
        modalities: list[str] | None = typer.Argument(None),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> defaultdict[str, list[StudyData]]:
    """ Get the studies for a patient name, filtering for modalities. """
    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    settings = get_settings()

    with QueryPacs(settings) as query:
        scans = query.get_studies_for_patient(SearchTerms(pat_name=patient_name, modalities=modalities))

    data: list[StudyData] = []
    for studies in scans.values():
        data.extend(studies)

    if len(data) == 0:
        logger.warning('No studies found.')
        return defaultdict()

    rich.print(create_studies_table(data, title=f'{len(data)} studies for patient named {patient_name}',
                                    columns=settings.study_columns))

    return scans


@app.command(rich_help_panel='Query')
def list_studies_patient_id(
        patient_id: str = typer.Argument(..., help='Patient ID to query'),
        modalities: list[str] | None = typer.Argument(None),
        study_descriptions: str | None =
        typer.Option(None, '--study_descr', '-d', help='Study description for filtering'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> \
        defaultdict[str, list[StudyData]]:
    """ Get the studies for a patient ID, filtering for modalities. """
    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    if isinstance(study_descriptions, typer.models.ParameterInfo):
        study_descriptions = study_descriptions.default

    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)
    settings = get_settings()

    with QueryPacs(settings) as query:
        studies = query.get_studies_for_patient(
            SearchTerms(patid=patient_id, modalities=modalities, study_desc=study_descriptions))

    data: list[StudyData] = []
    for study in studies.values():
        data.extend(study)

    if len(data) == 0:
        logger.warning('No studies found.')
        return defaultdict()

    rich.print(
        create_studies_table(data, title=f'{len(data)} studies for patient id {patient_id}', columns=settings.study_columns))

    return studies


@app.command(rich_help_panel='Query')
def list_studies_accession_number(
        accession_number: str = typer.Argument(..., help='Accession number (16 characters).'),
        modalities: list[str] | None = typer.Argument(None),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> list[StudyData]:
    """ List the studies for an accession number, filtering for modalities. """
    if isinstance(modalities, typer.models.ArgumentInfo):
        modalities = modalities.default

    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)
    settings = get_settings()

    with QueryPacs(settings) as query:
        studies = query.get_studies(
            SearchTerms(accession_number=validate_accession_number(accession_number), modalities=modalities))

    if len(studies) == 0:
        logger.warning('No studies found.')
        return []

    rich.print(create_studies_table(studies, title=f'{len(studies)} studies for accession number {accession_number}',
                                    columns=settings.study_columns))

    return studies


@app.command(rich_help_panel='Query')
def list_studies_date(
        from_date: datetime = typer.Option(..., '--start', '-s',
                                           formats=["%Y-%m-%d", "%Y%m%d"], help='Start date'),
        to_date: datetime = typer.Option(CURRENT_DATE, '--end', '-e',
                                         formats=["%Y-%m-%d", "%Y%m%d"], help='End date'),
        study_descriptions: list[str] | None =
        typer.Option(None, '--study_descr', '-d',
                     help='Study description for filtering, can be used multiple times.'),
        patient_id: str | None = typer.Option(None, '--patient_id', '-p',
                                                 help='Patient ID for filtering'),
        modalities: list[str] | None =
        typer.Option(None, '--modalities', '-m',
                     help='Modalities used for filtering, can be used multiple times.'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> None:
    """ Get all studies between two dates, filtering any of the study descriptions and modalities.\n
    Does not download images.\n
    The number of responses from the PACS is limited, if no results show try more filtering
    (descriptions and/or modalities or shorten the date range).
    """
    if isinstance(study_descriptions, typer.models.ParameterInfo):
        study_descriptions = study_descriptions.default

    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    if isinstance(patient_id, typer.models.ParameterInfo):
        patient_id = patient_id.default

    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    settings = get_settings()

    with QueryPacs(settings) as query:
        if study_descriptions is None or len(study_descriptions) == 0:
            search_terms = SearchTerms(date_range=(from_date, to_date), modalities=modalities, patid=patient_id)
            studies = query.get_studies(search_terms)

            rich.print(
                create_studies_table(studies, columns=settings.study_columns,
                                     title=f'{len(studies)} studies for date {from_date:%Y-%m-%d} to {to_date:%Y-%m-%d}')
            )
            return

        studies = []
        for study_description in study_descriptions:
            search_terms = SearchTerms(
                date_range=(from_date, to_date),
                modalities=modalities,
                patid=patient_id,
                study_desc=study_description
            )
            studies.extend(query.get_studies(search_terms))

    if len(studies) == 0:
        logger.warning('No studies found.')

    rich.print(
        create_studies_table(studies, title=f'{len(studies)} studies for date {from_date:%Y-%m-%d} to {to_date:%Y-%m-%d}',
                             columns=settings.study_columns))


@app.command(rich_help_panel='Query')
def studyuid_from_acc_number_file(
        filename: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True),
        output: Path | None = typer.Argument(None, file_okay=True, dir_okay=False, readable=True),
        verbose: bool = typer.Option(False, '--verbose', '-v'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> list[StudyData]:
    """ Load a CSV file, read the column 'AccessionNumber' and write all studies to output.
    Does not download images. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    with QueryPacs(get_settings()) as query:
        subject_studies = []
        for accession_number in get_accession_numbers(filename):
            subject_studies.extend(query.get_studies(SearchTerms(accession_number=accession_number)))

    if output is not None:
        data = [(x.PatientName, x.StudyInstanceUID, x.StudyDescription) for x in subject_studies]
        pd.DataFrame(data).to_csv(output, index=False, header=['PatientName', 'StudyInstanceUID', 'Description'])

    return subject_studies


@app.command(rich_help_panel='Query')
def echo_pacs(verbose: bool = typer.Option(False, '-v', help='Print more output'),
              very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> None:
    """ Send C-ECHO to server. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)
    settings = get_settings()

    dicom_qr.echo.echo_scu(settings)

    logger.info('Success')


@app.command(rich_help_panel='Retrieve')
def download_from_patientid_date(
        patient_id: str,
        study_date: datetime = typer.Argument(..., formats=["%Y-%m-%d", "%Y%m%d"]),
        modalities: list[str] | None = typer.Option(None, '--modality', '-m',
                                                       help='Filter series based on modalities'),
        sop_class_uid: list[str] | None =
        typer.Option(None, '--sop-class-uid', '-s',
                     help='Filter series based on SOPClassUID'),
        dumpdir: Path | None =
        typer.Option(None, exists=False, file_okay=False, dir_okay=True, writable=True,
                     help='Override output folder.'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> list[SeriesData]:
    """ Download the images from the patientID and date, filtering for modalities. """
    if isinstance(dumpdir, typer.models.ParameterInfo):
        dumpdir = dumpdir.default

    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    series = dl.from_search(
        search_terms=SearchTerms(date_range=study_date.date(), patid=patient_id, modalities=modalities),
        anonymizer=dummy_anonymize,
        folder_callback=dummy_filename_callback,
        dumpdir=dumpdir,
        sop_class_uid=sop_class_uid)

    if verbose:
        rich.print(create_series_table(series))

    return series


@app.command(rich_help_panel='Retrieve')
def download_from_name_date(
        patient_name: str,
        study_date: datetime = typer.Argument(..., formats=['%Y-%m-%d', '%Y%m%d']),
        modalities: list[str] | None = typer.Option(None, '--modality', '-m',
                                                       help='Filter series based on modalities'),
        sop_class_uid: list[str] | None = typer.Option(None, '--sop-class-uid', '-s',
                                                          help='Filter series based on SOPClassUID'),
        dumpdir: Path | None = typer.Option(None, exists=False, file_okay=False, dir_okay=True,
                                               writable=True,
                                               help='Override output folder.'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> list[SeriesData]:
    """ Download the images from the patient name and date, filtering for modalities. """
    if isinstance(dumpdir, typer.models.ParameterInfo):
        dumpdir = dumpdir.default

    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    series = dl.from_search(
        SearchTerms(date_range=study_date.date(), pat_name=patient_name, modalities=modalities),
        anonymizer=dummy_anonymize,
        folder_callback=dummy_filename_callback,
        dumpdir=dumpdir,
        sop_class_uid=sop_class_uid)

    if verbose:
        rich.print(create_series_table(series))

    return series


@app.command(rich_help_panel='Retrieve')
def download_from_accession_number(
        accession_number: str = typer.Argument(..., help='Accession number.'),
        modalities: list[str] | None = typer.Option(None, '--modality', '-m', help='Filter series based on modalities'),
        sop_class_uid: list[str] | None = typer.Option(None, '--sop-class-uid', '-s',
                                                          help='Filter series based on SOPClassUID'),
        dumpdir: Path | None = typer.Option(None, exists=False, file_okay=False, dir_okay=True, writable=True,
                                               help='Override output folder.'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> list[SeriesData]:
    """ Download the images from the accession number, filtering for modalities. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)
    settings = get_settings()

    if isinstance(dumpdir, typer.models.ParameterInfo):
        dumpdir = dumpdir.default

    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    if dumpdir is not None:
        settings.base_folder = dumpdir

    if modalities is not None and len(modalities) == 0:
        modalities = None

    accession_number = validate_accession_number(accession_number)
    series = dl.from_accession_number(accession_number, modalities, dummy_retrieve_progress, settings, sop_class_uid,
                                      verbose)
    logger.debug('Finished.')
    return series


@app.command(rich_help_panel='Retrieve')
def download_from_studyuid(
        study_uid: str = typer.Argument(..., help='Study UID to download'),
        modalities: list[str] | None = typer.Option(None, '--modality', '-m', help='Filter series based on modalities'),
        sop_class_uid: list[str] | None = typer.Option(None, '--sop-class-uid', '-s',
                                                          help='Filter series based on SOPClassUID'),
        dumpdir: Path | None = typer.Option(None, exists=False, file_okay=False, dir_okay=True, writable=True,
                                               help='Override output folder.'),
        _: bool = typer.Option(False, '--no_store_scp', help='No local C_STORE SCP server.'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> list[SeriesData]:
    """ Download a study, filtering for modalities. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)
    settings = get_settings()

    if isinstance(dumpdir, typer.models.ParameterInfo):
        dumpdir = dumpdir.default

    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    if dumpdir is not None:
        settings.base_folder = dumpdir
        logger.debug(f'Setting output folder to: "{dumpdir.absolute()}"')

    if modalities is not None and len(modalities) == 0:
        modalities = None

    series = []
    with RichProgressObject(disable=DISABLE_PROGRESS, console=console) as progress:
        with QueryPacs(settings) as query:
            series.extend(query.get_series_for_study(study_uid, modalities=modalities))

        if len(series) == 0:
            logger.warning('No series found to download.')
            return series

        if verbose:
            progress.print(create_series_table(series))

        series_task = progress.add_task('[green]Series...', total=len(series))
        with get_retrieve(settings, SeriesUidMap(series).uid_map, dummy_filename_callback, dummy_retrieve_progress,
                          dummy_anonymize,
                          sop_class_uid=sop_class_uid) as retrieve:
            for serie in series:
                progress.advance(series_task)
                try:
                    retrieve.retrieve_images_for_a_series(serie)
                except RetrieveError as e:
                    logger.error(f'Failed to retrieve images for series "{serie.SeriesNumber}": {e}.')
            progress.stop_task(series_task)
            progress.remove_task(series_task)

    logger.debug('Finished.')
    return series


@app.command(rich_help_panel='Retrieve')
def download_from_studyuid_file(
        filename: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True,
                                        help='Input'),
        modalities: list[str] | None = typer.Option(None, '--modality', '-m', help='Filter series based on modalities'),
        sop_class_uid: list[str] | None = typer.Option(None, '--sop-class-uid', '-s',
                                                          help='Filter series based on SOPClassUID'),
        already_processed: Path | None = typer.Option(None, exists=True, file_okay=True, dir_okay=False, writable=False,
                                                         help='File with already processed UIDs.'),
        dumpdir: Path | None = typer.Option('dumpdir', exists=False, file_okay=False, dir_okay=True, writable=True,
                                               help='Override output folder.'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> None:
    """ Download the studies listed in file (column name: StudyInstanceUID),
    filtering for modalities and/or sop_class_uid. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    settings = get_settings()

    if isinstance(dumpdir, typer.models.ParameterInfo):
        dumpdir = dumpdir.default

    if isinstance(modalities, typer.models.ParameterInfo):
        modalities = modalities.default

    if isinstance(sop_class_uid, typer.models.ParameterInfo):
        sop_class_uid = sop_class_uid.default

    if dumpdir is not None:
        settings.base_folder = dumpdir
        logger.debug(f'Setting output folder to: "{dumpdir.absolute()}"')

    if modalities is not None and len(modalities) == 0:
        modalities = None

    if sop_class_uid is not None and len(sop_class_uid) == 0:
        sop_class_uid = None

    output_filename = Path(f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    logger.debug(f'Processed file: {output_filename}')
    study_uids = _get_uids(filename, already_processed)

    dl.from_study_uid_list(
        study_uids=study_uids,
        output_filename=output_filename,
        modalities=modalities,
        sop_class_uid=sop_class_uid,
        settings=settings)
    logger.debug('Finished.')


def _process_deident_files(input_dir: Path, output_dir: Path, options: Options) -> str:
    dicom_anonimyzer = DeidAnonymizer(options)
    dicom_filter = DeidFilter(options)

    prefix = options.xnat_prefix
    if options.xnat_prefix is None and options.xnat_project is not None:
        consonants = set('bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ')
        prefix = ''.join([x for x in options.xnat_project if x in consonants])
        logger.debug(f'{prefix=}')

    files = [x for x in input_dir.rglob('*') if x.is_file()]
    with RichProgressObject(disable=DISABLE_PROGRESS, console=console) as progress:
        progress.set_progress_text('[green]files...')
        progress.start()
        progress.set_progress_count(0, len(files))
        for index, input_filename in enumerate(files, start=1):
            progress.set_progress_text(f'[green]{input_filename.name}')
            try:
                ds: pydicom.Dataset = pydicom.dcmread(input_filename)
            except pydicom.errors.InvalidDicomError as e:
                logger.error(f'Error loading "{input_filename}". {e}')
                progress.set_progress_count(index, len(files))
                continue

            _, results = dicom_filter.check_dataset(ds)
            blacklisted = True
            for result in results:
                if result.group == 'blacklist':
                    blacklisted = False
                    logger.info(f'"{input_filename.name}" is flagged. '
                                f'filter=[italic]{result.group}[/italic], reason=\'{result.reason}\'')
                    break

            if not blacklisted:
                # Image is blacklisted, on to the next one.
                progress.set_progress_count(index, len(files))
                continue

            try:
                if options.pixel_anonymize:
                    ds = dicom_anonimyzer.pixel_anonymize(ds)
                ds = dicom_anonimyzer.pseudonymize(ds)
            except DeindentError as e:
                logger.error(f'Error de-identifying "{input_filename}". {e}')
                progress.set_progress_count(index, len(files))
                continue

            if options.xnat_project:
                ds.PatientComments = (f'Project:{options.xnat_project} Subject:{prefix}_{ds.PatientID} '
                                      f'Session:{prefix}_{ds.PatientID}_{ds.StudyDate}')

            relative_folder = input_filename.parent.relative_to(input_dir)

            (output_dir / relative_folder).mkdir(exist_ok=True, parents=True)
            pydicom.dcmwrite(output_dir / relative_folder / Path(get_prefix(ds) + ds.SOPInstanceUID + '.dcm'), ds)
            progress.set_progress_count(index, len(files))
    return str(dicom_anonimyzer)


@app.command(rich_help_panel='De-identify')
def deident_check_files(
        input_dir: Path = typer.Argument(..., exists=False, file_okay=False, dir_okay=True, writable=True,
                                         help='input folder.'),
        recipe: Path = typer.Option(None, '--recipe', '-r', help='Recipe to de-identify'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> None:
    """ Check files against the filters in the recipe and log the results. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    options = Options(
        recipe_path=Path(__file__).parent / 'deid_filter.dicom',
        verbose=verbose,
        very_verbose=very_verbose,
    )

    if recipe is not None:
        if not recipe.exists():
            logger.error(f'Recipe does not exist: {recipe}')
            return
        options.recipe_path = recipe

    dicom_filter = DeidFilter(options)

    files = [x for x in input_dir.rglob('*') if x.is_file()]
    with RichProgressObject(disable=DISABLE_PROGRESS, console=console) as progress:
        progress.set_progress_text('[green]files...')
        progress.start()
        for index, input_filename in enumerate(files, start=1):
            progress.set_progress_count(index, len(files))

            try:
                dataset: pydicom.Dataset = pydicom.dcmread(input_filename)
            except pydicom.errors.InvalidDicomError as e:
                logger.error(f'Error loading "{input_filename}". {e}')
                continue

            flagged, results = dicom_filter.check_dataset(dataset)
            if not flagged:
                continue

            for result in results:
                logger.info(
                    f'"{input_filename}" is flagged. filter=[italic]{result.group}[/italic], reason=\'{result.reason}\'')


@app.command(rich_help_panel='De-identify')
def deident_retain_patient_id_name(
        input_dir: Path = typer.Argument(..., exists=False, file_okay=False, dir_okay=True, writable=True,
                                         help='input folder.'),
        output_dir: Path = typer.Argument(..., exists=False, file_okay=False, dir_okay=True, writable=True,
                                          help='output folder.'),
        recipe: Path = typer.Option(None, '--recipe', '-r', help='Recipe to de-identify'),
        log_file: Path = typer.Option(None, '--log', '-l', help='Log UID lookup to file'),
        date_offset: int = typer.Option(None, '--date-offset', '-d', help='Date offset to de-identify'),
        xnat_project: str = typer.Option(None, '--xnat-project',
                                         help='Add PatientComments tag for importing into the correct XNAT project'),
        xnat_prefix: str = typer.Option(None, '--xnat-prefix',
                                        help='Prefix added subject and session field for XNAT'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> None:
    """ Apply de-identification keeping the existing patient name and id. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    org_root = "1.2.840.113654.2.70.1."  # must end with .
    uid_deident = BasicUidDeident(org_root)

    options = Options(
        recipe_path=Path(__file__).parent / 'deid_anonymizer.dicom',
        verbose=verbose,
        very_verbose=very_verbose,
        uid_deident=uid_deident,
        date_offset=int(date_offset) if date_offset is not None else DEFAULT_DATE_OFFSET,
        xnat_project=xnat_project,
        xnat_prefix=xnat_prefix
    )

    if recipe is not None:
        if not recipe.exists():
            logger.error(f'Recipe does not exist: {recipe}')
            return
        options.recipe_path = recipe

    config = _process_deident_files(input_dir, output_dir, options)
    if verbose or very_verbose:
        table = Table(title="UID mapping")
        table.add_column('Original UID', justify='right')
        table.add_column('New UID', justify='right')

        for org, new in dict(sorted(uid_deident.uid_map.items())).items():
            table.add_row(org, new)

        with log_file.open(mode='w', encoding='utf8') if log_file else nullcontext() as output:
            if output:
                output.write(datetime.now().isoformat() + '\n\n')
                output.write(config + '\n\n')
            rich.print(table, file=output)


@app.command(rich_help_panel='De-identify')
def deident_replace_patient_id_name(
        input_dir: Path = typer.Argument(..., exists=False, file_okay=False, dir_okay=True, writable=True,
                                         help='input folder.'),
        output_dir: Path = typer.Argument(..., exists=False, file_okay=False, dir_okay=True, writable=True,
                                          help='output folder.'),
        patient_mapping: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, writable=True,
                                               help='CSV/XSLX file with the original patient IDs and the new ones.'),
        recipe: Path = typer.Option(None, '--recipe', '-r', help='Recipe to de-identify'),
        log_file: Path = typer.Option(None, '--log', '-l', help='Log UID lookup to file'),
        date_offset: int = typer.Option(None, '--date-offset', '-d', help='Date offset to de-identify'),
        time_offset: int = typer.Option(None, '--time-offset', '-e', help='Time offset to de-identify'),
        xnat_project: str = typer.Option(None, '--xnat-project',
                                         help='Add PatientComments tag for importing into the correct XNAT project'),
        xnat_prefix: str = typer.Option(None, '--xnat-prefix',
                                        help='Prefix added subject and session field for XNAT'),
        pixel_anonymize: bool = typer.Option(False, '--pixel-anonymize', help='Perform pixel anonymization'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> None:
    """ Apply de-identification and use a lookup table to update patient name and id. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    patient_id_lookup = PatientLookupDeident.load_file(patient_mapping, 0, 1)

    org_root = "1.2.840.113654.2.70.1."  # must end with .
    uid_deident = BasicUidDeident(org_root)

    options = Options(
        recipe_path=Path(__file__).parent / 'deid_anonimyzer.dicom',
        verbose=verbose,
        very_verbose=very_verbose,
        uid_deident=uid_deident,
        patient_deident=patient_id_lookup,
        date_offset=int(date_offset) if date_offset is not None else DEFAULT_DATE_OFFSET,
        time_offset=int(time_offset) if time_offset is not None else DEFAULT_TIME_OFFSET,
        xnat_project=xnat_project,
        xnat_prefix=xnat_prefix,
        pixel_anonymize=pixel_anonymize
    )

    if recipe is not None:
        if not recipe.exists():
            logger.error(f'Recipe does not exist: {recipe}')
            return
        options.recipe_path = recipe

    config = _process_deident_files(input_dir, output_dir, options)
    if verbose or very_verbose:
        table = Table(title="UID mapping")
        table.add_column('Original UID', justify='right')
        table.add_column('New UID', justify='right')

        for org, new in dict(sorted(uid_deident.uid_map.items())).items():
            table.add_row(org, new)

        with log_file.open(mode='w', encoding='utf8') if log_file else nullcontext() as output:
            if output:
                output.write(datetime.now().isoformat() + '\n\n')
                output.write(config + '\n\n')
            rich.print(table, file=output)


@app.command(rich_help_panel='Store')
def send_data_to_dicom_node(
        destination: str = typer.Argument(..., help='Address of the destination DICOM node'),
        port: int = typer.Argument(..., help='Port of the destination DICOM node'),
        data_folder: Path =
        typer.Argument(..., exists=True, file_okay=True, dir_okay=True, help='File or folder to upload.'),
        recursive: bool = typer.Option(False, '--recursive', '-r', help='Recursive scanning of input'),
        verbose: bool = typer.Option(False, '--verbose', '-v', help='Print more output'),
        very_verbose: bool = typer.Option(False, '-vv', help='Print even more output')) -> None:
    """ Send DICOM files in a folder to a DICOM Store SCP node. """
    setup_logging(log_level=logging.DEBUG if verbose or very_verbose else logging.INFO,
                  dicom_log_level=logging.DEBUG if very_verbose else logging.WARNING)

    files = dicom_qr.store.get_files([str(data_folder)], recursive)
    logger.debug(f'Found {len(files)} files.')

    with StorePacs(addr=destination, port=port) as store, RichProgressObject(disable=DISABLE_PROGRESS,
                                                                             console=console) as progress:
        progress.set_progress_text('[green]files...')
        progress.start()
        for index, input_filename in enumerate(files, start=1):
            progress.set_progress_text(input_filename.name)
            progress.set_progress_count(index, len(files))
            store.store(input_filename, index=index)


def _get_uids(filename: Path, alreay_processed: Path | None) -> list[str]:
    studies_df = pd.read_csv(filename, dtype=str)
    df_keys = ['StudyInstanceUID', 'StudyUID']

    study_uids = []
    for key in df_keys:
        if key in studies_df:
            study_uids = studies_df[key].to_list()
            break

    logger.debug(f'Read {len(study_uids)} UIDs from "{filename}".')

    if alreay_processed is not None:
        processed_uids = pd.read_csv(alreay_processed, dtype=str)['StudyInstanceUID'].to_list()
        logger.debug(f'Read {len(processed_uids)} processed UIDs from "{alreay_processed}".')
        study_uids = [x for x in study_uids if x not in processed_uids]
        logger.debug(f'{len(study_uids)} UIDs to process further.')

    return study_uids


def version_callback(value: bool) -> None:
    """ Version callback. """
    if not value:
        return

    typer.echo(f'Version: {metadata.version("dicom_qr")}')

    try:
        filename = get_settings_filename(Path('settings.json'))
        typer.echo(f'Settings are loaded from: "{filename.absolute()}"')
        raise typer.Exit()
    except FileNotFoundError:
        typer.echo('Settings could not be loaded.')

    raise typer.Exit()


@app.callback()
def version(_: bool = typer.Option(None, '--version', callback=version_callback, is_eager=True,
                                   help='Show version info and exit.')) -> None:
    """ Version information"""
    return


if __name__ == "__main__":
    rich.traceback.install(width=200)
    app()
