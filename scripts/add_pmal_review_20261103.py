"""Add the user's 03/11/2026 PMAL review items to the existing supplemental bank.

No interface, navigation, or review-flow changes are made.  The platform's
existing loader adds these items to QQ; confirmed errors are seeded into the
existing adaptive error review once, on the requested review date.
"""
from pathlib import Path
import json

BANK = Path("pmma-adapted-bank.js")
MARK = "PMAL_DAILY_REVIEW_20261103_V1"

def q(id, subject, topic, level, statement, answer, comment, trap, basis, tip, source, **extra):
    return {
        "id": id, "m": subject, "a": topic, "n": level, "e": statement,
        "g": answer, "c": comment, "p": trap, "f": basis, "d": tip,
        "ce": "conteúdo", "src": source, "real": 1, **extra,
    }

PENAL = "Direito Penal"
PORT = "Língua Portuguesa"
ORIG = "Questão original enviada pelo usuário — CEBRASPE"
NEW = "Questão inédita autoral — padrão CEBRASPE, 03/11/2026"

ITEMS = [
    q("USR_DP_MS_TEMPO_20261103", PENAL, "Medida de segurança — lei aplicável no tempo", "muito_dificil",
      "A medida de segurança não constitui pena, mas medida terapêutica ou pedagógica destinada aos inimputáveis e, excepcionalmente, aos semi-imputáveis, autores de fatos típicos e ilícitos. Dessa forma, rege-se a medida de segurança pela lei vigente ao tempo da sentença.", "CERTO",
      "Gabarito da questão histórica do CESPE/TJ-AC/2012: certo. À época da prova, o art. 75 do Código Penal, na redação então vigente, dispunha que a medida de segurança se regia pela lei do tempo da sentença, prevalecendo, se diversa, a lei vigente ao tempo da execução. A redação foi revogada pela reforma de 1984; portanto, a referência temporal é essencial e não deve ser generalizada como texto atual do CP.",
      "A pegadinha é responder como se a questão fosse sobre a redação atual do Código. O item é histórico e reproduz a regra do antigo art. 75.",
      "Código Penal, art. 75, redação anterior à Lei 7.209/1984; CESPE/TJ-AC/2012, item 90.",
      "Regra histórica do art. 75: sentença; se diversa, execução. Identifique a redação temporal da lei.", ORIG,
      banca="CESPE/CEBRASPE", ano=2012, gabaritoVerificado=1),
    q("USR_DP_MS_TEMPO_NOVA_20261103", PENAL, "Medida de segurança — sucessão de leis", "muito_dificil",
      "Em questão que reproduza o art. 75 do Código Penal na redação anterior à reforma de 1984, a afirmação de que a medida de segurança se rege pela lei vigente ao tempo da sentença, prevalecendo, se diversa, a lei vigente ao tempo da execução, corresponde à disciplina legal então expressa.", "CERTO",
      "O item delimita expressamente a redação histórica do art. 75 do CP, que continha essa regra. A reforma de 1984 revogou o dispositivo, razão pela qual sua assertiva só pode ser tomada como válida com a ressalva temporal indicada.",
      "A banca pode manter a regra e retirar a referência ao texto histórico, levando o candidato a projetá-la automaticamente sobre o Código atual.",
      "Código Penal, art. 75, redação anterior à Lei 7.209/1984.",
      "Antes de julgar regra revogada, confira se o enunciado é histórico ou pergunta pelo direito vigente.", NEW),

    q("USR_DP_LEGALIDADE_20261103", PENAL, "Princípio da legalidade — lei em sentido estrito", "muito_dificil",
      "O princípio da legalidade é parâmetro fixador do conteúdo das normas penais incriminadoras, ou seja, os tipos penais de tal natureza somente podem ser criados por meio de lei em sentido estrito.", "CERTO",
      "O item está correto: a reserva legal exige lei em sentido estrito para definir crimes e cominar penas. Atos infralegais podem, nos limites admitidos, complementar norma penal em branco, mas não criar autonomamente o núcleo incriminador nem instituir pena.",
      "Não confunda a possibilidade de complemento técnico de norma penal em branco com autorização para decreto criar crime ou pena.",
      "CF, art. 5.º, XXXIX; CP, art. 1.º.",
      "Crime e pena exigem lei anterior; complemento infralegal não pode criar o núcleo proibido.", ORIG,
      banca="CESPE/CEBRASPE", ano=2013, gabaritoVerificado=1),
    q("USR_DP_LEGALIDADE_NOVA_20261103", PENAL, "Legalidade — norma penal em branco e reserva legal", "muito_dificil",
      "A lei pode remeter a ato administrativo a especificação técnica de elemento de norma penal em branco, desde que o ato complementar não substitua a lei na definição do núcleo essencial da conduta proibida nem na cominação da pena.", "CERTO",
      "A reserva legal não impede toda complementação normativa. Admite-se complemento técnico quando o tipo legal fixa o núcleo essencial e a sanção; o ato infralegal não pode inovar autonomamente criando a incriminação ou agravando a pena.",
      "A armadilha está nos extremos: nem toda remissão é vedada, nem a remissão autoriza delegação irrestrita do poder de incriminar.",
      "CF, art. 5.º, XXXIX; CP, art. 1.º; doutrina sobre normas penais em branco.",
      "Verifique quem definiu o núcleo e quem fixou a pena.", NEW),

    q("USR_DP_EXTRA_ATIVIDADE_20261103", PENAL, "Lei penal no tempo — extra-atividade", "muito_dificil",
      "No que diz respeito ao tema lei penal no tempo, a regra é a aplicação da lei apenas durante o seu período de vigência; a exceção é a extra-atividade da lei penal mais benéfica, que comporta duas espécies: a retroatividade e a ultra-atividade.", "CERTO",
      "A lei penal, em regra, rege os fatos praticados durante sua vigência. A lei mais benéfica pode alcançar fatos anteriores (retroatividade) ou continuar aplicável a fatos praticados durante sua vigência mesmo depois de revogada (ultra-atividade), ressalvadas as particularidades das leis temporárias e excepcionais.",
      "Extra-atividade é gênero: retroatividade olha para trás; ultra-atividade conserva a lei revogada para fato ocorrido quando vigorava.",
      "CF, art. 5.º, XL; CP, art. 2.º e parágrafo único.",
      "Lei benéfica: retroage ou ultra-age; a lei mais grave não retroage.", ORIG,
      banca="CESPE/CEBRASPE", ano=2017, gabaritoVerificado=1),
    q("USR_DP_EXTRA_ATIVIDADE_NOVA_20261103", PENAL, "Retroatividade e ultra-atividade — lex mitior", "muito_dificil",
      "Se uma lei penal posterior mais benéfica entrar em vigor antes do trânsito em julgado, sua incidência sobre fato anterior constitui ultra-atividade, pois a lei nova passa a reger fato cometido sob a vigência da lei antiga.", "ERRADO",
      "A aplicação da lei posterior benéfica a fato anterior é retroatividade. Ultra-atividade ocorre quando a lei antiga, embora revogada, continua regendo o fato praticado enquanto ela estava em vigor, como pode ocorrer com lei excepcional ou temporária nos limites legais.",
      "O item troca os nomes das duas direções temporais; a data do fato e a data da lei favorável resolvem a classificação.",
      "CF, art. 5.º, XL; CP, art. 2.º, parágrafo único, e art. 3.º.",
      "Nova lei voltando ao fato passado = retroatividade.", NEW),

    q("USR_DP_TEMPO_CRIME_20261103", PENAL, "Tempo do crime — teoria da atividade e resultado posterior", "muito_dificil",
      "Em sete de janeiro de 2017, João praticou conduta que, à época, configurava crime punível com prisão. O resultado desejado pelo autor, no entanto, foi alcançado somente dois meses depois, ou seja, em sete de março do mesmo ano, momento no qual a conduta criminosa tinha previsão de ser punida com pena menos grave, de restrição de direitos. Nessa situação hipotética, de acordo com a lei penal, João não poderá ser condenado com a pena de prisão em razão da retroatividade da lei mais benéfica.", "CERTO",
      "O tempo do crime é o momento da ação ou omissão, ainda que o resultado ocorra depois (teoria da atividade, CP, art. 4.º). Como a lei posterior, vigente quando ocorreu o resultado, é mais benéfica, retroage ao fato anterior, afastando a sanção mais grave, conforme art. 2.º, parágrafo único, do CP.",
      "Não confunda o momento do resultado com o tempo do crime. A lei posterior é aplicada aqui por ser mais benéfica, não porque o resultado fixa o tempo do delito.",
      "CP, arts. 2.º, parágrafo único, e 4.º; questão CESPE/CEBRASPE, 2017.",
      "Tempo do crime = ação/omissão; lei posterior benéfica pode retroagir.", ORIG,
      banca="CESPE/CEBRASPE", ano=2017, gabaritoVerificado=1),
    q("USR_DP_TEMPO_CRIME_NOVA_20261103", PENAL, "Tempo do crime — sucessão de leis e resultado", "muito_dificil",
      "Se a ação foi praticada sob lei que previa pena mais branda e o resultado naturalístico somente ocorreu após lei que agravou a resposta penal, aplica-se, em regra, a lei vigente no momento do resultado, por ser esse o instante de consumação do crime material.", "ERRADO",
      "O art. 4.º do CP adota a teoria da atividade para determinar o tempo do crime: considera-se praticado no momento da ação ou omissão, ainda que outro seja o momento do resultado. A lei posterior mais grave não retroage. A consumação posterior não desloca, para esse fim, o tempo do crime.",
      "A banca mistura consumação, que pode depender do resultado, com tempo do crime, definido pela teoria da atividade.",
      "CP, arts. 2.º e 4.º; CF, art. 5.º, XL.",
      "Consumação pode ser posterior; tempo do crime continua na ação ou omissão.", NEW),

    q("USR_DP_LEGITIMA_DEFESA_REAL_20261103", PENAL, "Legítima defesa — impossibilidade de reciprocidade real", "muito_dificil",
      "No que diz respeito às excludentes de ilicitude previstas na legislação penal brasileira, é plenamente possível a ocorrência de legítima defesa real contra legítima defesa real. Nessas hipóteses, a lei autoriza que os dois envolvidos reajam reciprocamente para repelir a conduta um do outro, visto que o ordenamento jurídico admite a reação defensiva mútua quando ambos estão tentando proteger seus direitos contra agressões atuais ou iminentes.", "ERRADO",
      "Não há legítima defesa real recíproca quando cada agente efetivamente pratica agressão injusta contra o outro: a reação de um pode ser legítima, mas a agressão injusta do primeiro não se torna legítima defesa. É possível legítima defesa real contra agressão em legítima defesa putativa, ou contra excesso, conforme os fatos.",
      "O item toma a alegação subjetiva de ambos como suficiente e ignora que a legítima defesa real exige agressão injusta; duas agressões reais recíprocas não se legitimam mutuamente.",
      "CP, art. 25; distinção doutrinária entre legítima defesa real, putativa e excesso.",
      "Real contra real recíproca: incompatível; examine putativa ou excesso como exceções fáticas.", ORIG,
      banca="CESPE/CEBRASPE", gabaritoVerificado=1),
    q("USR_DP_LEGITIMA_DEFESA_NOVA_20261103", PENAL, "Legítima defesa — agressão injusta e excesso", "muito_dificil",
      "Em confronto iniciado por agressões injustas simultâneas, a circunstância de ambos os envolvidos alegarem que pretendiam proteger direito próprio basta para reconhecer legítima defesa real recíproca, ainda que cada um mantenha a agressão contra o outro.", "ERRADO",
      "A intenção defensiva declarada não substitui os requisitos objetivos do art. 25 do CP. É preciso agressão injusta, atual ou iminente, e uso moderado dos meios necessários. A legítima defesa real recíproca é incompatível com a existência simultânea de agressões injustas atribuíveis a ambos, sem prejuízo da análise de putatividade ou excesso.",
      "A banca tenta converter a finalidade subjetiva de proteger um direito em prova automática da injustiça da agressão alheia.",
      "CP, art. 25.",
      "Alegação de defesa não basta: teste agressão injusta, atual/iminente, necessidade e moderação.", NEW),

    q("USR_DP_ITER_CRIMINIS_NOVA_01_20261103", PENAL, "Desistência voluntária — atos já praticados", "muito_dificil",
      "Depois de iniciar a execução de um furto e ainda podendo prosseguir, o agente voluntariamente abandona a subtração antes de inverter a posse do bem. Nessa hipótese, responde pela tentativa de furto, pois a interrupção ocorreu após o início da execução.", "ERRADO",
      "Na desistência voluntária, o agente ainda podia prosseguir, mas voluntariamente interrompe a execução; responde somente pelos atos já praticados, se constituírem infração penal autônoma. O início da execução, isoladamente, não impõe a punição por tentativa quando incide o art. 15 do CP.",
      "A fórmula da tentativa é que o agente inicia e não consuma por circunstâncias alheias à vontade. Aqui a não consumação decorreu de decisão voluntária de parar.",
      "CP, art. 15.",
      "Desistência: ainda podia continuar, mas para; responde pelos atos praticados.", NEW),
    q("USR_DP_ITER_CRIMINIS_NOVA_02_20261103", PENAL, "Arrependimento eficaz — esgotamento dos atos executórios", "muito_dificil",
      "O agente que esgota os atos executórios e, arrependido, impede eficazmente a produção do resultado responde pela tentativa do crime inicialmente pretendido, embora a pena possa ser reduzida por analogia ao arrependimento posterior.", "ERRADO",
      "No arrependimento eficaz, após esgotar a execução o agente atua com êxito para evitar o resultado. Pelo art. 15 do CP, responde apenas pelos atos já praticados, se puníveis autonomamente, e não pela tentativa do crime cujo resultado foi impedido.",
      "Não confunda arrependimento eficaz (art. 15, atua para evitar resultado) com arrependimento posterior (art. 16, reparação/restituição após consumação).",
      "CP, arts. 15 e 16.",
      "Esgotou atos e evitou resultado = arrependimento eficaz; crime-fim não fica em tentativa.", NEW),
    q("USR_DP_ITER_CRIMINIS_NOVA_03_20261103", PENAL, "Arrependimento posterior — momento e requisitos", "muito_dificil",
      "Em crime sem violência ou grave ameaça à pessoa, a restituição integral da coisa após o recebimento da denúncia, mas antes da sentença, assegura necessariamente a redução de pena do arrependimento posterior prevista no art. 16 do Código Penal.", "ERRADO",
      "O art. 16 exige reparação do dano ou restituição da coisa, por ato voluntário, até o recebimento da denúncia ou queixa. Se ocorrer depois desse marco, pode haver repercussão em outra fase da dosimetria, mas não está preenchido o requisito temporal do arrependimento posterior.",
      "O marco legal é o recebimento, não a sentença. O item também transforma redução obrigatória, quando preenchidos requisitos, em benefício sem limite temporal.",
      "CP, art. 16.",
      "Arrependimento posterior: sem violência/grave ameaça, voluntário e até o recebimento da inicial acusatória.", NEW),

    q("USR_PT_PREDICADO_NOVA_01_20261103", PORT, "Sintaxe — sujeito, predicado e núcleo", "muito_dificil",
      "Na oração “Chegaram ontem ao quartel os relatórios reservados”, o sujeito é “os relatórios reservados”, e o núcleo do predicado é a forma verbal “chegaram”.", "CERTO",
      "O sujeito simples posposto é “os relatórios reservados”, cujo núcleo é “relatórios”. O predicado é “chegaram ontem ao quartel”; trata-se de predicado verbal, cujo núcleo significativo é o verbo intransitivo “chegaram”.",
      "A ordem inversa pode levar à identificação errada de “ao quartel” como sujeito ou de “ontem” como núcleo.",
      "Sintaxe da oração: concordância verbal, identificação do sujeito e predicação.",
      "Localize o verbo, pergunte quem chegou e classifique o predicado pelo núcleo.", NEW),
    q("USR_PT_PREDICADO_NOVA_02_20261103", PORT, "Tipos de predicado — nominal e verbo-nominal", "muito_dificil",
      "Em “Após a vistoria, os equipamentos permaneceram seguros e a equipe os lacrou”, há predicado nominal na primeira oração e predicado verbo-nominal na segunda.", "ERRADO",
      "Na primeira oração, “permaneceram seguros” atribui estado ao sujeito por verbo de ligação, formando predicado nominal, cujo núcleo é o predicativo “seguros”. Na segunda, “lacrou” exprime ação e “os” retoma “equipamentos”; tal como redigida, a oração não apresenta predicativo, sendo predicado verbal. Portanto, o item está ERRADO.",
      "O item apresenta uma classificação sedutora, mas a segunda oração não contém predicativo do sujeito nem do objeto. Trata-se de predicado verbal. Gabarito: errado.",
      "Predicação verbal; verbo de ligação e predicativo; distinção entre predicado verbal, nominal e verbo-nominal.",
      "Para haver verbo-nominal, identifique simultaneamente ação e predicativo; objeto direto, por si, não é predicativo.", NEW),
    q("USR_PT_ADJUNTO_ADNOMINAL_NOVA_01_20261103", PORT, "Termos ligados ao nome — adjunto adnominal", "muito_dificil",
      "Em “A decisão dos conselheiros sobre a transferência foi contestada”, os termos “dos conselheiros” e “sobre a transferência” são necessariamente adjuntos adnominais, pois completam o sentido do substantivo “decisão”.", "ERRADO",
      "“Dos conselheiros” pode indicar o agente da decisão e funcionar como adjunto adnominal. Já “sobre a transferência” especifica o conteúdo/objeto da decisão e, na análise tradicional, tende a ser complemento nominal de “decisão”. A classificação depende da relação semântica e sintática, não apenas da proximidade com o substantivo.",
      "A preposição não decide sozinha entre adjunto adnominal e complemento nominal. Analise se o termo exprime agente/posse ou alvo/conteúdo de nome abstrato.",
      "Sintaxe nominal: adjunto adnominal e complemento nominal.",
      "Agente/possuidor pode ser adjunto; alvo ou conteúdo de nome abstrato pode ser complemento nominal.", NEW),
    q("USR_PT_ADJUNTO_ADNOMINAL_NOVA_02_20261103", PORT, "Termos ligados ao nome — valor semântico", "muito_dificil",
      "Em “A fiscalização dos agentes foi elogiada”, o segmento “dos agentes” pode ser classificado como adjunto adnominal se indicar quem realizou a fiscalização; em “A fiscalização dos contratos foi elogiada”, a mesma forma preposicionada pode ser complemento nominal, por indicar o objeto fiscalizado.", "CERTO",
      "A classificação depende do papel semântico: em “fiscalização dos agentes”, os agentes podem ser os fiscais (agente), favorecendo adjunto adnominal; em “fiscalização dos contratos”, os contratos são alvo da ação expressa pelo nome abstrato, favorecendo complemento nominal.",
      "A forma com preposição “de” não determina uma única função. O contraste agente versus alvo é o critério decisivo.",
      "Sintaxe nominal: adjunto adnominal e complemento nominal; valores semânticos de agente e paciente.",
      "Substitua o nome abstrato por verbo e observe quem pratica e quem recebe a ação.", NEW),
    q("USR_PT_PONTOVIRGULA_NOVA_01_20261103", PORT, "Pontuação — ponto e vírgula, ponto final e maiúsculas", "muito_dificil",
      "Em “O relatório foi concluído; os anexos, porém, ainda serão conferidos”, a substituição do ponto e vírgula por ponto final exige inicial maiúscula em “os”, sem outra alteração sintática obrigatória.", "CERTO",
      "As duas orações têm autonomia sintática e podem ser separadas por ponto final: “O relatório foi concluído. Os anexos, porém, ainda serão conferidos.” A mudança exige capitalizar a inicial da nova frase; “porém” mantém sua função e posição intercalada.",
      "Ponto e vírgula pode separar orações coordenadas relativamente autônomas. Ao converter em ponto final, ajuste a inicial da frase seguinte.",
      "Pontuação em orações coordenadas e emprego de maiúsculas após ponto final.",
      "Confirme a autonomia de cada oração e ajuste maiúscula/minúscula ao trocar o sinal.", NEW),
    q("USR_PT_PONTOVIRGULA_NOVA_02_20261103", PORT, "Pontuação — substituição por vírgula ou travessão", "muito_dificil",
      "Em “A equipe revisou o plano; em seguida, comunicou as alterações”, a troca do ponto e vírgula por vírgula preserva necessariamente a correção, pois os verbos têm o mesmo sujeito; já a troca por travessão é sempre vedada entre orações coordenadas.", "ERRADO",
      "A substituição por vírgula pode ser possível conforme a relação sintática e o ritmo, mas não decorre automaticamente da identidade do sujeito; além disso, a vírgula pode ser inadequada se separar orações coordenadas com pausa forte sem contexto que a justifique. O travessão não é sempre vedado: pode marcar pausa, destaque ou explicação. A decisão exige avaliar estrutura e sentido.",
      "O item usa “necessariamente” e “sempre”, ignorando que substituição de sinal depende da relação entre segmentos e do efeito de sentido.",
      "Pontuação expressiva e sintática: vírgula, ponto e vírgula e travessão.",
      "Teste cada substituição separadamente; preserve sintaxe, relação semântica e maiúsculas/minúsculas.", NEW),
]

ERROR_IDS = [x["id"] for x in ITEMS if x["id"].startswith("USR_DP_") and "_NOVA_" not in x["id"]]
ERROR_IDS += [x["id"] for x in ITEMS if x["id"].startswith("USR_PT_")]

def main():
    s = BANK.read_text(encoding="utf-8")
    if MARK in s:
        print("Review bank already applied.")
        return
    anchor = "  const ids = new Set(window.QQ.map(q => q.id));"
    if anchor not in s:
        raise SystemExit("Bank insertion anchor missing; no changes made.")
    ids = [x["id"] for x in ITEMS]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate IDs in incoming review batch.")
    block = f'''  // {MARK}\n  const dailyReviewItems = {json.dumps(ITEMS, ensure_ascii=False, separators=(",", ":"))};\n  items.push.apply(items, dailyReviewItems);\n  const dailyReviewErrorIds = {json.dumps(ERROR_IDS, ensure_ascii=False)};\n  function importPmalDailyReview20261103(){{\n    try{{\n      const storageKey='pmal26_import_daily_review_20261103_v1';\n      if(localStorage.getItem(storageKey)==='ok')return;\n      const stamp=new Date(2026,10,3,12,0,0,0).getTime();\n      dailyReviewErrorIds.forEach(function(id,index){{\n        const q=window.QQ.find(function(item){{return item.id===id;}});if(!q)return;\n        if(typeof window.asGet!=='function'||typeof window.asKey!=='function'||!window.S)return;\n        const rec=window.asGet(window.asKey(q),q.m,q.a);\n        const tag='daily_review_20261103_'+id;\n        if((rec.hist||[]).some(function(h){{return h&&h.importTag===tag;}}))return;\n        window.S.eids.add(q.id);\n        rec.hist.push({{id:q.id,ok:false,branco:false,ts:stamp+index,round:window.S.round,ans:q.g==='CERTO'?'ERRADO':'CERTO',g:q.g,conf:'duvida',ce:q.ce||'conteúdo',nv:q.n||'dificil',importTag:tag}});\n        rec.crit=true;rec.revLeft=Math.max(rec.revLeft||0,4);rec.due=stamp;rec.ivIdx=0;\n        if(typeof window.statusOf==='function')rec.status=window.statusOf(rec);\n        if(typeof window.SS==='function')window.SS();\n      }});\n      localStorage.setItem(storageKey,'ok');\n    }}catch(e){{console.warn('Falha ao importar revisão PMAL de 03/11/2026:',e);}}\n  }}\n  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',importPmalDailyReview20261103,{{once:true}});\n  else setTimeout(importPmalDailyReview20261103,0);\n  // {MARK}_END\n'''
    s = s.replace(anchor, block + anchor, 1)
    BANK.write_text(s, encoding="utf-8")
    print(f"OK: {len(ITEMS)} questions added; {len(ERROR_IDS)} confirmed-error prompts queued for the existing review flow.")

if __name__ == "__main__":
    main()
