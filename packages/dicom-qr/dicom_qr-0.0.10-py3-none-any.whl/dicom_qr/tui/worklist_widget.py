from __future__ import annotations

import csv
import functools
import typing
from pathlib import Path

from textual import on
from textual.containers import Horizontal
from textual.widgets import Button, DataTable, Static
from textual_fspicker import FileOpen, FileSave, Filters

from dicom_qr.database import StudyData
from dicom_qr.tui.download_screen import DownloadScreen

if typing.TYPE_CHECKING:
    from collections.abc import Iterable
    from textual.app import ComposeResult
    from textual.widgets.data_table import RowKey
    from dicom_qr.settings import PacsConfig


class WorklistWidget(Static):
    def __init__(self, pacs_config: PacsConfig, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)
        self.studies: list[StudyData] = []
        self.pacs_config = pacs_config
        self._selected_row: RowKey | None = None
        self._row_study_map: dict[RowKey, StudyData] = {}

    def compose(self) -> ComposeResult:
        yield DataTable(id='worklist_table')
        with Horizontal(id='button_bar'):
            yield Button(id='worklist_remove_study', label='Remove')
            yield Button(id='worklist_download', label='Download')
            yield Button(id='worklist_import', label='Import')
            yield Button(id='worklist_export', label='Export')

    def add_study(self, study: StudyData) -> None:
        self.studies.append(study)
        self._update_table()

    @on(Button.Pressed, '#worklist_remove_study')
    async def on_remove(self) -> None:
        if self._selected_row is None:
            self.notify('No row selected')
            return

        self.query_one('#worklist_table', DataTable).remove_row(self._selected_row)
        self._selected_row = None
        self._update_table()

    @on(DataTable.RowHighlighted, '#worklist_table')
    def row_selected(self, entry: DataTable.RowSelected) -> None:
        self._selected_row = entry.row_key

    @on(Button.Pressed, '#worklist_import')
    async def on_import(self) -> None:
        def load_worklist(filename: Path | None) -> None:
            self.studies = []

            if filename is None:
                self._update_table()
                return

            with filename.open('r', encoding='utf8') as csvfile:
                csv_reader = csv.reader(csvfile)

                header = next(csv_reader)
                for row in csv_reader:
                    self.studies.append(StudyData(**dict(zip(header, row, strict=False))))
                self._update_table()

        await self.app.push_screen(
            FileOpen(location=Path.cwd(), filters=Filters(('CSV', lambda p: p.suffix.lower() == '.csv'))),
            callback=functools.partial(load_worklist))

    @on(Button.Pressed, '#worklist_export')
    async def on_export(self) -> None:
        def csv_row(study: StudyData) -> Iterable[str]:
            return (study.StudyInstanceUID,
                    study.PatientID,
                    # study.PatientName,
                    # study.PatientSex,
                    # study.PatientBirthDate,
                    study.StudyID,
                    study.StudyDate,
                    study.StudyDescription,
                    study.StudyTime,
                    study.AccessionNumber,
                    study.BodyPartExamined)

        def save_worklist(filename: Path | None) -> None:
            if filename is None:
                return

            with filename.open('w', encoding='utf8') as csvfile:
                writer = csv.writer(csvfile, lineterminator='\n')
                writer.writerow([
                    'StudyInstanceUID',
                    'PatientID',
                    # 'PatientName',
                    # 'PatientSex',
                    # 'PatientBirthDate',
                    'StudyID',
                    'StudyDate',
                    'StudyDescription',
                    'StudyTime',
                    'AccessionNumber',
                    'BodyPartExamined'
                ])
                writer.writerows(csv_row(x) for x in self.studies)

        await self.app.push_screen(
            FileSave(location=Path.cwd(), filters=Filters(('CSV', lambda p: p.suffix.lower() == '.csv'))),
            callback=functools.partial(save_worklist))

    @on(Button.Pressed, '#worklist_download')
    async def on_download(self) -> None:
        screen = DownloadScreen(self.studies, self.pacs_config)
        await self.app.push_screen(screen)
        await screen.download()
        await screen.dismiss()

    def _update_table(self) -> None:
        data_table = self.query_one('#worklist_table', DataTable)

        data_table.cursor_type = 'row'
        data_table.clear(columns=True)
        data_table.zebra_stripes = True
        data_table.add_columns(
            'StudyInstanceUID',
            'PatientID',
            # 'PatientName',
            # 'PatientSex',
            # 'PatientBirthDate',
            'StudyID',
            'StudyDate',
            'StudyDescription',
            'StudyTime',
            'AccessionNumber',
            'BodyPartExamined')

        self._row_study_map.clear()
        for study in self.studies:
            row_key = data_table.add_row(
                study.StudyInstanceUID,
                study.PatientID,
                # study.PatientName,
                # study.PatientSex,
                # study.PatientBirthDate,
                study.StudyID,
                study.StudyDate,
                study.StudyDescription,
                study.StudyTime,
                study.AccessionNumber,
                study.BodyPartExamined)
            self._row_study_map[row_key] = study
