#!/usr/bin/env python3
import re
from pathlib import Path

src = Path('index.html').read_text(encoding='utf-8')
terms = [
    r'Novo ciclo', r'novo ciclo', r'não foi possível', r'nao foi possivel',
    r'ciclo', r'cycle', r'localStorage'
]

hits = []
seen = set()
for term in terms:
    for m in re.finditer(term, src, re.I):
        start = max(0, m.start() - 1200)
        end = min(len(src), m.end() + 1800)
        # dedup nearby matches
        bucket = m.start() // 1200
        key = (term.lower(), bucket)
        if key in seen:
            continue
        seen.add(key)
        snippet = src[start:end]
        hits.append((m.start(), term, snippet))

hits.sort(key=lambda x: x[0])
out = []
for i, (pos, term, snippet) in enumerate(hits, 1):
    out.append(f'===== HIT {i} | pos={pos} | termo={term} =====\n')
    out.append(snippet)
    out.append('\n\n')

Path('cycle-debug-report.txt').write_text(''.join(out), encoding='utf-8')
print(f'{len(hits)} blocos gravados em cycle-debug-report.txt')
