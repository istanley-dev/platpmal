from pathlib import Path
import json
import re

INDEX = Path('index.html')
MARK = 'PMAL_RECENT_USER_QUESTIONS_20260905_V1'

QUESTIONS = [
  {
    "id":"Q596585","m":"Direito Processual Penal Militar","a":"Polícia Judiciária Militar — delegação e oficial da reserva","n":"muito_dificil",
    "e":"À luz do Código de Processo Penal Militar, julgue o item a seguir, com relação à polícia judiciária militar, à ação penal militar e seu exercício, ao juiz e à denúncia. As atribuições de polícia judiciária militar são indelegáveis aos oficiais da reserva remunerada.",
    "g":"ERRADO",
    "c":"A assertiva erra ao transformar a regra de delegação em proibição absoluta. O CPPM admite delegação das atribuições de polícia judiciária militar e, em hipótese excepcional prevista em lei, permite a designação de oficial da reserva de posto mais elevado quando não houver oficial da ativa em condições de receber a delegação. Por isso, dizer que as atribuições são 'indelegáveis' aos oficiais da reserva remunerada é incorreto.",
    "p":"A palavra absoluta 'indelegáveis' elimina a exceção legal. Em CPPM, regra de oficial da ativa não significa proibição absoluta de oficial da reserva.",
    "f":"CPPM, art. 7º, especialmente §§ 1º e 5º.",
    "d":"PJM: ATIVA é a regra; RESERVA pode aparecer na exceção legal. Desconfie de 'indelegável'.",
    "ce":"lei seca","src":"CEBRASPE/STM 2018 — Q596585","real":1
  },
  {
    "id":"USR_CPPM_PJM_FUNCOES_20260905","m":"Direito Processual Penal Militar","a":"Polícia Judiciária Militar — funções e finalidade investigativa","n":"dificil",
    "e":"Com base no Código de Processo Penal Militar (CPPM), julgue o próximo item. A polícia judiciária militar exerce funções idênticas à polícia judiciária, e ambas têm como uma de suas finalidades o colhimento de elementos que indiquem a autoria e comprovem a materialidade do delito.",
    "g":"CERTO",
    "c":"A polícia judiciária militar exerce função investigativa equivalente à polícia judiciária comum, embora atue em âmbito material especializado. O CPPM atribui à polícia judiciária militar a apuração dos crimes militares e de sua autoria, e o inquérito policial militar reúne elementos necessários à apuração do fato delituoso e de sua autoria. A identidade mencionada no item é funcional, e não institucional.",
    "p":"A banca induz a rejeitar 'funções idênticas' por imaginar que as instituições e competências são idênticas. O ponto é a equivalência da função investigativa.",
    "f":"CPPM, arts. 8º e 9º.",
    "d":"PJM = polícia judiciária especializada: mesma FUNÇÃO investigativa, objeto militar.",
    "ce":"lei seca","src":"CEBRASPE — questão enviada pelo usuário em 05/09/2026 (ID não visível no recorte)","real":1
  },
  {
    "id":"USR_CPPM_DESERCAO_ESTAVEL_20260905","m":"Direito Processual Penal Militar","a":"Deserção — prazo de graça, estabilidade e agregação","n":"muito_dificil",
    "e":"Pedro, policial militar do estado de Alagoas, deixou de comparecer à unidade em que serve durante quinze dias do mês de agosto deste ano, sem licença, para viajar com a família. Ele, que já havia gozado férias no último mês de junho, não comunicou a seus superiores o motivo da ausência nem o período. Com referência a essa situação hipotética, julgue o item a seguir. A atitude de Pedro configura deserção do serviço militar, mas, se ele for praça com estabilidade, será colocado na condição de agregado, depois de cumpridas as formalidades legais.",
    "g":"CERTO",
    "c":"O crime de deserção consuma-se quando o militar se ausenta, sem licença, da unidade em que serve ou do lugar em que deve permanecer por mais de oito dias. Na parte procedimental, o CPPM distingue a praça estável da praça sem estabilidade: a praça com estabilidade é agregada, enquanto a praça especial ou sem estabilidade é excluída do serviço ativo. No retorno, a situação também é distinta: reversão para a praça estável e reinclusão para a praça sem estabilidade.",
    "p":"A CEBRASPE troca agregação por exclusão e reversão por reinclusão. A estabilidade da praça é o detalhe decisivo.",
    "f":"CPM, art. 187; CPPM, art. 456, § 4º, e art. 457, § 3º.",
    "d":"DESERÇÃO: +8 dias. ESTÁVEL = agrega/reverte. SEM estabilidade = exclui/reinclui.",
    "ce":"lei seca","src":"CEBRASPE — questão enviada pelo usuário em 05/09/2026 (ID não visível no recorte)","real":1
  },
  {
    "id":"USR_AMB_ACUMULACAO_20260905","m":"Legislação Penal Especial","a":"Crimes Ambientais (Lei 9.605/1998) — crimes de acumulação","n":"muito_dificil",
    "e":"Em relação a crimes ambientais, julgue o item a seguir, de acordo com a legislação de regência e a jurisprudência dos tribunais superiores. Diversos delitos previstos na Lei n.º 9.605/1998 são classificados como crimes de acumulação, ou seja, crimes em que a lesividade da conduta individual é diminuta, todavia, quando há a demonstração de que o comportamento é repetido por um grande número de pessoas em um mesmo contexto de risco, a soma dessas ações permite a constatação de uma lesividade relevante; assim, projetando-se uma proteção ao bem jurídico para o longo prazo, pune-se a conduta individual.",
    "g":"CERTO",
    "c":"A assertiva descreve corretamente a lógica dos chamados crimes de acumulação no direito penal ambiental: condutas individualmente de pequena lesividade podem adquirir relevância penal diante do risco de repetição generalizada e do efeito cumulativo sobre um bem jurídico difuso. Essa perspectiva ajuda a explicar a tutela antecipada e de longo prazo do meio ambiente e a cautela na aplicação do princípio da insignificância em determinados delitos ambientais.",
    "p":"A banca explora a intuição de que uma conduta isoladamente pequena seria sempre penalmente irrelevante. Em matéria ambiental, o potencial cumulativo pode ser decisivo.",
    "f":"Lei 9.605/1998 e construção jurisprudencial/doutrinária sobre delitos de acumulação e tutela penal ambiental.",
    "d":"AMBIENTAL: pequena ação × repetição coletiva = dano cumulativo relevante.",
    "ce":"jurisprudência","src":"CEBRASPE — questão enviada pelo usuário em 04/09/2026 (ID não visível no recorte)","real":1
  },
  {
    "id":"Q2985819","m":"Legislação Penal Especial","a":"Crimes Ambientais — responsabilidade da pessoa jurídica e desconsideração","n":"dificil",
    "e":"Com base na atual legislação ambiental brasileira, julgue o item que se segue. Na aplicação de penalidades derivadas de crimes ambientais, a responsabilidade de pessoas jurídicas não exclui a de pessoas físicas autoras, coautoras ou partícipes do mesmo fato, podendo, ainda, ser desconsiderada a pessoa jurídica sempre que sua personalidade for obstáculo ao ressarcimento de prejuízos causados à qualidade do meio ambiente.",
    "g":"CERTO",
    "c":"A Lei 9.605/1998 prevê expressamente que a responsabilidade da pessoa jurídica não exclui a das pessoas físicas autoras, coautoras ou partícipes do mesmo fato. Também admite a desconsideração da pessoa jurídica quando sua personalidade constituir obstáculo ao ressarcimento dos prejuízos causados à qualidade do meio ambiente.",
    "p":"A banca tenta fazer o candidato enxergar responsabilidade da pessoa jurídica e da pessoa física como alternativas excludentes. Elas podem coexistir.",
    "f":"Lei 9.605/1998, arts. 3º, parágrafo único, e 4º.",
    "d":"AMBIENTAL: PJ pode responder + PF pode responder; personalidade que bloqueia reparação pode ser desconsiderada.",
    "ce":"lei seca","src":"CEBRASPE/Prefeitura de Cachoeiro de Itapemirim 2024 — Q2985819","real":1
  },
  {
    "id":"USR_AMB_RISCO_INTEGRAL_20260905","m":"Legislação Penal Especial","a":"Crimes Ambientais — responsabilidade civil objetiva e risco integral","n":"muito_dificil",
    "e":"Determinada indústria lançou em um riacho resíduos sólidos que afetam a saúde humana. Apesar de a perícia ter atestado a presença de fenol, ferro e manganês no riacho, que expõem a saúde humana a perigo, não existem provas de que essa água seria destinada ao consumo de pessoas. Houve, contudo, a destruição de parte das nascentes do riacho pela ação da indústria. Considerando a situação hipotética precedente, julgue o item a seguir. A indústria poderá ser isentada da reparação do dano ambiental caso um de seus funcionários o tenha causado culposamente.",
    "g":"ERRADO",
    "c":"A obrigação civil de reparar o dano ambiental é objetiva. A jurisprudência do STJ adota a teoria do risco integral em matéria de responsabilidade civil ambiental, de modo que a ausência de dolo ou a alegação de culpa de empregado não afasta, por si só, o dever de reparação quando presentes dano e nexo causal com a atividade.",
    "p":"O item mistura responsabilidade penal subjetiva com responsabilidade civil ambiental objetiva. Culpa do funcionário não funciona como salvo-conduto civil da empresa.",
    "f":"CF, art. 225, § 3º; Lei 6.938/1981, art. 14, § 1º; jurisprudência do STJ sobre risco integral ambiental.",
    "d":"DANO AMBIENTAL CIVIL = objetiva + risco integral. Culpa não afasta automaticamente a reparação.",
    "ce":"jurisprudência","src":"CEBRASPE — questão enviada pelo usuário em 04/09/2026 (ID não visível no recorte)","real":1
  },
  {
    "id":"USR_AMB_BENEFICIO_PJ_20260905","m":"Legislação Penal Especial","a":"Crimes Ambientais — responsabilidade penal da pessoa jurídica: interesse ou benefício","n":"muito_dificil",
    "e":"Renato e Gabriel fundaram, em 2015, a empresa Camarões do Mangue Ltda., que visava a exploração da carcinicultura — criação de crustáceos — exclusivamente em área rural de manguezais de um estado federado. No referido ano, eles instalaram viveiros de grande porte e passaram a exercer atividade econômica muito lucrativa. Após três anos de atividade, os sócios perceberam que não detinham licença ambiental para o exercício da atividade. Tendo como referência essa situação hipotética, julgue o item que se segue. A empresa Camarões do Mangue Ltda. não será responsabilizada penalmente pela atividade ilegal de carcinicultura em manguezais caso os sócios tenham desviado todos os lucros da empresa, não gerando, com isso, nenhum benefício à entidade.",
    "g":"CERTO",
    "c":"A responsabilização penal da pessoa jurídica por crime ambiental exige, nos termos do art. 3º da Lei 9.605/1998, que a infração seja cometida por decisão de representante legal ou contratual, ou de órgão colegiado, no interesse ou benefício da entidade. Na hipótese descrita pelo item, o fato acrescenta expressamente que todos os lucros foram desviados e nenhum benefício foi gerado à entidade, afastando o requisito indicado pela norma para a responsabilização penal da pessoa jurídica naquela situação.",
    "p":"Crime praticado no ambiente empresarial não gera, automaticamente, responsabilidade penal da PJ. Procure decisão qualificada + interesse ou benefício da entidade.",
    "f":"Lei 9.605/1998, art. 3º.",
    "d":"CRIME AMBIENTAL DA PJ: decisão qualificada + interesse/benefício da entidade.",
    "ce":"lei seca","src":"CEBRASPE — questão enviada pelo usuário em 04/09/2026 (ID não visível no recorte)","real":1
  },
  {
    "id":"Q695609","m":"Legislação Penal Especial","a":"Crimes Ambientais — responsabilidade penal da pessoa jurídica: ato de empregado","n":"muito_dificil",
    "e":"Um funcionário de determinada empresa têxtil, por equívoco, provocou o lançamento de rejeitos do processo de tintura em um rio que fica próximo à sede da empresa. Vários peixes morreram e o abastecimento de água da cidade ficou prejudicado. Tendo como referência essa situação hipotética e à luz da legislação pertinente, julgue o item subsecutivo. No caso em questão, a pessoa jurídica da empresa têxtil não responderá por crime ambiental.",
    "g":"CERTO",
    "c":"A mera prática do fato por um empregado não basta para imputar automaticamente o crime ambiental à pessoa jurídica. O art. 3º da Lei 9.605/1998 exige decisão de representante legal ou contratual, ou de órgão colegiado, praticada no interesse ou benefício da entidade. A situação narrada atribui o lançamento, por equívoco, a um funcionário e não fornece os requisitos de imputação penal da pessoa jurídica.",
    "p":"Não confunda dano causado no exercício da atividade empresarial com responsabilidade penal automática da pessoa jurídica. O art. 3º traz requisitos próprios.",
    "f":"Lei 9.605/1998, art. 3º.",
    "d":"EMPREGADO causou ≠ PJ criminosa automaticamente. Procure art. 3º: decisão qualificada + interesse/benefício.",
    "ce":"lei seca","src":"CEBRASPE/IPHAN 2018 — Q695609","real":1
  },
  {
    "id":"USR_AMB_DUPLA_IMPUTACAO_20260905","m":"Legislação Penal Especial","a":"Crimes Ambientais — responsabilidade penal da pessoa jurídica e dupla imputação","n":"muito_dificil",
    "e":"Renato e Gabriel fundaram, em 2015, a empresa Camarões do Mangue Ltda., que visava a exploração da carcinicultura — criação de crustáceos — exclusivamente em área rural de manguezais de um estado federado. No referido ano, eles instalaram viveiros de grande porte e passaram a exercer atividade econômica muito lucrativa. Após três anos de atividade, os sócios perceberam que não detinham licença ambiental para o exercício da atividade. Tendo como referência essa situação hipotética, julgue o item que se segue. Conforme a jurisprudência do STF, a empresa em questão não responderá na esfera penal pelo crime de funcionamento sem licença ambiental, caso seus sócios, pessoas físicas, sejam absolvidos do mesmo crime.",
    "g":"ERRADO",
    "c":"O STF afastou a exigência de dupla imputação obrigatória para a responsabilização penal da pessoa jurídica por crimes ambientais. A persecução ou responsabilização da pessoa jurídica não depende necessariamente da responsabilização concomitante de determinada pessoa física. Portanto, a absolvição dos sócios não implica, por si só, absolvição automática da empresa.",
    "p":"A banca tenta ressuscitar a teoria da dupla imputação obrigatória: PF absolvida = PJ absolvida. Essa vinculação automática não prevalece no STF.",
    "f":"CF, art. 225, § 3º; STF, RE 548.181/PR.",
    "d":"AMBIENTAL: não há DUPLA IMPUTAÇÃO obrigatória. PF e PJ não precisam caminhar sempre juntas.",
    "ce":"jurisprudência","src":"CEBRASPE — questão enviada pelo usuário em 04/09/2026 (ID não visível no recorte)","real":1
  },
  {
    "id":"USR_TORT_NOTURNO_20260905","m":"Legislação Penal Especial","a":"Lei de Tortura (Lei 9.455/1997) — causas de aumento de pena","n":"dificil",
    "e":"Com base nas Leis n.º 13.869/2019 (Lei de Abuso de Autoridade), n.º 8.072/1990 (Lei de Crimes Hediondos), n.º 9.455/1997 (Lei de Tortura) e n.º 10.826/2003 (Estatuto do Desarmamento), julgue o item a seguir. O cometimento de crime de tortura no período noturno é causa de aumento de pena de um sexto a um terço.",
    "g":"ERRADO",
    "c":"O período noturno não figura entre as causas de aumento de pena previstas no § 4º do art. 1º da Lei 9.455/1997. A lei prevê hipóteses específicas de majorante, e a simples prática do crime durante a noite não autoriza aumento de um sexto a um terço.",
    "p":"A banca acrescenta uma circunstância intuitivamente agravadora — período noturno — que não consta do rol legal de majorantes da tortura.",
    "f":"Lei 9.455/1997, art. 1º, § 4º.",
    "d":"TORTURA: 'à noite' não é majorante. Só marque aumento se a hipótese estiver no § 4º.",
    "ce":"lei seca","src":"CEBRASPE/Prefeitura de Cachoeiro de Itapemirim 2024 — Guarda Municipal","real":1
  }
]

# Erros confirmados pelo usuário/screenshot. O item de responsabilidade civil foi acertado;
# o item de tortura não é migrado como erro porque o recorte mostra resposta correta e a mensagem é ambígua.
CONFIRMED_ERRORS = [
  'Q596585',
  'USR_CPPM_PJM_FUNCOES_20260905',
  'USR_CPPM_DESERCAO_ESTAVEL_20260905',
  'USR_AMB_ACUMULACAO_20260905',
  'Q2985819',
  'USR_AMB_BENEFICIO_PJ_20260905',
  'Q695609',
  'USR_AMB_DUPLA_IMPUTACAO_20260905',
]


def js_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def main():
    s = INDEX.read_text(encoding='utf-8')
    if MARK in s:
        print('Questões recentes já aplicadas.')
        return

    anchor = 'const SUBS=[...new Set(QQ.map(q=>q.m))];'
    pos = s.find(anchor)
    if pos < 0:
        raise SystemExit('Âncora SUBS não encontrada; abortando.')

    block = f'''\n// {MARK}\nvar QUESTIONS_20260905_RECENTES={js_json(QUESTIONS)};\nfunction pmalNormQ20260905(x){{return String(x||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();}}\nQUESTIONS_20260905_RECENTES.forEach(function(q){{\n  var nq=pmalNormQ20260905(q.e);\n  if(!QQ.some(function(x){{return x.id===q.id||pmalNormQ20260905(x.e)===nq;}}))QQ.push(q);\n}});\nvar IMPORT_20260905_RECENTES={js_json([{'id': x, 'kind':'erro','origin':'usuario_20260905'} for x in CONFIRMED_ERRORS])};\nfunction importRecentQuestions20260905(){{\n  try{{\n    var key='pmal26_import_user_questions_20260905_v1';\n    if(localStorage.getItem(key)==='ok')return;\n    var now=Date.now(),done=0;\n    IMPORT_20260905_RECENTES.forEach(function(meta,idx){{\n      var source=QUESTIONS_20260905_RECENTES.find(function(z){{return z.id===meta.id;}});if(!source)return;\n      var nq=pmalNormQ20260905(source.e);\n      var q=QQ.find(function(x){{return x.id===meta.id||pmalNormQ20260905(x.e)===nq;}});if(!q)return;\n      var rec=asGet(asKey(q),q.m,q.a),tag='lote_usuario_20260905_erro_'+meta.id;\n      var exists=(rec.hist||[]).some(function(h){{return h&&h.importTag===tag;}});\n      if(!exists){{\n        S.eids.add(q.id);\n        rec.hist.push({{id:q.id,ok:false,branco:false,ts:now-(idx+1),round:S.round,ans:q.g==='CERTO'?'ERRADO':'CERTO',g:q.g,conf:'duvida',ce:q.ce||'conteúdo',nv:q.n||'dificil',importTag:tag}});\n        rec.crit=true;rec.revLeft=Math.max(rec.revLeft||0,4);rec.due=now;rec.ivIdx=0;\n        if(typeof statusOf==='function')rec.status=statusOf(rec);\n        if(typeof flashGet==='function'&&typeof flashKey==='function'&&typeof topico==='function'){{var fr=flashGet(flashKey(q.m,topico(q.a)));fr.due=0;}}\n        done++;\n      }}\n    }});\n    SS();localStorage.setItem(key,'ok');localStorage.setItem(key+'_count',String(done));\n  }}catch(e){{console.warn('Falha ao importar questões recentes do usuário:',e);}}\n}}\n// Executa a migração depois que toda a plataforma tiver inicializado as funções/estado.\nif(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){{setTimeout(importRecentQuestions20260905,0);}});else setTimeout(importRecentQuestions20260905,0);\n// {MARK}_END\n\n'''
    s = s[:pos] + block + s[pos:]
    INDEX.write_text(s, encoding='utf-8')
    print(f'OK: {len(QUESTIONS)} questões recentes adicionadas; {len(CONFIRMED_ERRORS)} erros confirmados migrados para revisão.')


if __name__ == '__main__':
    main()
