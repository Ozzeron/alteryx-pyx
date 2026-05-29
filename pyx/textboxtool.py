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

from .tool import Tool


class TextBoxTool(Tool):
    """
    Represents a TextBox annotation tool in an Alteryx workflow.
    A visual label with no data connections.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxGuiToolkit.TextBox.TextBox'
        # TextBox has no EngineSettings
        self.engine_dll = ''
        self.engine_dll_entry_point = ''
        self._can_have_input = False
        self._can_have_output = False
        self.width = 100
        self.height = 40
        self.properties = {
            'Configuration': {
                'Text': '',
                'Font': {'@name': 'Arial', '@size': '8.25', '@style': '0'},
                'TextColor': {'@name': 'Black'},
                'FillColor': {'@name': 'White'},
                'Shape': {'@shape': '0'},
                'Justification': {'@Justification': '4'},
            },
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    @property
    def text(self) -> str:
        return self.properties.get('Configuration', {}).get('Text', '')

    @text.setter
    def text(self, value: str) -> None:
        self.properties.setdefault('Configuration', {})['Text'] = value

    @property
    def fill_color(self) -> str:
        return self.properties.get('Configuration', {}).get('FillColor', {}).get('@name', 'White')

    @fill_color.setter
    def fill_color(self, value: str) -> None:
        self.properties.setdefault('Configuration', {}).setdefault('FillColor', {})['@name'] = value

    @property
    def text_color(self) -> str:
        return self.properties.get('Configuration', {}).get('TextColor', {}).get('@name', 'Black')

    @text_color.setter
    def text_color(self, value: str) -> None:
        self.properties.setdefault('Configuration', {}).setdefault('TextColor', {})['@name'] = value

    @property
    def shape(self) -> int:
        return int(self.properties.get('Configuration', {}).get('Shape', {}).get('@shape', '0'))

    @shape.setter
    def shape(self, value: int) -> None:
        self.properties.setdefault('Configuration', {}).setdefault('Shape', {})['@shape'] = str(value)

    def toxml(self) -> ET.Element:
        """TextBox has no EngineSettings element."""
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

        # No EngineSettings for TextBox
        return root
