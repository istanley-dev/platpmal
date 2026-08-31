#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parent/'generate_dso_reading_cards.py'
s=p.read_text(encoding='utf-8')
old='''    if n!=1:\n        raise RuntimeError(f"Lei 5.346: não foi possível consolidar {label}")\n    return base.clean_lines(new)\n'''
new='''    if n!=1:\n        # Official PMAL and ALE base copies are not identical. The PMAL copy may\n        # already have judicially-invalid Lei 7.657 text removed, while ALE still\n        # displays it. Treat an already-correct art. 7 as idempotent, but keep all\n        # other consolidation misses fatal.\n        if label == "art. 7, antigo inciso VIII da Lei 7.657/2014" and "Os efeitos gerados pela alteração prevista" not in block:\n            return base.clean_lines(block)\n        if label == "art. 7 §1º II" and "Cadete" in block and "30 (trinta" in block:\n            return base.clean_lines(block)\n        if label == "art. 7 §1º III" and "Soldado" in block and "30 (trinta" in block:\n            return base.clean_lines(block)\n        raise RuntimeError(f"Lei 5.346: não foi possível consolidar {label}")\n    return base.clean_lines(new)\n'''
if old not in s:
    raise SystemExit('helper _replace_span esperado não encontrado')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Applied idempotent Lei 5.346 consolidation hotfix')
