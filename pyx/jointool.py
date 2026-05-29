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


class JoinTool(Tool):
    """
    Represents a Join tool in an Alteryx workflow.
    Joins two inputs on matching key fields (or by record position).
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.Join.Join'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxJoin'
        self.properties = {
            'Configuration': {
                '@joinByRecordPos': 'False',
                'JoinInfo': [
                    {'@connection': 'Left', 'Field': {'@field': ''}},
                    {'@connection': 'Right', 'Field': {'@field': ''}},
                ],
            },
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    @property
    def join_by_record_pos(self) -> bool:
        cfg = self.properties.get('Configuration', {})
        return cfg.get('@joinByRecordPos', 'False').lower() == 'true'

    @join_by_record_pos.setter
    def join_by_record_pos(self, value: bool) -> None:
        self.properties['Configuration']['@joinByRecordPos'] = str(value)

    @property
    def left_keys(self) -> List[str]:
        return self._get_keys('Left')

    @left_keys.setter
    def left_keys(self, value: List[str]) -> None:
        self._set_keys('Left', value)

    @property
    def right_keys(self) -> List[str]:
        return self._get_keys('Right')

    @right_keys.setter
    def right_keys(self, value: List[str]) -> None:
        self._set_keys('Right', value)

    def _get_keys(self, connection: str) -> List[str]:
        cfg = self.properties.get('Configuration', {})
        join_infos = cfg.get('JoinInfo', [])
        if isinstance(join_infos, dict):
            join_infos = [join_infos]
        for ji in join_infos:
            if ji.get('@connection') == connection:
                fields = ji.get('Field', [])
                if isinstance(fields, dict):
                    fields = [fields]
                return [f.get('@field', '') for f in fields]
        return []

    def _set_keys(self, connection: str, keys: List[str]) -> None:
        cfg = self.properties.setdefault('Configuration', {})
        join_infos = cfg.get('JoinInfo', [])
        if isinstance(join_infos, dict):
            join_infos = [join_infos]
        for ji in join_infos:
            if ji.get('@connection') == connection:
                ji['Field'] = (
                    {'@field': keys[0]} if len(keys) == 1
                    else [{'@field': k} for k in keys]
                )
                cfg['JoinInfo'] = join_infos
                return
        # Connection not found — add it
        join_infos.append({
            '@connection': connection,
            'Field': {'@field': keys[0]} if len(keys) == 1 else [{'@field': k} for k in keys],
        })
        cfg['JoinInfo'] = join_infos
