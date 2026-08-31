#!/usr/bin/env python3
import re
from pathlib import Path

src = Path('index.html').read_text(encoding='utf-8')

def balanced_function(name):
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',src)
    if not m:return ''
    start=src.find('{',m.start()); depth=0; quote=None; esc=False
    for i in range(start,len(src)):
        ch=src[i]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
            continue
        if ch in ('"',"'",'`'): quote=ch; continue
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:return src[m.start():i+1]
    return ''

out=[]
# Operations HTML
m=re.search(r'<div class="sec-k">Opera[cç][oõ]es</div>',src,re.I)
if m:
    nxt=re.search(r'<div class="sec-k">',src[m.end():],re.I)
    end=m.end()+nxt.start() if nxt else min(len(src),m.start()+12000)
    out.append('=== OPERACOES HTML ===\n'+src[m.start():end])

# select containing previous errors
m=re.search(r'<select[^>]*>[\s\S]{0,4000}?<option value="erros">Somente erradas anteriormente</option>[\s\S]{0,1000}?</select>',src,re.I)
if m: out.append('\n=== SELECT ERROS ===\n'+m.group(0))

# relevant function names
names=[]
for fm in re.finditer(r'function\s+([A-Za-z_$][\w$]*)\s*\(',src):
    n=fm.group(1)
    if re.search(r'revis|review|erro|wrong|mist',n,re.I): names.append(n)
names=sorted(set(names))
out.append('\n=== FUNCTIONS ===\n'+'\n'.join(names))
for n in names:
    body=balanced_function(n)
    if body and len(body)<18000:
        out.append('\n=== FUNCTION '+n+' ===\n'+body)

# nearby D+ scheduling snippets
for label,pat in [('D1',r'D\+1'),('D7',r'D\+7'),('D21',r'D\+21')]:
    mm=re.search(pat,src,re.I)
    if mm: out.append(f'\n=== {label} CONTEXT ===\n'+src[max(0,mm.start()-1200):min(len(src),mm.end()+2500)])

Path('review-ui-inspection.txt').write_text('\n'.join(out),encoding='utf-8')
print('review inspection written:',len(names),'functions',len(out),'sections')
