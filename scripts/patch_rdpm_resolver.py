#!/usr/bin/env python3
from pathlib import Path
import re

path = Path(__file__).resolve().parent / "generate_full_law_reading.py"
s = path.read_text(encoding="utf-8")

# Article suffixes such as 197-A are attached to the number. A spaced dash in
# "Art. 25 - O..." starts the article body and must never become suffix "O".
# Official Planalto HTML can split a heading as "Art." + CR/LF + "45.";
# allow line breaks only in that whitespace slot.
target_art_line = r'''ART_RE = re.compile(r"(?mi)^[ \t]*(?:Art\.|Artigo)[ \t\r\n]*(\d+)(?:\.?[º°oO])?(?:[-–—‑]([A-Za-z]{1,3}))?(?=[ \t\r\n.]|$)")'''
lines = s.splitlines()
art_indexes = [i for i, line in enumerate(lines) if line.startswith("ART_RE = re.compile(")]
if len(art_indexes) != 1:
    raise SystemExit(f"ART_RE source lines={len(art_indexes)}; expected 1")
lines[art_indexes[0]] = target_art_line
s = "\n".join(lines) + ("\n" if s.endswith("\n") else "")

# Prefer the current official PMAL Sislegis copy for the Estatuto.
old_lei5346 = "https://sapl.al.al.leg.br/media/sapl/public/normajuridica/1992/845/845_texto_integral.pdf"
new_lei5346 = "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/download/id/892/param/2/set/2/get/2416565e/dist/"
if old_lei5346 in s:
    s = s.replace(old_lei5346, new_lei5346, 1)
elif new_lei5346 not in s:
    raise SystemExit("Fonte da Lei 5.346 não encontrada para atualização")

# Official government hosts can be intermittently unavailable from GitHub
# runners. Retry transport failures without weakening any content validation.
helper = r'''def http_get(url: str, timeout=(12,45), attempts: int=3):
    last=None
    for attempt in range(attempts):
        try:
            r=S.get(url,timeout=timeout,allow_redirects=True)
            r.raise_for_status()
            return r
        except requests.RequestException as exc:
            last=exc
            if attempt+1<attempts:
                time.sleep(1.5*(attempt+1))
    raise last

def fetch_html'''
if "def http_get(" not in s:
    s, helper_n = re.subn(r'def fetch_html', lambda _m: helper, s, count=1)
    if helper_n != 1:
        raise SystemExit("Não foi possível inserir http_get")

s = s.replace('r=S.get(url,timeout=45); r.raise_for_status(); enc=', 'r=http_get(url,timeout=(12,45)); enc=', 1)
s = s.replace('r=S.get(url,timeout=60); r.raise_for_status(); return clean_lines(', 'r=http_get(url,timeout=(12,60)); return clean_lines(', 1)

new_block = r'''def resolve_rdpm() -> tuple[str,str]:
    # Official PMAL Sislegis record for Decreto Estadual 37.042/1996 (RDPMAL).
    direct_urls=[
        "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/download/id/792/param/2/set/1/get/c8f191d3/dist/",
    ]
    listing_urls=[
        "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/id/1/ordergrid/descricao_ASC/startgrid/260",
        "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/index/ordergrid/descricao_ASC/startgrid/1250",
    ]

    def extract_document(url: str):
        rr=http_get(url,timeout=(12,60),attempts=3)
        ct=(rr.headers.get("content-type") or "").lower()
        if rr.content.startswith(b"%PDF") or "pdf" in ct or "save" in ct:
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
            r=http_get(page_url,timeout=(12,45),attempts=3); soup=BeautifulSoup(r.text,"html.parser")
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
ns, n = re.subn(pat, lambda _m: new_block, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f"resolver patch count={n}; expected 1")
path.write_text(ns, encoding="utf-8")
print("Official-source retries + PMAL state laws + article parser patched (v8)")
