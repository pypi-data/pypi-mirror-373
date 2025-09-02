import typing

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Static
from textual_sortable_datatable import SortableDataTable

from dicom_qr.database import SeriesData
from dicom_qr.query import QueryError, QueryPacs
from dicom_qr.settings import PacsConfig
from dicom_qr.tui.search_terms import SearchEntry, _get_next_id


if typing.TYPE_CHECKING:
    from textual.widgets.data_table import RowKey

SEARCH_FIELDS = [
    ('StudyInstanceUID', 'StudyInstanceUID'),
    ('SeriesInstanceUID', 'SeriesInstanceUID'),
    ('Modality', 'Modality'),
    ('SeriesDescription', 'SeriesDescription'),
]
COLUMNS = ['SeriesDescription', 'ProtocolName', 'SeriesInstanceUID', 'Modality', 'SeriesNumber']


class SeriesWidget(Static):
    BINDINGS = [
        Binding('a', 'add_search_term', 'Add Search Term'),
    ]

    def __init__(self, pacs_config: PacsConfig, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)
        self.pacs_config = pacs_config
        self._search_results: list[SeriesData] = []
        self._row_series_map: dict[RowKey, SeriesData] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id='search_terms'):
            yield SearchEntry(id='id_0', fields=SEARCH_FIELDS)
        yield SortableDataTable(id='series_data_table')
        with Horizontal(id='button_bar'):
            yield Button(id='search', label='Search')
            yield Button(id='settings', label='⚙')

    @on(Button.Pressed, '#search')
    @on(Input.Submitted)
    def on_search(self) -> None:
        search_entries = self.query(SearchEntry).results()

        study_uid = None
        modalities = []
        for entry in search_entries:
            if entry.search_type == 'StudyInstanceUID':
                study_uid = entry.value
            if entry.search_type == 'Modality':
                modalities.append(entry.value)

        table = self.query_one('#series_data_table', DataTable)
        table.clear(columns=True)

        if study_uid is None:
            table.border_title = 'No study UID'
            return

        with QueryPacs(self.pacs_config) as query:
            try:
                self._search_results = query.get_series_for_study(study_uid=study_uid, modalities=modalities)
            except QueryError as e:
                self._search_results = []
                self.notify(e.response.ErrorComment, severity='error')
                return
        self._add_to_table(self._search_results)

    async def view_study(self, study_uid: str) -> None:
        self.query_one('#id_0', SearchEntry).set_type_value('StudyInstanceUID', study_uid)

        table = self.query_one('#series_data_table', DataTable)
        table.clear(columns=True)
        table.loading = True

        with QueryPacs(self.pacs_config) as query:
            try:
                self._search_results = query.get_series_for_study(study_uid=study_uid, modalities=[])
            except QueryError as e:
                self._search_results = []
                self.notify(e.response.ErrorComment, severity='error')
                return
        self._add_to_table(self._search_results)
        table.loading = False

    def _add_to_table(self, series: list[SeriesData]) -> None:
        table = self.query_one('#series_data_table', DataTable)

        table.border_title = f'Results ({len(series)} rows)'
        table.add_columns(*COLUMNS)
        self._row_series_map.clear()
        for index, serie in enumerate(series, 1):
            label = Text(str(index), style='#B0FC38 italic', justify='right')
            row_key = table.add_row(*(getattr(serie, x) for x in COLUMNS), label=label)
            self._row_series_map[row_key] = serie

    def action_add_search_term(self) -> None:
        new_entry = SearchEntry(id=_get_next_id(self.query(SearchEntry).results()), fields=SEARCH_FIELDS)
        self.query_one('#search_terms', Vertical).mount(new_entry)
        new_entry.scroll_visible()

    @on(SearchEntry.Remove)
    def remove_search_term(self, entry: SearchEntry.Remove) -> None:
        if len(list(self.query(SearchEntry).results(SearchEntry))) == 1:
            return

        self.query_one(f'#{entry.id}', SearchEntry).remove()
