# Pyx, a Python module for creating, reading, and editing Alteryx Designer workflows entirely in code
# Fork: alteryx-pyx — extended for automotive data pipelines
#
# GNU GPL v3 — see COPYING for details.

from .tool import Tool


class AppendFieldsTool(Tool):
    """
    Represents an Append Fields tool in an Alteryx workflow.

    Plugin: AlteryxBasePluginsGui.AppendFields.AppendFields

    XML shape::

        <Configuration>
          <CartesianMode>Error</CartesianMode>
          <SelectConfiguration>
            <Configuration outputConnection="Output">
              <SelectFields>
                <SelectField field="*Unknown" selected="True" />
              </SelectFields>
            </Configuration>
          </SelectConfiguration>
        </Configuration>
    """

    def __init__(self, tool_id: int):
        super().__init__(tool_id)
        self.plugin = 'AlteryxBasePluginsGui.AppendFields.AppendFields'
        self.engine_dll = 'AlteryxBasePluginsEngine.dll'
        self.engine_dll_entry_point = 'AlteryxAppendFields'

    @property
    def _cfg(self) -> dict:
        return self.properties.get('Configuration', {}) if self.properties else {}

    @property
    def cartesian_mode(self) -> str:
        """Cartesian mode: 'Error', 'Warning', or 'Allow'."""
        v = self._cfg.get('CartesianMode', 'Error')
        if isinstance(v, dict):
            return v.get('#text', 'Error')
        return str(v) if v else 'Error'

    @cartesian_mode.setter
    def cartesian_mode(self, value: str) -> None:
        cfg = self.properties.get('Configuration')
        if cfg is None:
            self.properties['Configuration'] = {}
            cfg = self.properties['Configuration']
        existing = cfg.get('CartesianMode')
        if isinstance(existing, dict):
            existing['#text'] = value
        else:
            cfg['CartesianMode'] = value

    @property
    def select_fields(self) -> list:
        """Returns list of dicts with 'field' and 'selected' keys from SelectConfiguration."""
        sel_cfg = self._cfg.get('SelectConfiguration', {})
        if not sel_cfg:
            return []
        inner = sel_cfg.get('Configuration', {})
        if isinstance(inner, list):
            inner = inner[0] if inner else {}
        sf = inner.get('SelectFields', {})
        if not sf:
            return []
        raw = sf.get('SelectField', [])
        if isinstance(raw, dict):
            raw = [raw]
        return [{'field': f.get('@field', ''), 'selected': f.get('@selected', 'True')} for f in raw]
