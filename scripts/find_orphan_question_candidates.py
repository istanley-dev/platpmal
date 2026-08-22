#!/usr/bin/env python3
import re,json,math,unicodedata
from pathlib import Path

src=Path('index.html').read_text(encoding='utf-8')
audit=json.loads(Path('law-bank-runtime-audit.json').read_text(encoding='utf-8'))
orphans=set(audit['orphan_devices'])

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

def var_block(name):
    m=re.search(r'\b(?:var|let|const)\s+'+re.escape(name)+r'\s*=',src)
    return balanced(m.end()) if m else ''

def split_props(obj):
    s=obj.strip()[1:-1];out=[];st=0;d=0;q=None;esc=False
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

def prop(p):
    m=re.match(r'\s*(["\'])(.*?)\1\s*:\s*(.*)$',p,re.S)
    if not m:return None,None
    k=m.group(2);v=m.group(3).strip()
    if v.startswith(('"',"'")):
        try:
            if v[0]=='"':v=json.loads(v)
            else:v=bytes(v[1:-1],'utf-8').decode('unicode_escape')
        except: v=v[1:-1]
    return k,v

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
        o=src[st:end];qid=js_field(o,'id')
        if qid:out[qid]={x:js_field(o,x) for x in ['id','e','c','f','m','a','g']}
    return list(out.values())

DEV={}
for p in split_props(var_block('DISP')):
    k,v=prop(p)
    if k in orphans:DEV[k]=str(v)
qs=questions()
STOP=set('a o as os um uma de da do das dos e em no na nos nas ao aos para por com sem que se ser são eh é do da seu sua seus suas como quando onde entre sobre artigo art lei codigo código constituicao constituição federal dispõe trata segundo forma regra termos'.split())
def norm(s):
    s=''.join(c for c in unicodedata.normalize('NFKD',str(s).lower()) if not unicodedata.combining(c))
    return re.findall(r'[a-z]{3,}|\d+[a-z]?',s)
def tok(s):return [x for x in norm(s) if x not in STOP and not (x.isdigit() and len(x)==4)]
# document frequency over question texts
qsets=[]
for q in qs:qsets.append(set(tok(' '.join([q['e'],q['c'],q['f'],q['a'],q['m']]))))
df={}
for st in qsets:
    for x in st:df[x]=df.get(x,0)+1
N=max(1,len(qs))
def idf(x):return math.log((N+1)/(df.get(x,0)+1))+1

out=[]
for k,text in sorted(DEV.items()):
    dset=set(tok(text))
    # emphasize rare device tokens
    weighted={x:idf(x) for x in dset}
    den=sum(weighted.values()) or 1
    cands=[]
    # expected article/diploma hints
    art=k.split(' ',1)[1] if ' ' in k else ''
    for q,st in zip(qs,qsets):
        inter=dset & st
        if not inter:continue
        score=sum(weighted[x] for x in inter)/den
        # bonus if exact article number and diploma family appear in foundation
        f=norm(q['f'])
        if art and art.lower() in f:score+=0.06
        if score>=0.18:
            cands.append((score,q))
    cands.sort(key=lambda x:x[0],reverse=True)
    top=[]
    for sc,q in cands[:5]:
        top.append({'score':round(sc,3),'id':q['id'],'g':q['g'],'m':q['m'],'a':q['a'],'f':q['f'][:320],'e':q['e'][:520],'c':q['c'][:420]})
    out.append({'key':k,'device':text[:1200],'candidates':top})

summary={
 'orphan_count':len(orphans),'orphan_device_texts_found':len(DEV),
 'with_candidate_ge_018':sum(bool(x['candidates']) for x in out),
 'with_candidate_ge_030':sum(any(c['score']>=.30 for c in x['candidates']) for x in out),
 'devices':out
}
Path('law-bank-orphan-candidates.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:summary[k] for k in ['orphan_count','orphan_device_texts_found','with_candidate_ge_018','with_candidate_ge_030']},ensure_ascii=False))
