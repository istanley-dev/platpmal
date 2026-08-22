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

def js_string_field(obj,name):
    m=re.search(r'"'+re.escape(name)+r'"\s*:\s*"((?:\\.|[^"\\])*)"',obj,re.S)
    if not m:return ''
    try:return json.loads('"'+m.group(1)+'"')
    except:return m.group(1)

def question_objects():
    out=[]
    for m in re.finditer(r'\{\s*"id"\s*:\s*"',src):
        start=m.start();depth=0;quote=False;esc=False;end=None
        for i in range(start,min(len(src),start+25000)):
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
        obj=src[start:end]
        qid=js_string_field(obj,'id')
        if qid:out.append({'id':qid,'f':js_string_field(obj,'f'),'m':js_string_field(obj,'m'),'a':js_string_field(obj,'a'),'e':js_string_field(obj,'e'),'g':js_string_field(obj,'g'),'c':js_string_field(obj,'c')})
    # de-dup ids, prefer later object (final bank can contain overrides)
    d={}
    for q in out:d[q['id']]=q
    return list(d.values())

SPECIAL=[
 (r'14\.?133','L14133',r'14\.?133'),(r'11\.?343','L11343',r'11\.?343'),(r'8\.?069|\bECA\b','L8069',r'(?:8\.?069|\bECA\b)'),
 (r'8\.?072|11\.?464','L8072',r'(?:8\.?072|11\.?464)'),(r'13\.?869','L13869',r'13\.?869'),
 (r'11\.?340|\bLMP\b|Lei Maria da Penha','L11340',r'(?:11\.?340|\bLMP\b|Lei Maria da Penha)'),
 (r'10\.?826','L10826',r'10\.?826'),(r'9\.?503|\bCTB\b','L9503',r'(?:9\.?503|\bCTB\b)'),(r'12\.?850','L12850',r'12\.?850'),
 (r'9\.?455','L9455',r'9\.?455'),(r'7\.?716','L7716',r'7\.?716'),(r'9\.?605','L9605',r'9\.?605'),(r'7\.?960','L7960',r'7\.?960'),
 (r'9\.?099|\bJECRIM\b','L9099',r'(?:9\.?099|\bJECRIM\b)'),(r'10\.?259|\bJEF\b','L10259',r'(?:10\.?259|\bJEF\b)'),
 (r'8\.?429|14\.?230','L8429',r'(?:8\.?429|14\.?230)'),(r'8\.?987','L8987',r'8\.?987'),(r'9\.?784','L9784',r'9\.?784'),
 (r'8\.?112','L8112',r'8\.?112'),(r'4\.?717','L4717',r'4\.?717'),(r'13\.?300','L13300',r'13\.?300'),(r'7\.?210','LEP',r'7\.?210'),
 (r'12\.?016','L12016',r'12\.?016'),(r'9\.?474','L9474',r'9\.?474'),(r'12\.?830','L12830',r'12\.?830'),(r'12\.?037','L12037',r'12\.?037'),
 (r'9\.?507','L9507',r'9\.?507'),(r'9\.?296','L9296',r'9\.?296')]

def parse_ref(f):
    if not f:return None
    if re.search(r'Lei\s*n?º?\.?\s*5\.?346',f,re.I):
        m=re.search(r'5\.?346\/?\d{0,4}[,:\s]{0,4}[Aa]rts?\.?\s*(\d+)',f)
        return 'Lei5346 '+m.group(1) if m else 'Lei 5.346'
    if re.search(r'CADH|Pacto de S[ãa]o Jos[ée]|Conven[çc][ãa]o Americana',f,re.I):
        m=re.search(r'(?:CADH|S[ãa]o Jos[ée]|Americana)\D{0,12}[Aa]rts?\.?\s*(\d+)',f,re.I)
        return 'CADH '+m.group(1) if m else 'CADH'
    if re.search(r'37\.?042',f):
        m=re.search(r'37\.?042\/?\d{0,4}[,:\s]{0,4}[Aa]rts?\.?\s*(\d+)',f)
        return 'RD '+m.group(1) if m else 'RD'
    if re.search(r'14\.?751',f):
        m=re.search(r'14\.?751\/?\d{0,4}[,:\s]{0,4}[Aa]rts?\.?\s*(\d+)',f)
        return 'LO '+m.group(1) if m else 'LO'
    for detect,pfx,full in SPECIAL:
        if re.search(detect,f,re.I):
            m=re.search(r'(?:'+full+r')\/?\d{0,4}[,:\s]{0,4}[Aa]rts?\.?\s*(\d+)',f,re.I)
            return pfx+' '+m.group(1) if m else pfx
    dipl=None
    if re.search(r'\bCPPM\b',f):dipl='CPPM'
    elif re.search(r'\bCPP\b',f):dipl='CPP'
    elif re.search(r'\bCPM\b',f):dipl='CPM'
    elif re.search(r'\bCP\b',f):dipl='CP'
    elif re.search(r'\bCF\b',f):dipl='CF'
    if not dipl:return None
    m=re.search(r'[Aa]rts?\.?\s*(\d+)',f)
    return dipl+' '+m.group(1) if m else None

DISP=var_block('DISP'); props=split_props(DISP) if DISP else []
entries=[]
for p in props:
    k=prop_key(p)
    if k:entries.append({'key':k,'raw':p[p.find(':')+1:].strip()[:5000]})
keys=set(e['key'] for e in entries)
qs=question_objects(); qids=set(q['id'] for q in qs)
links={k:[] for k in keys}; missing_keys={}; unparsed=[]; legal_ref_questions=0
legal_hint=re.compile(r'\b(?:CF|CP|CPP|CPM|CPPM|CADH|ECA|CTB|JECRIM|JEF|LEP)\b|Lei\s|Decreto\s|\b\d{1,2}\.\d{3}\b',re.I)
for q in qs:
    f=q.get('f','')
    if legal_hint.search(f):legal_ref_questions+=1
    k=parse_ref(f)
    if k:
        if k in keys:links[k].append(q['id'])
        else:missing_keys.setdefault(k,[]).append({'id':q['id'],'f':f[:300]})
    elif legal_hint.search(f):
        unparsed.append({'id':q['id'],'f':f[:300]})

orphans=sorted(k for k,v in links.items() if not v)
linked_qids=set(x for v in links.values() for x in v)
# same content text registered under more than one key
raw_groups={}
for e in entries:raw_groups.setdefault(e['raw'],[]).append(e['key'])
duplicate_contents=[v for v in raw_groups.values() if len(v)>1]

struct={
 'devices':len(keys),'questions_extracted':len(qs),'questions_with_legal_hint':legal_ref_questions,
 'linked_questions_unique':len(linked_qids),'linked_device_count':len(keys)-len(orphans),'orphan_device_count':len(orphans),
 'orphan_devices':orphans,'missing_device_key_count':len(missing_keys),'missing_device_keys':missing_keys,
 'unparsed_legal_reference_count':len(unparsed),'unparsed_legal_references':unparsed[:200],
 'duplicate_device_content_groups':duplicate_contents,
 'links_per_device':{k:len(v) for k,v in sorted(links.items())}
}
fn_names=['parseRef','buildKeyToQids','readingOrder','readingPlanInfo','startLeituraQuiz','renderBiblio','ldRead']
funcs={n:func_block(n) for n in fn_names}
summary={'source_chars':len(src),'device_count':len(entries),'device_keys':[e['key'] for e in entries],'question_id_count':len(qids),'functions_found':{n:bool(v) for n,v in funcs.items()}}
Path('law-bank-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
Path('law-bank-structural.json').write_text(json.dumps(struct,ensure_ascii=False,indent=2),encoding='utf-8')
Path('law-bank-devices.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
Path('law-bank-linking.txt').write_text('\n\n'.join('=== '+n+' ===\n'+v for n,v in funcs.items()),encoding='utf-8')
Path('cycle-debug-report.txt').write_text('Banco de Leis auditado. Veja law-bank-summary.json, law-bank-structural.json, law-bank-devices.json e law-bank-linking.txt.\n',encoding='utf-8')
print(json.dumps({k:struct[k] for k in ['devices','questions_extracted','questions_with_legal_hint','linked_questions_unique','linked_device_count','orphan_device_count','missing_device_key_count','unparsed_legal_reference_count']},ensure_ascii=False))
