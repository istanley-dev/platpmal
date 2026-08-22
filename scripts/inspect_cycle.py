#!/usr/bin/env python3
import re
from pathlib import Path

src = Path('index.html').read_text(encoding='utf-8')

def clean(s):
    return re.sub(r'\s+', ' ', s).strip()

out = []

# 1) Todos os contextos compactos de ciclo/cycle.
out.append('=== OCORRENCIAS CICLO/CYCLE ===\n')
for i, m in enumerate(re.finditer(r'ciclo|cycle', src, re.I), 1):
    a=max(0,m.start()-260); b=min(len(src),m.end()+420)
    out.append(f'{i:03d} pos={m.start()}: {clean(src[a:b])}\n')

# 2) Mensagens de falha/erro e toasts próximas de novo/reset/ciclo.
out.append('\n=== MENSAGENS DE FALHA POSSIVEIS ===\n')
for i, m in enumerate(re.finditer(r'n[aã]o foi poss[ií]vel|n[aã]o foi|imposs[ií]vel|falh|erro|toast\s*\(', src, re.I), 1):
    a=max(0,m.start()-220); b=min(len(src),m.end()+360)
    chunk=clean(src[a:b])
    if re.search(r'ciclo|cycle|reset|hist[oó]r|progres|miss[aã]o|cron', chunk, re.I):
        out.append(f'{i:03d} pos={m.start()}: {chunk}\n')

# 3) IDs/classes/botoes contendo ciclo/reset/recomeçar/novo.
out.append('\n=== ELEMENTOS HTML RELACIONADOS ===\n')
for i, m in enumerate(re.finditer(r'<(?:button|div|a)[^>]{0,500}(?:ciclo|cycle|reset|recome|reinici|novo)[^>]{0,500}>', src, re.I), 1):
    out.append(f'{i:03d} pos={m.start()}: {clean(m.group(0))}\n')

# 4) Funções nomeadas e listeners cujo corpo inicial menciona ciclo/reset/histórico.
out.append('\n=== FUNCOES/LISTENERS RELACIONADOS ===\n')
for m in re.finditer(r'function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{', src):
    start=m.start(); chunk=src[start:min(len(src), start+2400)]
    if re.search(r'ciclo|cycle|reset|hist[oó]r|progresso|progress', chunk, re.I):
        out.append(f'function {m.group(1)} pos={start}: {clean(chunk[:1800])}\n')
for m in re.finditer(r'getElementById\(["\']([^"\']+)["\']\)\.addEventListener\([^;]{0,3000}', src):
    chunk=m.group(0)
    if re.search(r'ciclo|cycle|reset|recome|reinici|hist[oó]r', chunk, re.I):
        out.append(f'listener #{m.group(1)} pos={m.start()}: {clean(chunk[:1800])}\n')

Path('cycle-debug-report.txt').write_text(''.join(out), encoding='utf-8')
print('Relatório compacto de ciclo gravado.')
