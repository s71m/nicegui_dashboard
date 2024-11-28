from nicegui import ui
import random
from enum import Enum
from typing import Optional, Callable, Union

# Global variables to track drag and drop state
dragged = None
drop_target = None


class CardTemplate(ui.card):
    def __init__(self, name: str, card_dict: dict, cls_card_container) -> None:  # Removed on_close parameter
        super().__init__()
        self.name = name
        self.card_dict = card_dict
        self.cls_card_container = cls_card_container
        self.ui_info_label = None
        self.overlay = None
        self.left_zone = None
        self.right_zone = None

        self.classes('w-full h-full shadow-lg transition-shadow hover:shadow-xl p-0 relative')
        self.style(f'height: {self.cls_card_container.card_height}px;')

        self.render()

    def render(self):
        """Template method defining the card structure"""
        with self:
            self.header()
            self.content()
            self.drag_zones()

    def header(self):
        """Creates the card header with drag handle and controls"""
        with ui.row().classes('w-full flex items-center min-h-[2.5rem] bg-[#262b2e] rounded-t'):
            # Draggable name element
            with ui.element('span').props('draggable') \
                    .classes(
                'w-16 flex items-center justify-center text-base font-medium text-white cursor-move ml-2') as header:
                ui.html(self.name).classes('select-text truncate')

            header.on('dragstart', self.handle_drag_start)
            header.on('dragend', self.handle_drag_end)

            # Vertical divider
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

    def drag_zones(self):
        """Add transparent left and right drop zones over the card."""
        with ui.element('div').classes('absolute left-0 right-0 bottom-0 top-[2.5rem] flex overlay').style(
                'pointer-events: none;') as self.overlay:
            with ui.element('div').classes('w-1/2 h-full left-zone').style('pointer-events: none;'):
                self.left_zone = ui.element('div').classes('w-full h-full')
                self.left_zone.on('dragover.prevent', self.handle_left_drag_over)
                self.left_zone.on('dragleave', self.handle_drag_leave)
                self.left_zone.on('drop', self.handle_drop_left)

            with ui.element('div').classes('w-1/2 h-full right-zone').style('pointer-events: none;'):
                self.right_zone = ui.element('div').classes('w-full h-full')
                self.right_zone.on('dragover.prevent', self.handle_right_drag_over)
                self.right_zone.on('dragleave', self.handle_drag_leave)
                self.right_zone.on('drop', self.handle_drop_right)

    def handle_drag_start(self, e):
        global dragged
        dragged = self
        ui.run_javascript('''
            document.querySelectorAll('.left-zone, .right-zone').forEach(zone => {
                zone.style.pointerEvents = 'auto';
            });
        ''')

    def handle_drag_end(self, e):
        global drop_target
        if drop_target == self:
            drop_target = None
        self.remove_highlight()
        ui.run_javascript('''
            document.querySelectorAll('.left-zone, .right-zone').forEach(zone => {
                zone.style.pointerEvents = 'none';
            });
        ''')

    def handle_left_drag_over(self, e):
        global drop_target
        if self != dragged:
            drop_target = self
            self.left_zone.classes(add='highlight')
            self.right_zone.classes(remove='highlight')

    def handle_right_drag_over(self, e):
        global drop_target
        if self != dragged:
            drop_target = self
            self.right_zone.classes(add='highlight')
            self.left_zone.classes(remove='highlight')

    def handle_drag_leave(self, e):
        self.remove_highlight()

    def remove_highlight(self):
        self.left_zone.classes(remove='highlight')
        self.right_zone.classes(remove='highlight')

    def handle_drop_left(self, e):
        global dragged, drop_target
        if dragged and drop_target and dragged != drop_target:
            self.cls_card_container.reorder_cards(dragged, drop_target, position='left')
            dragged = None
            drop_target = None
        self.remove_highlight()

    def handle_drop_right(self, e):
        global dragged, drop_target
        if dragged and drop_target and dragged != drop_target:
            self.cls_card_container.reorder_cards(dragged, drop_target, position='right')
            dragged = None
            drop_target = None
        self.remove_highlight()

    def handle_fullscreen(self):
        ui.run_javascript(f'''
            const element = document.querySelector(".q-card[id='c{self.id}']");
            if (!document.fullscreenElement) {{
                element.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        ''')

    def handle_remove(self):  # Changed to sync, removed async
        self.cls_card_container.remove_card(self.name)  # Direct removal


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
            ui_chart.on_point_click(self.handle_chart_select)

    def handle_chart_select(self, e):
        if e:
            info_text = f"Clicked point - Name: {e.name}, Value: {e.value}"
            self.ui_info_label.set_text(info_text)


class CardType(Enum):
    CHART = ChartCard


class CardContainer(ui.grid):
    def __init__(self, columns: int = 3,
                 card_type: Union[CardType, dict] = CardType.CHART,
                 card_height: int = 300,
                 on_remove: Optional[Callable[[str], None]] = None):
        super().__init__(columns=columns)
        self.ui_cards = {}
        self.card_type = card_type.value
        self.card_height = card_height
        self.on_remove = on_remove
        self.classes('w-full')
        ui.add_head_html('''
        <style>
            .left-zone .highlight {
                background-color: rgba(211, 211, 211, 0.3);
            }
            .right-zone .highlight {
                background-color: rgba(128, 255, 128, 0.2);
            }
        </style>
        ''')

    def add_card(self, card_name: str, card_dict: dict) -> None:
        if card_name not in self.ui_cards:
            with self:
                self.ui_cards[card_name] = self.card_type(
                    card_name,
                    card_dict,
                    self
                )

    def remove_card(self, card_name: str) -> None:
        if card_name in self.ui_cards:
            self.ui_cards[card_name].delete()
            del self.ui_cards[card_name]

    def clear_cards(self) -> None:
        for card in list(self.ui_cards.values()):
            card.delete()
        self.ui_cards.clear()

    def reorder_cards(self, dragged_card: CardTemplate, target_card: CardTemplate, position: str = 'left') -> None:
        dragged_name = dragged_card.name
        target_name = target_card.name

        if dragged_name not in self.ui_cards or target_name not in self.ui_cards:
            return

        if position == 'left':
            insert_code = 'parent.insertBefore(draggedCard, targetCard);'
        else:
            insert_code = 'parent.insertBefore(draggedCard, targetCard.nextSibling);'

        ui.run_javascript(f'''
            const draggedCard = document.querySelector(".q-card[id='c{dragged_card.id}']");
            const targetCard = document.querySelector(".q-card[id='c{target_card.id}']");
            if (draggedCard && targetCard) {{
                const parent = draggedCard.parentNode;
                {insert_code}
            }}
        ''')

        cards = list(self.ui_cards.items())
        dragged_idx = next(i for i, (name, _) in enumerate(cards) if name == dragged_name)
        target_idx = next(i for i, (name, _) in enumerate(cards) if name == target_name)

        cards.pop(dragged_idx)

        if position == 'left':
            insert_idx = target_idx if target_idx > dragged_idx else target_idx
        else:
            insert_idx = target_idx + 1 if target_idx >= dragged_idx else target_idx + 1

        cards.insert(insert_idx, (dragged_name, dragged_card))
        self.ui_cards = dict(cards)

@ui.page("/")
def main():
    # Add some example cards
    container = CardContainer(columns=3, card_height=400)

    # Add sample cards with random data
    for i in range(6):
        card_name = f'Chart {i + 1}'
        card_data = {'data': f'Sample data for {card_name}'}
        container.add_card(card_name, card_data)

ui.run(dark=True)