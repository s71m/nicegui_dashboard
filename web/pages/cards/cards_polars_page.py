from typing import Set, Dict, Optional
from datetime import date
import polars as pl
from nicegui import ui

from web.components.pageinfo import PageInfo
from web.pagetemplate import PageTemplate


def get_column_definitions(df: pl.DataFrame, checkbox_field: Optional[str] = None) -> list[dict]:
    """Generate AG Grid column definitions with basic filters based on Polars types."""
    column_defs = []

    for col_name in df.columns:
        dtype = df.schema[col_name]
        col_def = {
            'field': col_name,
            'headerName': col_name.replace('_', ' ').title(),
            'floatingFilter': True
        }

        # Add checkbox if specified
        if checkbox_field and col_name == checkbox_field:
            col_def['checkboxSelection'] = True
            col_def['headerCheckboxSelection'] = True

        # Add basic filter based on data type
        if dtype in (pl.Float32, pl.Float64, pl.Int32, pl.Int64):
            col_def['filter'] = 'agNumberColumnFilter'
        elif dtype == pl.Boolean:
            col_def['filter'] = 'agSetColumnFilter'
        elif dtype == pl.Date:
            col_def['filter'] = 'agDateColumnFilter'
        else:  # Default to text filter for strings and other types
            col_def['filter'] = 'agTextColumnFilter'

        column_defs.append(col_def)

    return column_defs


class CardsPolarsPage(PageTemplate):
    def __init__(self, pageinfo: PageInfo):

        self.df = pl.DataFrame({
            'name': pl.Series(['Card ' + str(i) for i in range(1, 15)], dtype=pl.String),
            'description': pl.Series(['Description ' + str(i) for i in range(1, 15)], dtype=pl.String),
            'quantity': pl.Series([i * 10 for i in range(1, 15)], dtype=pl.Int32),
            'value': pl.Series([i * 1.5 for i in range(1, 15)], dtype=pl.Float32),
            'active': pl.Series([i % 2 == 0 for i in range(1, 15)], dtype=pl.Boolean),
            'created_date': pl.Series([date(2024, 1, i) for i in range(1, 15)], dtype=pl.Date)
        })

        # Track selected cards and their UI references
        self.selected_card_names: Set[str] = set()
        self.card_ui_elements: Dict[str, ui.card] = {}

        # UI component references
        self.search_input: Optional[ui.input] = None
        self.data_grid: Optional[ui.aggrid] = None
        self.cards_display_grid: Optional[ui.grid] = None

        super().__init__(pageinfo)

    def sidebar(self):
        """Create sidebar with search and data grid"""
        with ui.row().classes('w-full'):
            ui.input(placeholder='Quick search...', on_change=self._handle_quick_search) \
                .props('dense before-style="border-color: red"') \
                .classes('w-full custom-input')

        # Configure data grid with Polars column definitions
        grid_config = {
            'defaultColDef': {
                'sortable': True,
                'filter': True,
                'resizable': True,
                'floatingFilter': True
            },
            'columnDefs': get_column_definitions(self.df, checkbox_field='name'),
            'rowSelection': 'multiple',
            'rowMultiSelectWithClick': True,
            ':getRowId': '(params) => params.data.name',
            'rowData': self.df.to_dicts(),
            'suppressFieldDotNotation': True
        }

        self.data_grid = ui.aggrid(grid_config, theme='balham-dark') \
            .classes('w-full') \
            .style(f'height: {self.pageconf.get("sidebar_cards_grid_height")}px')

    def main(self):
        """Initialize main content area with cards grid"""
        self.cards_display_grid = ui.grid(columns=self.pageconf.get("cards_per_row")).classes('w-full')

    def events(self):
        """Bind all event handlers"""
        self.data_grid.on('selectionChanged', self._handle_card_selection_change)

    def _handle_quick_search(self, event):
        """Filter grid data based on search input"""
        search_text = event.value if event.value is not None else ''
        self.data_grid.options['quickFilterText'] = search_text
        self.data_grid.update()

    async def _handle_card_selection_change(self, _):
        """Update displayed cards based on grid selection"""
        selected_rows = await self.data_grid.get_selected_rows()
        newly_selected_names = {row['name'] for row in selected_rows}

        # Remove cards that were deselected
        cards_to_remove = self.selected_card_names - newly_selected_names
        for card_name in cards_to_remove:
            self._remove_card(card_name)

        # Add newly selected cards
        cards_to_add = newly_selected_names - self.selected_card_names
        for card_name in cards_to_add:
            self._create_and_display_card(card_name)

        self.selected_card_names = newly_selected_names

    def _create_and_display_card(self, card_name: str):
        """Create and display a new card in the grid"""
        card_data = self.df.filter(pl.col('name') == card_name).to_dicts()[0]
        if not card_data:
            return

        with self.cards_display_grid:
            with ui.card().classes('w-full h-full').style(
                    f'height: {self.pageconf.get("card_height")}px; padding: 0') as card:
                # Card header
                with ui.row().classes('w-full flex items-center h-10 bg-[#262b2e]'):
                    ui.label(card_name).classes('flex-grow text-md pl-2')
                    # Icons container
                    with ui.row().classes('flex gap-2 mr-2'):
                        # Fullscreen toggle icon
                        ui.icon('fullscreen', size='24px') \
                            .classes('cursor-pointer text-gray-400 hover:text-white') \
                            .on('click', lambda: ui.run_javascript(f'''
                                const element = document.querySelector(".q-card[id='c{card.id}']");
                                if (!document.fullscreenElement) {{
                                    element.requestFullscreen();
                                }} else {{
                                    document.exitFullscreen();
                                }}
                            '''))

                        # Close icon
                        ui.icon('close', size='24px') \
                            .classes('cursor-pointer text-gray-400 hover:text-white') \
                            .on('click', lambda: self._remove_card(card_name))

                # Card content
                with ui.column().classes('p-4'):
                    # Display all fields except name
                    for field, value in card_data.items():
                        if field != 'name':
                            formatted_field = field.replace('_', ' ').title()
                            ui.label(f"{field}: {value}").classes('mb-1')

            self.card_ui_elements[card_name] = card

    def _remove_card(self, card_name: str):
        """Remove a card from display and optionally update grid selection"""
        if card_name in self.card_ui_elements:
            # Remove UI element
            self.card_ui_elements[card_name].delete()
            self.card_ui_elements.pop(card_name)

            # Update selection tracking
            self.selected_card_names.discard(card_name)

            # Update grid selection
            self.data_grid.run_row_method(card_name, 'setSelected', False)