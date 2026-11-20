#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")

s, removed = re.subn(
    r"\n?<!-- PMAL_LAW_DSO_PERSISTENCE_V1 -->[\s\S]*?<!-- /PMAL_LAW_DSO_PERSISTENCE_V1 -->\n?",
    "\n",
    s,
)
if removed > 1:
    raise SystemExit("ABORTADO: mais de um bloco auxiliar de persistência encontrado.")

load_anchor = "S.lawMemory=p.lawMemory||{cards:{},daily:{}};"
load_add = (
    "S.lawMemory=p.lawMemory||{cards:{},daily:{}};"
    "S.lawDso=p.lawDso||{version:1,cycle:1,day:1,round:1,history:{}};"
    "S.lawDsoReadingV3=p.lawDsoReadingV3||{};"
)
save_anchor = "lawMemory:S.lawMemory||{cards:{},daily:{}},legacyEids:"
save_add = (
    "lawMemory:S.lawMemory||{cards:{},daily:{}},"
    "lawDso:S.lawDso||{version:1,cycle:1,day:1,round:1,history:{}},"
    "lawDsoReadingV3:S.lawDsoReadingV3||{},legacyEids:"
)

ls_start = s.find("function LS(){")
ss_start = s.find("function SS(){", ls_start)
ss_end = s.find("// ══════════", ss_start)
if ls_start < 0 or ss_start < 0 or ss_end < 0:
    raise SystemExit("ABORTADO: funções LS()/SS() não localizadas.")
ls_part = s[ls_start:ss_start]
ss_part = s[ss_start:ss_end]
if load_add in ls_part and save_add in ss_part:
    print("Persistência canônica do Banco de Leis já instalada.")
elif ls_part.count(load_anchor) == 1 and ss_part.count(save_anchor) == 1:
    ls_part = ls_part.replace(load_anchor, load_add, 1)
    ss_part = ss_part.replace(save_anchor, save_add, 1)
    s = s[:ls_start] + ls_part + ss_part + s[ss_end:]
else:
    raise SystemExit(
        "ABORTADO: pontos de LS()/SS() divergentes. "
        f"load_anchor={ls_part.count(load_anchor)}, save_anchor={ss_part.count(save_anchor)}"
    )

checks = [
    "S.lawDso=p.lawDso||{version:1,cycle:1,day:1,round:1,history:{}};",
    "S.lawDsoReadingV3=p.lawDsoReadingV3||{};",
    "lawDso:S.lawDso||{version:1,cycle:1,day:1,round:1,history:{}},",
    "lawDsoReadingV3:S.lawDsoReadingV3||{},",
    "function LS(){",
    "function SS(){",
]
missing = [x for x in checks if x not in s]
if missing:
    raise SystemExit("ABORTADO: verificação da persistência canônica falhou: " + ", ".join(missing))
if "PMAL_LAW_DSO_PERSISTENCE_V1" in s:
    raise SystemExit("ABORTADO: bloco auxiliar antigo permaneceu no HTML.")

p.write_text(s, encoding="utf-8")
print("OK: LS() restaura e SS() salva lawDso + lawDsoReadingV3 no armazenamento principal.")
