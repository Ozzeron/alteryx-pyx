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


class RunningTotalTool(Tool):
    """
    Represents a RunningTotal tool in an Alteryx workflow.
    Computes a running total for selected fields, optionally grouped.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.RunningTotal.RunningTotal'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxRunningTotal'
        self.properties = {
            'Configuration': {
                'GroupByFields': {},
                'RunningTotalFields': {},
            },
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    def _get_field_list(self, section: str) -> List[str]:
        cfg = self.properties.get('Configuration', {})
        container = cfg.get(section, {})
        if not container:
            return []
        raw = container.get('Field', [])
        if isinstance(raw, dict):
            raw = [raw]
        return [f.get('@field', '') for f in raw]

    def _set_field_list(self, section: str, value: List[str]) -> None:
        cfg = self.properties.setdefault('Configuration', {})
        fields = [{'@field': f} for f in value]
        cfg[section] = {
            'Field': fields[0] if len(fields) == 1 else fields
        }

    @property
    def group_by(self) -> List[str]:
        return self._get_field_list('GroupByFields')

    @group_by.setter
    def group_by(self, value: List[str]) -> None:
        self._set_field_list('GroupByFields', value)

    @property
    def running_total_fields(self) -> List[str]:
        return self._get_field_list('RunningTotalFields')

    @running_total_fields.setter
    def running_total_fields(self, value: List[str]) -> None:
        self._set_field_list('RunningTotalFields', value)
