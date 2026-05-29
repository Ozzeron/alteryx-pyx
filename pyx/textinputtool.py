# Pyx, a Python module for creating, reading, and editing Alteryx Designer workflows entirely in code
# Fork: alteryx-pyx — extended for automotive data pipelines
#
# GNU GPL v3 — see COPYING for details.

from .tool import Tool


class TextInputTool(Tool):
    """
    Represents a Text Input tool in an Alteryx workflow.

    Plugin: AlteryxBasePluginsGui.TextInput.TextInput

    XML shape::

        <Configuration>
          <NumRows value="103" />
          <Fields>
            <Field name="make" />
            <Field name="model" />
          </Fields>
          <Data>
            <r><c>BUICK</c><c>ENCLAVE</c></r>
            ...
          </Data>
        </Configuration>
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.TextInput.TextInput'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxTextInput'
        super()._can_have_input(False)

    @property
    def _cfg(self) -> dict:
        return self.properties.get('Configuration', {}) if self.properties else {}

    @property
    def num_rows(self) -> int:
        """Number of data rows."""
        nr = self._cfg.get('NumRows', {})
        if isinstance(nr, dict):
            return int(nr.get('@value', 0) or 0)
        return int(nr or 0)

    @property
    def columns(self) -> list:
        """Column names as a list of strings."""
        fields_node = self._cfg.get('Fields', {})
        if not fields_node:
            return []
        raw = fields_node.get('Field', [])
        if isinstance(raw, dict):
            raw = [raw]
        return [f.get('@name', '') for f in raw]

    @property
    def rows(self) -> list:
        """All data rows — each row is a list of string cell values."""
        data_node = self._cfg.get('Data', {})
        if not data_node:
            return []
        raw_rows = data_node.get('r', [])
        if isinstance(raw_rows, dict):
            raw_rows = [raw_rows]
        result = []
        for row in raw_rows:
            cells = row.get('c', [])
            if isinstance(cells, str):
                cells = [cells]
            elif isinstance(cells, dict):
                cells = [str(cells)]
            result.append([str(c) if c is not None else '' for c in cells])
        return result

    def preview_rows(self, n: int = 3) -> list:
        """Return the first *n* rows."""
        return self.rows[:n]
