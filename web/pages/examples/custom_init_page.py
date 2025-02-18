#web/pages/examples/custom_init_page.py
from nicegui import ui

from ...pagetemplate import PageTemplate


class CustomInitPage(PageTemplate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def sidebar(self) -> None:
        ui.label("This is the sidebar label").classes("text-primary")

    def main(self) -> None:
        ui.label("This is the main label").classes("text-primary")