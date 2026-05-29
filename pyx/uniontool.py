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


class UnionTool(Tool):
    """
    Represents a Union tool in an Alteryx workflow.
    Combines multiple input streams into one.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.Union.Union'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxUnion'
        self.properties = {
            'Configuration': {
                'ByName_ErrorMode': 'Warning',
                'ByName_OutputMode': 'All',
                'Mode': 'ByName',
                'SetOutputOrder': {'@value': 'False'},
            },
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    @property
    def mode(self) -> str:
        cfg = self.properties.get('Configuration', {})
        return cfg.get('Mode') or cfg.get('AutoResetMode', 'ByName')

    @mode.setter
    def mode(self, value: str) -> None:
        cfg = self.properties.setdefault('Configuration', {})
        # Support both schema variants
        if 'AutoResetMode' in cfg:
            cfg['AutoResetMode'] = value
        else:
            cfg['Mode'] = value

    @property
    def error_mode(self) -> str:
        cfg = self.properties.get('Configuration', {})
        return cfg.get('ByName_ErrorMode', 'Warning')

    @error_mode.setter
    def error_mode(self, value: str) -> None:
        self.properties.setdefault('Configuration', {})['ByName_ErrorMode'] = value

    @property
    def output_mode(self) -> str:
        cfg = self.properties.get('Configuration', {})
        return cfg.get('ByName_OutputMode', 'All')

    @output_mode.setter
    def output_mode(self, value: str) -> None:
        self.properties.setdefault('Configuration', {})['ByName_OutputMode'] = value
