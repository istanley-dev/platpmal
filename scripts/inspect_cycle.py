#!/usr/bin/env python3
import re
from pathlib import Path

src = Path('index.html').read_text(encoding='utf-8')

def clean(s):
    return re.sub(r'\s+', ' ', s).strip()

def balanced_from(start, op='{', cl='}'):
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
        if ch in ('"',"'",'`'):
            quote=ch;continue
        if ch==op:depth+=1
        elif ch==cl:
            depth-=1
            if depth==0:return src[p:i+1]
    return ''

def var_block(name):
    m=re.search(r'\b(?:var|let|const)\s+'+re.escape(name)+r'\s*=',src)
    return balanced_from(m.end()) if m else ''

def func_block(name):
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',src)
    if not m:return ''
    body=balanced_from(m.start())
    return src[m.start():src.find('{',m.start())]+body

out=[]
out.append('=== LAW BANK: DISP ===\n')
disp=var_block('DISP')
out.append(disp+'\n')
out.append('\n=== BIB_ORDER ===\n'+var_block('BIB_ORDER')+'\n')
out.append('\n=== BIB_COLORS ===\n'+var_block('BIB_COLORS')+'\n')
for fn in ['buildKeyToQids','readingOrder','readingPlanInfo','startLeituraQuiz','renderBiblio','ldRead']:
    out.append('\n=== FUNCTION '+fn+' ===\n'+func_block(fn)+'\n')

out.append('\n=== DECLARACOES RELACIONADAS A LEI/BIB/MAP/QID ===\n')
for m in re.finditer(r'\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=',src):
    name=m.group(1)
    if re.search(r'LAW|LEI|ART|BIB|DISP|KEY|MAP|QID|READ',name,re.I):
        out.append(f'-- {name} pos={m.start()} --\n{clean(src[m.start():min(len(src),m.start()+5000)])}\n')

# Snippets de todos os usos do mapa/dispositivos, para identificar a regra de vínculo.
out.append('\n=== USOS DE buildKeyToQids / DISP ===\n')
for pat in [r'buildKeyToQids\s*\(',r'\bDISP\s*\[',r'Object\.keys\(DISP\)']:
    for m in re.finditer(pat,src):
        out.append(f'pos={m.start()} {clean(src[max(0,m.start()-700):min(len(src),m.end()+1800)])}\n')

# Extrai objetos de questão que mencionam explicitamente art./lei/decreto/CF/CP/CPP/CPM/CPPM.
out.append('\n=== QUESTOES COM REFERENCIA LEGAL EXPLICITA ===\n')
# O banco usa objetos compactos {"id":"...",...}; capturamos os que cabem numa janela razoável.
qpat=re.compile(r'\{\s*"id"\s*:\s*"([^"]+)"')
count=0
for m in qpat.finditer(src):
    # busca fim simples do objeto respeitando strings
    start=m.start(); depth=0; quote=False; esc=False; end=None
    for i in range(start,min(len(src),start+18000)):
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
            if depth==0:
                end=i+1;break
    if not end:continue
    obj=src[start:end]
    if re.search(r'Lei\s*(?:n[ºo°.]*)?\s*\d|Decreto\s*(?:n[ºo°.]*)?\s*\d|art\.?\s*\d|CF/88|Constitui[cç][aã]o Federal|\bCPPM\b|\bCPP\b|\bCPM\b|C[oó]digo Penal',obj,re.I):
        count+=1
        out.append(obj+'\n')
out.append(f'\nTOTAL_QUESTOES_LEGAIS_EXPLICITAS={count}\n')

Path('cycle-debug-report.txt').write_text(''.join(out),encoding='utf-8')
print('Auditoria do Banco de Leis gravada em cycle-debug-report.txt')
