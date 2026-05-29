import sys, json, os
sys.path.insert(0, '.')
from pyx.workflow import Workflow

wf = Workflow.read(r'C:\Users\Ozzze\.openclaw\workspace\projects\alteryx-analysis\workflows\001_133697_pull.xml')

original_size = os.path.getsize(r'C:\Users\Ozzze\.openclaw\workspace\projects\alteryx-analysis\workflows\001_133697_pull.xml')

compact = wf.to_compact_json()
compact_str = json.dumps(compact, indent=2)

print(f'Original XML size: {original_size:,} bytes')
print(f'Compact JSON size: {len(compact_str):,} bytes')
print(f'Compression ratio: {original_size / len(compact_str):.1f}x smaller')
print()
print('Sample tool entries:')
for tid, info in list(compact['tools'].items())[:8]:
    print(f'  [{tid}] plugin={info["plugin"].split(".")[-1]} config={info["config"]}')

print()
print('Containers:')
for tid, info in compact['tools'].items():
    if 'Container' in info['plugin']:
        print(f'  [{tid}] {info["config"]}')

print()
print('Macros:')
for tid, info in compact['tools'].items():
    if 'macro' in (info.get('config') or {}):
        print(f'  [{tid}] {info["config"]}')

# Test other workflows
print()
print('Testing other workflows...')
for fn in ['002_133697_NO_NCOA_SUPPRESSION.xml', '003_133697_Email_Suppression.xml', '004_133697_FINAL_NEW.xml']:
    path = rf'C:\Users\Ozzze\.openclaw\workspace\projects\alteryx-analysis\workflows\{fn}'
    wf2 = Workflow.read(path)
    from collections import Counter
    types = Counter(type(t).__name__ for t in wf2.tools.values())
    print(f'  {fn}: {len(wf2.tools)} tools, {len(wf2.connections)} connections')
    print(f'    types: {dict(types)}')
