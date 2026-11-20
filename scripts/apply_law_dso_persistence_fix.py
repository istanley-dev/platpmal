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

if s.count(load_add) == 1 and s.count(save_add) == 1:
    print("Persistência canônica do Banco de Leis já instalada.")
elif s.count(load_anchor) == 1 and s.count(save_anchor) == 1:
    s = s.replace(load_anchor, load_add, 1)
    s = s.replace(save_anchor, save_add, 1)
else:
    raise SystemExit(
        "ABORTADO: não foi possível localizar exatamente os pontos de LS()/SS(). "
        f"load_anchor={s.count(load_anchor)}, save_anchor={s.count(save_anchor)}"
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
