from typing import Any

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from dicom_qr.settings import PacsConfig


class SettingsScreen(ModalScreen):
    CSS_PATH = 'pacs_app.tcss'
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self, pacs_config: PacsConfig, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pacs_config = pacs_config

    def compose(self) -> ComposeResult:
        yield Label("PACS settings", id='title')
        with Grid():
            yield Label('Server AE title')
            yield Input(value=self.pacs_config.server_ae_title, disabled=True)
            yield Label('Server AE port')
            yield Input(value=str(self.pacs_config.server_ae_port), type='integer', disabled=True)
            yield Label('Server AE IP')
            yield Input(value=self.pacs_config.server_ae_ip, disabled=True)
            yield Label('Client AE title')
            yield Input(value=self.pacs_config.client_ae_title, disabled=True)
            yield Label('Client AE port')
            yield Input(value=str(self.pacs_config.client_ae_port), type='integer', disabled=True)
            yield Label('Base folder')
            yield Input(value=str(self.pacs_config.base_folder), disabled=True)
            yield Label('Folder Template')
            yield Input(value=str(self.pacs_config.folder_template), disabled=True)
        with Horizontal():
            yield Button("Ok", id="ok")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
            return

        # Update self.pacs_config from UI.
        self.app.pop_screen()
        return
