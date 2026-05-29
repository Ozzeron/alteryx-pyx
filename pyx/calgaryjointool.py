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

from dataclasses import dataclass
from typing import List

from .tool import Tool


@dataclass
class CalgaryJoinField:
    field: str          # input field to match
    index_field: str    # Calgary index field
    query_type: str = "value"
    end_field: str = ""


class CalgaryJoinTool(Tool):
    """
    Represents a CalgaryJoin tool in an Alteryx workflow.
    Performs an indexed lookup against a Calgary (.cydb) database.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'CalgaryPluginsGui.CalgaryJoin.CalgaryJoin'
        self.engine_dll = 'CalgaryPlugins.dll'
        self.engine_dll_entry_point = 'AlteryxCalgaryJoin'
        self.properties = {
            'Configuration': {
                'RootFileName': '',
                'LinkedTables': None,
                'CountOnly': {'@value': 'False'},
                'JoinMode': {'@value': 'False'},
                'MatchAll': {'@value': 'False'},
                'OutputUnjoined': {'@value': 'True'},
                'Query': None,
                'JoinFields': {},
            },
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    def _cfg(self) -> dict:
        return self.properties.setdefault('Configuration', {})

    @property
    def root_file_name(self) -> str:
        return self._cfg().get('RootFileName', '')

    @root_file_name.setter
    def root_file_name(self, value: str) -> None:
        self._cfg()['RootFileName'] = value

    @property
    def output_unjoined(self) -> bool:
        val = self._cfg().get('OutputUnjoined', {})
        if isinstance(val, dict):
            return val.get('@value', 'True').lower() == 'true'
        return True

    @output_unjoined.setter
    def output_unjoined(self, value: bool) -> None:
        self._cfg()['OutputUnjoined'] = {'@value': str(value)}

    @property
    def join_fields(self) -> List[CalgaryJoinField]:
        jf = self._cfg().get('JoinFields', {})
        if not jf:
            return []
        raw = jf.get('Field', [])
        if isinstance(raw, dict):
            raw = [raw]
        result = []
        for f in raw:
            result.append(CalgaryJoinField(
                field=f.get('@field', ''),
                index_field=f.get('@indexField', ''),
                query_type=f.get('@queryType', 'value'),
                end_field=f.get('@endField', ''),
            ))
        return result

    @join_fields.setter
    def join_fields(self, value: List[CalgaryJoinField]) -> None:
        fields = []
        for cjf in value:
            d: dict = {
                '@field': cjf.field,
                '@indexField': cjf.index_field,
                '@queryType': cjf.query_type,
                '@endField': cjf.end_field,
            }
            fields.append(d)
        self._cfg()['JoinFields'] = {
            'Field': fields[0] if len(fields) == 1 else fields
        }
