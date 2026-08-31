#!/usr/bin/env python3
"""Build a static, repository-backed integral law bank for the 65-day DSO plan.

This is a maintenance/build tool only. The published site never downloads laws at
runtime: it reads the committed law-reading/ JSON files.
"""
from __future__ import annotations

import json
import re
import time
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

import generate_full_law_reading as base
import generate_dso_reading_cards as dyn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "law-reading"
OUT.mkdir(exist_ok=True)

PMAL_LEI5346 = "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/download/id/892/param/2/set/2/get/2416565e/dist/"


def fetch_pmal_lei5346() -> str:
    """Require the newer PMAL base copy; amendments below are then applied article-by-article."""
    last = None
    for attempt in range(10):
        try:
            r = base.http_get(PMAL_LEI5346, timeout=(12, 75), attempts=1)
            reader = PdfReader(BytesIO(r.content))
            text = base.clean_lines("\n".join((p.extract_text() or "") for p in reader.pages))
            arts = dyn.parse_articles_exact(text)
            if len(arts) < 120 or not {"1", "7", "51", "54", "118", "135"}.issubset(arts):
                raise RuntimeError(f"cópia PMAL incompleta: {len(arts)} artigos reconhecidos")
            return text
        except Exception as exc:
            last = exc
            if attempt < 9:
                time.sleep(min(2 + attempt, 8))
    raise RuntimeError(f"Lei 5.346: não foi possível carregar a base oficial PMAL: {last}")


def _replace_current_item(block: str, roman: str, replacement: str, next_roman: str) -> str:
    pat = re.compile(
        rf"(?ms)(^|\n)({re.escape(roman)}\s*[–—-]\s*.*?)(?=\n{re.escape(next_roman)}\s*[–—-])"
    )
    new, n = pat.subn(lambda m: m.group(1) + replacement, block, count=1)
    if n != 1:
        raise RuntimeError(f"Lei 5.346: não foi possível substituir inciso {roman}")
    return base.clean_lines(new)


def consolidate_lei5346(arts: dict[str, str]) -> dict[str, str]:
    """Apply only enacted/current changes missing from the PMAL consolidated PDF.

    Sources incorporated:
    - TJAL ADI 0801346-70.2014.8.02.0000: Lei 7.657/2014 unconstitutional ex tunc.
    - Lei 8.409/2021: art. 7 VIII-X and art. 134-A.
    - Lei 9.381/2024: arts. 51, 54 and 118.
    """
    out = dict(arts)

    # Art. 7: remove the invalid Lei 7.657/2014 insertion if the base still prints it.
    a7 = out["7"]
    a7 = re.sub(
        r"(?ms)\nVIII\s*[–—-]\s*Os efeitos gerados pela alteração prevista.*?(?=\n§\s*1[º°oO]?)",
        "",
        a7,
        count=1,
    )
    # Ex-tunc restoration of the previous valid Cadete limit (Lei 6.803/2007).
    a7 = re.sub(
        r"(?i)II\s*[–—-]\s*Cadete\s*[–—-]\s*(?:de\s*)?18\s*\(dezoito\)\s*a\s*40\s*\(quarenta\)\s*anos\s*;?",
        "II – Cadete – 18 (dezoito) a 30 (trinta) anos;",
        a7,
        count=1,
    )
    a7 = re.sub(
        r"(?is)\s*\(Redação dada pela Lei nº\s*7\.657,\s*de\s*10\.09\.2014\)\.?",
        "",
        a7,
        count=1,
    )
    if "possuir aptidão psicológica" not in a7.lower():
        additions = (
            "\nVIII – possuir aptidão psicológica para o preenchimento da vaga, aferida por meio de avaliação psicológica de caráter eliminatório;"
            "\nIX – atestar, por exame toxicológico de larga janela de detecção, que não utiliza droga ilícita; e"
            "\nX – o exame toxicológico constituirá a última etapa do concurso, devendo ser exigido apenas aos candidatos aprovados em todas as etapas anteriores e classificados dentro do número de vagas, como requisito para a matrícula no respectivo curso de formação. (Acrescentados pela Lei nº 8.409/2021.)\n"
        )
        a7, n = re.subn(r"(?m)(^§\s*1[º°oO]?\b)", additions + r"\1", a7, count=1)
        if n != 1:
            raise RuntimeError("Lei 5.346: § 1º do art. 7 não localizado para inserir VIII-X")
    out["7"] = base.clean_lines(a7)

    # Art. 51: Lei 9.381/2024 replaced I and added II-A, II-B and §5º.
    a51 = _replace_current_item(
        out["51"],
        "I",
        "I – atingir a idade limite de 67 (sessenta e sete) anos; (Redação dada pela Lei nº 9.381/2024.)",
        "II",
    )
    if "II-A –" not in a51:
        ii_a = (
            "II-A – fica transferido, imediatamente, ex-officio, o Coronel QOEM (Quadro dos Oficiais do Estado Maior) que ocupar os cargos de Comandante Geral e Subcomandante Geral da Corporação quando exonerado dos referidos cargos para os quais foram nomeados e já possuírem o tempo mínimo de contribuição previdenciária;\n"
            "II-B – fica transferido, imediatamente, ex-officio, o oficial no último posto do quadro QOEM que completar 35 (trinta e cinco) anos de efetivo serviço, contados o tempo averbado, e o oficial do quadro QOE (Quadro de Oficiais Especialista) que completar 42 (quarenta e dois) anos de efetivo serviço, contados o tempo averbado;\n"
        )
        a51, n = re.subn(r"(?m)(^III\s*[–—-])", ii_a + r"\1", a51, count=1)
        if n != 1:
            raise RuntimeError("Lei 5.346: inciso III do art. 51 não localizado")
    if "§ 5º" not in a51 and "§ 5°" not in a51:
        a51 += (
            "\n§ 5º Não se aplica o contido no inciso II-B deste artigo, nos casos em que os oficiais ocuparem os cargos de Comandante Geral, Subcomandante Geral, Chefe da Assessoria Militar do Governador, Chefe da Assessoria Militar da Assembleia Legislativa, Chefe da Assessoria Militar do Tribunal de Justiça e Chefe da Assessoria Militar do Tribunal de Contas, assim como não se aplica o contido no inciso II-A, nos casos de, se houver, renomeação subsequente ao ato de exoneração, em um dos cargos previstos neste parágrafo. (Acrescentado pela Lei nº 9.381/2024.)"
        )
    out["51"] = base.clean_lines(a51)

    # Art. 54: current age is a single 72-year limit.
    out["54"] = _replace_current_item(
        out["54"],
        "I",
        "I – atingir a idade limite de 72 (setenta e dois) anos de idade; (Redação dada pela Lei nº 9.381/2024.)",
        "II",
    )

    # Art. 118: add the current third hypothesis before §1º.
    a118 = out["118"]
    if "III – ser sorteado para a função de Juiz Militar" not in a118:
        insertion = (
            "III – ser sorteado para a função de Juiz Militar, pelo Auditor Militar, com o cumprimento dos requisitos do art. 399 do Código de Processo Penal Militar. (Acrescentado pela Lei nº 9.381/2024.)\n"
        )
        a118, n = re.subn(r"(?m)(^§\s*1[º°oO]?\b)", insertion + r"\1", a118, count=1)
        if n != 1:
            raise RuntimeError("Lei 5.346: §1º do art. 118 não localizado")
    out["118"] = base.clean_lines(a118)

    out["134A"] = (
        "Art. 134-A. Aplica-se, supletiva e subsidiariamente, os dispositivos desta Lei ao Corpo de Bombeiros Militar de Alagoas. (Acrescentado pela Lei nº 8.409/2021.)"
    )

    # Hard guards: do not publish the known stale/invalid formulations.
    a7l = out["7"].lower()
    if "possuir aptidão psicológica" not in a7l or "exame toxicológico" not in a7l:
        raise RuntimeError("Lei 5.346 art. 7 não recebeu a Lei 8.409/2021")
    if "beneficiar os participantes do último concurso" in a7l:
        raise RuntimeError("Lei 5.346 art. 7 ainda contém dispositivo da Lei 7.657/2014 declarada inconstitucional")
    if not re.search(r"Cadete\s*[–—-]\s*(?:de\s*)?18\s*\(dezoito\)\s*a\s*30\s*\(trinta\)", out["7"], re.I):
        raise RuntimeError("Lei 5.346 art. 7 não restaurou o limite válido do Cadete")
    if "67 (sessenta e sete)" not in out["51"]:
        raise RuntimeError("Lei 5.346 art. 51 não reflete Lei 9.381/2024")
    if "72 (setenta e dois)" not in out["54"]:
        raise RuntimeError("Lei 5.346 art. 54 não reflete Lei 9.381/2024")
    if "Juiz Militar" not in out["118"]:
        raise RuntimeError("Lei 5.346 art. 118 não reflete Lei 9.381/2024")
    return out


def get_source(prefix: str):
    if prefix == "Lei5346":
        text = fetch_pmal_lei5346()
        return "Lei Estadual 5.346/1992 — Estatuto PMAL", PMAL_LEI5346, "static_official_pm_al_plus_enacted_amendments", text
    title, url, kind, text = dyn.source_text(prefix)
    return title, url, kind, text


def numeric_base(key: str) -> int:
    m = re.match(r"^(\d+)", key)
    if not m:
        raise ValueError(key)
    return int(m.group(1))


def expected_numeric_bases(lo: str, hi: str):
    if lo == "*" or not str(lo).isdigit() or not str(hi).isdigit():
        return None
    return set(range(int(lo), int(hi) + 1))


def main():
    prefixes = sorted({p for _, _, _, segs in base.PLAN for p, _, _ in segs})
    bank: dict[str, dict] = {}
    sources = {}

    for idx, prefix in enumerate(prefixes, 1):
        print(f"[{idx}/{len(prefixes)}] {prefix}", flush=True)
        title, url, kind, text = get_source(prefix)
        arts = dyn.parse_articles_exact(text)
        if prefix == "CPM" and "190" not in arts:
            recovered = dyn.recover_cpm190(url)
            if not recovered:
                raise RuntimeError("CPM art. 190 não recuperado")
            arts["190"] = recovered
        for (rp, key), notice in dyn.KNOWN_REVOKED.items():
            if rp == prefix and key not in arts:
                arts[key] = notice
        if prefix == "Lei5346":
            arts = consolidate_lei5346(arts)
        if not arts:
            raise RuntimeError(f"{prefix}: banco vazio")
        bank[prefix] = {"title": title, "sourceUrl": url, "kind": kind, "articles": arts}
        sources[prefix] = {"title": title, "url": url, "kind": kind, "articles": len(arts)}

    # Preserve CF permanent text only; dyn.source_text already scopes it before ADCT.
    if "18A" in bank["CF"]["articles"]:
        raise RuntimeError("CF: ADCT vazou para o banco permanente")

    for f in OUT.glob("c*-d*.json"):
        f.unlink()
    for f in OUT.glob("c*-d*.txt"):
        f.unlink()

    manifest = {
        "version": 5,
        "format": "static-integral-law-bank",
        "totalDays": len(base.PLAN),
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtimeNetworkRequired": False,
        "days": [],
        "sources": sources,
    }

    failures = []
    for cycle, day, label, segs in base.PLAN:
        sections = []
        total = 0
        for prefix, lo, hi in segs:
            arts = bank[prefix]["articles"]
            selected = base.select_range(arts, lo, hi)
            if not selected:
                failures.append(f"C{cycle}D{day} {prefix} {lo}-{hi}: vazio")
                continue
            keys = {k for k, _ in selected}
            if lo != "*":
                for boundary in (lo, hi):
                    norm = re.sub(r"[-–—‑\s]", "", boundary).upper()
                    if norm not in keys:
                        failures.append(f"C{cycle}D{day} {prefix}: limite {boundary} ausente")
                expected = expected_numeric_bases(lo, hi)
                if expected is not None:
                    present = {numeric_base(k) for k in keys}
                    missing = sorted(expected - present)
                    if missing:
                        failures.append(f"C{cycle}D{day} {prefix}: bases ausentes {missing[:25]}")
            cards = [{"key": k, "text": txt} for k, txt in selected]
            total += len(cards)
            sections.append({
                "prefix": prefix,
                "title": bank[prefix]["title"],
                "sourceUrl": bank[prefix]["sourceUrl"],
                "range": "texto integral da lei" if lo == "*" else f"arts. {lo} a {hi}",
                "articles": cards,
            })
        payload = {
            "version": 5,
            "format": "static-integral-law-bank",
            "cycle": cycle,
            "day": day,
            "label": label,
            "articleCount": total,
            "sections": sections,
        }
        path = OUT / f"c{cycle}-d{day:02d}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["days"].append({
            "cycle": cycle,
            "day": day,
            "label": label,
            "path": f"law-reading/{path.name}",
            "articleCount": total,
            "segments": segs,
        })

    if failures:
        raise RuntimeError("Falhas de cobertura:\n" + "\n".join(failures[:120]))
    if len(manifest["days"]) != 65:
        raise RuntimeError(f"dias gerados={len(manifest['days'])}, esperado=65")

    # Master internal bank. Daily payloads are materialized copies for fast/simple UI.
    master = {
        "version": 1,
        "format": "pmal-static-integral-bank",
        "description": "Banco interno de leitura integral usado pelo plano DSO; sem dependência de rede em runtime.",
        "laws": {
            p: {
                "title": x["title"],
                "sourceUrl": x["sourceUrl"],
                "kind": x["kind"],
                "articles": [{"key": k, "text": v} for k, v in sorted(x["articles"].items(), key=lambda kv: dyn.base.article_sort_key(kv[0]))],
            }
            for p, x in bank.items()
        },
    }
    (OUT / "bank.json").write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: banco integral estático criado; {len(manifest['days'])} dias DSO, {len(bank)} diplomas.", flush=True)


if __name__ == "__main__":
    main()
