#!/usr/bin/env python3
from __future__ import annotations

import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (PMAL study platform law source diagnostics; +https://github.com/istanley-dev/platpmal)"
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})

URLS = [
    "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/dist/1770415952/startgrid/660",
    "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/param/2/perPagegrid/50/ordergrid/titulo_ASC/startgrid/400",
    "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/startgrid/10/perPagegrid/50",
]

for page_url in URLS:
    print("\n===", page_url, "===", flush=True)
    try:
        r=S.get(page_url,timeout=45,allow_redirects=True)
        print("STATUS",r.status_code,"FINAL",r.url,flush=True)
        r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser")
        rows=[]
        for tr in soup.find_all("tr"):
            txt=tr.get_text(" ",strip=True)
            if "5.346" in txt and "POLICIAIS MILITARES" in txt.upper(): rows.append(tr)
        print("ROWS",len(rows),flush=True)
        for i,tr in enumerate(rows,1):
            print("ROW",i,tr.get_text(" ",strip=True)[:3000],flush=True)
            print("HTML",str(tr)[:15000],flush=True)
            for a in tr.find_all("a",href=True):
                print("LINK",a.get_text(" ",strip=True),urljoin(r.url,a["href"]),flush=True)
            for el in tr.find_all(True):
                for k,v in (el.attrs or {}).items():
                    vals=v if isinstance(v,list) else [v]
                    for item in vals:
                        s=str(item)
                        if any(x in s.lower() for x in ("download","arquivo","pdf","5346","5.346")):
                            print("ATTR",el.name,k,repr(s)[:2000],flush=True)
    except Exception as exc:
        print("ERROR",type(exc).__name__,repr(exc),flush=True)
