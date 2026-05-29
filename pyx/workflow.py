# Pyx, a Python module for creating, reading, and editing Alteryx Designer workflows entirely in code
# Copyright (C) 2020  David T. Wilcox
# Fork: alteryx-pyx — extended for automotive data pipelines

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from xml.dom import minidom
import xmltodict

from .connection import Connection
from .decorators import newobj
from .tool import Tool, ToolPosition
from .tool_factory import ToolFactory
from .containertool import ContainerTool
from .macrotool import MacroTool


class Workflow:
    """
    Contains operations to create, modify, read, and write Alteryx workflows.
    """

    def __init__(self):
        self._name: str = ''
        self._filename: str = ''
        self._yxmd_version: str = ''
        self._tools: Dict[int, Tool] = {}
        self._connections: List[Connection] = []
        self._properties: Dict[str, Any] = {}

    # ── Properties ─────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value: str) -> None:
        self._filename = value

    @property
    def yxmd_version(self) -> str:
        return self._yxmd_version

    @yxmd_version.setter
    def yxmd_version(self, value: str) -> None:
        self._yxmd_version = value

    @property
    def tools(self) -> Dict[int, Tool]:
        return self._tools

    @tools.setter
    def tools(self, value: Dict[int, Tool]) -> None:
        self._tools = value

    @property
    def connections(self) -> List[Connection]:
        return self._connections

    @connections.setter
    def connections(self, value: List[Connection]) -> None:
        self._connections = value

    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties

    @properties.setter
    def properties(self, value: Dict[str, Any]) -> None:
        self._properties = value

    # ── Tool / Connection mutators ──────────────────────────────────────────────

    @newobj
    def add_tool(self, tool: Tool) -> '__class__':
        """Adds the provided Tool instance to the workflow (replaces on duplicate ID)."""
        self.tools[tool.tool_id] = tool

    @newobj
    def remove_tool(self, tool_id: int) -> '__class__':
        """Removes the tool with the provided ID from the workflow."""
        self.tools.pop(tool_id, None)

    @newobj
    def add_connection(self, origin_tool_id: int, origin_output: str,
                       destination_tool_id: int, destination_input: str) -> '__class__':
        """Adds a connection between two tools."""
        self.connections.append(
            Connection(origin_tool_id, origin_output, destination_tool_id, destination_input)
        )

    @newobj
    def remove_connection(self, origin_tool_id: int, origin_output: str,
                          destination_tool_id: int, destination_input: str) -> '__class__':
        """Removes a connection from the workflow."""
        for c in self.connections:
            if (c.origin_tool_id == origin_tool_id
                    and c.origin_output == origin_output
                    and c.destination_tool_id == destination_tool_id
                    and c.destination_input == destination_input):
                self.connections.remove(c)

    def get_new_tool_id(self) -> int:
        """Gets a new unique tool ID (max existing + 1)."""
        if not self.tools:
            return 1
        return max(self.tools.keys()) + 1

    # ── Position helpers ────────────────────────────────────────────────────────

    def position_left(self, tool_id: int, padding: int = 100) -> ToolPosition:
        return ToolPosition(x=self.tools[tool_id].position.x - padding,
                            y=self.tools[tool_id].position.y)

    def position_right(self, tool_id: int, padding: int = 100) -> ToolPosition:
        return ToolPosition(x=self.tools[tool_id].position.x + padding,
                            y=self.tools[tool_id].position.y)

    def position_above(self, tool_id: int, padding: int = 100) -> ToolPosition:
        return ToolPosition(x=self.tools[tool_id].position.x,
                            y=self.tools[tool_id].position.y - padding)

    def position_below(self, tool_id: int, padding: int = 100) -> ToolPosition:
        return ToolPosition(x=self.tools[tool_id].position.x,
                            y=self.tools[tool_id].position.y + padding)

    # ── Query helpers ───────────────────────────────────────────────────────────

    def get_tools_by_plugin(self, plugin_name: str) -> List[Tool]:
        """Returns all tools with the given plugin name (case-insensitive suffix match ok)."""
        result = []
        for tool in self._tools.values():
            if tool.plugin == plugin_name or tool.plugin.endswith(plugin_name):
                result.append(tool)
        return result

    def get_tools_in_container(self, container_id: int) -> List[Tool]:
        """Returns all tools whose container_id matches the given container tool ID."""
        return [t for t in self._tools.values()
                if getattr(t, 'container_id', None) == container_id]

    # ── Compact JSON export ─────────────────────────────────────────────────────

    def to_compact_json(self, max_expr_len: int = 200) -> dict:
        """
        Returns a minimal dict representation of the workflow suitable for LLM context.
        Format: {tool_id: {plugin, annotation, key_config}} plus a connections list.
        Much smaller than the full XML.
        """
        tools_out = {}
        for tid, tool in self._tools.items():
            plugin = tool.plugin or (
                f"macro:{getattr(tool, 'macro_path', '')}" if isinstance(tool, MacroTool) else 'unknown'
            )

            # Best-effort annotation text
            annotation = ''
            if tool.properties:
                ann = tool.properties.get('Annotation', {})
                if ann:
                    annotation = (ann.get('DefaultAnnotationText') or ann.get('Name') or '')

            # Key config — extract the most useful bits per tool type
            key_config = _extract_key_config(tool, max_expr_len=max_expr_len)

            tools_out[str(tid)] = {
                'plugin': plugin,
                'pos': f"{tool.position.x},{tool.position.y}",
                'annotation': annotation or None,
                'config': key_config or None,
            }

        connections_out = [
            {
                'from': f"{c.origin_tool_id}:{c.origin_output}",
                'to': f"{c.destination_tool_id}:{c.destination_input}",
            }
            for c in self._connections
        ]

        return {
            'name': self._name,
            'version': self._yxmd_version,
            'tools': tools_out,
            'connections': connections_out,
        }

    # ── XML serialization ───────────────────────────────────────────────────────

    def toxml(self) -> ET.Element:
        """Returns an XML representation of the workflow."""
        ayx_doc = ET.Element('AlteryxDocument')
        ayx_doc.set('yxmdVer', self.yxmd_version)

        tools_elem = ET.SubElement(ayx_doc, 'Nodes')
        for tool in self.tools.values():
            tools_elem.extend(tool.toxml())

        connections_elem = ET.SubElement(ayx_doc, 'Connections')
        for connection in self.connections:
            connections_elem.extend(connection.toxml())

        xml_str: str = xmltodict.unparse({'Root': {'Properties': self.properties}})
        props_elem: ET.Element = ET.fromstring(xml_str)
        ayx_doc.extend(props_elem)

        return ayx_doc

    def __repr__(self) -> str:
        xml = self.toxml()
        text = ET.tostring(xml, 'utf-8')
        parsed = minidom.parseString(text)
        return parsed.toprettyxml(indent='  ').replace('&quot;', '"')

    # ── Static methods ──────────────────────────────────────────────────────────

    @staticmethod
    def write(workflow: 'Workflow', filename: str, overwrite: bool = True) -> None:
        """Writes the workflow to a file."""
        if not overwrite and os.path.isfile(filename):
            raise FileExistsError(f"File '{filename}' already exists and overwrite is false")
        with open(filename, 'w') as f:
            f.write(str(workflow))

    @staticmethod
    def read(filename: str) -> 'Workflow':
        """Reads a workflow from an Alteryx XML file (.yxmd / .yxmc / .xml)."""
        workflow = Workflow()
        workflow.filename = filename

        with open(filename) as wf:
            xml = xmltodict.parse(wf.read())

        ayx_doc = xml['AlteryxDocument']

        try:
            workflow.name = ayx_doc['Properties']['MetaInfo']['Name']
        except (KeyError, TypeError):
            workflow.name = os.path.splitext(os.path.basename(filename))[0]

        workflow.yxmd_version = ayx_doc.get('@yxmdVer', '')

        # ── Parse nodes ────────────────────────────────────────────────────────
        nodes_section = ayx_doc.get('Nodes', {})
        if not nodes_section:
            workflow.properties = ayx_doc.get('Properties', {})
            return workflow

        raw_nodes = nodes_section.get('Node', [])
        if isinstance(raw_nodes, dict):
            raw_nodes = [raw_nodes]

        def _parse_node(node: dict, container_id: Optional[int] = None) -> None:
            """Parse a single node dict and add to workflow.tools, recursing into ChildNodes."""
            from .textboxtool import TextBoxTool

            tool_id: int = int(node['@ToolID'])
            gui_settings = node.get('GuiSettings', {})

            # ── Macro detection ─────────────────────────────────────────────────
            if ToolFactory.is_macro_node(node):
                tool = MacroTool.from_node_dict(tool_id, node)
            else:
                plugin = gui_settings.get('@Plugin', '')
                tool = ToolFactory.create_tool(plugin, tool_id)
                tool.plugin = plugin

                engine_settings = node.get('EngineSettings', {})
                if engine_settings:
                    tool.engine_dll = engine_settings.get('@EngineDll', '')
                    tool.engine_dll_entry_point = engine_settings.get('@EngineDllEntryPoint', '')

                tool.properties = node.get('Properties', {})

            # ── Position ────────────────────────────────────────────────────────
            position = gui_settings.get('Position', {})
            if position:
                tool.position = ToolPosition(
                    x=int(position.get('@x', 0)),
                    y=int(position.get('@y', 0)),
                )

            # ── Container-specific extras ───────────────────────────────────────
            if isinstance(tool, ContainerTool):
                tool.width = int(position.get('@width', 200))
                tool.height = int(position.get('@height', 160))
                child_nodes_section = node.get('ChildNodes', {})
                if child_nodes_section:
                    child_raw = child_nodes_section.get('Node', [])
                    if isinstance(child_raw, dict):
                        child_raw = [child_raw]
                    tool._child_nodes_raw = child_raw
                    tool.children = [int(c['@ToolID']) for c in child_raw if '@ToolID' in c]
                    # Recursively parse child tools
                    for child_node in child_raw:
                        _parse_node(child_node, container_id=tool_id)

            # ── TextBox width/height ────────────────────────────────────────────
            if isinstance(tool, TextBoxTool):
                tool.width = int(position.get('@width', 100))
                tool.height = int(position.get('@height', 40))

            # ── Container membership ────────────────────────────────────────────
            if container_id is not None:
                tool.container_id = container_id  # type: ignore[attr-defined]

            workflow.tools[tool_id] = tool

        for node in raw_nodes:
            _parse_node(node, container_id=None)

        # ── Parse connections ───────────────────────────────────────────────────
        connections_section = ayx_doc.get('Connections', {})
        if connections_section:
            raw_connections = connections_section.get('Connection', [])
            if isinstance(raw_connections, dict):
                raw_connections = [raw_connections]

            for connection in raw_connections:
                origin = connection.get('Origin', {})
                destination = connection.get('Destination', {})

                origin_tool_id = int(origin.get('@ToolID', 0))
                origin_conn = origin.get('@Connection', 'Output')
                dest_tool_id = int(destination.get('@ToolID', 0))
                dest_conn = destination.get('@Connection', 'Input')

                workflow.connections.append(
                    Connection(origin_tool_id, origin_conn, dest_tool_id, dest_conn)
                )

                if origin_tool_id in workflow.tools:
                    workflow.tools[origin_tool_id].add_output(
                        dest_tool_id, origin_conn, dest_conn
                    )
                if dest_tool_id in workflow.tools:
                    workflow.tools[dest_tool_id].add_input(
                        origin_tool_id, origin_conn, dest_conn
                    )

        workflow.properties = ayx_doc.get('Properties', {})
        return workflow

    @staticmethod
    def run(filename: str, executable_path: str, overwrite: bool = True) -> None:
        """Runs the workflow using a locally installed copy of the Alteryx engine."""
        cmd = f"{executable_path} {filename}"
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, creationflags=0x08000000)
        process.wait()


# ── Helper: compact config extraction ──────────────────────────────────────────

def _extract_key_config(tool: Tool, max_expr_len: int = 200) -> Optional[dict]:
    """Extract the most informative config fields for LLM-friendly compact JSON."""
    from .formulatool import FormulaTool
    from .jointool import JoinTool
    from .uniquetool import UniqueTool
    from .summarizetool import SummarizeTool
    from .runningtotaltool import RunningTotalTool
    from .containertool import ContainerTool
    from .calgaryjointool import CalgaryJoinTool
    from .recordidtool import RecordIDTool
    from .filtertool import FilterTool
    from .generaterowstool import GenerateRowsTool

    cfg = tool.properties.get('Configuration', {}) if tool.properties else {}
    if not cfg:
        return None

    if isinstance(tool, FormulaTool):
        formulas = tool.formulas
        def _trunc(s): return s if len(s) <= max_expr_len else s[:max_expr_len] + '...'
        return {'formulas': [{'field': f.field, 'expr': _trunc(f.expression)} for f in formulas]}

    if isinstance(tool, JoinTool):
        return {'left_keys': tool.left_keys, 'right_keys': tool.right_keys}

    if isinstance(tool, UniqueTool):
        return {'key_fields': tool.key_fields}

    if isinstance(tool, SummarizeTool):
        return {'fields': [{'field': f.field, 'action': f.action} for f in tool.summarize_fields]}

    if isinstance(tool, RunningTotalTool):
        return {'group_by': tool.group_by, 'total_fields': tool.running_total_fields}

    if isinstance(tool, ContainerTool):
        return {'caption': tool.caption, 'disabled': tool.disabled,
                'children': tool.children}

    if isinstance(tool, CalgaryJoinTool):
        return {'db': tool.root_file_name,
                'join_fields': [{'field': f.field, 'index': f.index_field}
                                for f in tool.join_fields]}

    if isinstance(tool, RecordIDTool):
        return {'field': tool.field_name, 'start': tool.start_value, 'type': tool.field_type, 'pos': tool.field_position}

    if isinstance(tool, FilterTool):
        try:
            mode = str(tool.filter_mode)
            if mode == 'Custom':
                expr = str(tool.expression or '')
                if len(expr) > max_expr_len:
                    expr = expr[:max_expr_len] + f'... [{len(expr)} chars]'
                return {'mode': mode, 'expression': expr}
            return {'mode': mode}
        except Exception:
            pass

    if isinstance(tool, GenerateRowsTool):
        return {'init': tool.init_expr, 'cond': tool.cond_expr, 'loop': tool.loop_expr}

    if isinstance(tool, MacroTool):
        return {'macro': tool.macro_path, 'values': tool.macro_values}

    # Generic fallback: grab simple string values from config
    simple = {}
    for k, v in cfg.items():
        if isinstance(v, str) and not k.startswith('@'):
            simple[k] = v if len(v) <= max_expr_len else v[:max_expr_len] + f'... [{len(v)} chars]'
    return simple or None
