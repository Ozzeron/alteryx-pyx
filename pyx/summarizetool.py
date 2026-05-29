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
class SummarizeField:
    field: str
    action: str         # e.g. "GroupBy", "Count", "Sum", "Min", "Max", "Concat", ...
    rename: str = ""


class SummarizeTool(Tool):
    """
    Represents a Summarize tool in an Alteryx workflow.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxSpatialPluginsGui.Summarize.Summarize'
        self.engine_dll = 'AlteryxSpatialPluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxSummarize'
        self.properties = {
            'Configuration': {'SummarizeFields': {}},
            'Annotation': {
                '@DisplayMode': '0',
                'Name': None,
                'DefaultAnnotationText': None,
                'Left': {'@value': 'False'},
            }
        }

    @property
    def summarize_fields(self) -> List[SummarizeField]:
        cfg = self.properties.get('Configuration', {})
        sf = cfg.get('SummarizeFields', {})
        if not sf:
            return []
        raw = sf.get('SummarizeField', [])
        if isinstance(raw, dict):
            raw = [raw]
        result = []
        for f in raw:
            result.append(SummarizeField(
                field=f.get('@field', ''),
                action=f.get('@action', ''),
                rename=f.get('@rename', ''),
            ))
        return result

    @summarize_fields.setter
    def summarize_fields(self, value: List[SummarizeField]) -> None:
        fields = []
        for sf in value:
            d: dict = {'@field': sf.field, '@action': sf.action}
            if sf.rename:
                d['@rename'] = sf.rename
            fields.append(d)

        cfg = self.properties.setdefault('Configuration', {})
        cfg['SummarizeFields'] = {
            'SummarizeField': fields[0] if len(fields) == 1 else fields
        }
