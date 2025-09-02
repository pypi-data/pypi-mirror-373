import asyncio
from typing import Any

from textual.app import ComposeResult, App
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import ProgressBar, Label

from dicom_qr.database import StudyData, SeriesUidMap
from dicom_qr.query import QueryPacs, QueryError
from dicom_qr.retrieve import get_retrieve
from dicom_qr.retrieve_utils import AssociationError
from dicom_qr.scp import dummy_filename_callback
from dicom_qr.settings import PacsConfig


class DownloadScreen(ModalScreen[None]):
    CSS_PATH = 'pacs_app.tcss'

    def __init__(self, studies: list[StudyData], pacs_config: PacsConfig, **kwargs: str | None) -> None:
        super().__init__(**kwargs)
        self._studies = studies
        self.pacs_config = pacs_config

    def compose(self) -> ComposeResult:
        with Vertical():
            yield ProgressBar(id='study_progress', total=len(self._studies))
            yield ProgressBar(id='series_progress')
            yield Label(id='download_label')

    async def download(self) -> None:
        study_progressbar = self.query_one('#study_progress', ProgressBar)
        series_progressbar = self.query_one('#series_progress', ProgressBar)
        progresslabel = self.query_one('#download_label', Label)
        for study in self._studies:
            study_progressbar.advance(1)
            progresslabel.update(f'Study: {study.StudyDescription}')
            await asyncio.sleep(0.1)

            with QueryPacs(self.pacs_config) as query:
                try:
                    series = query.get_series_for_study(study.StudyInstanceUID)
                except QueryError as e:
                    self.notify(e.response.ErrorComment, severity='error')
                    continue

            try:
                with get_retrieve(self.pacs_config, SeriesUidMap(series).uid_map, dummy_filename_callback) as retrieve:
                    for serie in series:
                        series_progressbar.advance(1)
                        progresslabel.update(f'Serie: {serie.SeriesDescription}')

                        await asyncio.sleep(0.1)
                        retrieve.retrieve_images_for_a_series(serie)
            except AssociationError:
                self.notify('Not allowed to download.')
                break
                # # Simulate download
                # series_progressbar.update(total=len(series), progress=0)
                # for serie in series:
                #     series_progressbar.advance(1)
                #     progresslabel.update(f'Serie: {serie.SeriesDescription}')
                #
                #     await asyncio.sleep(0.33)


class DownloadApp(App):
    CSS_PATH = 'pacs_app.tcss'
    BINDINGS = [('b', 'download')]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.studies = [StudyData(StudyInstanceUID=f'{x}') for x in range(50)]
        self.pacs_config = PacsConfig()

    async def action_download(self) -> None:
        screen = DownloadScreen(self.studies, self.pacs_config)
        await self.app.push_screen(screen)
        await screen.download()
        await screen.dismiss()


if __name__ == '__main__':
    app = DownloadApp()
    app.run()
