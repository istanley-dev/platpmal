from pathlib import Path
import re

s=Path('index.html').read_text(encoding='utf-8')
print('SIZE',len(s))

for pat in [r'\bQQ\s*=', r'\bQQ\s*=\s*\[', r'\bQQ\.push', r'QUESTIONS_20260813', r'QUESTIONS_20260819_ATUALIZACAO']:
    print('\nPATTERN',pat)
    for m in list(re.finditer(pat,s))[:12]:
        a=max(0,m.start()-1200); b=min(len(s),m.start()+3200)
        print('---',m.start(),'---')
        print(s[a:b].replace('\n',' ')[:4400])

print('\nQUESTION ARRAY DEFINITIONS')
for m in re.finditer(r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*\[\s*\{\s*["\']id["\']\s*:',s):
    name=m.group(1); print('NAME',name,'POS',m.start())
    print(s[m.start():m.start()+1800].replace('\n',' '))
    print('---')

print('\nQUESTION CONCAT / PUSH')
for m in re.finditer(r'QQ\.(?:push|concat)|QQ\s*=\s*QQ\.concat|\.concat\(QUESTIONS_',s):
    a=max(0,m.start()-1000); b=min(len(s),m.start()+2200)
    print('---',m.start(),'---')
    print(s[a:b].replace('\n',' ')[:3200])
