#!/usr/bin/env python3
from __future__ import annotations

import re
import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (PMAL study platform article diagnostics; +https://github.com/istanley-dev/platpmal)"
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})

SOURCES = {
    "L14133": (
        "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm",
        [45,71,72,114,150,151,194],
    ),
    "CPM": (
        "https://www.planalto.gov.br/ccivil_03/decreto-lei/del1001compilado.htm",
        [13,25,26,48,68,108,135,194,253,254,354],
    ),
}

PATTERNS = {
    "candidate_v5": re.compile(r"(?mi)^[ \t]*(?:Art\.|Artigo)[ \t]*(\d+)(?:\.?[º°oO])?(?:[-–—‑]([A-Za-z]{1,3}))?(?=[ \t\n.]|$)"),
    "header_flexible": re.compile(r"(?mi)^[ \t]*(?:Art\.|Artigo)[ \t]*(\d+)(?:[ \t]*\.?[ \t]*[º°oO])?(?:[ \t]*[-–—‑][ \t]*([A-Z]{1,3})(?=[. \t\n]))?(?=[. \t\n-–—‑]|$)"),
}

def clean_lines(text: str) -> str:
    text=text.replace("\xa0"," ").replace("\u00ad","")
    text=re.sub(r"[ \t]+"," ",text)
    text=re.sub(r" *\n *","\n",text)
    text=re.sub(r"\n{3,}","\n\n",text)
    return text.strip()

def fetch_html(url: str) -> str:
    r=S.get(url,timeout=45); r.raise_for_status(); enc=r.apparent_encoding or r.encoding or "latin-1"
    try: html=r.content.decode(enc,errors="replace")
    except LookupError: html=r.content.decode("latin-1",errors="replace")
    soup=BeautifulSoup(html,"html.parser")
    for tag in soup.find_all(["script","style","strike","s","del"]): tag.decompose()
    for tag in soup.find_all(style=True):
        attrs=getattr(tag,"attrs",None)
        if attrs and "line-through" in str(attrs.get("style","")).lower(): tag.decompose()
    return clean_lines(soup.get_text("\n"))

for name,(url,boundaries) in SOURCES.items():
    print(f"\n===== {name} =====", flush=True)
    text=fetch_html(url)
    print("CHARS",len(text),flush=True)
    for pname,pat in PATTERNS.items():
        labels=[]
        for m in pat.finditer(text):
            labels.append(m.group(1)+((m.group(2) or "").upper() if m.lastindex and m.lastindex>=2 else ""))
        print("PATTERN",pname,"COUNT",len(labels),flush=True)
        print("MISSING",[str(b) for b in boundaries if str(b) not in labels],flush=True)
        print("NEAR_LABELS",[(x,labels[max(0,i-2):i+3]) for x in map(str,boundaries) for i,v in enumerate(labels) if v==x][:30],flush=True)

    for b in boundaries:
        print(f"\n--- {name} BOUNDARY {b} ---",flush=True)
        # Show every line containing the literal article marker, preserving repr.
        rx_line=re.compile(rf"(?i)^.*\bArt(?:igo)?\.?\s*{b}(?!\d).*$")
        line_hits=[ln for ln in text.splitlines() if rx_line.search(ln)]
        print("LINE_HITS",len(line_hits),flush=True)
        for ln in line_hits[:12]: print("LINE",repr(ln),flush=True)
        # Also show raw context if the marker and number were separated by newlines/tags.
        rx_ctx=re.compile(rf"(?is).{{0,180}}\bArt(?:igo)?\.?\s*{b}(?!\d).{{0,350}}")
        hits=rx_ctx.findall(text)
        print("CTX_HITS",len(hits),flush=True)
        for h in hits[:5]: print("CTX",repr(h),flush=True)
