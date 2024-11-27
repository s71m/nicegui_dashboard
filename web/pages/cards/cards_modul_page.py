from typing import Set, Optional
from datetime import date
import polars as pl

from nicegui import ui

from web.components.cards import CardContainer, CardType
from web.components.pageinfo import PageInfo
from web.pages.cards.cards_polars_page import map_polars_aggrid_schema
from web.pagetemplate import PageTemplate


class CardsModulPage(PageTemplate):
    def __init__(self, pageinfo: PageInfo):
        # Initialize data
        self.df = pl.DataFrame({
            'name': pl.Series(['Card ' + str(i) for i in range(1, 15)], dtype=pl.String),
            'description': pl.Series(['Description ' + str(i+5) for i in range(1, 15)], dtype=pl.String),
            'value': pl.Series([i * 1.5 for i in range(1, 15)], dtype=pl.Float32),
            'active': pl.Series([i % 2 == 0 for i in range(1, 15)], dtype=pl.Boolean),
            'created_date': pl.Series([date(2024, 1, i) for i in range(1, 15)], dtype=pl.Date)
        })

        # Track selected cards
        self.selected_card_names: Set[str] = set()

        # UI component references
        self.ui_cards_aggrid: Optional[ui.aggrid] = None
        self.ui_card_container: Optional[CardContainer] = None

        super().__init__(pageinfo)

    def sidebar(self):
        """Create sidebar with search and data grid"""
        with ui.row().classes('w-full'):
            ui.input(placeholder='Quick search by name...', on_change=self.handle_search) \
                .props('dense clearable').classes('w-full')

        # Configure data grid with community edition features
        grid_config = {
            'defaultColDef': {
                'sortable': True,
                'filter': True,
                'resizable': True
            },
            'columnDefs': map_polars_aggrid_schema(self.df, checkbox_field='name'),
            'rowSelection': 'multiple',
            'rowMultiSelectWithClick': True,
            ':getRowId': '(params) => params.data.name',
            'rowData': self.df.to_dicts(),
            'suppressFieldDotNotation': True
        }

        self.ui_cards_aggrid = ui.aggrid(grid_config, theme='balham-dark').classes('w-full') \
            .style(f'height: {self.pageconf.get("sidebar_cards_grid_height")}px')
        self.ui_cards_aggrid.on('selectionChanged', self.handle_card_select)

    def main(self):
        """Initialize main content area with cards grid"""
        self.ui_card_container = CardContainer(
            columns=self.pageconf.get("cards_per_row"),
            card_type=CardType.CHART,
            card_height=self.pageconf.get("card_height"),
            on_remove=self.handle_card_remove
        )

    async def handle_search(self, event):
        """Filter grid data based on name field"""
        search_text = event.value if event.value is not None else ''

        if search_text:
            await self.ui_cards_aggrid.run_grid_method('setFilterModel', {
                'name': {
                    'type': 'contains',
                    'filter': search_text
                }
            })
        else:
            # Clear filters when search is empty
            await self.ui_cards_aggrid.run_grid_method('setFilterModel', None)

    async def handle_card_remove(self, card_name: str):
        """Handle card removal triggered by X button click"""
        if card_name in self.selected_card_names:
            await self.ui_cards_aggrid.run_row_method(card_name, 'setSelected', False)
            #self.selected_card_names.remove(card_name)

    async def handle_card_select(self, _):
        """Update displayed cards based on grid selection"""
        selected_rows = await self.ui_cards_aggrid.get_selected_rows()
        newly_selected_names = {row['name'] for row in selected_rows}

        # Remove cards that were deselected
        cards_to_remove = self.selected_card_names - newly_selected_names
        for card_name in cards_to_remove:
            self.ui_card_container.remove_card(card_name)

        # Add newly selected cards
        cards_to_add = newly_selected_names - self.selected_card_names
        for card_name in cards_to_add:
            card_dict = self.df.filter(pl.col('name') == card_name).to_dicts()[0]
            self.ui_card_container.add_card(card_name, card_dict)

        self.selected_card_names = newly_selected_names