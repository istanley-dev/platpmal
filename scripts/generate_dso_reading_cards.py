#!/usr/bin/env python3
"""Generate exact structured article cards for the 65-day DSO law plan."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import generate_full_law_reading as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "law-reading"
OUT.mkdir(exist_ok=True)


def scope_text(prefix: str, text: str) -> str:
    """Keep only the legal corpus targeted by the DSO range.

    The Planalto Constitution page contains the permanent Constitution followed by
    the ADCT. Both restart article numbering. DSO references such as CF art. 5º and
    CF arts. 18–36 refer to the permanent Constitution, so parsing must stop before
    the ADCT heading or later ADCT articles can overwrite the constitutional ones.
    """
    if prefix == "CF":
        markers = [
            r"(?i)ATO\s+DAS\s+DISPOSI[CÇ][OÕ]ES\s+CONSTITUCIONAIS\s+TRANSIT[OÓ]RIAS",
            r"(?i)ADCT\b",
        ]
        cuts = []
        for pat in markers:
            m = re.search(pat, text)
            if m:
                cuts.append(m.start())
        if cuts:
            text = text[:min(cuts)]
        # Safety: the permanent Constitution must still reach art. 250, while
        # ADCT-specific art. 18-A must not be present in the scoped text.
        if not re.search(r"(?mi)^\s*Art\.\s*250\b", text):
            raise RuntimeError("CF: recorte anterior ao ADCT não alcançou o art. 250")
        if re.search(r"(?mi)^\s*Art\.\s*18[-–—‑]A\b", text):
            raise RuntimeError("CF: conteúdo do ADCT vazou para a Constituição permanente")
    return text


def source_text(prefix: str):
    if prefix == "RD":
        text, url = base.resolve_rdpm()
        return "Decreto Estadual 37.042/1996 — RDPMAL", url, "official_pm_al", text
    title, url, kind = base.SOURCES[prefix]
    text = base.fetch_pdf_text(url) if kind == "pdf" else base.fetch_html(url)
    return title, url, kind, scope_text(prefix, text)


def expected_numeric_bases(lo: str, hi: str):
    if lo == "*" or not str(lo).isdigit() or not str(hi).isdigit():
        return None
    return set(range(int(lo), int(hi) + 1))


def numeric_base(key: str) -> int:
    m = re.match(r"^(\d+)", key)
    if not m:
        raise ValueError(key)
    return int(m.group(1))


def main():
    # Remove obsolete day payloads from previous formats in a clean, deterministic build.
    for old in OUT.glob("c*-d*.txt"):
        old.unlink()
    for old in OUT.glob("c*-d*.json"):
        old.unlink()

    prefixes = sorted({p for _, _, _, segs in base.PLAN for p, _, _ in segs})
    cache = {}
    sources = {}

    for idx, prefix in enumerate(prefixes, 1):
        print(f"[{idx}/{len(prefixes)}] {prefix}", flush=True)
        title, url, kind, text = source_text(prefix)
        articles = base.parse_articles(text)
        if not articles:
            raise RuntimeError(f"{prefix}: nenhum artigo reconhecido em {url}")
        cache[prefix] = articles
        sources[prefix] = {
            "title": title,
            "url": url,
            "kind": kind,
            "articles": len(articles),
        }
        time.sleep(.12)

    # Hard guard against the exact CF/ADCT collision found during audit.
    cf = cache.get("CF", {})
    if "5" not in cf or "18" not in cf or "36" not in cf:
        raise RuntimeError("CF: artigos permanentes esperados não foram reconhecidos")
    if "18A" in cf:
        raise RuntimeError("CF: art. 18-A do ADCT apareceu no corpus da Constituição")
    if "250" not in cf:
        raise RuntimeError("CF: corpus permanente terminou antes do art. 250")

    manifest = {
        "version": 4,
        "format": "structured-article-cards",
        "totalDays": len(base.PLAN),
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "days": [],
        "sources": sources,
    }
    failures = []

    for cycle, day, label, segs in base.PLAN:
        sections = []
        total = 0
        day_failures = []
        for prefix, lo, hi in segs:
            selected = base.select_range(cache[prefix], lo, hi)
            if not selected:
                day_failures.append(f"C{cycle}D{day} {prefix} {lo}-{hi}: vazio")
                continue

            keys = {k for k, _ in selected}
            if lo != "*":
                for boundary in (lo, hi):
                    norm = re.sub(r"[-–—‑\s]", "", boundary).upper()
                    if norm not in keys:
                        day_failures.append(f"C{cycle}D{day} {prefix}: limite {boundary} ausente")

                expected = expected_numeric_bases(lo, hi)
                if expected is not None:
                    present = {numeric_base(k) for k in keys}
                    missing_bases = sorted(expected - present)
                    if missing_bases:
                        day_failures.append(
                            f"C{cycle}D{day} {prefix}: artigos-base ausentes {missing_bases[:20]}"
                        )

            src = sources[prefix]
            range_label = "texto integral da lei" if lo == "*" else f"arts. {lo} a {hi}"
            cards = [{"key": k, "text": text} for k, text in selected]
            total += len(cards)
            sections.append({
                "prefix": prefix,
                "title": src["title"],
                "sourceUrl": src["url"],
                "range": range_label,
                "articles": cards,
            })

        if day_failures:
            failures.extend(day_failures)
            continue

        payload = {
            "version": 4,
            "format": "structured-article-cards",
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
        raise RuntimeError("Falhas de cobertura:\n" + "\n".join(failures[:100]))
    if len(manifest["days"]) != 65:
        raise RuntimeError(f"Foram gerados {len(manifest['days'])} dias, esperado 65")

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for entry in manifest["days"]:
        data = json.loads((ROOT / entry["path"]).read_text(encoding="utf-8"))
        exact = sum(len(s.get("articles", [])) for s in data.get("sections", []))
        if exact != entry["articleCount"]:
            raise RuntimeError(f"{entry['path']}: manifesto={entry['articleCount']} json={exact}")

    # Named content guards for the first day of each PDF cycle.
    c1d1 = json.loads((OUT / "c1-d01.json").read_text(encoding="utf-8"))
    cf5 = c1d1["sections"][0]["articles"][0]["text"]
    if "direitos e deveres individuais e coletivos" not in cf5.lower():
        raise RuntimeError("C1D1: art. 5º não parece ser o art. 5º da Constituição permanente")

    print(f"OK: {len(manifest['days'])} dias DSO estruturados em cartões de artigo", flush=True)


if __name__ == "__main__":
    main()
