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


class RecordIDTool(Tool):
    """
    Represents a RecordID tool in an Alteryx workflow.
    Adds a sequential record ID field to each record.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.RecordID.RecordID'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxRecordID'
        self.properties = {
            'Configuration': {
                'FieldName': 'RecordID',
                'StartValue': '1',
                'FieldType': {'@size': '6', '#text': 'Int32'},
                'FieldSize': '6',
                'Position': '0',
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
    def field_name(self) -> str:
        return self._cfg().get('FieldName', 'RecordID')

    @field_name.setter
    def field_name(self, value: str) -> None:
        self._cfg()['FieldName'] = value

    @property
    def start_value(self) -> int:
        return int(self._cfg().get('StartValue', '1'))

    @start_value.setter
    def start_value(self, value: int) -> None:
        self._cfg()['StartValue'] = str(value)

    @property
    def field_type(self) -> str:
        ft = self._cfg().get('FieldType', {})
        if isinstance(ft, dict):
            return ft.get('#text', 'Int32')
        return str(ft)

    @field_type.setter
    def field_type(self, value: str) -> None:
        cfg = self._cfg()
        ft = cfg.get('FieldType', {})
        if isinstance(ft, dict):
            ft['#text'] = value
        else:
            cfg['FieldType'] = {'@size': str(self.field_size), '#text': value}

    @property
    def field_size(self) -> int:
        return int(self._cfg().get('FieldSize', '6'))

    @field_size.setter
    def field_size(self, value: int) -> None:
        cfg = self._cfg()
        cfg['FieldSize'] = str(value)
        ft = cfg.get('FieldType', {})
        if isinstance(ft, dict):
            ft['@size'] = str(value)

    @property
    def field_position(self) -> int:
        """0 = prepend (before first field), 1 = append (after last field)."""
        val = self._cfg().get('Position', '0')
        try:
            return int(val)
        except (ValueError, TypeError):
            return 0

    @field_position.setter
    def field_position(self, value: int) -> None:
        self._cfg()['Position'] = str(value)
