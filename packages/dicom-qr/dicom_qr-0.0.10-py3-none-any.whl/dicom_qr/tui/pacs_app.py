import logging
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, TabbedContent, TabPane, Header, Footer

from dicom_qr.logger import setup_logging
from dicom_qr.settings import get_settings
from dicom_qr.tui.series import SeriesWidget
from dicom_qr.tui.settings import SettingsScreen
from dicom_qr.tui.studies import StudiesWidget
from dicom_qr.tui.worklist_widget import WorklistWidget


class PacsApp(App):
    CSS_PATH = 'pacs_app.tcss'

    BINDINGS = [
        Binding('q', 'quit', 'Quit')
    ]

    def __init__(self, settings_file: Path = Path('settings.json')) -> None:
        super().__init__()
        setup_logging(log_level=logging.WARNING, dicom_log_level=logging.WARNING)
        self.pacs_config = get_settings(settings_file)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane('Studies', id='tab_studies'):
                yield StudiesWidget(self.pacs_config)
            with TabPane('Series', id='tab_series'):
                yield SeriesWidget(self.pacs_config)
            with TabPane('Worklist', id='tab_worklist'):
                yield WorklistWidget(id='worklist', pacs_config=self.pacs_config)
        yield Footer()

    @on(Button.Pressed, '#settings')
    def on_settings(self) -> None:
        settings_screen = SettingsScreen(self.pacs_config)
        self.push_screen(settings_screen)
        self.pacs_config = settings_screen.pacs_config

    @on(StudiesWidget.ViewStudy)
    async def on_view_study(self, message: StudiesWidget.ViewStudy) -> None:
        self.query_one(TabbedContent).active = 'tab_series'
        series_widget = self.query_one(SeriesWidget)
        await series_widget.view_study(message.study_uid)
