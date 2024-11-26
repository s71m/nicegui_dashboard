from typing import Set, Dict, Optional
from nicegui import ui
from web.components.pageinfo import PageInfo
from web.pagetemplate import PageTemplate


class CardsPage(PageTemplate):
    def __init__(self, pageinfo: PageInfo):
        # Sample data for display
        self.card_data_list = [
            {'name': f'Card {i}', 'description': f'Description {i}'}
            for i in range(1, 15)
        ]

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

        # Configure data grid
        grid_config = {
            'defaultColDef': {
                'sortable': True,
                'filter': True,
                'resizable': True,
                'floatingFilter': True
            },
            'columnDefs': [
                {
                    'headerName': 'Name',
                    'field': 'name',
                    'checkboxSelection': True,
                    'headerCheckboxSelection': True,
                },
                {
                    'headerName': 'Description',
                    'field': 'description',
                }
            ],
            'rowSelection': 'multiple',
            'rowMultiSelectWithClick': True,
            ':getRowId': '(params) => params.data.name',
            'rowData': self.card_data_list
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
        card_data = next((item for item in self.card_data_list if item['name'] == card_name), None)
        if not card_data:
            return

        with self.cards_display_grid:
            with ui.card().classes('w-full h-full').style(f'height: {self.pageconf.get("card_height")}px; padding: 0') as card:
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
                    ui.label(card_data['description'])

            self.card_ui_elements[card_name] = card

    def _remove_card(self, card_name: str):
        """
        Remove a card from display and optionally update grid selection

        Args:
            card_name: Name of the card to remove
        """
        if card_name in self.card_ui_elements:
            # Remove UI element
            self.card_ui_elements[card_name].delete()
            self.card_ui_elements.pop(card_name)

            # Update selection tracking
            self.selected_card_names.discard(card_name)

            # Update grid selection
            self.data_grid.run_row_method(card_name, 'setSelected', False)
