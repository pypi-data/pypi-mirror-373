
import dateutil.parser
import rich.box
import rich.table

from dicom_qr.database import SeriesData, StudyData
from dicom_qr.settings import ColumnLayout, StudyColumns, SeriesColumns

# noinspection PyArgumentList
DEFAULT_STUDY_COLUMNS = [
    ColumnLayout(StudyColumns.INDEX),
    ColumnLayout(StudyColumns.PATIENT_ID),
    ColumnLayout(StudyColumns.STUDY_DATE),
    ColumnLayout(StudyColumns.STUDY_DESCRIPTION, 'left'),
]

# noinspection PyArgumentList
DEFAULT_SERIES_COLUMNS = [
    ColumnLayout(SeriesColumns.INDEX),
    ColumnLayout(SeriesColumns.STUDYINSTANCEUID, no_wrap = True),
    ColumnLayout(SeriesColumns.SERIESINSTANCEUID, no_wrap = True),
    ColumnLayout(SeriesColumns.MODALITY),
    ColumnLayout(SeriesColumns.SERIESNUMBER),
    ColumnLayout(SeriesColumns.SERIESDESCRIPTION, 'left'),
]


def create_series_table(series: list[SeriesData], title: str = 'Series found',
                        columns: list[ColumnLayout] | None = None) -> rich.table.Table:
    """ Create a rich Table from the series data.
    :param series: series to display.
    :param title: table title.
    :param columns: columns to display. If None uses the default columns.
    :return:  table
    """
    if columns is None:
        columns = DEFAULT_SERIES_COLUMNS

    table = rich.table.Table(title=title, box=rich.box.SQUARE_DOUBLE_HEAD)
    for col in columns:
        table.add_column(col.name, justify=col.justify, no_wrap=col.no_wrap)

    for index, study in enumerate(series, 1):
        data = []
        for col in columns:
            if col.name == SeriesColumns.INDEX:
                data.append(str(index))
                continue

            data.append(str(getattr(study, col.name)))

        table.add_row(*data)

    return table


def create_studies_table(studies: list[StudyData], title: str = 'Studies found',
                         columns: list[ColumnLayout] | None = None) -> rich.table.Table:
    """ Create a rich Table from the studies data.
    :param studies: studies to display.
    :param title: table title.
    :param columns: columns to display. If None uses the default columns.
    :return: table
    """
    if columns is None:
        columns = DEFAULT_STUDY_COLUMNS
    table = rich.table.Table(title=title, box=rich.box.SQUARE_DOUBLE_HEAD)
    for col in columns:
        table.add_column(col.name, justify=col.justify, no_wrap=col.no_wrap)

    studies = sorted(studies, key=lambda x: x.StudyDate)

    for index, study in enumerate(studies, 1):
        data = []
        for col in columns:
            if col.name == StudyColumns.INDEX:
                data.append(str(index))
                continue

            if col.name in {StudyColumns.STUDY_DATE, StudyColumns.PATIENT_BIRTHDATE}:
                try:
                    date = getattr(study, col.name)
                    data.append(dateutil.parser.parse(date).date().strftime('%Y-%m-%d'))
                except dateutil.parser.ParserError:
                    data.append('NoDate')
                continue

            if col.name == StudyColumns.MODALITIES:
                data.append('/'.join(study.ModalitiesInStudy))
                continue

            data.append(getattr(study, col.name))

        table.add_row(*data)

    return table
