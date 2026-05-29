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

from .tool import Tool


class BrowseTool(Tool):
    """
    Represents a BrowseV2 tool in an Alteryx workflow.
    A sink tool for browsing/inspecting data. Has no output connections.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.BrowseV2.BrowseV2'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxBrowseV2'
        self._can_have_output = False
        self.properties = {
            'Configuration': {
                'TempFile': '',
                'TempFileDataProfiling': None,
                'Layout': {'View1': {'Hints': {'Table': None}}},
            },
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    @property
    def temp_file(self) -> str:
        cfg = self.properties.get('Configuration', {})
        return cfg.get('TempFile', '')

    @temp_file.setter
    def temp_file(self, value: str) -> None:
        self.properties.setdefault('Configuration', {})['TempFile'] = value
