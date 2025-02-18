# web/components/vueflow/vueflow.py
from typing import Optional, Dict, List, Any, Callable
import json
from nicegui.element import Element
from nicegui import ui
from pathlib import Path


class VueFlow(Element, component='vueflow.vue'):
    def __init__(
            self,
            nodes: Optional[List[Dict]] = None,
            edges: Optional[List[Dict]] = None,
            options: Optional[Dict] = None,
            style: Optional[Dict] = None,
            on_node_clicked: Optional[Callable] = None,
    ) -> None:
        super().__init__()

        self._props['nodes'] = nodes or []
        self._props['edges'] = edges or []
        self._props['options'] = options or {'fitView': True}
        self._props['style'] = style or {'width': '800px', 'height': '800px'}

        self._nodes = nodes or []

        if on_node_clicked:
            self.on('node_clicked', lambda e: on_node_clicked({
                'node_data': e.args.get('data')
            }))

        self.on('nodes_updated', self._handle_nodes_update)
        self.on('save_to_file', self._handle_save_to_file)
        self.on('load_from_file', self._handle_load_from_file)

    def _handle_nodes_update(self, event):
        """Store the updated nodes."""
        self._nodes = event.args

    async def _handle_save_to_file(self, event):
        """Handle saving diagram to file."""
        try:
            nodes = await self.get_nodes()
            edges = await self.get_edges()
            viewport = await self.get_viewport()

            flow_data = {
                'nodes': nodes,
                'edges': edges,
                'viewport': viewport
            }

            with open('diagram.json', 'w') as f:
                json.dump(flow_data, f, indent=2)

            ui.notify('Diagram saved successfully')
        except Exception as e:
            ui.notify(f'Error saving diagram: {str(e)}', type='error')

    async def _handle_load_from_file(self, event):
        """Handle loading diagram from file."""
        try:
            if not Path('diagram.json').exists():
                ui.notify('No saved diagram found', type='warning')
                return

            with open('diagram.json', 'r') as f:
                flow_data = json.load(f)

            await self.restore_diagram(flow_data)
            ui.notify('Diagram loaded successfully')
        except Exception as e:
            ui.notify(f'Error loading diagram: {str(e)}', type='error')

    async def get_nodes(self) -> List[Dict]:
        """Return current nodes."""
        return await self.run_method('getNodes')

    async def get_nodes_data(self) -> List[Dict]:
        """Return only the 'data' part of each node."""
        nodes = await self.get_nodes()
        return [node.get('data', {}) for node in nodes]

    async def get_edges(self) -> List[Dict]:
        """Return current edges."""
        return await self.run_method('getEdges')

    async def get_viewport(self) -> Dict:
        """Return current viewport state."""
        return await self.run_method('getViewport')

    def add_node(self, node: dict) -> None:
        """Add a new node."""
        self.run_method('addNode', node)

    def update_node(self, node_id: str, updates: dict) -> None:
        """Update an existing node."""
        self.run_method('updateNode', node_id, updates)

    def update_data(self, nodes: List[Dict], edges: List[Dict]) -> None:
        """Update nodes and edges."""
        self._props['nodes'] = nodes
        self._props['edges'] = edges
        self.run_method('updateData', nodes, edges)

    async def restore_diagram(self, flow_data: Dict) -> None:
        """Restore diagram from saved data."""
        # Just use updateData which is what worked before
        self.update_data(flow_data['nodes'], flow_data['edges'])
        if 'viewport' in flow_data:
            await self.run_method('setViewport', flow_data['viewport'])