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

from typing import List

from .tool import Tool


class UniqueTool(Tool):
    """
    Represents a Unique tool in an Alteryx workflow.
    Outputs unique records based on selected key fields.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.Unique.Unique'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxUnique'
        self.properties = {
            'Configuration': {'UniqueFields': {}},
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    @property
    def key_fields(self) -> List[str]:
        cfg = self.properties.get('Configuration', {})
        uf = cfg.get('UniqueFields', {})
        if not uf:
            return []
        raw = uf.get('Field', [])
        if isinstance(raw, dict):
            raw = [raw]
        return [f.get('@field', '') for f in raw]

    @key_fields.setter
    def key_fields(self, value: List[str]) -> None:
        cfg = self.properties.setdefault('Configuration', {})
        fields = [{'@field': f} for f in value]
        cfg['UniqueFields'] = {
            'Field': fields[0] if len(fields) == 1 else fields
        }
