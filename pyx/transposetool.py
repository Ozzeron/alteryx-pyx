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


class TransposeTool(Tool):
    """
    Represents a Transpose tool in an Alteryx workflow.
    Pivots data from columns to rows.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.Transpose.Transpose'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxTranspose'
        self.properties = {
            'Configuration': {
                'ErrorWarn': 'Warn',
                'KeyFields': {},
                'DataFields': {},
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
    def error_warn(self) -> str:
        return self._cfg().get('ErrorWarn', 'Warn')

    @error_warn.setter
    def error_warn(self, value: str) -> None:
        self._cfg()['ErrorWarn'] = value

    @property
    def key_fields(self) -> List[str]:
        kf = self._cfg().get('KeyFields', {})
        if not kf:
            return []
        raw = kf.get('Field', [])
        if isinstance(raw, dict):
            raw = [raw]
        return [f.get('@field', '') for f in raw]

    @key_fields.setter
    def key_fields(self, value: List[str]) -> None:
        fields = [{'@field': f} for f in value]
        self._cfg()['KeyFields'] = {
            'Field': fields[0] if len(fields) == 1 else fields
        }

    @property
    def data_fields(self) -> List[str]:
        """Returns selected data fields (where @selected != 'False')."""
        df = self._cfg().get('DataFields', {})
        if not df:
            return []
        raw = df.get('Field', [])
        if isinstance(raw, dict):
            raw = [raw]
        return [
            f.get('@field', '')
            for f in raw
            if f.get('@selected', 'True').lower() != 'false'
        ]

    @data_fields.setter
    def data_fields(self, value: List[str]) -> None:
        fields = [{'@field': f, '@selected': 'True'} for f in value]
        self._cfg()['DataFields'] = {
            'Field': fields[0] if len(fields) == 1 else fields
        }
