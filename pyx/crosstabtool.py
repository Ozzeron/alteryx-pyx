# Pyx, a Python module for creating, reading, and editing Alteryx Designer workflows entirely in code
# Fork: alteryx-pyx — extended for automotive data pipelines
#
# GNU GPL v3 — see COPYING for details.

from .tool import Tool


class CrossTabTool(Tool):
    """
    Represents a Cross Tab tool in an Alteryx workflow.

    Plugin: AlteryxBasePluginsGui.CrossTab.CrossTab

    XML shape::

        <Configuration>
          <GroupFields>
            <Field field="DealerCode" />
          </GroupFields>
          <HeaderField field="Segment" />
          <DataField field="Count" />
          <Methods>...</Methods>
        </Configuration>
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.CrossTab.CrossTab'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxCrossTab'

    @property
    def _cfg(self) -> dict:
        return self.properties.get('Configuration', {}) if self.properties else {}

    @property
    def group_fields(self) -> list:
        """List of field names used for grouping."""
        gf = self._cfg.get('GroupFields', {})
        if not gf:
            return []
        raw = gf.get('Field', [])
        if isinstance(raw, dict):
            raw = [raw]
        return [f.get('@field', '') for f in raw]

    @property
    def header_field(self) -> str:
        """Field whose values become column headers."""
        hf = self._cfg.get('HeaderField', {})
        if isinstance(hf, dict):
            return hf.get('@field', '')
        return str(hf or '')

    @property
    def data_field(self) -> str:
        """Field whose values populate the cross-tab cells."""
        df = self._cfg.get('DataField', {})
        if isinstance(df, dict):
            return df.get('@field', '')
        return str(df or '')
