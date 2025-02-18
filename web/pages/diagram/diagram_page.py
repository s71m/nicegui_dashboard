from datetime import datetime
from pathlib import Path
import random
import json
from nicegui import ui

from web.components.vueflow.vueflow import VueFlow
from web.pagetemplate import PageTemplate


class DiagramPage(PageTemplate):
    def __init__(self, **kwargs):
        self.initial_nodes = [
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
        self.vue_flow = None
        super().__init__(**kwargs)

    def _add_resources(self):
        super()._add_resources()

        ui.add_head_html('''
            <link href="/static/vueflow/css/style.css" rel="stylesheet" />
            <link href="/static/vueflow/css/theme-default.css" rel="stylesheet" />
            <link href="/static/vueflow/css/controls/style.css" rel="stylesheet" />
            <link href="/static/vueflow/css/node-resizer/style.css" rel="stylesheet" />
            <link href="/static/vueflow/css/myvueflow.css" rel="stylesheet" />
            <script src="/static/vueflow/vueflow-component.umd.js" defer></script>
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
            # combined_data = {
            #     'nodes': nodes,
            #     'edges': edges
            # }
            mermaid_data = self.generate_mermaid(nodes, edges)
            self.mermaid_diagram.content = mermaid_data
            ui.notify(f'Mermaid Flow Syntax:\n{mermaid_data}')
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
            filepath = Path('diagram.json').resolve()
            with open(filepath, 'w') as f:
                json.dump(flow_data, f, indent=2)
            ui.notify(f'Diagram saved successfully at: {filepath}', type='positive')
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

    def generate_mermaid(self, nodes, edges):
        mermaid_syntax = [
            "%%{init: {'theme': 'dark'}}%%",
            "flowchart TD"
        ]

        # Process nodes
        for node in nodes:
            node_id = f"node{node['id']}"

            if 'data' in node:
                if 'title' in node['data'] and 'description' in node['data']:
                    # For nodes with title and description, use title=description format
                    node_content = f"{node['data']['title']}={node['data']['description']}"
                elif 'label' in node['data']:
                    # For nodes with just label, use the label
                    node_content = node['data']['label']
                else:
                    node_content = f"Node {node['id']}"

            mermaid_syntax.append(f'    {node_id}["{node_content}"]')

        # Add blank line before edges
        mermaid_syntax.append("")

        # Process edges
        for edge in edges:
            source_id = f"node{edge['source']}"
            target_id = f"node{edge['target']}"
            mermaid_syntax.append(f"    {source_id} --> {target_id}")

        return "\n".join(mermaid_syntax)

    def sidebar(self) -> None:
        with ui.column().classes('w-48 gap-2'):
            ui.button('Add Default Node', on_click=self.add_default_node)
            ui.button('Add Simple Node', on_click=self.add_simple_node)
            ui.button('Add Detail Node', on_click=self.add_detail_node)
            ui.button('Update Default Node1', on_click=self.update_default_node1)
            ui.button('Show Nodes', on_click=self.show_nodes)
            ui.button('Show Edges', on_click=self.show_edges)
            ui.button('Generate mermaid', on_click=self.show_data)
            ui.button('Save Diagram', on_click=self.save_diagram)
            ui.button('Load Diagram', on_click=self.load_diagram)

    def main(self) -> None:
        with ui.row().classes('w-full gap-4 p-4'):
            with ui.column():
                self.vue_flow = VueFlow(
                    nodes=self.initial_nodes,
                    options={'fitView': True},
                    style={'width': '800px', 'height': '800px'},
                    on_node_clicked=self.on_node_clicked_handler
                )

            with ui.column().classes('w-[500px]'):
                self.mermaid_diagram = ui.mermaid('''
                    %%{init: {'theme': 'dark'}}%%
                    flowchart TD
                        A[Start] --> B[End]
                ''').classes('w-[500px] h-[500px] bg-gray-800 p-4 rounded shadow')