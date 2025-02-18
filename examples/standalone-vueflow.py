from datetime import datetime
from pathlib import Path
import random
import json
from nicegui import ui, app
from web.components.vueflow.vueflow import VueFlow

PROJECT_ROOT = Path(__file__).resolve().parent.parent
app.add_static_files('/static', str(PROJECT_ROOT/'web/static'))


class VueFlowPage:
    def __init__(self, nodes):
        self.initial_nodes = nodes

    def add_head_resources(self):
        ui.add_head_html('''
            <link href="/static/vueflow/css/style.css" rel="stylesheet" />
            <link href="/static/vueflow/css/theme-default.css" rel="stylesheet" />
            <link href="/static/vueflow/css/controls/style.css" rel="stylesheet" />
            <link href="/static/vueflow/css/node-resizer/style.css" rel="stylesheet" />
            <link href="/static/vueflow/css/myvueflow.css" rel="stylesheet" />
            <script src="/static/vueflow-component.umd.js" defer></script>
            <style>

            </style>
        ''')

    def on_node_clicked_handler(self, e):
        ui.notify(f'Node clicked: {e}')

    def add_default_node(self):
        id = datetime.now().strftime('%Y%m%d%H%M%S')
        new_node = {
            'id': id,
            'position': {'x': random.randint(50, 400), 'y': random.randint(50, 500)},
            'data': {'label': f'Default Node {id}'},
            'style': {'backgroundColor': 'green', 'width': '150px', 'height': '50px'}
        }
        self.vue_flow.add_node(new_node)
        ui.notify(f"Default Node {id} added")

    def add_simple_node(self):
        id = datetime.now().strftime('%Y%m%d%H%M%S')
        new_node = {
            'id': id,
            'type': 'simple',
            'position': {'x': random.randint(50, 400), 'y': random.randint(50, 500)},
            'data': {'label': f'Simple Node {id}'},
            'resizing': True
        }
        self.vue_flow.add_node(new_node)
        ui.notify(f"Simple Node {id} added")

    def add_detail_node(self):
        id = datetime.now().strftime('%Y%m%d%H%M%S')
        new_node = {
            'id': id,
            'type': 'detail',
            'position': {'x': random.randint(50, 400), 'y': random.randint(50, 500)},
            'data': {
                'title': f'Detail Node {id}',
                'description': f'Description for node {id}'
            }
        }
        self.vue_flow.add_node(new_node)
        ui.notify(f"Detail Node {id} added")

    async def show_nodes(self):
        nodes = await self.vue_flow.get_nodes()
        ui.notify(f'Current nodes: {json.dumps(nodes, indent=2)}')

    async def show_edges(self):
        edges = await self.vue_flow.get_edges()
        ui.notify(f'Current edges: {json.dumps(edges, indent=2)}')

    async def show_data(self):
        try:
            nodes = await self.vue_flow.get_nodes()
            edges = await self.vue_flow.get_edges()

            combined_data = {
                'nodes': nodes,
                'edges': edges
            }

            ui.notify(f'Flow Data: {json.dumps(combined_data, indent=2)}')
        except Exception as e:
            ui.notify(f'Error getting flow data: {str(e)}', type='negative')

    async def save_diagram(self):
        try:
            nodes = await self.vue_flow.get_nodes()
            edges = await self.vue_flow.get_edges()
            viewport = await self.vue_flow.get_viewport()

            flow_data = {
                'nodes': nodes,
                'edges': edges,
                'viewport': viewport
            }

            with open('diagram.json', 'w') as f:
                json.dump(flow_data, f, indent=2)

            ui.notify('Diagram saved successfully')
        except Exception as e:
            ui.notify(f'Error saving diagram: {str(e)}', type='negative')

    async def load_diagram(self):
        try:
            if not Path('diagram.json').exists():
                ui.notify('No saved diagram found', type='warning')
                return

            with open('diagram.json', 'r') as f:
                flow_data = json.load(f)

            await self.vue_flow.restore_diagram(flow_data)
            ui.notify('Diagram loaded successfully')
        except Exception as e:
            ui.notify(f'Error loading diagram: {str(e)}', type='negative')

    def update_default_node1(self):
        updated_data = {
            'data': {'label': 'Updated Default Node 1'},
            'position': {'x': random.randint(50, 400), 'y': random.randint(50, 500)},
            'style': {'backgroundColor': 'lightgray', 'width': '150px', 'height': '50px'}
        }
        self.vue_flow.update_node('1', updated_data)
        ui.notify("Default Node 1 updated")

    def render(self):
        self.add_head_resources()

        with ui.row():
            with ui.column().classes('w-48'):
                ui.button('Add Default Node', on_click=self.add_default_node)
                ui.button('Add Simple Node', on_click=self.add_simple_node)
                ui.button('Add Detail Node', on_click=self.add_detail_node)
                ui.button('Update Default Node1', on_click=self.update_default_node1)
                ui.button('Show Nodes', on_click=self.show_nodes)
                ui.button('Show Edges', on_click=self.show_edges)
                ui.button('Show Data', on_click=self.show_data)
                ui.button('Save Diagram', on_click=self.save_diagram)
                ui.button('Load Diagram', on_click=self.load_diagram)

            with ui.column():
                self.vue_flow = VueFlow(
                    nodes=self.initial_nodes,
                    options={'fitView': True},
                    style={'width': '800px', 'height': '800px'},
                    on_node_clicked=self.on_node_clicked_handler
                )


@ui.page('/')
def index_page():
    initial_nodes = [
        {
            'id': '1',
            'position': {'x': 100, 'y': 50},
            'data': {'label': 'Default Node 1'},
            'style': {'backgroundColor': 'lightgray', 'width': '150px', 'height': '50px'}
        },
        {
            'id': '2',
            'type': 'simple',
            'position': {'x': 100, 'y': 200},
            'data': {'label': 'Simple Node'}
        },
        {
            'id': '3',
            'type': 'detail',
            'position': {'x': 100, 'y': 350},
            'data': {
                'title': 'Detail Node',
                'description': 'This is a detailed node with title and description'
            }
        }
    ]

    cls_vf = VueFlowPage(initial_nodes)
    cls_vf.render()


ui.run(uvicorn_reload_includes='*.py,*.js,*.vue', dark=True, port=8010)