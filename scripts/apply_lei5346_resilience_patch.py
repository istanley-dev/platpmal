#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parent / "generate_dso_reading_cards.py"
s = path.read_text(encoding="utf-8")

if "def fetch_current_lei5346()" in s:
    print("Lei 5.346 resilience patch already applied")
    raise SystemExit(0)

old_const = 'PMAL_LEI5346 = "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/download/id/892/param/2/set/2/get/2416565e/dist/"\n'
new_const = old_const + 'ALE_LEI5346 = "https://sapl.al.al.leg.br/media/sapl/public/normajuridica/1992/845/845_texto_integral.pdf"\n'
if old_const not in s:
    raise SystemExit("PMAL_LEI5346 constant not found")
s = s.replace(old_const, new_const, 1)

marker = "\ndef source_text(prefix: str):\n"
if marker not in s:
    raise SystemExit("source_text marker not found")

helpers = r'''
def fetch_pdf_text_attempts(url: str, attempts: int) -> str:
    from io import BytesIO
    from pypdf import PdfReader
    r = base.http_get(url, timeout=(10, 60), attempts=attempts)
    return base.clean_lines("\n".join((p.extract_text() or "") for p in PdfReader(BytesIO(r.content)).pages))


def validate_current_lei5346(text: str) -> dict[str, str]:
    articles = parse_articles_exact(text)
    required = ("1", "14", "30", "51", "52", "54", "88", "104", "105", "135")
    missing = [k for k in required if k not in articles]
    if missing:
        raise RuntimeError(f"Lei 5.346: fonte sem limites/artigos necessários {missing}")

    # Currentness guards based on Lei 9.381/2024: art. 51 uses age 67 and
    # art. 54 uses age 72. A pre-2024 consolidated copy must never be published.
    a51 = articles["51"].lower()
    a54 = articles["54"].lower()
    if "67" not in a51 or "72" not in a54:
        raise RuntimeError("Lei 5.346: fonte acessível, porém não reflete a atualização de 2024 nos arts. 51/54")
    return articles


def fetch_current_lei5346() -> tuple[str, str, str]:
    errors = []
    candidates = [
        ("official_pm_al", PMAL_LEI5346, 8),
        ("official_ale_al", ALE_LEI5346, 3),
    ]
    for kind, url, attempts in candidates:
        try:
            text = fetch_pdf_text_attempts(url, attempts)
            validate_current_lei5346(text)
            print(f"Lei5346: fonte vigente validada via {kind}", flush=True)
            return text, url, kind
        except Exception as exc:
            errors.append(f"{kind}: {type(exc).__name__}: {exc}")
            print(f"Lei5346: {kind} indisponível ou desatualizada; tentando próxima fonte", flush=True)
    raise RuntimeError("Lei 5.346: nenhuma fonte oficial vigente pôde ser validada | " + " | ".join(errors))
'''
s = s.replace(marker, helpers + marker, 1)

old_branch = '''    if prefix == "Lei5346":\n        url = PMAL_LEI5346\n        text = official_pdf_with_proxy(prefix, url)\n        return title, url, "official_pm_al", text\n'''
new_branch = '''    if prefix == "Lei5346":\n        text, url, source_kind = fetch_current_lei5346()\n        return title, url, source_kind, text\n'''
if old_branch not in s:
    raise SystemExit("Lei5346 source branch not found")
s = s.replace(old_branch, new_branch, 1)

path.write_text(s, encoding="utf-8")
print("Applied resilient/current Lei 5.346 source patch")
