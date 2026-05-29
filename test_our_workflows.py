"""
Test alteryx-pyx on our real Alteryx workflow templates.
"""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from pyx.workflow import Workflow
from pyx.layout import layout_vertical, layout_horizontal, apply_layout

WORKFLOWS_DIR = pathlib.Path(r"C:\Users\Ozzze\.openclaw\workspace\projects\alteryx-analysis\workflows")
files = {
    "001_pull":       "001_133697_pull.xml",
    "002_suppression":"002_133697_NO_NCOA_SUPPRESSION.xml",
    "003_email":      "003_133697_Email_Suppression.xml",
    "004_final":      "004_133697_FINAL_NEW.xml",
    "130914_ncoa":    "130914_NCOA_results.xml",
}

print("=" * 70)
print("ALTERYX-PYX TEST — Our workflow templates")
print("=" * 70)

for name, fname in files.items():
    path = WORKFLOWS_DIR / fname
    print(f"\n{'─'*60}")
    print(f"[{name}]  {fname}")
    print(f"  File size: {path.stat().st_size:,} bytes")

    try:
        wf = Workflow.read(str(path))
    except Exception as e:
        print(f"  ❌ READ ERROR: {e}")
        continue

    print(f"  ✅ Parsed: {len(wf.tools)} tools, {len(wf.connections)} connections")

    # Plugin distribution
    plugin_counts = {}
    for tool in wf.tools.values():
        key = tool.plugin.split(".")[-1] if tool.plugin else (f"macro:{tool.macro_path}" if hasattr(tool, 'macro_path') and tool.macro_path else "Unknown")
        plugin_counts[key] = plugin_counts.get(key, 0) + 1
    top = sorted(plugin_counts.items(), key=lambda x: -x[1])[:8]
    print(f"  Top tools: {', '.join(f'{k}={v}' for k,v in top)}")

    # Containers
    containers = wf.get_tools_by_plugin("ToolContainer")
    if containers:
        print(f"  Containers ({len(containers)}):")
        for c in containers:
            disabled = getattr(c, 'disabled', False)
            caption = getattr(c, 'caption', '')
            children = wf.get_tools_in_container(c.tool_id)
            print(f"    [{c.tool_id}] '{caption}' disabled={disabled} children={len(children)}")

    # Formulas
    formulas = wf.get_tools_by_plugin("Formula")
    if formulas:
        print(f"  Formulas ({len(formulas)}):")
        for f in formulas[:3]:
            ff_list = getattr(f, 'formulas', [])
            for ff in ff_list[:2]:
                expr = getattr(ff, 'expression', str(ff))[:60]
                field = getattr(ff, 'field', '?')
                print(f"    [{f.tool_id}] {field} = {expr}")
        if len(formulas) > 3:
            print(f"    ... and {len(formulas)-3} more formula tools")

    # Filters
    filters = wf.get_tools_by_plugin("Filter")
    if filters:
        print(f"  Filters ({len(filters)}):")
        for flt in filters[:3]:
            expr = ""
            try:
                cfg = flt.properties.get("Configuration", {})
                expr = cfg.get("Expression", cfg.get("Simple", {}).get("Operator", ""))
                if isinstance(expr, str):
                    expr = expr[:60]
            except:
                pass
            print(f"    [{flt.tool_id}] {expr}")
        if len(filters) > 3:
            print(f"    ... and {len(filters)-3} more filters")

    # Calgary joins
    calgary = wf.get_tools_by_plugin("CalgaryJoin")
    if calgary:
        print(f"  CalgaryJoins ({len(calgary)}):")
        for cj in calgary:
            rfn = getattr(cj, 'root_file_name', '?')
            jf = getattr(cj, 'join_fields', [])
            fields_str = ', '.join(f"{getattr(f,'field','?')}→{getattr(f,'index_field','?')}" for f in jf[:2])
            print(f"    [{cj.tool_id}] {pathlib.Path(rfn).name} | {fields_str}")

    # Macros
    macros = wf.get_tools_by_plugin("Macro")
    if not macros:
        # Try by macro_path
        macros = [t for t in wf.tools.values() if hasattr(t, 'macro_path') and t.macro_path]
    if macros:
        print(f"  Macros ({len(macros)}):")
        for m in macros[:3]:
            mp = getattr(m, 'macro_path', '?')
            print(f"    [{m.tool_id}] {mp}")

    # I/O files
    inputs = wf.get_tools_by_plugin("DbFileInput")
    outputs = wf.get_tools_by_plugin("DbFileOutput")
    if inputs or outputs:
        print(f"  I/O: {len(inputs)} inputs, {len(outputs)} outputs")
        for inp in inputs[:3]:
            try:
                fp = inp.properties.get("Configuration", {}).get("File", {})
                if isinstance(fp, str):
                    print(f"    IN  [{inp.tool_id}] {pathlib.Path(fp).name}")
            except:
                pass
        for out in outputs[:3]:
            try:
                fp = out.properties.get("Configuration", {}).get("File", {})
                if isinstance(fp, str):
                    dis = out.properties.get("Configuration", {}).get("Disable", "False")
                    print(f"    OUT [{out.tool_id}] {pathlib.Path(fp).name} {'[DISABLED]' if dis=='True' else ''}")
            except:
                pass

    # compact JSON size
    try:
        compact = wf.to_compact_json()
        compact_str = json.dumps(compact)
        orig_size = path.stat().st_size
        ratio = orig_size / len(compact_str)
        print(f"  compact_json: {len(compact_str):,} chars  (vs {orig_size:,} bytes XML  →  {ratio:.1f}× smaller)")
    except Exception as e:
        print(f"  compact_json error: {e}")

    # layout test (only on small file)
    if name == "001_pull":
        print(f"  Layout test (vertical)...")
        try:
            positions = layout_vertical(wf)
            apply_layout(wf, positions)
            xs = [t.position.x for t in wf.tools.values()]
            ys = [t.position.y for t in wf.tools.values()]
            print(f"    x range: {min(xs)}–{max(xs)},  y range: {min(ys)}–{max(ys)}")
            print(f"    ✅ Layout OK")
        except Exception as e:
            print(f"    ❌ Layout error: {e}")

print(f"\n{'='*70}")
print("DONE")
