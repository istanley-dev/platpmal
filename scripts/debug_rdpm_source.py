#!/usr/bin/env python3
from __future__ import annotations

import re
from io import BytesIO

import requests
from pypdf import PdfReader

URL = "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/download/id/792/param/2/set/1/get/c8f191d3/dist/"
UA = "Mozilla/5.0 (PMAL study platform RDPM diagnostics; +https://github.com/istanley-dev/platpmal)"

r = requests.get(URL, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"}, timeout=60, allow_redirects=True)
print("STATUS", r.status_code, flush=True)
print("FINAL", r.url, flush=True)
print("CONTENT-TYPE", r.headers.get("content-type"), flush=True)
print("CONTENT-LENGTH", len(r.content), flush=True)
print("FIRST-BYTES", repr(r.content[:80]), flush=True)
r.raise_for_status()

if not r.content.startswith(b"%PDF"):
    print("NOT_PDF_SAMPLE", r.text[:5000], flush=True)
    raise SystemExit(2)

reader = PdfReader(BytesIO(r.content))
print("PAGES", len(reader.pages), flush=True)
page_texts = []
for i, page in enumerate(reader.pages, 1):
    txt = page.extract_text() or ""
    page_texts.append(txt)
    print(f"PAGE {i} CHARS {len(txt)}", flush=True)
    if i <= 3:
        print(f"--- PAGE {i} SAMPLE ---", flush=True)
        print(txt[:8000], flush=True)

text = "\n".join(page_texts).replace("\xa0", " ").replace("\u00ad", "")
print("TOTAL_CHARS", len(text), flush=True)

patterns = {
    "strict_current": r"(?mi)^[ \t]*(?:Art\.|Artigo)[ \t]*(\d+)(?:[º°oO])?(?:[ \t]*[-–—‑][ \t]*([A-Za-z]{1,3}))?[ \t]*(?:[.º°])?(?=[ \t\n])",
    "loose_art": r"(?i)\bArt(?:igo)?\.?\s*(\d{1,3})(?:\s*[º°oO])?(?:\s*[-–—‑]?\s*([A-Za-z]{1,3}))?",
    "number_prefix": r"(?mi)^\s*(\d{1,3})\s*[º°oO]?\s*[-–—.:]",
}
for name, pat in patterns.items():
    matches = list(re.finditer(pat, text))
    labels = []
    for m in matches:
        labels.append(m.group(1) + ((m.group(2) or "").upper() if m.lastindex and m.lastindex >= 2 else ""))
    print("PATTERN", name, "COUNT", len(matches), flush=True)
    print("LABELS_HEAD", labels[:80], flush=True)
    print("LABELS_TAIL", labels[-40:], flush=True)
    for boundary in ("1", "25", "38", "66", "81", "107"):
        print("BOUNDARY", name, boundary, boundary in labels, flush=True)

for boundary in (1, 25, 38, 66, 81, 107):
    print(f"--- CONTEXT {boundary} ---", flush=True)
    rx = re.compile(rf"(?is).{{0,250}}(?:Art(?:igo)?\.?\s*)?{boundary}\s*[º°oO]?.{{0,700}}")
    hits = rx.findall(text)
    for h in hits[:5]:
        print(repr(h), flush=True)
