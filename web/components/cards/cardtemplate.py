from typing import Callable, Optional
from nicegui import ui

class CardTemplate(ui.card):
    def __init__(self, name: str, card_dict: dict, cls_card_container, on_close: Callable = None, **kwargs) -> None:
        super().__init__()
        self.name = name
        self.card_dict = card_dict
        self.cls_card_container = cls_card_container
        self.on_close = on_close
        self.kwargs = kwargs

        self.ui_info_label = None
        self.overlay = None
        self.zones = {}  # Dictionary to store zones

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
            with ui.element('span').props('draggable') \
                    .classes('w-16 flex items-center justify-center text-base font-medium text-white cursor-move ml-2') as header:
                ui.html(self.name).classes('select-text truncate')

            header.on('dragstart', self.handle_drag_start)
            header.on('dragend', self.handle_drag_end)

            ui.element('div').classes('w-px h-5 bg-gray-600')
            self.ui_info_label = ui.label('').classes('text-white text-sm flex-grow px-1 py-2 text-right')

            with ui.row().classes('flex items-center gap-0.5 mr-1 shrink-0'):
                ui.icon('fullscreen', size='24px') \
                    .classes('cursor-pointer text-gray-600 hover:text-white') \
                    .on('click', self.handle_fullscreen)
                ui.icon('close', size='24px') \
                    .classes('cursor-pointer text-gray-600 hover:text-white') \
                    .on('click', self.handle_remove)

    def content(self):
        """Abstract method to be implemented by subclasses"""
        raise NotImplementedError

    def drag_zones(self):
        """Add transparent left and right drop zones over the card."""
        with ui.element('div').classes('absolute inset-[0.2rem] flex overlay').style('pointer-events: none;') as self.overlay:
            for side in ['left', 'right']:
                with ui.element('div').classes(f'w-1/2 h-full {side}-zone').style('pointer-events: none;'):
                    zone = ui.element('div').classes('w-full h-full')
                    self.zones[side] = zone
                    zone.on('dragover.prevent', lambda e, s=side: self.handle_drag_over(e, s))
                    zone.on('dragleave', self.handle_drag_leave)
                    zone.on('drop', lambda e, s=side: self.handle_drop(e, s))

    def handle_fullscreen(self):
        ui.run_javascript(f'''
            const element = document.querySelector(".q-card[id='c{self.id}']");
            if (!document.fullscreenElement) {{
                element.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        ''')

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

    def handle_drag_over(self, e, side: str):
        global drop_target
        if self != dragged:
            drop_target = self
            self.zones[side].classes(add='highlight')
            other_side = 'right' if side == 'left' else 'left'
            self.zones[other_side].classes(remove='highlight')

    def handle_drag_leave(self, e):
        self.remove_highlight()

    def remove_highlight(self):
        for zone in self.zones.values():
            zone.classes(remove='highlight')

    def handle_drop(self, e, side: str):
        global dragged, drop_target
        if dragged and drop_target and dragged != drop_target:
            self.cls_card_container.reorder_cards(dragged, drop_target, position=side)
            dragged = None
            drop_target = None
        self.remove_highlight()

    async def handle_remove(self):
        if self.on_close:
            await self.on_close(self.name)