#!/usr/bin/env python3
import re, json
from pathlib import Path

src=Path('index.html').read_text(encoding='utf-8')
if 'PMAL_LAW_REF_V2' not in src:
    raise SystemExit('ERRO: parser v2 não foi aplicado')

def balanced(start,op='{',cl='}'):
    p=src.find(op,start)
    if p<0:return ''
    depth=0;quote=None;esc=False
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

def split_props(obj):
    s=obj.strip()[1:-1] if obj.strip().startswith('{') and obj.strip().endswith('}') else obj
    out=[];start=0;depth=0;quote=None;esc=False
    for i,ch in enumerate(s):
        if quote:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==quote:quote=None
            continue
        if ch in ('"',"'",'`'):quote=ch;continue
        if ch in '{[(':depth+=1
        elif ch in '}])':depth-=1
        elif ch==',' and depth==0:out.append(s[start:i].strip());start=i+1
    if s[start:].strip():out.append(s[start:].strip())
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
        st=m.start();depth=0;quote=False;esc=False;end=None
        for i in range(st,min(len(src),st+25000)):
            ch=src[i]
            if quote:
                if esc:esc=False
                elif ch=='\\':esc=True
                elif ch=='"':quote=False
                continue
            if ch=='"':quote=True;continue
            if ch=='{':depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:end=i+1;break
        if not end:continue
        obj=src[st:end];qid=js_field(obj,'id')
        if qid:out[qid]={'id':qid,'f':js_field(obj,'f'),'e':js_field(obj,'e'),'g':js_field(obj,'g'),'c':js_field(obj,'c')}
    return list(out.values())

DISP=var_block('DISP')
keys=set()
for p in split_props(DISP):
    k=prop_key(p)
    if k:keys.add(k)

SPECS=[
 (r'(?:Lei\s*(?:n[ºo°.]*)?\s*)?5\.?346(?:/\d{2,4})?','Lei5346','Lei 5.346'),
 (r'(?:CADH|Pacto de S[ãa]o Jos[ée]|Conven[çc][ãa]o Americana)','CADH','CADH'),
 (r'(?:Decreto\s*)?37\.?042(?:/\d{2,4})?','RD','RD'),
 (r'(?:Lei\s*)?14\.?751(?:/\d{2,4})?','LO','LO'),
 (r'(?:Lei\s*)?14\.?133(?:/\d{2,4})?','L14133','L14133'),
 (r'(?:Lei\s*)?11\.?343(?:/\d{2,4})?','L11343','L11343'),
 (r'(?:(?:Lei\s*)?8\.?069(?:/\d{2,4})?|\bECA\b)','L8069','L8069'),
 (r'(?:(?:Lei\s*)?8\.?072(?:/\d{2,4})?|11\.?464)','L8072','L8072'),
 (r'(?:Lei\s*)?13\.?869(?:/\d{2,4})?','L13869','L13869'),
 (r'(?:(?:Lei\s*)?11\.?340(?:/\d{2,4})?|\bLMP\b|Lei Maria da Penha)','L11340','L11340'),
 (r'(?:Lei\s*)?10\.?826(?:/\d{2,4})?','L10826','L10826'),
 (r'(?:(?:Lei\s*)?9\.?503(?:/\d{2,4})?|\bCTB\b)','L9503','L9503'),
 (r'(?:Lei\s*)?12\.?850(?:/\d{2,4})?','L12850','L12850'),
 (r'(?:Lei\s*)?9\.?455(?:/\d{2,4})?','L9455','L9455'),
 (r'(?:Lei\s*)?7\.?716(?:/\d{2,4})?','L7716','L7716'),
 (r'(?:Lei\s*)?9\.?605(?:/\d{2,4})?','L9605','L9605'),
 (r'(?:Lei\s*)?7\.?960(?:/\d{2,4})?','L7960','L7960'),
 (r'(?:(?:Lei\s*)?9\.?099(?:/\d{2,4})?|\bJECRIM\b)','L9099','L9099'),
 (r'(?:(?:Lei\s*)?10\.?259(?:/\d{2,4})?|\bJEF\b)','L10259','L10259'),
 (r'(?:(?:Lei\s*)?8\.?429(?:/\d{2,4})?|14\.?230)','L8429','L8429'),
 (r'(?:Lei\s*)?8\.?987(?:/\d{2,4})?','L8987','L8987'),
 (r'(?:Lei\s*)?9\.?784(?:/\d{2,4})?','L9784','L9784'),
 (r'(?:Lei\s*)?8\.?112(?:/\d{2,4})?','L8112','L8112'),
 (r'(?:Lei\s*)?4\.?717(?:/\d{2,4})?','L4717','L4717'),
 (r'(?:Lei\s*)?13\.?300(?:/\d{2,4})?','L13300','L13300'),
 (r'(?:(?:Lei\s*)?7\.?210(?:/\d{2,4})?|\bLEP\b)','LEP','LEP'),
 (r'(?:Lei\s*)?12\.?016(?:/\d{2,4})?','L12016','L12016'),
 (r'(?:Lei\s*)?9\.?474(?:/\d{2,4})?','L9474','L9474'),
 (r'(?:Lei\s*)?12\.?830(?:/\d{2,4})?','L12830','L12830'),
 (r'(?:Lei\s*)?12\.?037(?:/\d{2,4})?','L12037','L12037'),
 (r'(?:Lei\s*)?9\.?507(?:/\d{2,4})?','L9507','L9507'),
 (r'(?:Lei\s*)?9\.?296(?:/\d{2,4})?','L9296','L9296')]

RECOG_WORD=re.compile(r'\b(?:Lei|CF(?:/88)?|CPPM|CPP|CPM|CP|CADH|ECA|CTB|LMP|LEP|JECRIM|JEF|Decreto)\b',re.I)

def norm_art(v):
    v=re.sub(r'\s+','',str(v or '')).replace('‐','-').replace('‑','-').replace('–','-').replace('—','-').replace('.','')
    v=v.replace('º','').replace('°','')
    v=re.sub(r'^(\d+)[oO]$',r'\1',v)
    m=re.match(r'^(\d+)(?:-?([A-Fa-f]))?$',v)
    return (m.group(1)+(m.group(2).upper() if m.group(2) else '')) if m else ''

def parse_refs(f):
    if not f:return []
    text=re.sub(r'\.\s+(?=(?:Lei|CF(?:/88)?|CPPM|CPP|CPM|CP|CADH|ECA|CTB|LMP|LEP|JECRIM|JEF|Decreto)\b)','; ',str(f),flags=re.I)
    refs=[];seen=set()
    for clause in text.split(';'):
        if not clause.strip():continue
        toks=[]
        for pat,dipl,base in SPECS:
            for m in re.finditer(pat,clause,re.I):toks.append({'start':m.start(),'end':m.end(),'dipl':dipl,'base':base,'special':True,'used':False})
        for m in re.finditer(r'\b(CPPM|CPP|CPM|CP|CF)(?:/88)?\b',clause,re.I):
            d=m.group(1).upper();toks.append({'start':m.start(),'end':m.end(),'dipl':d,'base':d,'special':False,'used':False})
        toks.sort(key=lambda x:x['start'])
        arts=[]
        for am in re.finditer(r'\b[Aa]rts?\.?\s*([^:;]{1,60})',clause):
            seg=am.group(1).split('§',1)[0]
            seg=re.split(r'\.\s',seg,1)[0]
            cut=RECOG_WORD.search(seg)
            if cut:seg=seg[:cut.start()]
            nums=[]
            for nm in re.finditer(r'\d+[A-Fa-f]\b|\d+(?:\s*\.?\s*[º°oO]\.?)?(?:\s*[-‐‑–—]\s*[A-Fa-f])?',seg):
                a=norm_art(nm.group(0))
                if a and a not in nums:nums.append(a)
            if nums:arts.append({'start':am.start(),'nums':nums})
        for a in arts:
            if not toks:continue
            best=min(toks,key=lambda t:abs(a['start']-((t['start']+t['end'])/2)))
            best['used']=True
            for art in a['nums']:
                key=('Lei5346 '+art) if best['dipl']=='Lei5346' else best['dipl']+' '+art
                if key not in seen:
                    seen.add(key);refs.append({'key':key,'base':best['base'],'art':art,'dipl':best['dipl']})
        for t in toks:
            if t['special'] and not t['used']:
                key=t['base']
                if key not in seen:
                    seen.add(key);refs.append({'key':key,'base':t['base'],'art':'','dipl':t['dipl']})
    return refs

qs=questions();links={k:set() for k in keys};fallback=[];unresolved=[];multi=0;linked_qids=set();ref_count=0
samples={}
WATCH={'b_9','b_12','pm1','c3_21','c3_30','c3_38','rp_pcal2012_086','c3_41','c3_42'}
ordinal_artifacts=[]
for q in qs:
    refs=parse_refs(q.get('f',''))
    if len(refs)>1:multi+=1
    if q['id'] in WATCH:samples[q['id']]={'f':q.get('f',''),'refs':[r['key'] for r in refs]}
    for r in refs:
        ref_count+=1
        if re.search(r'\s\d+[Oo]$',r['key']):ordinal_artifacts.append({'id':q['id'],'key':r['key'],'f':q.get('f','')})
        if r['key'] in keys:
            links[r['key']].add(q['id']);linked_qids.add(q['id'])
        elif r['base'] in keys:
            links[r['base']].add(q['id']);linked_qids.add(q['id']);fallback.append({'id':q['id'],'requested':r['key'],'fallback':r['base'],'f':q.get('f','')[:240]})
        else:
            unresolved.append({'id':q['id'],'requested':r['key'],'base':r['base'],'f':q.get('f','')[:240]})
orphans=sorted(k for k,v in links.items() if not v)
report={
 'schema':2,'parser_marker':'PMAL_LAW_REF_V2','device_count':len(keys),'question_count':len(qs),
 'reference_count':ref_count,'linked_question_count':len(linked_qids),'linked_device_count':len(keys)-len(orphans),
 'orphan_device_count':len(orphans),'orphan_devices':orphans,'multi_linked_question_count':multi,
 'fallback_reference_count':len(fallback),'fallback_references':fallback[:500],
 'unresolved_reference_count':len(unresolved),'unresolved_references':unresolved[:500],
 'ordinal_artifact_count':len(ordinal_artifacts),'ordinal_artifacts':ordinal_artifacts[:100],
 'known_case_samples':samples,
 'links_per_device':{k:len(v) for k,v in sorted(links.items())}
}
Path('law-bank-parser-v2-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['device_count','question_count','reference_count','linked_question_count','linked_device_count','orphan_device_count','multi_linked_question_count','fallback_reference_count','unresolved_reference_count','ordinal_artifact_count']},ensure_ascii=False))
