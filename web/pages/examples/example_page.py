from nicegui import ui

from web.pagetemplate import PageTemplate


class ExamplePage(PageTemplate):
    """Example implementation of page"""

    def sidebar(self) -> None:
        ui.label("This is the sidebar label").classes("text-primary")

    def main(self) -> None:
        ui.label("This is the main label").classes("text-primary")