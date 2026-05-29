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
from typing import Dict, Any
from enum import Enum
from datetime import datetime


def _text(v, default=''):
    """Handle both plain string and {'#text': ...} dict from xmltodict."""
    if isinstance(v, dict):
        return v.get('#text', default)
    return v if isinstance(v, str) else default


def _xml_bool(v, default=False):
    s = _text(v, '').lower()
    return s in ('true', '1', 'yes') if s else default


class FilterMode(Enum):
    SIMPLE = 'Simple'
    CUSTOM = 'Custom'

    def __str__(self) -> str:
        return self.value


class FilterOperator(Enum):
    IS_FALSE = 'IsFalse'
    IS_TRUE = 'IsTrue'
    IS_EMPTY = 'IsEmpty'
    IS_NOT_EMPTY = 'IsNotEmpty'
    IS_NULL = 'IsNull'
    IS_NOT_NULL = 'IsNotNull'
    EQUAL = '='
    NOT_EQUAL = '!='
    GREATER_THAN = '&gt;'
    GREATER_THAN_OR_EQUAL = '&gt;='
    LESS_THAN = '&lt;'
    LESS_THAN_OR_EQUAL = '&lt;='
    CONTAINS = 'Contains'
    DOES_NOT_CONTAIN = 'NotContains'
    DATE_RANGE = 'DateRange'
    PERIOD_AFTER = 'PeriodAfter'
    PERIOD_BEFORE = 'PeriodBefore'

    def __str__(self) -> str:
        return self.value


class FilterDateType(Enum):
    FIXED = 'Fixed'
    YESTERDAY = 'Yesterday'
    TODAY = 'Today'
    TOMORROW = 'Tomorrow'

    def __str__(self) -> str:
        return self.value


class FilterPeriodType(Enum):
    DAYS = 'Days'
    WEEKS = 'Weeks'
    MONTHS = 'Months'
    QUARTERS = 'Quarters'
    YEARS = 'Years'

    def __str__(self) -> str:
        return self.value


class FilterTool(Tool):
    """
    Represents a Filter tool in an Alteryx workflow.
    """
    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.Filter.Filter'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxFilter'

    @property
    def filter_mode(self) -> FilterMode:
        return FilterMode(_text(self._configuration.get('Mode'), 'Custom'))

    @filter_mode.setter
    def filter_mode(self, value: FilterMode) -> None:
        mode_node = self._configuration.get('Mode')
        if isinstance(mode_node, dict):
            mode_node['#text'] = str(value)
        else:
            self._configuration['Mode'] = str(value)

    @property
    def operator(self) -> FilterOperator:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter operator when not in simple mode')
        return FilterOperator(_text(self._config_simple.get('Operator'), ''))

    @operator.setter
    def operator(self, value: FilterOperator) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot set filter operator when not in simple mode')
        op_node = self._config_simple.get('Operator')
        if isinstance(op_node, dict):
            op_node['#text'] = str(value)
        else:
            self._config_simple['Operator'] = str(value)

    @property
    def field(self) -> str:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter field when not in simple mode')
        simple = self._config_simple
        field_node = simple.get('Field', {})
        return _text(field_node, '')

    @field.setter
    def field(self, value: str) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot set filter field when not in simple mode')
        if value == '':
            raise ValueError('Filter field cannot be empty.')
        field_node = self._config_simple.get('Field')
        if isinstance(field_node, dict):
            field_node['#text'] = value
        else:
            self._config_simple['Field'] = value

    @property
    def operand(self) -> str:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter operand when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        return _text(operands.get('Operand', {}), '')

    @operand.setter
    def operand(self, value: str) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot set filter operand when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        op_node = operands.get('Operand')
        if isinstance(op_node, dict):
            op_node['#text'] = value
        else:
            operands['Operand'] = value

    @property
    def ignore_time_in_datetime(self) -> bool:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter ignore time in datetime flag when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        return _xml_bool(operands.get('IgnoreTimeInDateTime', 'false'))

    @ignore_time_in_datetime.setter
    def ignore_time_in_datetime(self, value: bool) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot set filter ignore time in datetime flag  when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        node = operands.get('IgnoreTimeInDateTime')
        if isinstance(node, dict):
            node['#text'] = str(value)
        else:
            operands['IgnoreTimeInDateTime'] = str(value)

    @property
    def date_type(self) -> FilterDateType:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter date type when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        return FilterDateType(_text(operands.get('DateType', {}), 'Fixed'))

    @date_type.setter
    def date_type(self, value: FilterDateType) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter date type when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        node = operands.get('DateType')
        if isinstance(node, dict):
            node['#text'] = str(value)
        else:
            operands['DateType'] = str(value)

    @property
    def period_date(self) -> datetime:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter period date when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        return datetime.strptime(_text(operands.get('PeriodDate', {}), ''), '%Y-%m-%d %H:%M:%S')

    @period_date.setter
    def period_date(self, value: datetime) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot set filter period date when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        node = operands.get('PeriodDate')
        if isinstance(node, dict):
            node['#text'] = value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            operands['PeriodDate'] = value.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def period_type(self) -> FilterPeriodType:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter period type when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        return FilterPeriodType(_text(operands.get('PeriodType', {}), 'Days'))

    @period_type.setter
    def period_type(self, value: FilterPeriodType) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter period type when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        node = operands.get('PeriodType')
        if isinstance(node, dict):
            node['#text'] = str(value)
        else:
            operands['PeriodType'] = str(value)

    @property
    def period_count(self) -> int:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter period count when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        return int(_text(operands.get('PeriodCount', {}), '0'))

    @period_count.setter
    def period_count(self, value: int) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter period count when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        node = operands.get('PeriodCount')
        if isinstance(node, dict):
            node['#text'] = str(value)
        else:
            operands['PeriodCount'] = str(value)

    @property
    def start_date(self) -> datetime:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter start date when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        return datetime.strptime(_text(operands.get('StartDate', {}), ''), '%Y-%m-%d %H:%M:%S')

    @start_date.setter
    def start_date(self, value: datetime) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot set filter start date when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        node = operands.get('StartDate')
        if isinstance(node, dict):
            node['#text'] = value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            operands['StartDate'] = value.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def end_date(self) -> datetime:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot get filter end date when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        return datetime.strptime(_text(operands.get('EndDate', {}), ''), '%Y-%m-%d %H:%M:%S')

    @end_date.setter
    def end_date(self, value: datetime) -> None:
        if self.filter_mode != FilterMode.SIMPLE:
            raise RuntimeWarning('Cannot set filter end date when not in simple mode')
        operands = self._config_simple.get('Operands', {})
        node = operands.get('EndDate')
        if isinstance(node, dict):
            node['#text'] = value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            operands['EndDate'] = value.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def expression(self) -> str:
        return _text(self._configuration.get('Expression'), '')

    @expression.setter
    def expression(self, value: str) -> None:
        if value == '':
            raise ValueError('Filter expression cannot be empty.')
        expr_node = self._configuration.get('Expression')
        if isinstance(expr_node, dict):
            expr_node['#text'] = value
        else:
            self._configuration['Expression'] = value

    @property
    def _configuration(self) -> Dict[str, Any]:
        if self.properties:
            return self.properties['Configuration']
        else:
            raise NameError('Properties does not contain Configuration')

    @property
    def _config_simple(self) -> Dict[str, Any]:
        if self.properties:
            return self.properties['Configuration']['Simple']
        else:
            raise NameError('Properties does not contain Configuration > Simple')

