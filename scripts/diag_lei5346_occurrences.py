#!/usr/bin/env python3
from __future__ import annotations

import re
from io import BytesIO
import requests
from pypdf import PdfReader

URLS = [
    ("PMAL", "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/download/id/892/param/2/set/2/get/2416565e/dist/"),
    ("ALE", "https://sapl.al.al.leg.br/media/sapl/public/normajuridica/1992/845/845_texto_integral.pdf"),
]
UA = "Mozilla/5.0 (PMAL study platform diagnostics)"

for name, url in URLS:
    print(f"\n===== {name} =====", flush=True)
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=(15, 90), allow_redirects=True)
        print("STATUS", r.status_code, "BYTES", len(r.content), "FINAL", r.url, flush=True)
        r.raise_for_status()
        reader = PdfReader(BytesIO(r.content))
        print("PAGES", len(reader.pages), flush=True)
        pages = []
        for i, page in enumerate(reader.pages, 1):
            txt = page.extract_text() or ""
            pages.append(txt)
            normalized = re.sub(r"\s+", " ", txt)
            if re.search(r"(?i)\bArt(?:igo)?\.?\s*51(?:\D|$)", txt) or re.search(r"(?i)\bArt(?:igo)?\.?\s*54(?:\D|$)", txt):
                print(f"--- PAGE {i} MATCH ---", flush=True)
                print(normalized[:12000], flush=True)

        text = "\n".join(pages)
        text = text.replace("\xa0", " ").replace("\u00ad", "")
        # Broad contexts, independent from production parser.
        for key in ("51", "54"):
            print(f"\n### ALL CONTEXTS ART {key} ###", flush=True)
            pats = [
                re.compile(rf"(?is).{{0,500}}\bArt(?:igo)?\.?\s*{key}(?!\d).{{0,2500}}"),
                re.compile(rf"(?is).{{0,500}}\bART(?:IGO)?\.?\s*{key}(?!\d).{{0,2500}}"),
            ]
            seen=[]
            for pat in pats:
                for m in pat.finditer(text):
                    ctx=re.sub(r"\s+", " ", m.group(0)).strip()
                    if ctx not in seen:
                        seen.append(ctx)
            print("COUNT", len(seen), flush=True)
            for idx,ctx in enumerate(seen,1):
                print(f"CONTEXT {idx}: {ctx}", flush=True)

        for needle in ["67 (sessenta e sete)", "72 (setenta e dois)", "Lei nº 9.381", "Lei n° 9.381", "9.381/2024", "9381"]:
            hits=[]
            for i,p in enumerate(pages,1):
                if needle.lower() in p.lower(): hits.append(i)
            print("NEEDLE", repr(needle), "PAGES", hits, flush=True)
    except Exception as exc:
        print("ERROR", type(exc).__name__, repr(exc), flush=True)
