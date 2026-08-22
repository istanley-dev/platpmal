#!/usr/bin/env python3
import re, json, subprocess
from pathlib import Path

src=Path('index.html').read_text(encoding='utf-8')
if 'PMAL_LAW_REF_V21' not in src:
    raise SystemExit('ERRO: parser v2.1 não aplicado')

def balanced(start,op='{',cl='}'):
    p=src.find(op,start)
    if p<0:return ''
    d=0;q=None;esc=False
    for i in range(p,len(src)):
        ch=src[i]
        if q:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==q:q=None
            continue
        if ch in ('"',"'",'`'):q=ch;continue
        if ch==op:d+=1
        elif ch==cl:
            d-=1
            if d==0:return src[p:i+1]
    return ''

def fn(name):
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',src)
    if not m:raise SystemExit('função ausente: '+name)
    return src[m.start():src.find('{',m.start())]+balanced(m.start())

def var_block(name):
    m=re.search(r'\b(?:var|let|const)\s+'+re.escape(name)+r'\s*=',src)
    return balanced(m.end()) if m else ''

def split_props(obj):
    s=obj.strip()
    if s.startswith('{') and s.endswith('}'):s=s[1:-1]
    out=[];st=0;d=0;q=None;esc=False
    for i,ch in enumerate(s):
        if q:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==q:q=None
            continue
        if ch in ('"',"'",'`'):q=ch;continue
        if ch in '{[(':d+=1
        elif ch in '}])':d-=1
        elif ch==',' and d==0:out.append(s[st:i].strip());st=i+1
    if s[st:].strip():out.append(s[st:].strip())
    return out

def prop_key(p):
    m=re.match(r'\s*(["\'])(.*?)\1\s*:',p,re.S)
    if m:return m.group(2)
    m=re.match(r'\s*([A-Za-z_$][\w$]*)\s*:',p)
    return m.group(1) if m else None

def js_field(obj,name):
    m=re.search(r'"'+re.escape(name)+r'"\s*:\s*"((?:\\.|[^"\\])*)"',obj,re.S)
    if not m:return ''
    try:return json.loads('"'+m.group(1)+'"')
    except:return m.group(1)

def questions():
    out={}
    for m in re.finditer(r'\{\s*"id"\s*:\s*"',src):
        st=m.start();d=0;q=False;esc=False;end=None
        for i in range(st,min(len(src),st+25000)):
            ch=src[i]
            if q:
                if esc:esc=False
                elif ch=='\\':esc=True
                elif ch=='"':q=False
                continue
            if ch=='"':q=True;continue
            if ch=='{':d+=1
            elif ch=='}':
                d-=1
                if d==0:end=i+1;break
        if not end:continue
        obj=src[st:end];qid=js_field(obj,'id')
        if qid:out[qid]={'id':qid,'f':js_field(obj,'f')}
    return list(out.values())

keys=[]
for p in split_props(var_block('DISP')):
    k=prop_key(p)
    if k:keys.append(k)
qs=questions()
parser=fn('parseRefs')
watch=['b_9','b_12','pm1','c3_21','c3_30','c3_38','rp_pcal2012_086','leg_racismo_003','L9455_ATUAL_2026_01']

node=f'''const fs=require('fs');
const DIPL_NOME={{}};
{parser}
const keys=new Set({json.dumps(keys,ensure_ascii=False)});
const qs={json.dumps(qs,ensure_ascii=False)};
const watch=new Set({json.dumps(watch)});
const links={{}}; for(const k of keys)links[k]=new Set();
let linkedQ=new Set(),fallback=[],unresolved=[],multi=0,refsN=0,yearAsArticle=[],ordinal=[],samples={{}};
for(const q of qs){{
  const rs=parseRefs(q.f||''); refsN+=rs.length; if(rs.length>1)multi++;
  if(watch.has(q.id))samples[q.id]={{f:q.f,refs:rs.map(r=>r.key)}};
  for(const r of rs){{
    if(/\\s\\d+[Oo]$/.test(r.key))ordinal.push({{id:q.id,key:r.key,f:q.f}});
    const n=parseInt(r.art||'',10); if(n>=1900&&n<=2100)yearAsArticle.push({{id:q.id,key:r.key,f:q.f}});
    let k=null;
    if(keys.has(r.key))k=r.key; else if(r.baseKey&&keys.has(r.baseKey)){{k=r.baseKey;fallback.push({{id:q.id,requested:r.key,fallback:k,f:(q.f||'').slice(0,240)}});}} else unresolved.push({{id:q.id,requested:r.key,base:r.baseKey||'',f:(q.f||'').slice(0,240)}});
    if(k){{links[k].add(q.id);linkedQ.add(q.id);}}
  }}
}}
const orphans=Object.keys(links).filter(k=>links[k].size===0).sort();
const report={{schema:3,parser_marker:'PMAL_LAW_REF_V21',device_count:keys.size,question_count:qs.length,reference_count:refsN,linked_question_count:linkedQ.size,linked_device_count:keys.size-orphans.length,orphan_device_count:orphans.length,orphan_devices:orphans,multi_linked_question_count:multi,fallback_reference_count:fallback.length,fallback_references:fallback,unresolved_reference_count:unresolved.length,unresolved_references:unresolved,ordinal_artifact_count:ordinal.length,ordinal_artifacts:ordinal,year_as_article_count:yearAsArticle.length,year_as_article:yearAsArticle,known_case_samples:samples,links_per_device:Object.fromEntries(Object.entries(links).map(([k,v])=>[k,v.size]))}};
fs.writeFileSync('law-bank-runtime-audit.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({{device_count:report.device_count,question_count:report.question_count,reference_count:report.reference_count,linked_question_count:report.linked_question_count,linked_device_count:report.linked_device_count,orphan_device_count:report.orphan_device_count,multi_linked_question_count:report.multi_linked_question_count,fallback_reference_count:report.fallback_reference_count,unresolved_reference_count:report.unresolved_reference_count,ordinal_artifact_count:report.ordinal_artifact_count,year_as_article_count:report.year_as_article_count}}));
'''
Path('/tmp/law-runtime-audit.js').write_text(node,encoding='utf-8')
r=subprocess.run(['node','--check','/tmp/law-runtime-audit.js'],capture_output=True,text=True)
if r.returncode:
    print(r.stdout);print(r.stderr);raise SystemExit('ERRO de sintaxe no parser runtime')
r=subprocess.run(['node','/tmp/law-runtime-audit.js'],capture_output=True,text=True)
print(r.stdout.strip())
if r.returncode:
    print(r.stderr);raise SystemExit('ERRO ao executar auditoria runtime')
report=json.loads(Path('law-bank-runtime-audit.json').read_text(encoding='utf-8'))
if report['ordinal_artifact_count']!=0 or report['year_as_article_count']!=0:
    raise SystemExit('ERRO: parser ainda produziu ordinal/ano como artigo')
