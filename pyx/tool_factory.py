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

from typing import Dict

from .tool import Tool
from .inputtool import InputTool
from .selecttool import SelectTool
from .autofieldtool import AutofieldTool
from .filtertool import FilterTool
from .sorttool import SortTool
from .outputtool import OutputTool
from .formulatool import FormulaTool
from .jointool import JoinTool
from .uniontool import UnionTool
from .uniquetool import UniqueTool
from .summarizetool import SummarizeTool
from .runningtotaltool import RunningTotalTool
from .generaterowstool import GenerateRowsTool
from .transposetool import TransposeTool
from .recordidtool import RecordIDTool
from .browsetool import BrowseTool
from .textboxtool import TextBoxTool
from .containertool import ContainerTool
from .calgaryjointool import CalgaryJoinTool
from .macrotool import MacroTool


class ToolFactory:
    """
    Creates a concrete tool class based on a plugin name.
    Unknown plugins fall back to the base Tool class (no exception raised).
    """
    registry: Dict[str, type] = {
        # Original tools
        'AlteryxBasePluginsGui.DbFileInput.DbFileInput': InputTool,
        'AlteryxBasePluginsGui.AlteryxSelect.AlteryxSelect': SelectTool,
        'AlteryxBasePluginsGui.AutoField.AutoField': AutofieldTool,
        'AlteryxBasePluginsGui.Filter.Filter': FilterTool,
        'AlteryxBasePluginsGui.Sort.Sort': SortTool,
        'AlteryxBasePluginsGui.DbFileOutput.DbFileOutput': OutputTool,
        # New tools
        'AlteryxBasePluginsGui.Formula.Formula': FormulaTool,
        'AlteryxBasePluginsGui.Join.Join': JoinTool,
        'AlteryxBasePluginsGui.Union.Union': UnionTool,
        'AlteryxBasePluginsGui.Unique.Unique': UniqueTool,
        'AlteryxSpatialPluginsGui.Summarize.Summarize': SummarizeTool,
        'AlteryxBasePluginsGui.RunningTotal.RunningTotal': RunningTotalTool,
        'AlteryxBasePluginsGui.GenerateRows.GenerateRows': GenerateRowsTool,
        'AlteryxBasePluginsGui.Transpose.Transpose': TransposeTool,
        'AlteryxBasePluginsGui.RecordID.RecordID': RecordIDTool,
        'AlteryxBasePluginsGui.BrowseV2.BrowseV2': BrowseTool,
        'AlteryxGuiToolkit.TextBox.TextBox': TextBoxTool,
        'AlteryxGuiToolkit.ToolContainer.ToolContainer': ContainerTool,
        'CalgaryPluginsGui.CalgaryJoin.CalgaryJoin': CalgaryJoinTool,
    }

    @staticmethod
    def create_tool(plugin: str, tool_id: int) -> Tool:
        """
        Returns a concrete Tool subclass if the plugin is recognised,
        otherwise falls back gracefully to the base Tool class.
        """
        if plugin in ToolFactory.registry:
            return ToolFactory.registry[plugin](tool_id)
        # Graceful fallback — never raise for unknown plugins
        return Tool(tool_id)

    @staticmethod
    def is_macro_node(node_dict: dict) -> bool:
        """
        Returns True if the node dict represents a macro instance.
        Macro nodes have no @Plugin in GuiSettings but have @Macro in EngineSettings.
        """
        gui = node_dict.get('GuiSettings', {})
        engine = node_dict.get('EngineSettings', {})
        return '@Plugin' not in gui and '@Macro' in engine
