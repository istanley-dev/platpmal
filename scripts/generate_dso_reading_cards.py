#!/usr/bin/env python3
"""Generate exact, structured daily article cards for the 65-day DSO law plan.

This intentionally reuses the audited official-source fetch/parsing functions from
`generate_full_law_reading.py`, but writes JSON where each selected article is an
explicit object. The browser therefore never has to infer article boundaries from
plain text (where internal references such as "Art. 29" could be mistaken for a
new card).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import generate_full_law_reading as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "law-reading"
OUT.mkdir(exist_ok=True)


def source_text(prefix: str):
    if prefix == "RD":
        text, url = base.resolve_rdpm()
        return "Decreto Estadual 37.042/1996 — RDPMAL", url, "official_pm_al", text
    title, url, kind = base.SOURCES[prefix]
    text = base.fetch_pdf_text(url) if kind == "pdf" else base.fetch_html(url)
    return title, url, kind, text


def main():
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
        for prefix, lo, hi in segs:
            selected = base.select_range(cache[prefix], lo, hi)
            if not selected:
                failures.append(f"C{cycle}D{day} {prefix} {lo}-{hi}: vazio")
                continue

            if lo != "*":
                keys = {k for k, _ in selected}
                for boundary in (lo, hi):
                    norm = boundary.replace("-", "").replace("–", "").replace("—", "").replace("‑", "").upper()
                    if norm not in keys:
                        failures.append(f"C{cycle}D{day} {prefix}: limite {boundary} ausente")

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

        if failures:
            continue

        payload = {
            "version": 4,
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

    # Exact structured audit: count JSON article objects, not textual references.
    for entry in manifest["days"]:
        data = json.loads((ROOT / entry["path"]).read_text(encoding="utf-8"))
        exact = sum(len(s.get("articles", [])) for s in data.get("sections", []))
        if exact != entry["articleCount"]:
            raise RuntimeError(f"{entry['path']}: manifesto={entry['articleCount']} json={exact}")

    print(f"OK: {len(manifest['days'])} dias DSO estruturados em cartões de artigo", flush=True)


if __name__ == "__main__":
    main()
