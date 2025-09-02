import typing
from collections.abc import Iterator
from typing import Any

import dateutil.parser
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, DataTable, Input, Static, Switch
from textual_sortable_datatable import SortableDataTable

from dicom_qr.database import StudyData
from dicom_qr.query import QueryError, QueryPacs
from dicom_qr.search import SearchTerms
from dicom_qr.settings import ColumnLayout, PacsConfig, StudyColumns
from dicom_qr.tui.search_terms import SearchEntry, _get_next_id
from dicom_qr.tui.worklist_widget import WorklistWidget

if typing.TYPE_CHECKING:
    from textual.widgets.data_table import RowKey

SEARCH_FIELDS = [
    ('PatientID', 'PatientID'),
    ('PatientName', 'PatientName'),
    ('AccessionNumber', 'AccessionNumber'),
    ('StudyDescription', 'StudyDescription'),
    ('StudyInstanceUID', 'StudyInstanceUID'),
    ('Modalities', 'Modalities'),
    ('StudyDate', 'StudyDate')
]

PHI_COLUMNS = [StudyColumns.PATIENT_NAME, StudyColumns.PATIENT_BIRTHDATE, StudyColumns.PATIENT_ID,
               StudyColumns.PATIENT_SEX]


def _create_search_term(search_entries: Iterator[SearchEntry]) -> SearchTerms:
    search: dict[str, Any] = {}
    for search_entry in search_entries:
        match search_entry.search_type:
            case 'PatientID':
                search['patid'] = search_entry.value
            case 'PatientName':
                search['pat_name'] = search_entry.value
            case 'AccessionNumber':
                search['accession_number'] = search_entry.value
            case 'StudyInstanceUID':
                search['study_uid'] = search_entry.value
            case 'StudyDescription':
                search['study_desc'] = search_entry.value
            case 'Modalities':
                search['modalities'] = search_entry.value.split()
            case 'StudyDate':
                search['date_range'] = dateutil.parser.parse(search_entry.value)
    return SearchTerms(**search)


def _create_table_row(columns: list[ColumnLayout], study: StudyData) -> list[Text]:
    data = []
    for x in columns:
        # noinspection PyTypeChecker
        value = getattr(study, x.name.value)
        if isinstance(value, list | set | tuple):
            data.append(Text('/'.join(sorted(value)), justify=x.justify, no_wrap=x.no_wrap))
            continue
        data.append(Text(str(value), justify=x.justify, no_wrap=x.no_wrap))
    return data


class StudiesWidget(Static):
    class ViewStudy(Message):
        def __init__(self, study_uid: str) -> None:
            self.study_uid = study_uid
            super().__init__()

    BINDINGS = [
        Binding('a', 'add_search_term', 'Add Search Term'),
        Binding('v', 'view_series_in_study', 'View Series in Study'),
        Binding('d', 'download_study', 'Download Study'),
    ]

    def __init__(self, pacs_config: PacsConfig, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pacs_config = pacs_config
        self._search_results: list[StudyData] = []
        self._selected_row: RowKey | None = None
        self._row_study_map: dict[RowKey, StudyData] = {}
        self._anonymous: bool = False

    def compose(self) -> ComposeResult:
        with Vertical(id='search_terms'):
            yield SearchEntry(id='id_0', fields=SEARCH_FIELDS)
        table: SortableDataTable = SortableDataTable(id='study_data_table')
        table.cursor_type = 'row'
        table.zebra_stripes = True
        yield table
        with Horizontal(id='button_bar'):
            anonymous = Switch(id='anonymous', value=False)
            anonymous.tooltip = 'Anonymous mode, hides PHI'
            yield anonymous
            yield Button(id='search', label='Search')
            yield Button(id='settings', label='⚙')

    @on(Button.Pressed, '#search')
    @on(Input.Submitted)
    async def on_search(self) -> None:
        search_entries = self.query(SearchEntry)

        with QueryPacs(self.pacs_config) as query:
            try:
                self._search_results = query.get_studies(_create_search_term(search_entries.results()))
                self.notify(f'Found {len(self._search_results)} '
                            f'{"study" if len(self._search_results) == 1 else "studies"}.',
                            severity='information')
            except QueryError as e:
                self._search_results = []
                self.notify(e.response.ErrorComment, severity='error')
                return

        await self._update_table()

    async def _update_table(self) -> None:
        table = self.query_one('#study_data_table', DataTable)
        table.clear(columns=True)
        self._row_study_map.clear()

        results = sorted(self._search_results, key=lambda x: x.StudyDate)

        table.border_title = f'Results ({len(results)} rows)'
        columns = self._get_columns()

        table.add_columns(*[x.name for x in columns])

        for index, study in enumerate(results):
            row_key = table.add_row(
                *_create_table_row(columns, study),
                label=Text(str(index + 1), style='#B0FC38 italic', justify='right')
            )
            self._row_study_map[row_key] = study
        table.focus()

    def _get_columns(self) -> list[ColumnLayout]:
        if self.pacs_config.study_columns is None:
            # noinspection PyArgumentList
            columns = [
                ColumnLayout(StudyColumns.STUDY_DATE),
                ColumnLayout(StudyColumns.MODALITIES),
                ColumnLayout(StudyColumns.STUDY_DESCRIPTION)
            ]
        else:
            columns = [x for x in self.pacs_config.study_columns if x.name != StudyColumns.INDEX]
        if self._anonymous:
            columns = list(filter(lambda c: c.name not in PHI_COLUMNS, columns))
        return columns

    def action_add_search_term(self) -> None:
        new_entry = SearchEntry(id=_get_next_id(self.query(SearchEntry).results()), fields=SEARCH_FIELDS)
        self.query_one('#search_terms', Vertical).mount(new_entry)
        new_entry.scroll_visible()

    @on(Switch.Changed)
    async def anonymous_mode(self, entry: Switch.Changed) -> None:
        self._anonymous = entry.value
        self.notify(f'Anonymous mode {"On" if self._anonymous else "Off"}', severity='information')

        await self._update_table()

    @on(SearchEntry.Remove)
    def remove_search_term(self, entry: SearchEntry.Remove) -> None:
        if len(list(self.query(SearchEntry).results(SearchEntry))) == 1:
            return

        self.query_one(f'#{entry.id}', SearchEntry).remove()

    @on(DataTable.RowHighlighted, '#study_data_table')
    def row_selected(self, entry: DataTable.RowSelected) -> None:
        self._selected_row = entry.row_key

    async def action_view_series_in_study(self) -> None:
        if not self._selected_row:
            return

        selected_study = self._row_study_map[self._selected_row].StudyInstanceUID
        self.post_message(StudiesWidget.ViewStudy(selected_study))

    async def action_download_study(self) -> None:
        if not self._selected_row:
            return

        worklist = self.app.query_one('#worklist', WorklistWidget)
        worklist.add_study(self._row_study_map[self._selected_row])
