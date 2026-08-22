#!/usr/bin/env python3
import json
import re
from pathlib import Path

INDEX = Path("index.html")
FIX_DIR = Path("comment-fixes")


def load_fixes():
    fixes = {}
    for path in sorted(FIX_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise SystemExit(f"{path}: esperado array JSON")
        for item in data:
            qid = item.get("id")
            if not qid:
                raise SystemExit(f"{path}: correção sem id")
            if qid in fixes:
                raise SystemExit(f"ID duplicado nas correções: {qid}")
            fixes[qid] = item
    if not fixes:
        raise SystemExit("Nenhuma correção encontrada")
    return fixes


def patch_questions(text, fixes):
    decoder = json.JSONDecoder()
    replacements = []
    found = set()
    occurrences = 0

    for m in re.finditer(r'\{"id"\s*:', text):
        start = m.start()
        try:
            obj, size = decoder.raw_decode(text[start:])
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        qid = obj.get("id")
        if qid not in fixes:
            continue
        # Só trata objetos que têm a estrutura de questão.
        if not {"id", "m", "a", "e", "g"}.issubset(obj):
            continue

        fix = fixes[qid]
        expected_g = fix.get("expected_g")
        if expected_g and obj.get("g") != expected_g:
            raise SystemExit(
                f"ABORTADO: {qid} deveria ter gabarito {expected_g}, "
                f"mas o index contém {obj.get('g')}. Nenhum gabarito será alterado."
            )

        original_e = obj.get("e")
        original_g = obj.get("g")
        for field in ("c", "d", "f", "p"):
            if field in fix:
                obj[field] = fix[field]

        if obj.get("e") != original_e or obj.get("g") != original_g:
            raise SystemExit(f"ABORTADO: tentativa de alterar enunciado/gabarito em {qid}")

        new_raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        replacements.append((start, start + size, new_raw))
        found.add(qid)
        occurrences += 1

    missing = sorted(set(fixes) - found)
    if missing:
        raise SystemExit("IDs de correção não encontrados no index: " + ", ".join(missing))

    # Substitui de trás para frente para preservar os offsets capturados.
    for start, end, new_raw in sorted(replacements, reverse=True):
        text = text[:start] + new_raw + text[end:]

    return text, occurrences


def patch_ai_generator(text):
    marker = "PMAL_COMMENT_GATE_V1"
    if marker in text:
        return text, False

    old_prompt = '- Todos os campos são obrigatórios e devem ter conteúdo substancial`;'
    new_prompt = '''- Todos os campos são obrigatórios e devem ter conteúdo substancial
- O campo "c" deve ter NO MÍNIMO 120 caracteres e funcionar como uma mini-explicação: diga expressamente por que o gabarito é CERTO ou ERRADO e aplique a regra, fato ou conceito ao enunciado.
- Se o gabarito for ERRADO, "c" deve identificar precisamente o trecho/ideia que torna a assertiva errada e apresentar a regra, dado ou formulação correta.
- Se o gabarito for CERTO, "c" deve explicar qual regra, fato ou conceito confirma a assertiva; citar apenas um artigo não basta.
- É PROIBIDO substituir a explicação por instruções como "revise", "consulte", "verifique", "veja o comentário da banca", "mantenha a literalidade" ou mandar o aluno buscar a resposta fora da plataforma.
- "p", "f" e "d" também devem vir preenchidos: pegadinha concreta, fundamento pertinente e bizu/resumo respectivamente`;'''
    if old_prompt not in text:
        raise SystemExit("Não encontrei o marcador final do prompt da IA para instalar a trava")
    text = text.replace(old_prompt, new_prompt, 1)

    old_check = "if(!Array.isArray(newQs)||newQs.length===0)throw new Error('A IA não retornou questões. Tente novamente.');"
    new_check = """if(!Array.isArray(newQs)||newQs.length===0)throw new Error('A IA não retornou questões. Tente novamente.');
    // PMAL_COMMENT_GATE_V1 — impede comentário-placeholder de entrar no banco gerado por IA.
    const weakCommentRx=/(?:\\brev(?:ise|isar)\\b|\\bconsulte?\\b|\\bverifique\\b|coment[aá]rio da banca|mantenha a literalidade|busque? (?:na|o) (?:banca|material|fonte))/i;
    const validGeneratedQuestion=q=>{
      if(!q||!q.e||!q.g||!q.m||!['CERTO','ERRADO'].includes(q.g))return false;
      if(typeof q.c!=='string'||q.c.trim().length<120||weakCommentRx.test(q.c))return false;
      if(typeof q.p!=='string'||q.p.trim().length<20)return false;
      if(typeof q.f!=='string'||q.f.trim().length<8)return false;
      if(typeof q.d!=='string'||q.d.trim().length<15)return false;
      return true;
    };
    const rejectedWeak=newQs.filter(q=>!validGeneratedQuestion(q)).length;
    newQs=newQs.filter(validGeneratedQuestion);
    if(newQs.length===0)throw new Error('A IA respondeu, mas nenhuma questão passou na validação de comentário técnico. Gere novamente.');"""
    if old_check not in text:
        raise SystemExit("Não encontrei a validação do array gerado pela IA para instalar a trava")
    text = text.replace(old_check, new_check, 1)

    old_toast = "toast('✨ '+added+' novas questões geradas e adicionadas ao banco!');"
    new_toast = "toast('✨ '+added+' novas questões geradas e adicionadas ao banco!'+(rejectedWeak?' · '+rejectedWeak+' rejeitada(s) por comentário técnico fraco.':''));"
    if old_toast not in text:
        raise SystemExit("Não encontrei o toast da geração de IA para registrar rejeições")
    text = text.replace(old_toast, new_toast, 1)

    return text, True


def main():
    fixes = load_fixes()
    if len(fixes) != 85:
        raise SystemExit(f"Esperadas 85 correções auditadas; encontrei {len(fixes)}")

    original = INDEX.read_text(encoding="utf-8")
    patched, occurrences = patch_questions(original, fixes)
    patched, gate_installed = patch_ai_generator(patched)

    if patched == original:
        print("Nenhuma alteração necessária; index já corrigido.")
        return

    INDEX.write_text(patched, encoding="utf-8")
    print(f"Aplicadas correções em {occurrences} ocorrência(s) para {len(fixes)} IDs auditados.")
    print("Enunciados e gabaritos preservados por validação.")
    print("Trava do gerador IA instalada." if gate_installed else "Trava do gerador IA já estava instalada.")


if __name__ == "__main__":
    main()
