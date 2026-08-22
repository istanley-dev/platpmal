#!/usr/bin/env python3
import json, runpy
from pathlib import Path

ns=runpy.run_path('scripts/inspect_cycle.py')
keys=ns['keys']; qs=ns['qs']; parse_ref=ns['parse_ref']

def base_for(k):
    if not k:return None
    if k.startswith('Lei5346 '):return 'Lei 5.346'
    p=k.split(' ',1)[0]
    if p in {'CADH','RD','LO','L14133','L11343','L8069','L8072','L13869','L11340','L10826','L9503','L12850','L9455','L7716','L9605','L7960','L9099','L10259','L8429','L8987','L9784','L8112','L4717','L13300','LEP','L12016','L9474','L12830','L12037','L9507','L9296'}:
        return p
    return None

exact={k:[] for k in keys}; effective={k:[] for k in keys}; fallback=[]; unresolved=[]
for q in qs:
    k=parse_ref(q.get('f',''))
    if not k: continue
    if k in keys:
        exact[k].append(q['id']); effective[k].append(q['id']); continue
    b=base_for(k)
    if b and b in keys:
        effective[b].append(q['id']); fallback.append({'id':q['id'],'requested':k,'fallback':b,'f':q.get('f','')[:240]})
    else:
        unresolved.append({'id':q['id'],'requested':k,'f':q.get('f','')[:240]})

exact_q=set(x for v in exact.values() for x in v)
eff_q=set(x for v in effective.values() for x in v)
report={
 'device_count':len(keys),
 'exact_linked_device_count':sum(bool(v) for v in exact.values()),
 'effective_linked_device_count':sum(bool(v) for v in effective.values()),
 'exact_orphan_device_count':sum(not v for v in exact.values()),
 'effective_orphan_device_count':sum(not v for v in effective.values()),
 'exact_linked_question_count':len(exact_q),
 'effective_linked_question_count':len(eff_q),
 'fallback_question_count':len(fallback),
 'fallback_links':fallback,
 'unresolved_exact_reference_count':len(unresolved),
 'unresolved_exact_references':unresolved,
 'effective_orphan_devices':sorted(k for k,v in effective.items() if not v)
}
Path('law-bank-effective-links.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['device_count','exact_linked_device_count','effective_linked_device_count','exact_orphan_device_count','effective_orphan_device_count','exact_linked_question_count','effective_linked_question_count','fallback_question_count','unresolved_exact_reference_count']},ensure_ascii=False))
