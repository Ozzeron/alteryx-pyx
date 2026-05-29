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
from typing import List

from .tool import Tool


class ContainerTool(Tool):
    """
    Represents a ToolContainer in an Alteryx workflow.
    Containers group child tools visually and can be disabled/folded.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxGuiToolkit.ToolContainer.ToolContainer'
        # Containers have no engine
        self.engine_dll = ''
        self.engine_dll_entry_point = ''
        self._can_have_input = False
        self._can_have_output = False
        self.width = 200
        self.height = 160
        # IDs of tools inside this container
        self.children: List[int] = []
        # Raw child node dicts (set during read) for round-trip XML fidelity
        self._child_nodes_raw: list = []
        self.properties = {
            'Configuration': {
                'Caption': f'Container {tool_id}',
                'Style': {
                    '@TextColor': '#314c4a',
                    '@FillColor': '#ecf2f2',
                    '@BorderColor': '#314c4a',
                    '@Transparency': '25',
                    '@Margin': '25',
                },
                'Disabled': {'@value': 'False'},
                'Folded': {'@value': 'False'},
            },
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    @property
    def caption(self) -> str:
        return self.properties.get('Configuration', {}).get('Caption', '')

    @caption.setter
    def caption(self, value: str) -> None:
        self.properties.setdefault('Configuration', {})['Caption'] = value

    @property
    def disabled(self) -> bool:
        val = self.properties.get('Configuration', {}).get('Disabled', {})
        if isinstance(val, dict):
            return val.get('@value', 'False').lower() == 'true'
        return False

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self.properties.setdefault('Configuration', {})['Disabled'] = {'@value': str(value)}

    @property
    def folded(self) -> bool:
        val = self.properties.get('Configuration', {}).get('Folded', {})
        if isinstance(val, dict):
            return val.get('@value', 'False').lower() == 'true'
        return False

    @folded.setter
    def folded(self, value: bool) -> None:
        self.properties.setdefault('Configuration', {})['Folded'] = {'@value': str(value)}

    @property
    def style(self) -> dict:
        return self.properties.get('Configuration', {}).get('Style', {})

    @style.setter
    def style(self, value: dict) -> None:
        self.properties.setdefault('Configuration', {})['Style'] = value

    def toxml(self) -> ET.Element:
        """
        Container XML includes a <ChildNodes> section and has no <EngineSettings>.
        Position element includes width/height attributes.
        """
        root = ET.Element('Root')
        node = ET.SubElement(root, 'Node')
        node.set('ToolID', str(self.tool_id))

        gui = ET.SubElement(node, 'GuiSettings')
        gui.set('Plugin', self.plugin)
        pos = ET.SubElement(gui, 'Position')
        pos.set('x', str(self.position.x))
        pos.set('y', str(self.position.y))
        pos.set('width', str(self.width))
        pos.set('height', str(self.height))

        xml_str = xmltodict.unparse({'Root': {'Properties': self.properties}})
        props_elem = ET.fromstring(xml_str)
        node.extend(props_elem)

        # ChildNodes section
        if self._child_nodes_raw or self.children:
            child_nodes_elem = ET.SubElement(node, 'ChildNodes')
            if self._child_nodes_raw:
                # Round-trip: re-serialize the raw dicts
                for raw_child in self._child_nodes_raw:
                    child_xml = xmltodict.unparse({'Node': raw_child})
                    child_node_elem = ET.fromstring(child_xml)
                    child_nodes_elem.append(child_node_elem)
            else:
                # Minimal: just reference tool IDs
                for child_id in self.children:
                    child_elem = ET.SubElement(child_nodes_elem, 'Node')
                    child_elem.set('ToolID', str(child_id))

        # No EngineSettings for Container
        return root
