#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parent / "generate_dso_reading_cards.py"
s = path.read_text(encoding="utf-8")

if "def consolidate_lei5346_articles(" in s:
    print("Lei 5.346 consolidation patch already applied")
    raise SystemExit(0)

old_const = 'PMAL_LEI5346 = "https://central.pm.al.gov.br/sistemas/public/sislegis/publico/download/id/892/param/2/set/2/get/2416565e/dist/"\n'
new_const = old_const + '''ALE_LEI5346 = "https://sapl.al.al.leg.br/media/sapl/public/normajuridica/1992/845/845_texto_integral.pdf"\nLEI8409_URL = "https://sapl.al.al.leg.br/media/sapl/public/normajuridica/2021/1993/lei_no_8.409_de_3_de_maio_de_2021.pdf"\nLEI9381_URL = "https://sapl.al.al.leg.br/media/sapl/public/normajuridica/2024/3159/lei_no_9.381_de_21_de_outubro_de_2024.pdf"\nADI7657_URL = "https://www2.tjal.jus.br/cposg5/search.do?cbPesquisa=NUMPROC&dePesquisaNuUnificado=0804610-59.2014.8.02.0000&foroNumeroUnificado=0000&numeroDigitoAnoUnificado=0804610-59.2014&paginaConsulta=1&tipoNuProcesso=UNIFICADO"\n'''
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


def fetch_lei5346_base() -> tuple[str, str, str]:
    """Fetch an official base copy; later enactments are overlaid explicitly."""
    errors=[]
    for kind,url,attempts in [
        ("official_pm_al_base", PMAL_LEI5346, 8),
        ("official_ale_al_base", ALE_LEI5346, 4),
    ]:
        try:
            text=fetch_pdf_text_attempts(url, attempts)
            arts=parse_articles_exact(text)
            required=("1","7","14","30","51","52","54","88","104","105","118","134","135")
            missing=[k for k in required if k not in arts]
            if missing:
                raise RuntimeError(f"base sem artigos {missing}")
            print(f"Lei5346: base oficial carregada via {kind}",flush=True)
            return text,url,kind
        except Exception as exc:
            errors.append(f"{kind}: {type(exc).__name__}: {exc}")
    raise RuntimeError("Lei 5.346: nenhuma base oficial pôde ser lida | "+" | ".join(errors))


def _replace_span(block: str, pattern: str, replacement: str, label: str) -> str:
    new,n=re.subn(pattern,replacement,block,count=1,flags=re.S|re.I)
    if n!=1:
        raise RuntimeError(f"Lei 5.346: não foi possível consolidar {label}")
    return base.clean_lines(new)


def consolidate_lei5346_articles(articles: dict[str,str]) -> dict[str,str]:
    """Consolidate official base with enacted post-base changes and binding ADI.

    Base PMAL/ALE PDFs are stale. This overlay applies only changes verified in:
    - TJAL ADI 0804610-59.2014.8.02.0000: Lei 7.657/2014 unconstitutional ex tunc;
    - Lei 8.409/2021: art. 7 VIII-X and art. 134-A;
    - Lei 9.381/2024: arts. 51 I, 51 II-A/II-B/§5, 54 I and 118 III.
    """
    out=dict(articles)

    # Art. 7: remove the unconstitutional Lei 7.657/2014 caput VIII and restore
    # Cadete/Soldado age limits from valid Lei 6.803/2007 (30 years).
    a7=out["7"]
    a7=_replace_span(
        a7,
        r"\nVIII\s*[–—-]\s*Os efeitos gerados pela alteração prevista.*?(?=\n§\s*1[º°])",
        "\n",
        "art. 7, antigo inciso VIII da Lei 7.657/2014",
    )
    a7=_replace_span(
        a7,
        r"(§\s*1[º°].*?I\s*[–—-].*?)(\nII\s*[–—-].*?)(?=\nIII\s*[–—-])",
        lambda m: m.group(1)+"\nII – Cadete – 18 (dezoito) a 30 (trinta) anos; (Redação vigente da Lei nº 6.803, de 14.02.2007; Lei nº 7.657/2014 declarada inconstitucional com efeitos ex tunc.)",
        "art. 7 §1º II",
    )
    a7=_replace_span(
        a7,
        r"\nIII\s*[–—-].*?(?=\n§\s*2[º°])",
        "\nIII – Soldado – 18 (dezoito) a 30 (trinta) anos. (Redação vigente da Lei nº 6.803, de 14.02.2007; Lei nº 7.657/2014 declarada inconstitucional com efeitos ex tunc.)",
        "art. 7 §1º III",
    )
    # Lei 8.409/2021: insert current VIII-X immediately before §1º.
    insert_8409=(
        "\nVIII – possuir aptidão psicológica para o preenchimento da vaga, aferida por meio de avaliação psicológica de caráter eliminatório;"
        "\nIX – atestar, por exame toxicológico de larga janela de detecção, que não utiliza droga ilícita; e"
        "\nX – o exame toxicológico constituirá a última etapa do concurso, devendo ser exigido apenas aos candidatos aprovados em todas as etapas anteriores e classificados dentro do número de vagas, como requisito para a matrícula no respectivo curso de formação. (Acrescidos pela Lei nº 8.409, de 3 de maio de 2021.)\n"
    )
    a7=a7.replace("\n§ 1º",insert_8409+"§ 1º",1)
    if "VIII – possuir aptidão psicológica" not in a7 or "X – o exame toxicológico" not in a7:
        raise RuntimeError("Lei 5.346: falha ao aplicar Lei 8.409/2021 no art. 7")
    out["7"]=base.clean_lines(a7)

    # Lei 8.409/2021: art. 134-A.
    out["134A"]=(
        "Art. 134-A. Aplica-se, supletiva e subsidiariamente, os dispositivos desta Lei ao Corpo de Bombeiros Militar de Alagoas. "
        "(Acrescido pela Lei nº 8.409, de 3 de maio de 2021.)"
    )

    # Lei 9.381/2024: replace current age rule in art. 51, preserve remaining
    # provisions from the base, and add II-A, II-B and §5º.
    a51=out["51"]
    a51=_replace_span(
        a51,
        r"\nI\s*[–—-]\s*atingir.*?(?=\nII\s*[–—-])",
        "\nI – atingir a idade limite de 67 (sessenta e sete) anos; (Redação dada pela Lei nº 9.381, de 21 de outubro de 2024.)",
        "art. 51 I",
    )
    insertion_51=(
        "\nII-A – fica transferido, imediatamente, ex-officio, o Coronel QOEM (Quadro dos Oficiais do Estado Maior) que ocupar os cargos de Comandante Geral e Subcomandante Geral da Corporação quando exonerado dos referidos cargos para os quais foram nomeados e já possuírem o tempo mínimo de contribuição previdenciária;"
        "\nII-B – fica transferido, imediatamente, ex-officio, o oficial no último posto do quadro QOEM que completar 35 (trinta e cinco) anos de efetivo serviço, contados o tempo averbado, e o oficial do quadro QOE (Quadro de Oficiais Especialista) que completar 42 (quarenta e dois) anos de efetivo serviço, contados o tempo averbado; (Incisos II-A e II-B acrescidos pela Lei nº 9.381, de 21 de outubro de 2024.)\n"
    )
    if "II-A – fica transferido" not in a51:
        pos=re.search(r"\nIII\s*[–—-]",a51)
        if not pos:
            raise RuntimeError("Lei 5.346: art. 51 III não localizado para inserir II-A/II-B")
        a51=a51[:pos.start()]+insertion_51+a51[pos.start():]
    if "§ 5º Não se aplica o contido no inciso II-B" not in a51:
        a51 += (
            "\n§ 5º Não se aplica o contido no inciso II-B deste artigo, nos casos em que os oficiais ocuparem os cargos de Comandante Geral, Subcomandante Geral, Chefe da Assessoria Militar do Governador, Chefe da Assessoria Militar da Assembleia Legislativa, Chefe da Assessoria Militar do Tribunal de Justiça e Chefe da Assessoria Militar do Tribunal de Contas, assim como não se aplica o contido no inciso II-A, nos casos de, se houver, renomeação subsequente ao ato de exoneração, em um dos cargos previstos neste parágrafo. (Acrescido pela Lei nº 9.381, de 21 de outubro de 2024.)"
        )
    out["51"]=base.clean_lines(a51)

    # Lei 9.381/2024: art. 54 I = 72 years.
    a54=out["54"]
    a54=_replace_span(
        a54,
        r"\nI\s*[–—-]\s*atingir.*?(?=\nII\s*[–—-])",
        "\nI – atingir a idade limite de 72 (setenta e dois) anos de idade; (Redação dada pela Lei nº 9.381, de 21 de outubro de 2024.)",
        "art. 54 I",
    )
    out["54"]=base.clean_lines(a54)

    # Lei 9.381/2024: art. 118 III.
    a118=out["118"]
    if "III – ser sorteado para a função de Juiz Militar" not in a118:
        insert=(
            "\nIII – ser sorteado para a função de Juiz Militar, pelo Auditor Militar, com o cumprimento dos requisitos do art. 399 do Código de Processo Penal Militar. (Acrescido pela Lei nº 9.381, de 21 de outubro de 2024.)\n"
        )
        m=re.search(r"\n§\s*1[º°]",a118)
        if not m:
            raise RuntimeError("Lei 5.346: art. 118 §1º não localizado para inserir inciso III")
        a118=a118[:m.start()]+insert+a118[m.start():]
    out["118"]=base.clean_lines(a118)

    # Hard guards: never publish the stale or unconstitutional states again.
    guards={
        "7": ["VIII – possuir aptidão psicológica","IX – atestar, por exame toxicológico","Cadete – 18 (dezoito) a 30","Soldado – 18 (dezoito) a 30"],
        "51": ["67 (sessenta e sete)","II-A – fica transferido","II-B – fica transferido","§ 5º Não se aplica"],
        "54": ["72 (setenta e dois)"],
        "118": ["III – ser sorteado para a função de Juiz Militar"],
        "134A": ["Corpo de Bombeiros Militar de Alagoas"],
    }
    for key,needles in guards.items():
        for needle in needles:
            if needle.lower() not in out[key].lower():
                raise RuntimeError(f"Lei 5.346 consolidada: {key} não contém {needle!r}")
    if "Cadete – de 18 (dezoito) a 40" in out["7"] or "Os efeitos gerados pela alteração prevista" in out["7"]:
        raise RuntimeError("Lei 5.346 consolidada: redação inconstitucional da Lei 7.657/2014 ainda presente no art. 7")
    return out
'''
s = s.replace(marker, helpers + marker, 1)

old_branch = '''    if prefix == "Lei5346":\n        url = PMAL_LEI5346\n        text = official_pdf_with_proxy(prefix, url)\n        return title, url, "official_pm_al", text\n'''
new_branch = '''    if prefix == "Lei5346":\n        text, url, source_kind = fetch_lei5346_base()\n        return title, url, source_kind + "+consolidated_8409_9381_ADI7657", text\n'''
if old_branch not in s:
    raise SystemExit("Lei5346 source branch not found")
s = s.replace(old_branch, new_branch, 1)

old_hook = '''        articles = parse_articles_exact(text)\n        if prefix == "CPM" and "190" not in articles:\n'''
new_hook = '''        articles = parse_articles_exact(text)\n        if prefix == "Lei5346":\n            articles = consolidate_lei5346_articles(articles)\n            print("Lei5346: base oficial consolidada com ADI 7.657 + Leis 8.409/2021 e 9.381/2024", flush=True)\n        if prefix == "CPM" and "190" not in articles:\n'''
if old_hook not in s:
    raise SystemExit("main article parse hook not found")
s = s.replace(old_hook, new_hook, 1)

path.write_text(s, encoding="utf-8")
print("Applied Lei 5.346 legal consolidation patch")
