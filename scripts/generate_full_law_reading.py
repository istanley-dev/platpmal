#!/usr/bin/env python3
"""Generate the integral daily reading texts used by the PMAL DSO law cycles.

The DSO PDFs define *what range to read*. Federal text is refreshed from official
Planalto pages when this script runs. The Alagoas institutional texts are resolved
from official AL sources whenever possible. Output is split by day so mobile clients
only download today's reading.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "law-reading"
OUT.mkdir(exist_ok=True)

UA = "Mozilla/5.0 (PMAL study platform law reader; +https://github.com/istanley-dev/platpmal)"
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})

SOURCES = {
    "CF": ("Constituição Federal de 1988", "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm", "html"),
    "CP": ("Código Penal", "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm", "html"),
    "L14133": ("Lei 14.133/2021", "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm", "html"),
    "CADH": ("Convenção Americana sobre Direitos Humanos", "https://www.planalto.gov.br/ccivil_03/decreto/d0678.htm", "html"),
    "CPP": ("Código de Processo Penal", "https://www.planalto.gov.br/ccivil_03/decreto-lei/del3689compilado.htm", "html"),
    "LO": ("Lei 14.751/2023", "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14751.htm", "html"),
    "L7716": ("Lei 7.716/1989", "https://www.planalto.gov.br/ccivil_03/leis/l7716.htm", "html"),
    "L8072": ("Lei 8.072/1990", "https://www.planalto.gov.br/ccivil_03/leis/l8072.htm", "html"),
    "L13869": ("Lei 13.869/2019", "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/l13869.htm", "html"),
    "L10826": ("Lei 10.826/2003", "https://www.planalto.gov.br/ccivil_03/leis/2003/l10.826compilado.htm", "html"),
    "L12850": ("Lei 12.850/2013", "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12850.htm", "html"),
    "L9605": ("Lei 9.605/1998", "https://www.planalto.gov.br/ccivil_03/leis/l9605.htm", "html"),
    "L11340": ("Lei 11.340/2006", "https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2006/lei/l11340.htm", "html"),
    "L9455": ("Lei 9.455/1997", "https://www.planalto.gov.br/ccivil_03/leis/l9455.htm", "html"),
    "L7960": ("Lei 7.960/1989", "https://www.planalto.gov.br/ccivil_03/leis/l7960.htm", "html"),
    "L9099": ("Lei 9.099/1995", "https://www.planalto.gov.br/ccivil_03/leis/l9099.htm", "html"),
    "L11343": ("Lei 11.343/2006", "https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2006/lei/l11343.htm", "html"),
    "L10259": ("Lei 10.259/2001", "https://www.planalto.gov.br/ccivil_03/leis/leis_2001/l10259.htm", "html"),
    "CPM": ("Código Penal Militar", "https://www.planalto.gov.br/ccivil_03/decreto-lei/del1001compilado.htm", "html"),
    "CPPM": ("Código de Processo Penal Militar", "https://www.planalto.gov.br/ccivil_03/decreto-lei/del1002compilado.htm", "html"),
    "L8069": ("Estatuto da Criança e do Adolescente", "https://www.planalto.gov.br/ccivil_03/leis/l8069.htm", "html"),
    "L9503": ("Código de Trânsito Brasileiro", "https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm", "html"),
    "Lei5346": ("Lei Estadual 5.346/1992", "https://sapl.al.al.leg.br/media/sapl/public/normajuridica/1992/845/845_texto_integral.pdf", "pdf"),
}

PLAN = [
(1,1,"CF/88 — art. 5º",[("CF","5","5")]),(1,2,"CF/88 — arts. 6º a 11",[("CF","6","11")]),(1,3,"CF/88 — arts. 12 a 17",[("CF","12","17")]),(1,4,"CF/88 — arts. 18 a 36",[("CF","18","36")]),(1,5,"Código Penal — arts. 1º a 28",[("CP","1","28")]),(1,6,"CF/88 — arts. 136 a 144",[("CF","136","144")]),(1,7,"Lei 14.133/2021 — arts. 1º a 44",[("L14133","1","44")]),(1,8,"Lei 14.133/2021 — arts. 45 a 71",[("L14133","45","71")]),(1,9,"Lei 14.133/2021 — arts. 72 a 114",[("L14133","72","114")]),(1,10,"Lei 14.133/2021 — arts. 115 a 150",[("L14133","115","150")]),(1,11,"Lei 14.133/2021 — arts. 151 a 194",[("L14133","151","194")]),(1,12,"CADH — arts. 1º a 40",[("CADH","1","40")]),(1,13,"CADH — arts. 41 a 82",[("CADH","41","82")]),(1,14,"CPP — arts. 4º a 23",[("CPP","4","23")]),(1,15,"CPP — arts. 24 a 62",[("CPP","24","62")]),(1,16,"Lei 14.751/2023 — Lei Orgânica Nacional das PMs/CBMs",[("LO","*","*")]),(1,17,"Lei 7.716/1989 + Lei 8.072/1990 — racismo e crimes hediondos",[("L7716","*","*"),("L8072","*","*")]),(1,18,"Lei 13.869/2019 — Abuso de Autoridade",[("L13869","*","*")]),(1,19,"Lei 10.826/2003 — Estatuto do Desarmamento",[("L10826","*","*")]),(1,20,"Lei 12.850/2013 — Organização Criminosa",[("L12850","*","*")]),(1,21,"Lei 9.605/1998 — Crimes Ambientais",[("L9605","*","*")]),(1,22,"Lei 11.340/2006 — Maria da Penha",[("L11340","*","*")]),(1,23,"Lei 9.455/1997 + Lei 7.960/1989 — Tortura e Prisão Temporária",[("L9455","*","*"),("L7960","*","*")]),(1,24,"Lei 9.099/1995 — arts. 1º a 59",[("L9099","1","59")]),(1,25,"Lei 9.099/1995 — arts. 60 a 97",[("L9099","60","97")]),(1,26,"Lei 11.343/2006 — arts. 1º a 47",[("L11343","1","47")]),(1,27,"Lei 11.343/2006 — arts. 48 a 75",[("L11343","48","75")]),(1,28,"Lei 10.259/2001 — Juizados Especiais Federais",[("L10259","*","*")]),
(2,1,"CPM — arts. 1º a 12",[("CPM","1","12")]),(2,2,"CPPM — arts. 1º a 28",[("CPPM","1","28")]),(2,3,"CPM — arts. 13 a 25",[("CPM","13","25")]),(2,4,"CPPM — arts. 29 a 46",[("CPPM","29","46")]),(2,5,"CPM — arts. 26 a 29 e 48 a 68",[("CPM","26","29"),("CPM","48","68")]),(2,6,"CPPM — arts. 243 a 271",[("CPPM","243","271")]),(2,7,"CPM — arts. 69 a 108",[("CPM","69","108")]),(2,8,"CPPM — arts. 451 a 460",[("CPPM","451","460")]),(2,9,"CPM — arts. 109 a 135",[("CPM","109","135")]),(2,10,"ECA — arts. 1º a 32",[("L8069","1","32")]),(2,11,"ECA — arts. 33 a 73",[("L8069","33","73")]),(2,12,"CPM — arts. 136 a 194",[("CPM","136","194")]),(2,13,"CTB — arts. 1º a 73",[("L9503","1","73")]),(2,14,"CPM — arts. 195 a 253",[("CPM","195","253")]),(2,15,"CPM — arts. 254 a 310",[("CPM","254","310")]),(2,16,"CPM — arts. 311 a 354",[("CPM","311","354")]),(2,17,"ECA — arts. 74 a 109",[("L8069","74","109")]),(2,18,"CTB — arts. 74 a 129-B",[("L9503","74","129B")]),(2,19,"CTB — arts. 130 a 200",[("L9503","130","200")]),(2,20,"ECA — arts. 110 a 163",[("L8069","110","163")]),(2,21,"ECA — arts. 194 a 197",[("L8069","194","197")]),(2,22,"ECA — arts. 197-A a 224",[("L8069","197A","224")]),(2,23,"ECA — arts. 225 a 244-C",[("L8069","225","244C")]),(2,24,"CTB — arts. 201 a 268-A",[("L9503","201","268A")]),(2,25,"CTB — arts. 269 a 341",[("L9503","269","341")]),(2,26,"ECA — arts. 245 a 267",[("L8069","245","267")]),
(3,1,"Lei Estadual 5.346/1992 — arts. 1º a 14",[("Lei5346","1","14")]),(3,2,"Lei Estadual 5.346/1992 — arts. 15 a 30",[("Lei5346","15","30")]),(3,3,"Lei Estadual 5.346/1992 — arts. 31 a 52",[("Lei5346","31","52")]),(3,4,"Lei Estadual 5.346/1992 — arts. 53 a 88",[("Lei5346","53","88")]),(3,5,"Lei Estadual 5.346/1992 — arts. 89 a 104",[("Lei5346","89","104")]),(3,6,"Lei Estadual 5.346/1992 — arts. 105 a 135",[("Lei5346","105","135")]),(3,7,"Decreto Estadual 37.042/1996 — arts. 1º a 25",[("RD","1","25")]),(3,8,"Decreto Estadual 37.042/1996 — arts. 26 a 38",[("RD","26","38")]),(3,9,"Decreto Estadual 37.042/1996 — arts. 39 a 66",[("RD","39","66")]),(3,10,"Decreto Estadual 37.042/1996 — arts. 67 a 81",[("RD","67","81")]),(3,11,"Decreto Estadual 37.042/1996 — arts. 82 a 107",[("RD","82","107")]),]

ART_RE = re.compile(r"(?mi)^[ \t]*(?:Art\.|Artigo)[ \t]*(\d+)(?:[º°oO])?(?:[ \t]*[-–—‑][ \t]*([A-Za-z]{1,3}))?[ \t]*(?:[.º°])?(?=[ \t\n])")

def art_code(v: str) -> int:
    v = re.sub(r"[\s.º°oO\-–—‑]", "", str(v)).upper(); m = re.match(r"^(\d+)([A-Z]*)$", v)
    if not m: raise ValueError(v)
    suffix=0
    for ch in m.group(2): suffix=suffix*27+(ord(ch)-64)
    return int(m.group(1))*1000+suffix

def clean_lines(text: str) -> str:
    text=text.replace("\xa0"," ").replace("\u00ad",""); text=re.sub(r"[ \t]+"," ",text); text=re.sub(r" *\n *","\n",text); text=re.sub(r"\n{3,}","\n\n",text); return text.strip()

def parse_articles(text: str) -> dict[str,str]:
    text=clean_lines(text); ms=list(ART_RE.finditer(text)); out={}
    for i,m in enumerate(ms):
        key=m.group(1)+((m.group(2) or "").upper()); end=ms[i+1].start() if i+1<len(ms) else len(text); block=clean_lines(text[m.start():end])
        if len(block)>=15: out[key]=block
    return out

def fetch_html(url: str) -> str:
    r=S.get(url,timeout=45); r.raise_for_status(); enc=r.apparent_encoding or r.encoding or "latin-1"
    try: html=r.content.decode(enc,errors="replace")
    except LookupError: html=r.content.decode("latin-1",errors="replace")
    soup=BeautifulSoup(html,"html.parser")
    for tag in soup.find_all(["script","style","strike","s","del"]): tag.decompose()
    for tag in soup.find_all(style=True):
        if "line-through" in str(tag.get("style","")).lower(): tag.decompose()
    return clean_lines(soup.get_text("\n"))

def fetch_pdf_text(url: str) -> str:
    from io import BytesIO
    from pypdf import PdfReader
    r=S.get(url,timeout=60); r.raise_for_status(); return clean_lines("\n".join((p.extract_text() or "") for p in PdfReader(BytesIO(r.content)).pages))

def resolve_rdpm() -> tuple[str,str]:
    urls=["https://sistemas.pm.al.gov.br/sistemas/public/sislegis/publico/index/id/1/dist/1495053443/ordergrid/link_externo_DESC/startgrid/260","https://sistemas.pm.al.gov.br/sistemas/public/sislegis/publico/index/dist/1484785043/perPagegrid/50/ordergrid/descricao_ASC/startgrid/1250"]
    for page_url in urls:
        try:
            r=S.get(page_url,timeout=45); r.raise_for_status(); soup=BeautifulSoup(r.text,"html.parser"); target=None
            for tr in soup.find_all("tr"):
                txt=tr.get_text(" ",strip=True)
                if "37.042" in txt and "REGULAMENTO DISCIPLINAR" in txt.upper(): target=tr; break
            if not target: continue
            links=[urljoin(page_url,a["href"]) for a in target.find_all("a",href=True)]
            for found in re.findall(r"https?://[^\"'<> ]+",str(target)): links.append(found.replace("&amp;","&"))
            for link in dict.fromkeys(links):
                try:
                    rr=S.get(link,timeout=45,allow_redirects=True); rr.raise_for_status(); ct=(rr.headers.get("content-type") or "").lower()
                    if rr.content.startswith(b"%PDF") or "pdf" in ct:
                        from io import BytesIO
                        from pypdf import PdfReader
                        rd=clean_lines("\n".join((p.extract_text() or "") for p in PdfReader(BytesIO(rr.content)).pages))
                    else: rd=clean_lines(BeautifulSoup(rr.text,"html.parser").get_text("\n"))
                    arts=parse_articles(rd)
                    if all(str(n) in arts for n in (1,25,38,66,81,107)): return rd,rr.url
                except Exception: continue
        except Exception: continue
    raise RuntimeError("Não foi possível resolver uma fonte integral do RDPMAL no PMAL Sislegis")

def select_range(articles: dict[str,str],lo: str,hi: str):
    pairs=sorted(articles.items(),key=lambda kv:art_code(kv[0]))
    if lo=="*": return pairs
    a,b=art_code(lo),art_code(hi); return [(k,v) for k,v in pairs if a<=art_code(k)<=b]

def main():
    cache={}; src_meta={}; prefixes=sorted({p for _,_,_,segs in PLAN for p,_,_ in segs})
    for idx,p in enumerate(prefixes,1):
        print(f"[{idx}/{len(prefixes)}] {p}",flush=True)
        if p=="RD": text,url=resolve_rdpm(); title="Decreto Estadual 37.042/1996 — RDPMAL"; kind="official_pm_al"
        else:
            title,url,kind=SOURCES[p]; text=fetch_pdf_text(url) if kind=="pdf" else fetch_html(url)
        arts=parse_articles(text)
        if not arts: raise RuntimeError(f"{p}: nenhum artigo reconhecido em {url}")
        cache[p]=arts; src_meta[p]={"title":title,"url":url,"kind":kind,"articles":len(arts)}; time.sleep(.15)
    missing=[]
    for cycle,day,label,segs in PLAN:
        for p,lo,hi in segs:
            selected=select_range(cache[p],lo,hi)
            if not selected: missing.append(f"C{cycle}D{day} {p} {lo}-{hi}: vazio"); continue
            if lo!="*":
                keys={k for k,_ in selected}
                for boundary in (lo,hi):
                    norm=re.sub(r"[-–—‑]","",boundary).upper()
                    if norm not in keys: missing.append(f"C{cycle}D{day} {p}: limite {boundary} ausente")
    if missing: raise RuntimeError("Falhas de cobertura:\n"+"\n".join(missing[:80]))
    manifest={"version":3,"totalDays":len(PLAN),"generatedAt":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"days":[],"sources":src_meta}
    for cycle,day,label,segs in PLAN:
        sections=[]; article_count=0
        for p,lo,hi in segs:
            sel=select_range(cache[p],lo,hi); article_count+=len(sel); source=src_meta[p]; range_label="texto integral da lei" if lo=="*" else f"arts. {lo} a {hi}"; body="\n\n".join(v for _,v in sel); sections.append(f"{source['title']} — {range_label}\n\n{body}")
        text="\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n".join(sections).strip()+"\n"; path=OUT/f"c{cycle}-d{day:02d}.txt"; path.write_text(text,encoding="utf-8"); manifest["days"].append({"cycle":cycle,"day":day,"label":label,"path":f"law-reading/{path.name}","articleCount":article_count,"segments":segs})
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    pii=re.compile(r"istanley|gmail\.com|112[. ]*132[. ]*064|abra[aã]o barbosa canuto",re.I)
    for f in OUT.glob("c*-d*.txt"):
        if pii.search(f.read_text(encoding="utf-8")): raise RuntimeError(f"PII detectado em {f}")
    print(f"OK: {len(PLAN)} dias integrais gerados em {OUT}")

if __name__=="__main__": main()
