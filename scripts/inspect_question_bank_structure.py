from pathlib import Path
import re

s=Path('index.html').read_text(encoding='utf-8')
terms=['materia','assunto','gabarito','comentario','enunciado','texto','answer','subject','topic']
print('SIZE',len(s))
for t in terms:
    print('\nTERM',t)
    for m in list(re.finditer(t,s,re.I))[:12]:
        a=max(0,m.start()-350); b=min(len(s),m.start()+500)
        print('---',m.start(),'---')
        print(s[a:b].replace('\n',' ')[:900])

print('\nARRAY CANDIDATES')
# Show assignments near arrays whose first 2KB contains likely question keys
for m in re.finditer(r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*\[',s):
    name=m.group(1); chunk=s[m.start():m.start()+4000]
    score=sum(1 for k in ['materia','assunto','gabarito','coment','enunci','question','answer','subject','topic'] if k.lower() in chunk.lower())
    if score>=2:
        print('NAME',name,'POS',m.start(),'SCORE',score)
        print(chunk[:1800].replace('\n',' '))
        print('---')
