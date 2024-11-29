from enum import Enum
from typing import Set, Dict, Optional, Callable, Union, Awaitable
from datetime import date
import polars as pl

from nicegui import ui

from web.components.pageinfo import PageInfo
from web.pages.cards.cards_polars_page import map_polars_aggrid_schema

from web.pagetemplate import PageTemplate

# Global variables to track drag and drop state
dragged = None
drop_target = None


class CardTemplate(ui.card):
    def __init__(self, name: str, card_dict: dict, cls_card_container, on_close: Callable = None) -> None:
        super().__init__()
        self.name = name
        self.card_dict = card_dict
        self.cls_card_container = cls_card_container
        self.on_close = on_close
        self.ui_info_label = None

        # Setup drop zone behavior
        self.on('dragover.prevent', self.handle_drag_over)
        self.on('dragleave', self.handle_drag_end)
        self.on('drop', self.handle_drop)

        self.classes('w-full h-full shadow-lg transition-shadow hover:shadow-xl')
        self.style(f'height: {self.cls_card_container.card_height}px; padding: 0; width: 100%')

        self.initialize()

    def initialize(self):
        """Template method defining the card structure"""
        with self:
            self.header()
            self.content()

    def header(self):
        """Creates the card header with drag handle and controls"""
        with ui.row().classes('w-full flex items-center h-10 bg-[#262b2e] rounded-t'):
            # Draggable header
            with ui.element('span').props('draggable') \
                    .classes('text-lg font-bold text-white ml-4 mr-4 cursor-move') as header:
                ui.html(self.name).classes('select-text')

            header.on('dragstart', self.handle_drag_start)

            # Info label for updates
            self.ui_info_label = ui.label('').classes('text-white text-sm flex-grow')

            # Controls
            with ui.row().classes('flex gap-2 mr-2'):
                ui.icon('fullscreen', size='24px') \
                    .classes('cursor-pointer text-gray-200 hover:text-white') \
                    .on('click', self.handle_fullscreen)
                ui.icon('close', size='24px') \
                    .classes('cursor-pointer text-gray-200 hover:text-white') \
                    .on('click', self.handle_remove)

    def content(self):
        """Abstract method to be implemented by subclasses"""
        raise NotImplementedError

    def update_header(self, text: str):
        """Updates the header info label"""
        if self.ui_info_label:
            self.ui_info_label.set_text(text)

    def handle_fullscreen(self):
        ui.run_javascript(f'''
            const element = document.querySelector(".q-card[id='c{self.id}']");
            if (!document.fullscreenElement) {{
                element.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        ''')

    # Drag and drop handlers
    def handle_drag_start(self, e):
        global dragged
        dragged = self

    def handle_drag_over(self, e):
        global drop_target
        if self != dragged:
            drop_target = self
            self.classes(add='border-2 border-blue-500')

    def handle_drag_end(self, e):
        global drop_target
        if drop_target == self:
            drop_target = None
            self.classes(remove='border-2 border-blue-500')

    def handle_drop(self, e):
        global dragged, drop_target
        if dragged and drop_target and dragged != drop_target:
            self.cls_card_container.reorder_cards(dragged, drop_target)
            dragged = None
            drop_target = None

    async def handle_remove(self):
        if self.on_close:
            await self.on_close(self.name)


class CommonCard(CardTemplate):
    def content(self):
        """Implements basic grid content"""
        with ui.card_section().classes('pt-0'):
            with ui.grid(columns=2).classes('w-full gap-2 p-2'):
                for field, value in self.card_dict.items():
                    ui.label(field)
                    ui.label(str(value))


class ChartCard(CardTemplate):
    def content(self):
        """Implements chart content"""
        with ui.card_section().classes('pt-0 flex flex-col'):
            # Add chart
            options = {
                'tooltip': {'trigger': 'axis'},
                'xAxis': {
                    'type': 'category',
                    'data': list(self.card_dict.keys())
                },
                'yAxis': {'type': 'value'},
                'series': [{
                    'data': [v for v in self.card_dict.values() if isinstance(v, (int, float))],
                    'type': 'line'
                }]
            }
            ui_chart = ui.echart(options).classes('w-full flex-grow')
            ui_chart.on('click', self.handle_chart_select)

    def handle_chart_select(self, e):
        if e.get('componentType') == 'series':
            value = e.get('value', '')
            name = e.get('name', '')
            info_text = f"Selected: {name} - Value: {value}"
            self.update_header(info_text)


class CardType(Enum):
    COMMON = CommonCard
    CHART = ChartCard


class CardContainer(ui.grid):
    def __init__(self, columns: int = 3,
                 card_type: Union[CardType, Dict[str, CardType]] = CardType.COMMON,
                 card_height: int = 300,
                 on_remove: Optional[Callable[[str], Awaitable[None]]] = None):
        super().__init__(columns=columns)
        self.ui_cards = {}
        self.card_type = card_type.value
        self.card_height = card_height
        self.on_remove = on_remove
        self.classes('w-full')

    def add_card(self, card_name: str, card_dict: dict) -> None:
        if card_name not in self.ui_cards:
            with self:
                self.ui_cards[card_name] = self.card_type(
                    card_name,
                    card_dict,
                    self,
                    self.on_remove
                )

    def remove_card(self, card_name: str) -> None:
        """Remove card and handle UI cleanup"""
        if card_name in self.ui_cards:
            self.ui_cards[card_name].delete()
            del self.ui_cards[card_name]

    def clear_cards(self) -> None:
        """Remove all cards"""
        for card in list(self.ui_cards.values()):
            card.delete()
        self.ui_cards.clear()

    def reorder_cards(self, dragged_card: CardTemplate, target_card: CardTemplate) -> None:
        """Reorder cards after drag and drop"""
        dragged_name = dragged_card.name
        target_name = target_card.name

        # Get current order
        card_names = list(self.ui_cards.keys())
        dragged_idx = card_names.index(dragged_name)
        target_idx = card_names.index(target_name)

        # Create new order
        card_names.insert(target_idx, card_names.pop(dragged_idx))

        # Temporarily store all cards and clear the grid
        stored_cards = {}
        for name, card in self.ui_cards.items():
            stored_cards[name] = {
                'card_dict': card.card_dict,
                'card_type': card.__class__
            }
            card.delete()
        self.ui_cards.clear()

        # Rebuild grid in new order
        with self:
            for name in card_names:
                if name in stored_cards:
                    card_info = stored_cards[name]
                    self.ui_cards[name] = card_info['card_type'](
                        name,
                        card_info['card_dict'],
                        self,
                        self.on_remove
                    )


class CardsDndPage(PageTemplate):
    def __init__(self, **kwargs):
        # Initialize data
        self.df = pl.DataFrame({
            'name': pl.Series(['Card ' + str(i) for i in range(1, 15)], dtype=pl.String),
            'description': pl.Series(['Description ' + str(i) for i in range(1, 15)], dtype=pl.String),
            'quantity': pl.Series([i * 10 for i in range(1, 15)], dtype=pl.Int32),
            'value': pl.Series([i * 1.5 for i in range(1, 15)], dtype=pl.Float32),
            'active': pl.Series([i % 2 == 0 for i in range(1, 15)], dtype=pl.Boolean),
            'created_date': pl.Series([date(2024, 1, i) for i in range(1, 15)], dtype=pl.Date)
        })

        # Track selected cards
        self.selected_card_names: Set[str] = set()

        # UI component references
        self.ui_search_input: Optional[ui.input] = None
        self.ui_cards_aggrid: Optional[ui.aggrid] = None
        self.ui_card_container: Optional[CardContainer] = None

        super().__init__(**kwargs)

    def sidebar(self):
        """Create sidebar with search and data grid"""
        with ui.row().classes('w-full'):
            self.ui_search_input = ui.input(placeholder='Quick search...', on_change=self.handle_search) \
                .props('dense') \
                .classes('w-full custom-input')

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
            card_type=CardType.COMMON,
            card_height=self.pageconf.get("card_height"),
            on_remove=self.handle_card_remove
        )

    def handle_search(self, event):
        """Filter grid data based on search input"""
        search_text = event.value.lower() if event.value is not None else ''
        filtered_data = self.df.filter(
            pl.col('name').str.to_lowercase().str.contains(search_text) |
            pl.col('description').str.to_lowercase().str.contains(search_text)
        ).to_dicts()
        self.ui_cards_aggrid.options['rowData'] = filtered_data
        self.ui_cards_aggrid.update()

    async def handle_card_remove(self, card_name: str):
        """Handle card removal triggered by X button click"""
        if card_name in self.selected_card_names:
            await self.ui_cards_aggrid.run_row_method(card_name, 'setSelected', False)

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