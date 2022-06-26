from os import get_terminal_size as termsize
from rich.align import Align

from textual.app import App
from textual.widgets import Static
from textual import events

from termtyper.ui.settings_options import MenuSlide
from termtyper.ui.widgets.menu import Menu
from termtyper.ui.widgets.minimal_scrollview import MinimalScrollView

from ..ui.widgets import *  # NOQA
from ..utils import *  # NOQA


def percent(part, total):
    return int(part * total / 100)


class TermTyper(App):
    async def on_load(self) -> None:
        self.parser = Parser()
        self.current_space = "main_menu"
        self.x, self.y = termsize()
        self.settings = MenuSlide()

        self.top = Static("hi")
        self.bottom = MinimalScrollView("")

        # FOR MAIN MENU
        self.banner = Static(banners["welcome"])

        self.buttons = {
            "Start Typing!": self.load_typing_space,
            "Getting Started": self.load_getting_started,
            "Settings": self.load_settings,
            "Quit": self.action_quit,
        }
        self.menu = Menu("buttons", list(self.buttons.keys()))

        self.typing_screen = Screen()

        await self.bind("ctrl+q", "quit", "quit the application")

    async def on_mount(self) -> None:
        await self.setup_grid()
        await self.load_main_menu()

    async def setup_grid(self):
        self.grid = await self.view.dock_grid()
        self.grid.add_row("top", size=8)
        self.grid.add_row("bottom")
        self.grid.add_column("col")
        self.grid.add_areas(top="col,top", bottom="col,bottom")
        self.grid.place(top=self.top, bottom=self.bottom)

    async def load_help_menu(self):
        await self.top.update(HELP_BANNER)
        await self.bottom.update(HELP_MESSAGE)
        self.current_space = "help_menu"

    async def load_main_menu(self) -> None:
        """
        Renders the Main Menu
        """
        self.current_space = "main_menu"
        await self.top.update(self.banner)
        await self.bottom.update(self.menu)
        self.refresh()

    async def load_getting_started(self):
        self.current_space = "getting_started"
        self.getting_started_scroll = Align.center(GETTING_STARTERD_MESSAGE)
        await self.top.update(GETTING_STARTERD_BANNER)
        await self.bottom.update(self.getting_started_scroll)

    async def load_settings(self):
        """
        Renders the Settings
        """

        await self.top.update(self.settings.banner())
        await self.bottom.update(self.settings)
        self.current_space = "settings"

    async def load_typing_space(self) -> None:
        """
        Renders the Typing Space
        """

        self.current_space = "typing_space"
        self.race_hud = RaceHUD()
        await self.typing_screen._refresh_settings()
        await self.top.update(self.race_hud)
        await self.bottom.update(self.typing_screen)

    async def on_key(self, event: events.Key) -> None:
        if self.current_space == "help_menu":
            if event.key in ["ctrl+h", "escape"]:
                await self.load_settings()

        elif self.current_space == "main_menu":
            await self.menu.key_press(event)

        elif self.current_space == "settings":
            if event.key == "escape":
                await self.load_main_menu()
            elif event.key == "ctrl+h":
                await self.load_help_menu()
            else:
                await self.settings.key_press(event)
                await self.top.update(self.settings.banner())

        elif self.current_space == "getting_started":
            if event.key == "escape":
                await self.load_main_menu()
            elif event.key in ["j", "down"]:
                self.bottom.scroll_up()
            elif event.key in ["k", "up"]:
                self.bottom.scroll_down()

        elif self.current_space == "typing_space":
            if event.key == "escape":
                await self.load_main_menu()
                await self.typing_screen.reset_screen()
                return

            await self.typing_screen.key_add(event.key)

        self.top.refresh()
        self.bottom.refresh()

    async def handle_reset_hud(self, _: ResetHUD) -> None:
        self.race_hud.reset()

    async def handle_update_race_hud(self, event: UpdateRaceHUD) -> None:
        self.race_hud.update(event.completed, event.speed, event.accuracy)

    async def handle_button_clicked(self, e: ButtonClicked):
        await self.buttons[e.value]()
