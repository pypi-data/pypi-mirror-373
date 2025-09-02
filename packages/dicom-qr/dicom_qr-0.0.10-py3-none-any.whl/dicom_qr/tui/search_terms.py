from collections.abc import Iterator
from typing import Any

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Select, Input


class SearchEntry(Widget):
    """Search entry widget. Consists of a search field and value."""
    CSS_PATH = 'pacs_app.tcss'

    class Remove(Message):
        def __init__(self, _id: str | None) -> None:
            self.id = _id
            super().__init__()

    def __init__(self, fields: list[tuple[str, str]], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields = fields

    def compose(self) -> ComposeResult:
        with Horizontal(id='horizontal'):
            yield Button(label=Text('🗙', style='bold'), id='search_remove')
            yield Select(self.fields, id='field', allow_blank=False)
            yield Input(id='value', placeholder='Value...')

    @on(Button.Pressed, '#search_remove')
    def remove_search_term(self, _: Button.Pressed) -> None:
        self.post_message(self.Remove(self.id))

    def set_type_value(self, search_type: str, value: str) -> None:
        self.search_type = search_type
        self.value = value

    @property
    def search_type(self) -> str:
        return self.query_one(Select).value  # type: ignore

    @search_type.setter
    def search_type(self, search_type: str) -> None:
        self.query_one(Select).value = search_type

    @property
    def value(self) -> str:
        return self.query_one(Input).value  # type: ignore

    @value.setter
    def value(self, _value: str) -> None:
        self.query_one(Input).value = _value


def _get_next_id(entries: Iterator[SearchEntry]) -> str:
    max_id = max(int(x.id.lstrip('id_')) for x in entries)  # type: ignore
    return f'id_{max_id + 1}'
