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
out=[]
for name in [
    'pendingLawReview','startLawReviewGated','startYesterdayReview','startWeekReviewGated',
    'touchLeituraDia','readingOrder','readingPlanInfo','renderLeituraSub','renderBiblio',
    'bibRead','ldRead','dueLawReviewCards','startLeituraQuiz',
    'trackAnswer','answer','ans','renderQ','showRes','startQ'
]:
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',s)
    if m:out.append('\n=== '+name+' ===\n'+balanced(m.start())+'\n')
Path('law-review-functions.txt').write_text(''.join(out),encoding='utf-8')
print('law review functions extracted')
