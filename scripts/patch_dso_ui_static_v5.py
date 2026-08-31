#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
s = p.read_text(encoding="utf-8")

repls = [
    ("fetch('law-reading/manifest.json?v=4',{cache:'no-cache'})", "fetch('law-reading/manifest.json?v=5',{cache:'no-cache'})"),
    ("m.version!==4||m.format!=='structured-article-cards'", "m.version!==5||m.format!=='static-integral-law-bank'"),
    ("e.path+'?v=4'", "e.path+'?v=5'"),
    ("d.version!==4||d.format!=='structured-article-cards'", "d.version!==5||d.format!=='static-integral-law-bank'"),
    ("os cartões abaixo são os artigos da faixa prevista para este dia no PDF do DSO.", "os cartões abaixo vêm do Banco de Leis integral interno e seguem exatamente a faixa prevista para este dia no PDF do DSO."),
]
for old, new in repls:
    if old not in s:
        raise SystemExit(f"trecho esperado da UI não encontrado: {old}")
    s = s.replace(old, new, 1)

marker = "PMAL_DSO_STATIC_BANK_V5"
if marker not in s:
    s = s.replace(
        "<!-- PMAL_DSO_READING_CARDS_V3_START -->",
        "<!-- PMAL_DSO_READING_CARDS_V3_START -->\n<!-- PMAL_DSO_STATIC_BANK_V5 -->",
        1,
    )

p.write_text(s, encoding="utf-8")
print("UI ligada ao Banco de Leis integral estático V5")
