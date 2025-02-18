from typing import Optional, Dict, Set, Any, Callable
import polars as pl
from nicegui import ui


class AgGridPolars:
    def __init__(self,
                 df: pl.DataFrame,
                 checkbox_field: str,
                 grid_height: int,
                 on_selection_change: Callable,
                 theme: str = 'balham-dark'):
        self.df = df
        self.checkbox_field = checkbox_field
        self.grid_height = grid_height
        self.on_selection_change = on_selection_change
        self.theme = theme
        self.ui_grid: Optional[ui.aggrid] = None
        self.selected_items: Set[str] = set()

    def create_grid(self) -> ui.aggrid:
        """Create and configure the AG Grid component"""
        grid_config = {
            'defaultColDef': {
                'sortable': True,
                'filter': True,
                'resizable': True
            },
            'columnDefs': self.map_polars_aggrid_schema(),
            'rowSelection': 'multiple',
            'rowMultiSelectWithClick': True,
            ':getRowId': f'(params) => params.data.{self.checkbox_field}',
            'rowData': self.df.to_dicts(),
            'suppressFieldDotNotation': True
        }

        self.ui_grid = ui.aggrid(grid_config, theme=self.theme).classes('w-full') \
            .style(f'height: {self.grid_height}px')
        self.ui_grid.on('selectionChanged', self.handle_selection_change)
        return self.ui_grid

    def map_polars_aggrid_schema(self) -> list:
        """Map Polars schema to AG Grid column definitions"""
        column_defs = []

        # Add checkbox column
        if self.checkbox_field:
            column_defs.append({
                'field': self.checkbox_field,
                'checkboxSelection': True,
                'headerCheckboxSelection': True,
                # 'headerCheckboxSelectionFilteredOnly': True,
                # 'width': 50
            })

        # Map other columns
        for col_name, dtype in self.df.schema.items():
            if col_name == self.checkbox_field:
                continue

            col_def = {
                'field': col_name,
                'headerName': col_name.replace('_', ' ').title()
            }

            # Set column type-specific properties
            if dtype == pl.Boolean:
                col_def['filter'] = 'agSetColumnFilter'
            elif dtype in (pl.Float32, pl.Float64):
                col_def['filter'] = 'agNumberColumnFilter'
            elif dtype in (pl.Date, pl.Datetime):
                col_def['filter'] = 'agDateColumnFilter'

            column_defs.append(col_def)

        return column_defs

    async def handle_selection_change(self, _):
        """Process grid selection changes"""
        if self.ui_grid:
            selected_rows = await self.ui_grid.get_selected_rows()
            newly_selected = {row[self.checkbox_field] for row in selected_rows}

            # Call the provided callback with selection changes
            await self.on_selection_change(
                removed=self.selected_items - newly_selected,
                added=newly_selected - self.selected_items
            )

            self.selected_items = newly_selected

    async def search(self, search_text: str):
        """Apply search filter to the grid"""
        if not self.ui_grid:
            return

        if search_text:
            await self.ui_grid.run_grid_method('setFilterModel', {
                self.checkbox_field: {
                    'type': 'contains',
                    'filter': search_text
                }
            })
        else:
            await self.ui_grid.run_grid_method('setFilterModel', None)

    async def deselect_row(self, row_id: str):
        """Deselect a specific row by ID"""
        if self.ui_grid:
            await self.ui_grid.run_row_method(row_id, 'setSelected', False)