#!/usr/bin/env python3
import re, json
from pathlib import Path

src = Path('index.html').read_text(encoding='utf-8')

def balanced_after(pattern, open_ch='{', close_ch='}', max_chars=2000000):
    m = re.search(pattern, src, re.I)
    if not m:
        return None
    start = src.find(open_ch, m.end()-1)
    if start < 0:
        return None
    depth=0; quote=None; esc=False
    for i,ch in enumerate(src[start:start+max_chars], start):
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
            continue
        if ch in ('"',"'",'`'):
            quote=ch; continue
        if ch==open_ch: depth+=1
        elif ch==close_ch:
            depth-=1
            if depth==0: return src[start:i+1]
    return None

def func_body(name):
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',src)
    if not m:return None
    start=src.find('{',m.start())
    depth=0;quote=None;esc=False
    for i,ch in enumerate(src[start:],start):
        if quote:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==quote:quote=None
            continue
        if ch in ('"',"'",'`'):quote=ch;continue
        if ch=='{':depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:return src[m.start():i+1]
    return None

report={"schema":1,"source_len":len(src)}
for pat,name in [(r'\b(?:var|let|const)\s+DISP\s*=','DISP'),(r'\b(?:var|let|const)\s+BIB_ORDER\s*=','BIB_ORDER'),(r'\b(?:var|let|const)\s+BIB_COLORS\s*=','BIB_COLORS')]:
    block=balanced_after(pat)
    report[name]=block

for fn in ['buildKeyToQids','readingOrder','readingPlanInfo','startLeituraQuiz','renderBiblio','incidenceScore']:
    report['fn_'+fn]=func_body(fn)

# Capture snippets around every use of DISP outside the variable declaration.
uses=[]
for m in re.finditer(r'\bDISP\b',src):
    uses.append(src[max(0,m.start()-500):min(len(src),m.end()+900)])
report['DISP_uses']=uses[:80]

# Variable/object declarations whose names look related to law/device/article linking.
related=[]
for m in re.finditer(r'\b(?:var|let|const)\s+([A-Za-z_$][\w$]*(?:LAW|LEI|ART|BIB|DISP|KEY|MAP|LINK|QID)[A-Za-z0-9_$]*)\s*=',src,re.I):
    name=m.group(1)
    related.append({"name":name,"snippet":src[m.start():min(len(src),m.start()+3500)]})
report['related_decls']=related[:120]

Path('law-bank-extract.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('written law-bank-extract.json', len(json.dumps(report,ensure_ascii=False)))
