# Pyx, a Python module for creating, reading, and editing Alteryx Designer workflows entirely in code
# Copyright (C) 2020  David T. Wilcox

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
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class OutputToolConfiguration:
    """
    Contains configuration information for an OutputTool isntance.
    """
    output_file_name: str = ''
    max_records: int = -1 
    file_format: int = 0
    line_end_style: str = 'CRLF'
    delimiter: str = ','
    force_quotes: bool = False
    header_row: bool = True
    code_page: int = 28591
    write_bom: bool = True
    multi_file: bool = False


class OutputTool(Tool):
    """
    Represents an Output tool in an Alteryx workflow.
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.DbFileOutput.DbFileOutput'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxDbFileOutput'

        super()._can_have_output(False)
    def _text(self, v, default=''):
        """Handle both plain string and {'#text': ...} dict from xmltodict."""
        if isinstance(v, dict):
            return v.get('#text', default)
        return v if isinstance(v, str) else default

    def _xml_bool_prop(self, v, default=False):
        s = self._text(v, '').lower()
        return s in ('true', '1', 'yes') if s else default

    @property
    def _configuration(self):
        if self.properties:
            return self.properties.get('Configuration', {})
        return {}

    @property
    def output_file_name(self) -> str:
        return self._text(self._configuration.get('File', {}), '')

    @output_file_name.setter
    def output_file_name(self, value: str) -> None:
        cfg = self._configuration
        file_node = cfg.get('File', {})
        if isinstance(file_node, dict):
            file_node['#text'] = value
        else:
            cfg['File'] = value

    @property
    def disabled(self) -> bool:
        return self._xml_bool_prop(self._configuration.get('Disable', 'False'))

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._configuration['Disable'] = str(value)

    @property
    def max_records(self) -> int:
        file_node = self._configuration.get('File', {})
        if isinstance(file_node, dict):
            return int(file_node.get('@MaxRecords', -1) or -1)
        return -1

    @max_records.setter
    def max_records(self, value: int) -> None:
        cfg = self._configuration
        file_node = cfg.get('File')
        if not isinstance(file_node, dict):
            file_node = {'#text': str(file_node or ''), '@MaxRecords': str(value)}
            cfg['File'] = file_node
        else:
            file_node['@MaxRecords'] = str(value)

    @property
    def delimiter(self) -> str:
        opts = self._configuration.get('FormatSpecificOptions', {})
        return self._text(opts.get('Delimeter', ','), ',')

    @delimiter.setter
    def delimiter(self, value: str) -> None:
        opts = self._configuration.setdefault('FormatSpecificOptions', {})
        opts['Delimeter'] = value

    @property
    def header_row(self) -> bool:
        opts = self._configuration.get('FormatSpecificOptions', {})
        return self._xml_bool_prop(opts.get('HeaderRow', 'True'), True)

    @header_row.setter
    def header_row(self, value: bool) -> None:
        opts = self._configuration.setdefault('FormatSpecificOptions', {})
        opts['HeaderRow'] = str(value)
