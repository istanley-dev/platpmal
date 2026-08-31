#!/usr/bin/env python3
import re, json
from pathlib import Path

src = Path('index.html').read_text(encoding='utf-8')
terms = [r'revis[aã]o', r'revis[oõ]es', r'quest[oõ]es erradas', r'erros?', r'D\+1', r'D\+7', r'D\+21', r'caderno de erros', r'pendentes?']
report = {'chars': len(src), 'matches': {}, 'functions': [], 'ids': []}

for term in terms:
    rx = re.compile(term, re.I)
    arr=[]
    for m in list(rx.finditer(src))[:30]:
        a=max(0,m.start()-420); b=min(len(src),m.end()+700)
        snippet=src[a:b].replace('\n',' ')
        arr.append(snippet)
    report['matches'][term]=arr

# function names likely related to review/errors/navigation
for m in re.finditer(r'function\s+([A-Za-z_$][\w$]*)\s*\(', src):
    n=m.group(1)
    if re.search(r'rev|erro|wrong|mist|agenda|home|nav|quest', n, re.I):
        report['functions'].append(n)
report['functions']=sorted(set(report['functions']))

for m in re.finditer(r'id=["\']([^"\']+)["\']', src, re.I):
    v=m.group(1)
    if re.search(r'rev|erro|wrong|mist|agenda|home|nav|quest', v, re.I):
        report['ids'].append(v)
report['ids']=sorted(set(report['ids']))

Path('review-ui-inspection.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('review inspection written:', len(report['functions']), 'functions,', len(report['ids']), 'ids')
