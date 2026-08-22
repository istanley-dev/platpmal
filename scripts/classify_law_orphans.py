#!/usr/bin/env python3
import json,re
from pathlib import Path
r=json.loads(Path('law-bank-runtime-audit.json').read_text(encoding='utf-8'))
orphans=r['orphan_devices']; links=r['links_per_device']; keys=set(links)

def base(k):
    if k=='Lei 5.346':return k
    if ' ' not in k:return k
    return k.split(' ',1)[0]
def is_generic(k):
    return k=='Lei 5.346' or ' ' not in k
covered_generic=[];true_generic=[];specific=[]
for k in orphans:
    if is_generic(k):
        b=base(k)
        if k=='Lei 5.346':children=[x for x in keys if x.startswith('Lei5346 ')]
        else:children=[x for x in keys if x.startswith(b+' ')]
        linked=[x for x in children if links.get(x,0)>0]
        (covered_generic if linked else true_generic).append({'key':k,'linked_children':linked})
    else:specific.append(k)
from collections import Counter
cnt=Counter(base(k) for k in specific)
out={'orphan_total':len(orphans),'generic_headers_covered_by_children_count':len(covered_generic),'generic_headers_covered_by_children':covered_generic,'true_generic_gap_count':len(true_generic),'true_generic_gaps':true_generic,'specific_article_gap_count':len(specific),'specific_by_diploma':dict(sorted(cnt.items(),key=lambda x:(-x[1],x[0]))),'specific_article_gaps':specific}
Path('law-bank-gap-classification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ['orphan_total','generic_headers_covered_by_children_count','true_generic_gap_count','specific_article_gap_count','specific_by_diploma']},ensure_ascii=False))
