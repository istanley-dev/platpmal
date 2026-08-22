#!/usr/bin/env python3
import json
from pathlib import Path

index=Path('index.html').read_text(encoding='utf-8')
if 'PMAL_LAW_LINK_FALLBACK_V1' not in index:
    raise SystemExit('ERRO: fallback não foi aplicado ao index.html')

struct=json.loads(Path('law-bank-structural.json').read_text(encoding='utf-8'))
summary=json.loads(Path('law-bank-summary.json').read_text(encoding='utf-8'))
keys=set(summary.get('device_keys',[]))
missing=struct.get('missing_device_keys',{})
exact_orphans=set(struct.get('orphan_devices',[]))

def base_for(k):
    if not k:return None
    if k.startswith('Lei5346 '):return 'Lei 5.346'
    p=k.split(' ',1)[0]
    generic={'CADH','RD','LO','L14133','L11343','L8069','L8072','L13869','L11340','L10826','L9503','L12850','L9455','L7716','L9605','L7960','L9099','L10259','L8429','L8987','L9784','L8112','L4717','L13300','LEP','L12016','L9474','L12830','L12037','L9507','L9296'}
    return p if p in generic else None

fallback=[]
unresolved=[]
fallback_bases=set()
fallback_qids=set()
for requested,items in missing.items():
    base=base_for(requested)
    if base and base in keys:
        fallback_bases.add(base)
        for q in items:
            qid=q.get('id','')
            if qid:fallback_qids.add(qid)
            fallback.append({'id':qid,'requested':requested,'fallback':base,'f':q.get('f','')[:240]})
    else:
        for q in items:
            unresolved.append({'id':q.get('id',''),'requested':requested,'f':q.get('f','')[:240]})

newly_covered_bases=sorted(base for base in fallback_bases if base in exact_orphans)
effective_orphans=sorted(exact_orphans-set(newly_covered_bases))
report={
 'schema':1,
 'runtime_marker':'PMAL_LAW_LINK_FALLBACK_V1',
 'device_count':struct.get('devices',len(keys)),
 'exact_linked_device_count':struct.get('linked_device_count',0),
 'effective_linked_device_count':struct.get('linked_device_count',0)+len(newly_covered_bases),
 'exact_orphan_device_count':struct.get('orphan_device_count',len(exact_orphans)),
 'effective_orphan_device_count':len(effective_orphans),
 'exact_linked_question_count':struct.get('linked_questions_unique',0),
 'effective_linked_question_count':struct.get('linked_questions_unique',0)+len(fallback_qids),
 'fallback_question_count':len(fallback_qids),
 'fallback_target_base_count':len(fallback_bases),
 'newly_covered_generic_devices':newly_covered_bases,
 'fallback_links':fallback,
 'unresolved_exact_reference_count':len(unresolved),
 'unresolved_exact_references':unresolved,
 'effective_orphan_devices':effective_orphans,
 'nota':'Fallback somente para o cartão geral da MESMA lei quando o artigo específico citado não existe em DISP. CF/CP/CPP/CPM/CPPM não recebem fallback genérico.'
}
Path('law-bank-effective-links.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['device_count','exact_linked_device_count','effective_linked_device_count','exact_orphan_device_count','effective_orphan_device_count','exact_linked_question_count','effective_linked_question_count','fallback_question_count','fallback_target_base_count','unresolved_exact_reference_count']},ensure_ascii=False))
