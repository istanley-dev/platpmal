#!/usr/bin/env python3
import json
import re
from pathlib import Path

INDEX = Path("index.html")
REPORT = Path("comment-audit-report.json")
REPORT_LINES = Path("comment-audit-report.jsonl")

# O campo "c" é o comentário técnico principal. O campo "d" é apenas o resumo/bizu curto,
# então um "d" curto NÃO torna a questão deficiente.
WEAK_PATTERNS = {
    "manda consultar/revisar comentário externo": re.compile(r"(?:revise|revisar|consulte|consultar|verifique|verificar).{0,90}(?:coment[aá]rio|banca|material|fonte)", re.I),
    "placeholder jurisprudencial": re.compile(r"quest[aã]o jurisprudencial espec[ií]fica|mantenha a literalidade do gabarito", re.I),
    "placeholder factual de Alagoas": re.compile(r"item factual de alagoas|use a assertiva como ficha de memoriza[cç][aã]o", re.I),
    "orientação genérica sem resolver o item": re.compile(r"\b(?:revise a distin[cç][aã]o|verifique o regime jur[ií]dico|julgue conforme|revise o conceito|revise conceito|releia a regra|aten[cç][aã]o ao conceito)\b", re.I),
}

GENERIC_ONLY = re.compile(
    r"^\s*(?:gabarito oficial:\s*)?(?:certo|errado)[.!:]?\s*"
    r"(?:revise|revisar|verifique|consultar|consulte|aten[cç][aã]o|quest[aã]o|item factual)",
    re.I,
)


def iter_json_objects(text):
    decoder = json.JSONDecoder()
    for m in re.finditer(r'\{"id"\s*:', text):
        try:
            obj, _ = decoder.raw_decode(text[m.start():])
        except Exception:
            continue
        if isinstance(obj, dict):
            yield m.start(), obj


def reasons_for(q):
    reasons = []
    c = str(q.get("c") or "").strip()

    if not c:
        reasons.append("comentário técnico c ausente")
    elif len(c) < 45:
        reasons.append("comentário técnico c curto demais")

    for label, rx in WEAK_PATTERNS.items():
        if rx.search(c):
            reasons.append(label)

    if GENERIC_ONLY.search(c) and len(c) < 320:
        reasons.append("comentário é orientação genérica, não explicação")

    return list(dict.fromkeys(reasons))


def main():
    text = INDEX.read_text(encoding="utf-8")
    questions = []
    seen = set()

    for pos, q in iter_json_objects(text):
        if not {"id", "m", "a", "e", "g"}.issubset(q):
            continue
        key = (q.get("id"), q.get("e"), q.get("g"))
        if key in seen:
            continue
        seen.add(key)
        reasons = reasons_for(q)
        if not reasons:
            continue
        questions.append({
            "id": q.get("id"),
            "materia": q.get("m"),
            "assunto": q.get("a"),
            "gabarito": q.get("g"),
            "enunciado": q.get("e"),
            "comentario": q.get("c"),
            "detalhamento": q.get("d"),
            "fundamento": q.get("f"),
            "criterio_erro": q.get("ce"),
            "fonte": q.get("src"),
            "motivos_auditoria": reasons,
            "posicao_no_html": pos,
        })

    by_matter = {}
    for q in questions:
        by_matter[q["materia"]] = by_matter.get(q["materia"], 0) + 1

    payload = {
        "schema": 2,
        "descricao": "Auditoria do campo c (comentário técnico principal). O campo d é resumo curto e não é penalizado. Nenhum gabarito é alterado.",
        "total_suspeitos": len(questions),
        "por_materia": dict(sorted(by_matter.items(), key=lambda kv: (-kv[1], kv[0] or ""))),
        "questoes": questions,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_LINES.write_text("".join(json.dumps(q, ensure_ascii=False, separators=(",", ":")) + "\n" for q in questions), encoding="utf-8")
    print(f"Auditoria concluída: {len(questions)} questão(ões) com comentário principal suspeito.")
    for matter, count in payload["por_materia"].items():
        print(f"  {matter}: {count}")


if __name__ == "__main__":
    main()
