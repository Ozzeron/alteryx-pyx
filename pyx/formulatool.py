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
class FormulaField:
    field: str
    expression: str
    type: str = "V_String"
    size: str = "2147483647"
    enabled: bool = True


class FormulaTool(Tool):
    """
    Represents a Formula tool in an Alteryx workflow.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.Formula.Formula'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxFormula'
        self.properties = {
            'Configuration': {'FormulaFields': {}},
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    @property
    def formulas(self) -> List[FormulaField]:
        """Returns formula fields from the properties dict."""
        cfg = self.properties.get('Configuration', {})
        ff_container = cfg.get('FormulaFields', {})
        if not ff_container:
            return []
        raw = ff_container.get('FormulaField', [])
        if isinstance(raw, dict):
            raw = [raw]
        result = []
        for f in raw:
            result.append(FormulaField(
                field=f.get('@field', ''),
                expression=f.get('@expression', ''),
                type=f.get('@type', 'V_String'),
                size=f.get('@size', '2147483647'),
                enabled=f.get('@enabled', 'true').lower() != 'false' if '@enabled' in f else True,
            ))
        return result

    @formulas.setter
    def formulas(self, value: List[FormulaField]) -> None:
        fields = []
        for ff in value:
            d: dict = {
                '@expression': ff.expression,
                '@field': ff.field,
                '@size': ff.size,
                '@type': ff.type,
            }
            if not ff.enabled:
                d['@enabled'] = 'false'
            fields.append(d)

        if not self.properties:
            self.properties = {}
        if 'Configuration' not in self.properties:
            self.properties['Configuration'] = {}
        self.properties['Configuration']['FormulaFields'] = {
            'FormulaField': fields[0] if len(fields) == 1 else fields
        }
