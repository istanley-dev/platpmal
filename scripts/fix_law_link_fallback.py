#!/usr/bin/env python3
from pathlib import Path
import re

# PMAL: fallback seguro auditável; alteração de comentário também dispara o workflow.
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='PMAL_LAW_LINK_FALLBACK_V1'
if marker in s:
    print('fallback já aplicado')
    raise SystemExit(0)

m=re.search(r'function\s+buildKeyToQids\s*\([^)]*\)\s*\{',s)
if not m: raise SystemExit('buildKeyToQids não encontrada')
start=m.start(); brace=s.find('{',m.start());depth=0;quote=None;esc=False;end=None
for i in range(brace,len(s)):
    ch=s[i]
    if quote:
        if esc:esc=False
        elif ch=='\\':esc=True
        elif ch==quote:quote=None
        continue
    if ch in ('"',"'",'`'):quote=ch;continue
    if ch=='{':depth+=1
    elif ch=='}':
        depth-=1
        if depth==0:end=i+1;break
if not end: raise SystemExit('fim de buildKeyToQids não encontrado')
new=r'''/* PMAL_LAW_LINK_FALLBACK_V1 — vínculo exato primeiro; fallback só para cartão genérico da mesma lei */
function buildKeyToQids(){
  if(KEY_TO_QIDS)return KEY_TO_QIDS;
  KEY_TO_QIDS={};
  QQ.forEach(function(q){
    var r=parseRef(q.f);if(!r)return;
    var key=null;
    if(DISP[r.key])key=r.key;
    else if(r.baseKey&&DISP[r.baseKey])key=r.baseKey;
    if(!key)return;
    if(!KEY_TO_QIDS[key])KEY_TO_QIDS[key]=[];
    if(KEY_TO_QIDS[key].indexOf(q.id)<0)KEY_TO_QIDS[key].push(q.id);
  });
  return KEY_TO_QIDS;
}'''
s=s[:start]+new+s[end:]
p.write_text(s,encoding='utf-8')
print('fallback de vínculo aplicado')
