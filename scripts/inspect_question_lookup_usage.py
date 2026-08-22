#!/usr/bin/env python3
import re
from pathlib import Path
s=Path('index.html').read_text(encoding='utf-8')
out=[]
for pat in [r'QQ\.find',r'QQ\.filter',r'QQ\.forEach',r'findQ',r'getQuestion',r'\.id===',r'\.id\s*==']:
    out.append('\n=== '+pat+' ===\n')
    for m in list(re.finditer(pat,s))[:100]:
        sn=s[max(0,m.start()-500):min(len(s),m.end()+900)]
        out.append(re.sub(r'\s+',' ',sn)+'\n')
Path('question-lookup-usage.txt').write_text(''.join(out),encoding='utf-8')
print('question lookup usage report written')
