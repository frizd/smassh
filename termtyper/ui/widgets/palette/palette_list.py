from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem
from termtyper.src.parser import config_parser


class PaletteListItem(Label):
    ...


class PaletteList(ListView, can_focus=False):
    DEFAULT_CSS = """
    PaletteList {
        column-span: 2;
    }
    """

    def get_options(self):
        raise NotImplementedError

    def compose(self) -> ComposeResult:
        for option in self.get_options():
            yield ListItem(PaletteListItem(option))


class LanguagePaletteList(PaletteList):
    def get_options(self):
        return config_parser.configured_languages


class ThemePaletteList(PaletteList):
    def get_options(self):
        return config_parser.configured_themes
