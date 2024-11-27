import random
from enum import Enum
from typing import Set, Dict, Optional, Callable, Union, Awaitable

from nicegui import ui
from loguru import logger

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

        self.classes('w-full h-full shadow-lg transition-shadow hover:shadow-xl p-0')
        self.style(f'height: {self.cls_card_container.card_height}px;')

        self.render()

    def render(self):
        """Template method defining the card structure"""
        with self:
            self.header()
            self.content()

    def header(self):
        """Creates the card header with drag handle and controls"""
        with ui.row().classes('w-full flex items-center min-h-[2.5rem] bg-[#262b2e] rounded-t'):
            # Draggable name element
            with ui.element('span').props('draggable') \
                    .classes(
                'w-16 flex items-center justify-center text-base font-medium text-white cursor-move ml-2') as header:
                ui.html(self.name).classes('select-text truncate')

            header.on('dragstart', self.handle_drag_start)

            # Vertical divider as direct child
            ui.element('div').classes('w-px h-5 bg-gray-600')

            # Right-aligned info label
            self.ui_info_label = ui.label('').classes('text-white text-sm flex-grow px-1 py-2 text-right')

            # Controls
            with ui.row().classes('flex items-center gap-0.5 mr-1 shrink-0'):
                ui.icon('fullscreen', size='20px') \
                    .classes('cursor-pointer text-gray-300 hover:text-white p-0.5') \
                    .on('click', self.handle_fullscreen)
                ui.icon('close', size='20px') \
                    .classes('cursor-pointer text-gray-300 hover:text-white p-0.5') \
                    .on('click', self.handle_remove)

    def content(self):
        """Abstract method to be implemented by subclasses"""
        raise NotImplementedError


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

#
class ChartCard(CardTemplate):

    def content(self):
        """Implements chart content with random series data"""
        with ui.card_section().classes('p-2 w-full h-full'):
            options = {
                'tooltip': {},
                'grid': {
                    'top': 30,
                    'right': 30,
                    'bottom': 30,
                    'left': 30
                },
                'legend': {
                    'data': ['Sales', 'Revenue', 'Growth']
                },
                'xAxis': {
                    'type': 'category',
                    'data': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
                },
                'yAxis': {
                    'type': 'value'
                },
                'series': [
                    {
                        'name': 'Sales',
                        'type': 'bar',
                        'data': [random.randint(50, 200) for _ in range(6)]
                    },
                    {
                        'name': 'Revenue',
                        'type': 'line',
                        'data': [random.randint(100, 300) for _ in range(6)]
                    },
                    {
                        'name': 'Growth',
                        'type': 'bar',
                        'data': [random.randint(20, 100) for _ in range(6)]
                    }
                ]
            }
            ui_chart = ui.echart(options).classes('w-full h-full').props(f'id="{self.name}"')
            # ui_chart.on('click', self.handle_chart_select)
            ui_chart.on_point_click(self.handle_chart_select)

    def handle_chart_select(self, e):
        if e:
            info_text = f"Clicked point - Name: {e.name}, Value: {e.value}"
            self.ui_info_label.set_text(info_text)


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
        if card_name in self.ui_cards:
            self.ui_cards[card_name].delete()
            del self.ui_cards[card_name]

    def clear_cards(self) -> None:
        for card in list(self.ui_cards.values()):
            card.delete()
        self.ui_cards.clear()

    def reorder_cards(self, dragged_card: CardTemplate, target_card: CardTemplate) -> None:
        """Reorder cards by moving their DOM elements instead of rebuilding"""
        dragged_name = dragged_card.name
        target_name = target_card.name

        if dragged_name not in self.ui_cards or target_name not in self.ui_cards:
            return

        # Use JavaScript to reorder the DOM elements
        ui.run_javascript(f'''
            const draggedCard = document.querySelector(".q-card[id='c{dragged_card.id}']");
            const targetCard = document.querySelector(".q-card[id='c{target_card.id}']");
            if (draggedCard && targetCard) {{
                const parent = draggedCard.parentNode;
                const targetNext = targetCard.nextSibling;
                if (targetNext === draggedCard) {{
                    parent.insertBefore(draggedCard, targetCard);
                }} else {{
                    parent.insertBefore(draggedCard, targetNext);
                }}
            }}
        ''')

        # Update the internal order in ui_cards dictionary
        cards = list(self.ui_cards.items())
        dragged_idx = next(i for i, (name, _) in enumerate(cards) if name == dragged_name)
        target_idx = next(i for i, (name, _) in enumerate(cards) if name == target_name)

        cards.insert(target_idx if target_idx > dragged_idx else target_idx + 1,
                     cards.pop(dragged_idx))

        self.ui_cards = dict(cards)

        # Remove any lingering drag visual effects
        dragged_card.classes(remove='border-2 border-blue-500')
        target_card.classes(remove='border-2 border-blue-500')
