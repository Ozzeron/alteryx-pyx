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


class GenerateRowsTool(Tool):
    """
    Represents a GenerateRows tool in an Alteryx workflow.
    Generates rows by evaluating init/condition/loop expressions.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.GenerateRows.GenerateRows'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxGenerateRows'
        self.properties = {
            'Configuration': {
                'UpdateField': {'@value': 'True'},
                'UpdateField_Name': '',
                'CreateField_Name': '',
                'CreateField_Type': 'Double',
                'CreateField_Size': '8',
                'Expression_Init': '0',
                'Expression_Cond': '',
                'Expression_Loop': '',
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
    def update_field(self) -> bool:
        val = self._cfg().get('UpdateField', {})
        if isinstance(val, dict):
            return val.get('@value', 'True').lower() == 'true'
        return True

    @update_field.setter
    def update_field(self, value: bool) -> None:
        self._cfg()['UpdateField'] = {'@value': str(value)}

    @property
    def update_field_name(self) -> str:
        return self._cfg().get('UpdateField_Name', '')

    @update_field_name.setter
    def update_field_name(self, value: str) -> None:
        self._cfg()['UpdateField_Name'] = value

    @property
    def create_field_name(self) -> str:
        return self._cfg().get('CreateField_Name', '')

    @create_field_name.setter
    def create_field_name(self, value: str) -> None:
        self._cfg()['CreateField_Name'] = value

    @property
    def create_field_type(self) -> str:
        return self._cfg().get('CreateField_Type', 'Double')

    @create_field_type.setter
    def create_field_type(self, value: str) -> None:
        self._cfg()['CreateField_Type'] = value

    @property
    def init_expr(self) -> str:
        return self._cfg().get('Expression_Init', '')

    @init_expr.setter
    def init_expr(self, value: str) -> None:
        self._cfg()['Expression_Init'] = value

    @property
    def loop_expr(self) -> str:
        return self._cfg().get('Expression_Loop', '')

    @loop_expr.setter
    def loop_expr(self, value: str) -> None:
        self._cfg()['Expression_Loop'] = value

    @property
    def cond_expr(self) -> str:
        return self._cfg().get('Expression_Cond', '')

    @cond_expr.setter
    def cond_expr(self, value: str) -> None:
        self._cfg()['Expression_Cond'] = value
