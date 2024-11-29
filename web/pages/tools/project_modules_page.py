from nicegui import ui

from web.components.modulereloader import ModuleReloader
from web.pagetemplate import PageTemplate


class ProjectModulesPage(PageTemplate):
    """Implementation of CurrentModulesPage inheriting from PageTemplate."""

    def main(self) -> None:
        """Main content with a table of modules."""
        reloader = ModuleReloader()
        project_modules = reloader.get_project_modules()
        columns = [
            {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left', 'sortable': True},
            {'name': 'path', 'label': 'Path', 'field': 'path', 'align': 'left', 'sortable': True},
        ]

        # Create table with sorted modules
        ui.table(
            columns=columns,
            rows=sorted(project_modules, key=lambda x: x['name']),
            row_key='name'
        ).classes('w-full')

    def events(self) -> None:
        """Define event logic (if needed)."""
        pass
