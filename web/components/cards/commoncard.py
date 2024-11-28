import random

from web.components.cards.cardtemplate import CardTemplate
from nicegui import ui

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