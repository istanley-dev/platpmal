#!/usr/bin/env python3
import json,re,subprocess,tempfile
from pathlib import Path
s=Path('index.html').read_text(encoding='utf-8')
start='<!-- PMAL_DSO_LAW_CYCLES_V1_START -->';end='<!-- PMAL_DSO_LAW_CYCLES_V1_END -->'
assert start in s and end in s, 'marker do ciclo DSO ausente'
a=s.index(start);b=s.index(end,a)+len(end);blk=s[a:b]
checks={
 'marker': 'PMAL_DSO_LAW_CYCLES_V1' in blk,
 'plan_global': 'PMAL_DSO_LAW_PLAN' in blk,
 'coverage_layer': 'lawCoverageQuestions' in blk and 'lawcov_' in blk,
 'progress_by_completed_day': 'completeDsoLawDay' in blk and 'planToken' in blk,
 'spaced_review': all(x in blk for x in ['D+1','D+7','D+21']),
 'cebraspe_mix': all(x in blk for x in ['troca de conceitos','prazos/números','jurisprudência','lei seca']),
 'general_bank_isolated': "QQ.concat(lawCoverageQuestions())" in blk and "QQ.filter" not in blk,
}
# dias: conta objetos {n:...,label:...} apenas dentro do plano
plan_part=blk.split('var PMAL_DSO_LAW_PLAN=',1)[1].split('window.PMAL_DSO_LAW_PLAN',1)[0]
day_count=len(re.findall(r'\{n:\d+,label:',plan_part))
checks['day_count_65']=day_count==65
# sintaxe do JS injetado
m=re.search(r'<script id="pmal-dso-law-cycles-v1">([\s\S]*?)</script>',blk)
js=m.group(1) if m else ''
syntax_ok=False;syntax_error=''
if js:
    with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8') as f:
        f.write(js);name=f.name
    r=subprocess.run(['node','--check',name],capture_output=True,text=True)
    syntax_ok=r.returncode==0;syntax_error=(r.stderr or r.stdout).strip()[:1000]
checks['javascript_syntax']=syntax_ok
report={'schema':1,'marker':'PMAL_DSO_LAW_CYCLES_V1','dso_days':day_count,'checks':checks,'syntax_error':syntax_error,'ok':all(checks.values())}
Path('law-cycle-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
if not report['ok']: raise SystemExit(1)
