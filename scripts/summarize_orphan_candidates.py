#!/usr/bin/env python3
import json
from pathlib import Path
r=json.loads(Path('law-bank-orphan-candidates.json').read_text(encoding='utf-8'))
out=[]
for d in r['devices']:
    cs=[c for c in d['candidates'] if c['score']>=0.42]
    if cs:out.append({'key':d['key'],'device':d['device'],'candidates':cs[:3]})
res={'count':len(out),'devices':out}
Path('law-bank-strong-candidates.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'strong_device_count':len(out)},ensure_ascii=False))
