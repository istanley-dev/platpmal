#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
idx=(ROOT/'index.html').read_text(encoding='utf-8')
manifest=json.loads((ROOT/'law-reading/manifest.json').read_text(encoding='utf-8'))
issues=[]
if manifest.get('totalDays')!=65 or len(manifest.get('days',[]))!=65:issues.append('manifest precisa ter 65 dias')
if 'PMAL_DSO_FULL_LAW_READER_V2_START' not in idx:issues.append('marker V2 ausente do index')
for needle in ['pmalDsoIntegralDone','LEITURA INTEGRAL DO DIA','Li integralmente esta faixa','window.completeDsoLawDay=function()']:
    if needle not in idx:issues.append('index sem '+needle)
block=idx[idx.find('PMAL_DSO_FULL_LAW_READER_V2_START'):idx.find('PMAL_DSO_FULL_LAW_READER_V2_END')]
if 'if(!pmalFullDone())' not in block:issues.append('gate integral ausente')
if 'S.bibLidos' in block:issues.append('V2 não deve exigir bibLidos para avançar')
if 'QQ.filter' in block or 'QQ.push' in block:issues.append('V2 não deve tocar no pool QQ de simulados')
pii=re.compile(r'istanley|gmail\.com|112[. ]*132[. ]*064|abra[aã]o barbosa canuto',re.I)
for d in manifest.get('days',[]):
    f=ROOT/d['path']
    if not f.exists():issues.append('arquivo ausente '+d['path']);continue
    txt=f.read_text(encoding='utf-8')
    if len(txt)<80:issues.append('texto curto '+d['path'])
    if not re.search(r'\bArt\.?\s*\d+',txt,re.I):issues.append('sem artigos '+d['path'])
    if pii.search(txt):issues.append('PII '+d['path'])
sentinels={
 'law-reading/c1-d01.txt':['Art. 5'],
 'law-reading/c1-d11.txt':['Art. 151','Art. 194'],
 'law-reading/c2-d01.txt':['Art. 1','Art. 12'],
 'law-reading/c2-d23.txt':['Art. 225','Art. 244'],
 'law-reading/c3-d01.txt':['Art. 1','Art. 14'],
 'law-reading/c3-d11.txt':['Art. 82','Art. 107'],
}
for path,needles in sentinels.items():
    f=ROOT/path
    if f.exists():
      txt=f.read_text(encoding='utf-8')
      for n in needles:
        if n not in txt: issues.append(f'{path} sem {n}')
report={'schema':1,'total_days':manifest.get('totalDays'),'files_checked':len(manifest.get('days',[])),'issues':issues,'status':'ok' if not issues else 'fail'}
(ROOT/'law-reading-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if issues:sys.exit(1)
