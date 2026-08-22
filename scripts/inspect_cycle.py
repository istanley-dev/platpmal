#!/usr/bin/env python3
import re, json
from pathlib import Path

src=Path('index.html').read_text(encoding='utf-8')

def balanced(start,op='{',cl='}'):
    p=src.find(op,start)
    if p<0:return ''
    depth=0; quote=None; esc=False
    for i in range(p,len(src)):
        ch=src[i]
        if quote:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==quote:quote=None
            continue
        if ch in ('"',"'",'`'):quote=ch;continue
        if ch==op:depth+=1
        elif ch==cl:
            depth-=1
            if depth==0:return src[p:i+1]
    return ''

def var_block(name):
    m=re.search(r'\b(?:var|let|const)\s+'+re.escape(name)+r'\s*=',src)
    return balanced(m.end()) if m else ''

def func_block(name):
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',src)
    if not m:return ''
    b=balanced(m.start())
    return src[m.start():src.find('{',m.start())]+b

def split_props(obj):
    s=obj.strip()
    if s.startswith('{') and s.endswith('}'):s=s[1:-1]
    parts=[];start=0;depth=0;quote=None;esc=False
    for i,ch in enumerate(s):
        if quote:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==quote:quote=None
            continue
        if ch in ('"',"'",'`'):quote=ch;continue
        if ch in '{[(':depth+=1
        elif ch in '}])':depth-=1
        elif ch==',' and depth==0:
            parts.append(s[start:i].strip());start=i+1
    tail=s[start:].strip()
    if tail:parts.append(tail)
    return parts

def prop_key(p):
    m=re.match(r'\s*(["\'])(.*?)\1\s*:',p,re.S)
    if m:return m.group(2)
    m=re.match(r'\s*([A-Za-z_$][\w$]*)\s*:',p)
    return m.group(1) if m else None

DISP=var_block('DISP')
props=split_props(DISP) if DISP else []
entries=[]
for p in props:
    k=prop_key(p)
    if k:
        v=p[p.find(':')+1:].strip()
        entries.append({'key':k,'raw':v[:5000]})

q_ids=set(re.findall(r'"id"\s*:\s*"([^"]+)"',src))
fn_names=['buildKeyToQids','readingOrder','readingPlanInfo','startLeituraQuiz','renderBiblio','ldRead']
funcs={n:func_block(n) for n in fn_names}
linkfn=funcs.get('buildKeyToQids','')
quoted=re.findall(r'["\']([^"\']+)["\']',linkfn)
explicit_qids=sorted(set(x for x in quoted if x in q_ids))
missing_qid_like=sorted(set(x for x in quoted if re.match(r'^(?:q|c|r|ai_|chat_|adm|pen|const|cpp|cpm|lei|l)[A-Za-z0-9_\-]+$',x,re.I) and x not in q_ids))
summary={
 'source_chars':len(src),'device_count':len(entries),'device_keys':[e['key'] for e in entries],
 'question_id_count':len(q_ids),'link_function_found':bool(linkfn),
 'explicit_linked_qids_count':len(explicit_qids),'explicit_linked_qids':explicit_qids,
 'possible_missing_qids':missing_qid_like,'functions_found':{n:bool(v) for n,v in funcs.items()}
}
Path('law-bank-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
Path('law-bank-devices.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
Path('law-bank-linking.txt').write_text('\n\n'.join('=== '+n+' ===\n'+v for n,v in funcs.items()),encoding='utf-8')
Path('cycle-debug-report.txt').write_text('Banco de Leis auditado. Veja law-bank-summary.json, law-bank-devices.json e law-bank-linking.txt.\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
