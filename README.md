# alteryx-pyx

> Fork of [davidtwilcox/pyx](https://github.com/davidtwilcox/pyx) — extended for real-world automotive data pipelines.

A Python 3.10+ library for reading, writing, analyzing, and programmatically building [Alteryx Designer](https://www.alteryx.com/) workflow files (`.yxmd`, `.yxmc`, `.xml`).

## What's new in this fork

- **13 new tool classes** covering the full automotive pipeline toolset
- **ToolContainer**: reads nested `ChildNodes`, exposes `children`, `disabled`, `folded`
- **MacroTool**: detects macro instances (no Plugin in GuiSettings, `@Macro` in EngineSettings)
- **`Workflow.to_compact_json()`**: LLM-friendly compact dict, ~4-6× smaller than raw XML
- **`pyx/layout.py`**: topological layout algorithms (`layout_vertical`, `layout_horizontal`, `apply_layout`)
- **`get_tools_by_plugin()`** and **`get_tools_in_container()`** helpers
- Graceful fallback for unknown plugins (no crash)
- Python 3.10+ type hints throughout
- Recursive child-node parsing (workflows where all tools are inside containers)

## Requirements

- Python 3.10+
- `xmltodict`

## Installation

```bash
pip install alteryx-pyx
```

Or directly from source:

```bash
git clone https://github.com/Ozzeron/alteryx-pyx
cd alteryx-pyx
pip install -e .
```

## Supported tools

| Tool | Class | Plugin |
|---|---|---|
| Input Data | `InputTool` | `AlteryxBasePluginsGui.DbFileInput.DbFileInput` |
| Output Data | `OutputTool` | `AlteryxBasePluginsGui.DbFileOutput.DbFileOutput` |
| Select | `SelectTool` | `AlteryxBasePluginsGui.AlteryxSelect.AlteryxSelect` |
| Auto Field | `AutofieldTool` | `AlteryxBasePluginsGui.AutoField.AutoField` |
| Filter | `FilterTool` | `AlteryxBasePluginsGui.Filter.Filter` |
| Sort | `SortTool` | `AlteryxBasePluginsGui.Sort.Sort` |
| Formula | `FormulaTool` | `AlteryxBasePluginsGui.Formula.Formula` |
| Join | `JoinTool` | `AlteryxBasePluginsGui.Join.Join` |
| Union | `UnionTool` | `AlteryxBasePluginsGui.Union.Union` |
| Unique | `UniqueTool` | `AlteryxBasePluginsGui.Unique.Unique` |
| Summarize | `SummarizeTool` | `AlteryxSpatialPluginsGui.Summarize.Summarize` |
| Running Total | `RunningTotalTool` | `AlteryxBasePluginsGui.RunningTotal.RunningTotal` |
| Generate Rows | `GenerateRowsTool` | `AlteryxBasePluginsGui.GenerateRows.GenerateRows` |
| Transpose | `TransposeTool` | `AlteryxBasePluginsGui.Transpose.Transpose` |
| Record ID | `RecordIDTool` | `AlteryxBasePluginsGui.RecordID.RecordID` |
| Browse | `BrowseTool` | `AlteryxBasePluginsGui.BrowseV2.BrowseV2` |
| Text Box | `TextBoxTool` | `AlteryxGuiToolkit.TextBox.TextBox` |
| Tool Container | `ContainerTool` | `AlteryxGuiToolkit.ToolContainer.ToolContainer` |
| Calgary Join | `CalgaryJoinTool` | `CalgaryPluginsGui.CalgaryJoin.CalgaryJoin` |
| Macro instance | `MacroTool` | *(detected via `@Macro` in EngineSettings)* |
| Unknown | `Tool` *(base)* | *(any unrecognised plugin — no crash)* |

## Quick start

### Reading a workflow

```python
from pyx.workflow import Workflow

wf = Workflow.read('my_workflow.yxmd')
print(f"{len(wf.tools)} tools, {len(wf.connections)} connections")

# List all Formula tools
for t in wf.get_tools_by_plugin('AlteryxBasePluginsGui.Formula.Formula'):
    from pyx.formulatool import FormulaTool
    if isinstance(t, FormulaTool):
        for ff in t.formulas:
            print(f"  [{t.tool_id}] {ff.field} = {ff.expression}")
```

### Compact JSON (for LLM context)

```python
import json
from pyx.workflow import Workflow

wf = Workflow.read('my_workflow.yxmd')
compact = wf.to_compact_json()
print(json.dumps(compact, indent=2))
# Typically 4-6× smaller than the raw XML
```

### Working with containers

```python
from pyx.workflow import Workflow
from pyx.containertool import ContainerTool

wf = Workflow.read('my_workflow.yxmd')

for tool in wf.tools.values():
    if isinstance(tool, ContainerTool):
        print(f"Container '{tool.caption}': disabled={tool.disabled}, children={tool.children}")

# Get all tools inside a specific container
children = wf.get_tools_in_container(container_id=11678)
```

### Working with macros

```python
from pyx.workflow import Workflow
from pyx.macrotool import MacroTool

wf = Workflow.read('my_workflow.yxmd')

for tool in wf.tools.values():
    if isinstance(tool, MacroTool):
        print(f"[{tool.tool_id}] {tool.macro_path}: {tool.macro_values}")
```

### Layout algorithms

```python
from pyx.workflow import Workflow
from pyx.layout import layout_vertical, layout_horizontal, apply_layout

wf = Workflow.read('my_workflow.yxmd')

# Re-layout top-to-bottom
positions = layout_vertical(wf, x_start=50, y_start=50, v_gap=160)
apply_layout(wf, positions)

Workflow.write(wf, 'my_workflow_relaid.yxmd')
```

### Building a workflow from scratch

```python
from pyx.workflow import Workflow
from pyx.inputtool import InputTool
from pyx.formulatool import FormulaTool, FormulaField
from pyx.outputtool import OutputTool
from pyx.tool import ToolPosition

wf = Workflow()
wf.name = "My Workflow"
wf.yxmd_version = "2024.1"

# Input
inp = InputTool(1)
inp.position = ToolPosition(50, 50)

# Formula
frm = FormulaTool(2)
frm.position = ToolPosition(50, 210)
frm.formulas = [FormulaField(field="full_name", expression='[first] + " " + [last]')]

# Output
out = OutputTool(3)
out.position = ToolPosition(50, 370)

wf = wf.add_tool(inp).add_tool(frm).add_tool(out)
wf = wf.add_connection(1, "Output", 2, "Input")
wf = wf.add_connection(2, "Output", 3, "Input")

Workflow.write(wf, "output.yxmd")
```

### Calgary Join

```python
from pyx.calgaryjointool import CalgaryJoinTool, CalgaryJoinField

tool = CalgaryJoinTool(10)
tool.root_file_name = r"\\server\data\Calgary\mydb.cydb"
tool.join_fields = [
    CalgaryJoinField(field="Zip5", index_field="zip5", query_type="value")
]
```

### Summarize

```python
from pyx.summarizetool import SummarizeTool, SummarizeField

tool = SummarizeTool(20)
tool.summarize_fields = [
    SummarizeField(field="dealer_code", action="GroupBy"),
    SummarizeField(field="sale_count", action="Sum", rename="total_sales"),
]
```

## License

GPL v3 — same as the original `pyx` library. See [COPYING](COPYING).

Original work © 2020 David T. Wilcox. Fork extensions © 2024 contributors.
