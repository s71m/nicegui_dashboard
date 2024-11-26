from abc import abstractmethod, ABC
from typing import Optional

from nicegui import ui
from loguru import logger

from web.components.pageconf import globalpageconf
from web.components.pageinfo import PageInfo
from web.header import create_menu, reload_modules


async def on_save():
    # Handle post-save updates
    await ui.navigate.reload()


class PageTemplate(ABC):
    """Abstract base class for pages"""

    def __init__(self, pageinfo: PageInfo):
        self.pageinfo = pageinfo
        self.left_drawer: Optional[ui.left_drawer] = None

        self.has_sidebar = self.check_sidebar()

        self.pageconf = globalpageconf.load(self.pageinfo.route)
        # Template method that defines the overall page structure
        self.show()

    def show(self):
        """Template method defining the page creation algorithm"""
        self._add_resources()
        self.header()
        if self.has_sidebar:
            self._create_sidebar()
        self.main()
        self.events()

    def _add_resources(self):

        ui.add_head_html('''
            <link rel="stylesheet" href="/static/styles.css">
            <link rel="stylesheet" href="/static/header.css">            
        ''')

        if self.has_sidebar:
            ui.add_head_html('''
                <script src="/static/drawer.js"></script>         
            ''')


    def check_sidebar(self) -> bool:
        """Check if sidebar is implemented by checking MRO"""
        # Get method from current class
        sidebar_method = getattr(self.__class__, 'sidebar', None)

        # Check if method exists and is not from PageTemplate base class
        return sidebar_method is not None and sidebar_method.__qualname__.split('.')[0] != 'PageTemplate'

    def header(self) -> None:
        with ui.header():
            # Left side - can add logo or title here
            with ui.row().classes('items-center'):
                ui.label(self.pageinfo.route).classes('text-white text-xl font-bold').style('width: 350px;')
                if self.has_sidebar:
                    ui.button(icon='menu', on_click=lambda: self.left_drawer.toggle()) \
                        .props('flat color=white')


                ui.button(icon='settings',
                          on_click=lambda: globalpageconf.open_settings_dialog(
                              self.pageinfo,
                              #on_save=on_save
                          )).props('flat color=white')
                # Center - navigation menu
                ui.html(create_menu())

            # Right side - Module controls
            with ui.row().classes('gap-2'):
                ui.button(icon='sync', on_click=reload_modules).props(
                    'flat color=white')  # .props('icon=sync').classes('bg-green-600 hover:bg-green-700 text-white')

    def _create_sidebar(self) -> None:
        """Creates the sidebar structure with proper container"""
        width = self.pageconf.get('sidebar_width')  # or any value you want
        with ui.left_drawer().props(f'width={width}') as self.left_drawer:
            self.sidebar()

    def sidebar(self) -> None:
        """Override this method to provide sidebar content"""
        pass

    @abstractmethod
    def main(self) -> None:
        """Abstract method for main content, must be implemented by subclasses"""
        pass

    def events(self) -> None:
        """Events implementation, default is empty (no events)"""
        pass