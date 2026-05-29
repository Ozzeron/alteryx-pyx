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

import xml.etree.ElementTree as ET
import xmltodict
from typing import Dict

from .tool import Tool


class MacroTool(Tool):
    """
    Represents a macro instance tool in an Alteryx workflow.

    Macro tools differ from regular tools:
    - GuiSettings has no Plugin attribute
    - EngineSettings uses @Macro instead of @EngineDll / @EngineDllEntryPoint
    - Configuration contains Value elements (macro interface values)
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = ''  # Macros have no plugin
        self.engine_dll = ''
        self.engine_dll_entry_point = ''
        self.macro_path: str = ''
        self.macro_values: Dict[str, str] = {}
        self.properties = {
            'Configuration': {},
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    def _sync_values_to_properties(self) -> None:
        """Write macro_values dict into properties Configuration as Value list."""
        if not self.macro_values:
            return
        values = [{'@name': k, '#text': v} for k, v in self.macro_values.items()]
        self.properties.setdefault('Configuration', {})['Value'] = (
            values[0] if len(values) == 1 else values
        )

    def _sync_values_from_properties(self) -> None:
        """Read macro_values from properties Configuration Value list."""
        cfg = self.properties.get('Configuration', {})
        raw = cfg.get('Value', [])
        if isinstance(raw, dict):
            raw = [raw]
        self.macro_values = {
            v.get('@name', ''): v.get('#text', '')
            for v in raw
            if isinstance(v, dict)
        }

    def toxml(self) -> ET.Element:
        """Macro XML has no Plugin in GuiSettings and uses @Macro in EngineSettings."""
        self._sync_values_to_properties()

        root = ET.Element('Root')
        node = ET.SubElement(root, 'Node')
        node.set('ToolID', str(self.tool_id))

        gui = ET.SubElement(node, 'GuiSettings')
        # Intentionally no Plugin attribute for macros
        pos = ET.SubElement(gui, 'Position')
        pos.set('x', str(self.position.x))
        pos.set('y', str(self.position.y))

        xml_str = xmltodict.unparse({'Root': {'Properties': self.properties}})
        props_elem = ET.fromstring(xml_str)
        node.extend(props_elem)

        eng = ET.SubElement(node, 'EngineSettings')
        eng.set('Macro', self.macro_path)

        return root

    @classmethod
    def from_node_dict(cls, tool_id: int, node_dict: dict) -> 'MacroTool':
        """Create a MacroTool from a node dict (as parsed by xmltodict)."""
        tool = cls(tool_id)
        tool.macro_path = node_dict.get('EngineSettings', {}).get('@Macro', '')
        tool.properties = node_dict.get('Properties', {})
        tool._sync_values_from_properties()
        return tool
