#!/usr/bin/env python3
import re
from pathlib import Path
s=Path('index.html').read_text(encoding='utf-8')
def balanced(start):
    p=s.find('{',start);d=0;q=None;esc=False
    if p<0:return ''
    for i in range(p,len(s)):
        ch=s[i]
        if q:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==q:q=None
            continue
        if ch in ('"',"'",'`'):q=ch;continue
        if ch=='{':d+=1
        elif ch=='}':
            d-=1
            if d==0:return s[start:i+1]
    return ''
def func(name):
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',s)
    return balanced(m.start()) if m else ''
names=[
    'pendingLawReview','startLawReviewGated','startYesterdayReview','startWeekReviewGated',
    'computeTodaysArticles','touchLeituraDia','readingOrder','readingPlanInfo','renderLeituraSub','renderBiblio',
    'bibRead','ldRead','bibUpdCounter','buildLawReviewDeck','dueLawReviewCards','startLeituraQuiz',
    'trackAnswer','answer','ans','renderQ','showRes','startQ'
]
out=[];seen=set()
for name in names:
    b=func(name)
    if b:
        out.append('\n=== '+name+' ===\n'+b+'\n');seen.add(name)
# Também captura automaticamente qualquer função que manipule o estado da leitura diária.
for m in re.finditer(r'function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{',s):
    name=m.group(1)
    if name in seen: continue
    b=balanced(m.start())
    if b and ('leituraDia' in b or 'READ_DAILY_QTY' in b or 'bibLidos' in b):
        out.append('\n=== '+name+' ===\n'+b+'\n');seen.add(name)
Path('law-review-functions.txt').write_text(''.join(out),encoding='utf-8')
print('law review functions extracted:',len(seen))
