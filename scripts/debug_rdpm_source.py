#!/usr/bin/env python3
from __future__ import annotations

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (PMAL study platform RDPM diagnostics; +https://github.com/istanley-dev/platpmal)"
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})

URLS = [
    "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/ordergrid/descricao_ASC/startgrid/1250",
    "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/id/1/ordergrid/descricao_ASC/startgrid/260",
    "https://sistemas.pm.al.gov.br/sistemas/public/sislegis/publico/index/dist/1484785043/perPagegrid/50/ordergrid/descricao_ASC/startgrid/1250",
    "https://sistemas.pm.al.gov.br/sistemas/public/sislegis/publico/index/id/1/dist/1495053443/ordergrid/link_externo_DESC/startgrid/260",
]

ATTRS = {
    "href", "src", "onclick", "action", "method", "value", "name", "id", "class",
    "data-url", "data-href", "data-id", "data-file", "data-arquivo", "formaction",
}

for page_url in URLS:
    print("\n=== PAGE", page_url, "===", flush=True)
    try:
        r = S.get(page_url, timeout=45, allow_redirects=True)
        print("STATUS", r.status_code, "FINAL", r.url, "CT", r.headers.get("content-type"), flush=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        candidates = []
        for node in soup.find_all(["tr", "div", "li"]):
            txt = node.get_text(" ", strip=True)
            if "37.042" in txt or "RDPMAL" in txt.upper() or "REGULAMENTO DISCIPLINAR DA POLÍCIA MILITAR" in txt.upper():
                candidates.append(node)
        print("CANDIDATES", len(candidates), flush=True)
        for i, node in enumerate(candidates[:8], 1):
            print(f"--- CANDIDATE {i} {node.name} ---", flush=True)
            print("TEXT", node.get_text(" ", strip=True)[:2500], flush=True)
            print("HTML", str(node)[:12000], flush=True)
            for el in node.find_all(True):
                vals = {k: v for k, v in (el.attrs or {}).items() if k in ATTRS}
                if vals:
                    print("EL", el.name, vals, flush=True)
                for val in (el.attrs or {}).values():
                    seq = val if isinstance(val, list) else [val]
                    for item in seq:
                        s = str(item)
                        if "37.042" in s or "arquivo" in s.lower() or "download" in s.lower() or ".pdf" in s.lower():
                            print("ATTR_HIT", el.name, vals, repr(s)[:2000], flush=True)
            for form in node.find_all_parent("form")[:3]:
                print("PARENT_FORM", form.attrs, str(form)[:10000], flush=True)
        html = r.text
        for pat in [r"[^\"'<>\s]{0,180}37[._-]?042[^\"'<>\s]{0,260}", r"[^\"'<>\s]{0,180}(?:arquivo|download)[^\"'<>\s]{0,260}"]:
            hits = re.findall(pat, html, flags=re.I)
            print("REGEX", pat, "HITS", len(hits), flush=True)
            for h in hits[:25]:
                print("HIT", h[:1000], flush=True)
        for a in soup.find_all("a", href=True):
            href = urljoin(r.url, a["href"])
            label = a.get_text(" ", strip=True)
            if any(x in (href + " " + label).lower() for x in ("arquivo", "download", "pdf", "37.042", "rdpm")):
                print("LINK", label[:300], href, flush=True)
    except Exception as exc:
        print("ERROR", type(exc).__name__, repr(exc), flush=True)
