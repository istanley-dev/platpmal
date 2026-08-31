#!/usr/bin/env python3
from pathlib import Path
import re

path = Path(__file__).resolve().parent / "generate_full_law_reading.py"
s = path.read_text(encoding="utf-8")

new_block = r'''def resolve_rdpm() -> tuple[str,str]:
    # Official PMAL Sislegis record for Decreto Estadual 37.042/1996 (RDPMAL).
    # The old sistemas.pm.al.gov.br hostname currently presents a TLS hostname
    # mismatch in GitHub runners, so use the current official central.pm.al.gov.br.
    direct_urls=[
        "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/download/id/792/param/2/set/1/get/c8f191d3/dist/",
    ]
    listing_urls=[
        "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/id/1/ordergrid/descricao_ASC/startgrid/260",
        "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/ordergrid/descricao_ASC/startgrid/1250",
    ]

    def extract_document(url: str):
        rr=S.get(url,timeout=60,allow_redirects=True); rr.raise_for_status()
        ct=(rr.headers.get("content-type") or "").lower()
        if rr.content.startswith(b"%PDF") or "pdf" in ct:
            from io import BytesIO
            from pypdf import PdfReader
            text=clean_lines("\n".join((p.extract_text() or "") for p in PdfReader(BytesIO(rr.content)).pages))
        else:
            text=clean_lines(BeautifulSoup(rr.text,"html.parser").get_text("\n"))
        arts=parse_articles(text)
        if all(str(n) in arts for n in (1,25,38,66,81,107)):
            return text,rr.url
        return None

    for url in direct_urls:
        try:
            found=extract_document(url)
            if found: return found
        except Exception:
            pass

    for page_url in listing_urls:
        try:
            r=S.get(page_url,timeout=45); r.raise_for_status(); soup=BeautifulSoup(r.text,"html.parser")
            for tr in soup.find_all("tr"):
                txt=tr.get_text(" ",strip=True)
                if "37.042" not in txt or "REGULAMENTO DISCIPLINAR" not in txt.upper():
                    continue
                links=[urljoin(r.url,a["href"]) for a in tr.find_all("a",href=True)]
                for found_url in re.findall(r"https?://[^\"'<> ]+",str(tr)):
                    links.append(found_url.replace("&amp;","&"))
                for link in dict.fromkeys(links):
                    try:
                        found=extract_document(link)
                        if found: return found
                    except Exception:
                        continue
        except Exception:
            continue
    raise RuntimeError("Não foi possível resolver/validar a fonte integral oficial do RDPMAL no PMAL Sislegis")

def select_range'''

pat = r'def resolve_rdpm\(\) -> tuple\[str,str\]:.*?\ndef select_range'
ns, n = re.subn(pat, new_block, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f"resolver patch count={n}; expected 1")
path.write_text(ns, encoding="utf-8")
print("RDPM resolver patched to current official PMAL source")
