#!/usr/bin/env python3
from pathlib import Path
import re

P=Path('index.html')
s=P.read_text(encoding='utf-8')
orig=s
changes=[]

def rep(old,new,label,count=1):
    global s
    n=s.count(old)
    if n!=count:
        raise SystemExit(f'ERRO {label}: esperado {count}, encontrado {n}')
    s=s.replace(old,new,count)
    changes.append(label)

def replace_function(name,newfn):
    global s
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',s)
    if not m: raise SystemExit(f'função {name} não encontrada')
    start=m.start(); brace=s.find('{',m.start()); depth=0; quote=None; esc=False; end=None
    for i in range(brace,len(s)):
        ch=s[i]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
            continue
        if ch in ('"',"'",'`'): quote=ch; continue
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0: end=i+1; break
    if not end: raise SystemExit(f'fim da função {name} não encontrado')
    s=s[:start]+newfn+s[end:]
    changes.append('parser legal robusto')

NEW_PARSE=r'''function parseRef(f){
  if(!f)return null;
  function normArt(a){return String(a||'').replace(/[\-‐‑–—]/g,'').toUpperCase();}
  function artNear(pattern){
    var a=new RegExp(pattern+'[\\s\\S]{0,45}?[Aa]rts?\\.?\\s*(\\d+(?:[\\-‐‑–—]?[A-Za-z])?)','i').exec(f);
    if(a)return normArt(a[a.length-1]);
    var b=new RegExp('[Aa]rts?\\.?\\s*(\\d+(?:[\\-‐‑–—]?[A-Za-z])?)[\\s\\S]{0,45}?'+pattern,'i').exec(f);
    return b?normArt(b[1]):'';
  }
  const leiM=f.match(/Lei\s*n?º?\.?\s*5\.?346/i);
  if(leiM){
    const art=artNear('5\\.?346(?:\\/\\d{2,4})?');
    if(art)return {key:'Lei5346 '+art,label:'art. '+art+' do Estatuto dos PM de Alagoas (Lei 5.346/92)',dipl:'Lei5346',art:art,baseKey:'Lei 5.346'};
    return {key:'Lei 5.346',label:'Lei 5.346/92 (Estatuto PM/AL)',dipl:'Lei5346',art:'',baseKey:'Lei 5.346'};
  }
  const cadhM=f.match(/CADH|Pacto de S[ãa]o Jos[ée]|Conven[çc][ãa]o Americana/i);
  if(cadhM){
    const art=artNear('(?:CADH|Pacto de S[ãa]o Jos[ée]|Conven[çc][ãa]o Americana)');
    if(art)return {key:'CADH '+art,label:'art. '+art+' da CADH (Pacto de São José)',dipl:'CADH',art:art,baseKey:'CADH'};
    return {key:'CADH',label:'CADH — Convenção Americana sobre Direitos Humanos (Pacto de São José)',dipl:'CADH',art:'',baseKey:'CADH'};
  }
  const rdM=f.match(/37\.?042/);
  if(rdM){
    const art=artNear('37\\.?042(?:\\/\\d{2,4})?');
    if(art)return {key:'RD '+art,label:'art. '+art+' do Regulamento Disciplinar da PM/AL (Dec. 37.042/96)',dipl:'RD',art:art,baseKey:'RD'};
    return {key:'RD',label:'Regulamento Disciplinar da PM/AL (Decreto 37.042/1996)',dipl:'RD',art:'',baseKey:'RD'};
  }
  const loM=f.match(/14\.?751/);
  if(loM){
    const art=artNear('14\\.?751(?:\\/\\d{2,4})?');
    if(art)return {key:'LO '+art,label:'art. '+art+' da Lei Orgânica Nacional das PMs/CBMs (Lei 14.751/2023)',dipl:'LO',art:art,baseKey:'LO'};
    return {key:'LO',label:'Lei Orgânica Nacional das PMs/CBMs (Lei 14.751/2023)',dipl:'LO',art:'',baseKey:'LO'};
  }
  const LEIS_ESP=[
    {num:'14\\.?133',pfx:'L14133',nome:'Lei de Licitações (Lei 14.133/2021)'},
    {num:'11\\.?343',pfx:'L11343',nome:'Lei de Drogas (Lei 11.343/2006)'},
    {num:'8\\.?069',pfx:'L8069',nome:'ECA (Lei 8.069/1990)',alt:'\\bECA\\b'},
    {num:'8\\.?072',pfx:'L8072',nome:'Lei de Crimes Hediondos (Lei 8.072/1990)',alt:'11\\.?464'},
    {num:'13\\.?869',pfx:'L13869',nome:'Lei de Abuso de Autoridade (Lei 13.869/2019)'},
    {num:'11\\.?340',pfx:'L11340',nome:'Lei Maria da Penha (Lei 11.340/2006)',alt:'\\bLMP\\b|Lei Maria da Penha'},
    {num:'10\\.?826',pfx:'L10826',nome:'Estatuto do Desarmamento (Lei 10.826/2003)'},
    {num:'9\\.?503',pfx:'L9503',nome:'Código de Trânsito Brasileiro (Lei 9.503/1997)',alt:'\\bCTB\\b'},
    {num:'12\\.?850',pfx:'L12850',nome:'Lei de Organização Criminosa (Lei 12.850/2013)'},
    {num:'9\\.?455',pfx:'L9455',nome:'Lei de Tortura (Lei 9.455/1997)'},
    {num:'7\\.?716',pfx:'L7716',nome:'Lei do Racismo (Lei 7.716/1989)'},
    {num:'9\\.?605',pfx:'L9605',nome:'Lei de Crimes Ambientais (Lei 9.605/1998)'},
    {num:'7\\.?960',pfx:'L7960',nome:'Lei da Prisão Temporária (Lei 7.960/1989)'},
    {num:'9\\.?099',pfx:'L9099',nome:'Lei dos Juizados Especiais (Lei 9.099/1995)',alt:'\\bJECRIM\\b'},
    {num:'10\\.?259',pfx:'L10259',nome:'Lei dos Juizados Especiais Federais (Lei 10.259/2001)',alt:'\\bJEF\\b'},
    {num:'8\\.?429',pfx:'L8429',nome:'Lei de Improbidade Administrativa (Lei 8.429/1992)',alt:'14\\.?230'},
    {num:'8\\.?987',pfx:'L8987',nome:'Lei de Concessões e Permissões (Lei 8.987/1995)'},
    {num:'9\\.?784',pfx:'L9784',nome:'Lei do Processo Administrativo Federal (Lei 9.784/1999)'},
    {num:'8\\.?112',pfx:'L8112',nome:'Regime Jurídico dos Servidores Públicos Federais (Lei 8.112/1990)'},
    {num:'4\\.?717',pfx:'L4717',nome:'Lei da Ação Popular (Lei 4.717/1965)'},
    {num:'13\\.?300',pfx:'L13300',nome:'Lei do Mandado de Injunção (Lei 13.300/2016)'},
    {num:'7\\.?210',pfx:'LEP',nome:'Lei de Execução Penal (Lei 7.210/1984)'},
    {num:'12\\.?016',pfx:'L12016',nome:'Lei do Mandado de Segurança (Lei 12.016/2009)'},
    {num:'9\\.?474',pfx:'L9474',nome:'Lei do Refúgio (Lei 9.474/1997)'},
    {num:'12\\.?830',pfx:'L12830',nome:'Lei da Investigação Criminal pelo Delegado (Lei 12.830/2013)'},
    {num:'12\\.?037',pfx:'L12037',nome:'Lei de Identificação Criminal (Lei 12.037/2009)'},
    {num:'9\\.?507',pfx:'L9507',nome:'Lei do Habeas Data (Lei 9.507/1997)'},
    {num:'9\\.?296',pfx:'L9296',nome:'Lei da Interceptação Telefônica (Lei 9.296/1996)'}
  ];
  for(let idx=0;idx<LEIS_ESP.length;idx++){
    const le=LEIS_ESP[idx],fullPat=le.alt?('(?:'+le.num+'|'+le.alt+')'):('(?:'+le.num+')');
    if(new RegExp(fullPat,'i').test(f)){
      const art=artNear(fullPat+'(?:\\/\\d{2,4})?');
      if(art)return {key:le.pfx+' '+art,label:'art. '+art+' da '+le.nome,dipl:le.pfx,art:art,baseKey:le.pfx};
      return {key:le.pfx,label:le.nome,dipl:le.pfx,art:'',baseKey:le.pfx};
    }
  }
  let dipl=null;
  if(/\bCPPM\b/.test(f))dipl='CPPM'; else if(/\bCPP\b/.test(f))dipl='CPP'; else if(/\bCPM\b/.test(f))dipl='CPM'; else if(/\bCP\b/.test(f))dipl='CP'; else if(/\bCF\b/.test(f))dipl='CF';
  if(!dipl)return null;
  let art='';
  var after=new RegExp('(?:'+dipl+')[\\s\\S]{0,45}?[Aa]rts?\\.?\\s*(\\d+(?:[\\-‐‑–—]?[A-Za-z])?)').exec(f);
  if(after)art=normArt(after[1]);
  if(!art){var before=new RegExp('[Aa]rts?\\.?\\s*(\\d+(?:[\\-‐‑–—]?[A-Za-z])?)[\\s\\S]{0,45}?(?:'+dipl+')').exec(f);if(before)art=normArt(before[1]);}
  if(!art){var any=f.match(/[Aa]rts?\.?\s*(\d+(?:[\-‐‑–—]?[A-Za-z])?)/);if(any)art=normArt(any[1]);}
  if(!art)return null;
  const nome=DIPL_NOME[dipl]||dipl,prep=(dipl==='CF')?'da ':'do ';
  return {key:dipl+' '+art,label:'art. '+art+' '+prep+nome,dipl:dipl,art:art,baseKey:dipl};
}'''
replace_function('parseRef',NEW_PARSE)

# Conteúdo legal/jurisprudencial confirmado em fontes oficiais em 22/08/2026.
replacements=[
('Lei nº 14.133/2021 — Nova Lei de Licitações e Contratos Administrativos, substituindo progressivamente a Lei 8.666/1993. Modalidades: pregão, concorrência, concurso, leilão e diálogo competitivo (novidade). Critérios de julgamento: menor preço, maior desconto, melhor técnica/conteúdo artístico, técnica e preço, maior lance/oferta, maior retorno econômico (contratos de eficiência). Traz o Portal Nacional de Contratações Públicas (PNCP), o cadastro de sanções, e a matriz de risco em contratos de obras.',
 'Lei nº 14.133/2021 — Lei de Licitações e Contratos Administrativos. A Lei 8.666/1993 foi revogada em 30/12/2023, preservando-se os contratos licitados sob o regime anterior conforme as regras de transição. Modalidades: pregão, concorrência, concurso, leilão e diálogo competitivo. Critérios de julgamento: menor preço, maior desconto, melhor técnica ou conteúdo artístico, técnica e preço, maior lance e maior retorno econômico. Prevê PNCP, gestão de riscos e regras próprias de contratação.', 'Lei 14.133 geral'),
('Art. 14, Lei 14.133/2021 — É vedada a participação, direta ou indireta, na licitação ou na execução do contrato, do autor do anteprojeto ou projeto básico/executivo, pessoa física ou jurídica, salvo hipóteses excepcionais expressamente previstas em lei (como participação apenas na fase de elaboração de estudos preliminares em certos regimes).',
 'Art. 14, Lei 14.133/2021 — Em regra, é vedada a participação na licitação ou na execução do contrato do autor do anteprojeto, projeto básico ou projeto executivo e das empresas a ele vinculadas nas hipóteses legais. §2º: a critério da Administração e exclusivamente a seu serviço, autor/empresa podem apoiar planejamento, licitação ou gestão contratual, sob supervisão exclusiva de agentes públicos. §4º: a vedação não impede contratação integrada ou semi-integrada em que a elaboração do projeto integre o encargo do contratado.', 'Lei 14.133 art14'),
('Lei nº 8.987/1995 — Regime de concessão e permissão de serviços públicos. Concessão: exige licitação na modalidade concorrência, formaliza-se por CONTRATO administrativo. Permissão: também exige licitação prévia (qualquer modalidade compatível), formaliza-se por CONTRATO DE ADESÃO, com natureza PRECÁRIA, revogável unilateralmente pelo poder concedente a qualquer tempo. Princípio da continuidade do serviço admite interrupção em caso de inadimplemento do usuário (após aviso prévio) ou razões técnicas/segurança.',
 'Lei nº 8.987/1995 — Regime de concessão e permissão de serviços públicos. Concessão de serviço público: delegação mediante licitação na modalidade CONCORRÊNCIA ou DIÁLOGO COMPETITIVO, formalizada por contrato. Permissão: delegação mediante licitação, à pessoa física ou jurídica, formalizada por contrato de adesão e caracterizada pela precariedade. A continuidade admite interrupção nas hipóteses legais, inclusive inadimplemento do usuário após prévio aviso, considerado o interesse da coletividade.', 'Lei 8.987 geral'),
('Art. 2º, Lei 8.987/1995 — Define concessão de serviço público (delegação, mediante licitação na modalidade concorrência, à pessoa jurídica ou consórcio que demonstre capacidade para seu desempenho) e permissão de serviço público (delegação, mediante licitação, à pessoa física ou jurídica que demonstre capacidade, formalizada por contrato de adesão).',
 'Art. 2º, Lei 8.987/1995 — Concessão de serviço público é a delegação de sua prestação, feita pelo poder concedente, mediante licitação na modalidade CONCORRÊNCIA ou DIÁLOGO COMPETITIVO, à pessoa jurídica ou consórcio que demonstre capacidade. Permissão é a delegação, a título precário, mediante licitação, à pessoa física ou jurídica que demonstre capacidade para seu desempenho por sua conta e risco.', 'Lei 8.987 art2'),
('Art. 308, CTB — Participar de corrida, disputa ou competição automobilística, exibição ou demonstração de perícia em manobra não autorizada, gerando situação de risco à incolumidade pública ou privada: crime de perigo abstrato, dispensa lesão ou perigo concreto a pessoa determinada.',
 'Art. 308, CTB — Participar, na direção de veículo automotor em via pública, de corrida, disputa ou competição automobilística ou de exibição/demonstração de perícia em manobra não autorizada, GERANDO SITUAÇÃO DE RISCO à incolumidade pública ou privada. O STJ classifica o delito como crime de PERIGO CONCRETO: exige demonstração da potencialidade lesiva, embora não seja necessário resultado lesivo.', 'CTB art308'),
('Art. 38, CPP — Decadência: o ofendido decai do direito de queixa se não o exerce em 6 meses, contados do conhecimento da autoria.',
 'Art. 38, CPP — Regra geral: decadência do direito de queixa ou de representação em 6 meses, contados do dia em que o ofendido souber quem é o autor (ou, na ação privada subsidiária, do esgotamento do prazo para denúncia). §2º, incluído pela Lei 15.438/2026: nos crimes praticados no âmbito de violência doméstica e familiar contra a mulher, a ofendida tem prazo de 12 MESES.', 'CPP art38 2026'),
('Art. 49, CPP — A renúncia ao exercício do direito de queixa, por parte de um dos ofendidos, não impedirá que os demais a intentem — a renúncia é ato unilateral que não se estende automaticamente aos demais titulares do direito de queixa.',
 'Art. 49, CPP — A renúncia ao exercício do direito de queixa, EM RELAÇÃO A UM DOS AUTORES DO CRIME, a todos se estenderá. É consequência da indivisibilidade da ação penal privada. Não confunda autor do crime (querelado) com ofendido/titular do direito de queixa.', 'CPP art49'),
('Arts. 55 a 59, CPP — Disciplinam a perempção, causa de extinção da punibilidade exclusiva da ação penal privada, decorrente da inércia processual do querelante (ex.: deixar de promover andamento do processo durante 30 dias seguidos, ou faltar a atos processuais sem motivo justificado) — instituto que não se aplica à ação penal pública.',
 'Art. 55, CPP — O perdão poderá ser aceito por procurador com poderes especiais. Os arts. 55 a 59 tratam do PERDÃO do ofendido e de sua aceitação; as hipóteses de PEREMPÇÃO estão concentradas no art. 60. ⚠ CEBRASPE: 55–59 = perdão; 60 = perempção.', 'CPP art55'),
('Art. 74, CPP — A competência pela natureza da infração é, em regra, do júri, para os crimes dolosos contra a vida. §1º — o foro especial por prerrogativa de função prevalece sobre a competência do júri, quando previsto na própria Constituição.',
 'Art. 74, CPP — A competência pela natureza da infração será regulada pelas leis de organização judiciária, RESSALVADA a competência privativa do Tribunal do Júri. §1º: compete ao Júri julgar os crimes dolosos contra a vida previstos no dispositivo. Foro por prerrogativa previsto na própria Constituição pode prevalecer sobre o Júri.', 'CPP art74'),
('Art. 100, CPP — A decadência do direito de queixa ou de representação, nos crimes de ação penal privada ou pública condicionada, opera-se no prazo de 6 meses, contado do dia em que se veio a saber quem é o autor do crime, extinguindo a punibilidade.',
 'Art. 100, CPP — Se o juiz NÃO aceitar a arguição de suspeição, mandará autuar a petição em apartado, responderá em 3 dias e remeterá os autos da exceção, em 24 horas, ao juiz ou tribunal competente para julgá-la. ⚠ A decadência do direito de queixa/representação está no art. 38 do CPP (e art. 103 do CP), não no art. 100.', 'CPP art100'),
('Art. 798, CPP — Regra geral sobre prazos no processo penal: contam-se os prazos incluindo o dia do começo, salvo disposição em contrário, e todos os prazos correrão em cartório, salvo os que a lei determinar que corram em outro lugar.',
 'Art. 798, CPP — Os prazos processuais penais são contínuos e peremptórios. §1º: NÃO se computa o dia do começo e INCLUI-SE o dia do vencimento; se o vencimento cair em domingo/feriado, prorroga-se para o dia útil imediato. Art. 798-A: os prazos ficam suspensos de 20/12 a 20/1, salvo processos com réu preso, procedimentos da Lei Maria da Penha e medidas urgentes.', 'CPP art798'),
('Lei nº 11.343/2006 — Lei de Drogas. Distingue porte para uso pessoal (art. 28 — não gera pena privativa de liberdade, apenas advertência/prestação de serviços/medida educativa) de tráfico (art. 33 — reclusão de 5 a 15 anos). Critério do art. 28, §2º para diferenciar usuário de traficante é multifatorial (natureza/quantidade da droga, local, circunstâncias, conduta e antecedentes do agente). Prevê associação para o tráfico (art. 35, crime autônomo) e o tráfico privilegiado (art. 33, §4º — STF/STJ: não é hediondo).',
 'Lei nº 11.343/2006 — Lei de Drogas. O art. 28 prevê medidas sem pena privativa de liberdade para porte destinado a consumo pessoal; o art. 33 prevê tráfico (5 a 15 anos). O art. 28, §2º adota critérios multifatoriais. ATUALIZAÇÃO STF Tema 506: portar CANNABIS para consumo pessoal não configura infração penal, embora permaneça ilícito extrapenal; presume-se usuário, de forma relativa, quem portar até 40 g de cannabis ou 6 plantas fêmeas. Associação para o tráfico (art. 35) é autônoma; tráfico privilegiado (art. 33, §4º) não é hediondo.', 'Lei Drogas geral Tema506'),
('Art. 28, Lei 11.343/2006 — Quem adquire, guarda, tem em depósito, transporta ou traz consigo drogas para consumo pessoal está sujeito a advertência sobre os efeitos, prestação de serviços à comunidade e medida educativa — sem pena privativa de liberdade. §2º — para determinar se é para consumo pessoal, o juiz atenderá à natureza e quantidade da substância, ao local/condições da ação, às circunstâncias sociais/pessoais e à conduta/antecedentes do agente.',
 'Art. 28, Lei 11.343/2006 — A lei prevê advertência, prestação de serviços e medida educativa para porte destinado a consumo pessoal, sem pena privativa de liberdade, e o §2º adota critérios multifatoriais. STF Tema 506 (trânsito em julgado em 2025): quanto à CANNABIS para consumo pessoal, não há infração penal; a conduta continua ilícita extrapenal e admite advertência/medida educativa em procedimento não penal. Há presunção RELATIVA de uso pessoal até 40 g de cannabis ou 6 plantas fêmeas.', 'Lei Drogas art28 Tema506'),
('Lei nº 9.455/1997 — Lei de Tortura. Modalidades: constranger com violência/grave ameaça causando sofrimento físico/mental com finalidade específica (obter informação/confissão, aplicar castigo, discriminação — art.1º,I); submeter alguém sob guarda/poder/autoridade a sofrimento (art.1º,II). Omissão do agente que tinha dever de evitar/apurar: pena mais BRANDA (detenção 1-4 anos) que a modalidade ativa (reclusão 2-8 anos). Equiparado a hediondo: regime inicial fechado, veda fiança/graça/anistia (mas não indulto).',
 'Lei nº 9.455/1997 — Lei de Tortura. Modalidades incluem constrangimento com violência/grave ameaça e finalidades específicas, tortura-castigo e omissão de quem tinha dever de evitar/apurar. Desde a Lei 15.410/2026, inclui a submissão REITERADA da mulher a intenso sofrimento físico ou mental em contexto de violência doméstica/familiar. Tortura é equiparada a hediondo e é insuscetível de anistia, graça, INDULTO e fiança. Embora o texto legal mencione regime inicial fechado, STF/STJ afastam sua imposição automática: o regime deve ser fundamentado segundo as regras constitucionais e penais.', 'Lei Tortura geral'),
('Lei nº 8.072/1990 — Crimes Hediondos. Rol taxativo (art.1º): homicídio qualificado, latrocínio, extorsão qualificada pela morte, extorsão mediante sequestro, estupro, estupro de vulnerável, epidemia com resultado morte, falsificação de medicamentos, favorecimento da prostituição de vulnerável, genocídio, posse/porte de arma de fogo de uso proibido. Equipara-se a hediondo: tráfico de drogas, tortura, terrorismo. Regime inicial fechado (STF já flexibilizou a vedação absoluta à progressão). Vedados: anistia, graça, indulto, fiança.',
 'Lei nº 8.072/1990 — Crimes Hediondos. O rol é legal/taxativo e recebeu alterações relevantes em 2026, inclusive crimes de domínio social estruturado/favorecimento e diversos crimes sexuais do ECA. Tortura, tráfico ilícito de drogas e terrorismo recebem tratamento equiparado. Art. 2º: são insuscetíveis de anistia, graça, INDULTO e fiança. ⚠ O regime inicial fechado NÃO pode ser imposto automaticamente apenas pela hediondez; exige fundamentação conforme a jurisprudência constitucional.', 'Hediondos geral 2026'),
('Art. 112, LEP (redação da Lei 13.964/2019, Pacote Anticrime) — A progressão de regime de cumprimento de pena depende do cumprimento de percentual da pena no regime anterior: 16% (primário, crime sem violência/grave ameaça), 20% (reincidente, crime sem violência/grave ameaça), 25% (primário, crime com violência/grave ameaça), 30% (reincidente, crime com violência/grave ameaça), 40% (primário em hediondo/equiparado), 50% (primário em hediondo com morte, ou reincidente em hediondo/equiparado, ou comandante de organização criminosa, ou milícia com resultado morte), 60% (reincidente específico em hediondo/equiparado), 70% (reincidente específico em hediondo/equiparado com resultado morte). Exige ainda bom comportamento carcerário.',
 'Art. 112, LEP — REDAÇÃO VIGENTE EM 2026: regra geral de progressão = cumprimento de ao menos 1/6 da pena no regime anterior + mérito, observadas exceções. Primário com violência/grave ameaça: 25%; reincidente com violência/grave ameaça: 30%; reincidente nos demais crimes referidos: 20%; permanece a hipótese legal de 30% do inciso IV. Hediondo/equiparado: 70% se primário; 75% nas hipóteses do inciso VI (inclusive hediondo com resultado morte se primário, comando de organização ultraviolenta para hediondo/equiparado, milícia e feminicídio primário); 80% se reincidente em hediondo/equiparado; 85% se reincidente em hediondo/equiparado com resultado morte. §1º exige boa conduta carcerária e resultados do exame criminológico. Alterações: Leis 15.358/2026 e 15.402/2026.', 'LEP art112 2026'),
('Art. 41, Lei 8.112/1990 — Estágio probatório de 24 meses (interpretação atual: 3 anos, por força do art. 41 c/c a exigência constitucional de estágio probatório compatível com a estabilidade trienal), durante o qual o servidor é avaliado quanto a assiduidade, disciplina, capacidade de iniciativa, produtividade e responsabilidade.',
 'Art. 41, Lei 8.112/1990 — REMUNERAÇÃO é o vencimento do cargo efetivo acrescido das vantagens pecuniárias permanentes estabelecidas em lei. §3º: o vencimento do cargo efetivo, acrescido das vantagens de caráter permanente, é irredutível. ⚠ Estágio probatório está no art. 20, não no art. 41.', 'Lei 8.112 art41'),
('Art. 137, Lei 8.112/1990 — A demissão ou a destituição de cargo em comissão, por infringência do art. 117, incisos IX e XI (crime contra a administração pública; improbidade administrativa), incompatibiliza o ex-servidor para nova investidura em cargo público federal pelo prazo de 5 anos.',
 'Art. 137, Lei 8.112/1990 — A demissão ou destituição de cargo em comissão por infringência do art. 117, IX (valer-se do cargo para lograr proveito pessoal ou de outrem, em detrimento da dignidade da função pública) e XI (atuar como procurador/intermediário perante repartições públicas, salvo exceções legais) incompatibiliza o ex-servidor para nova investidura em cargo público federal por 5 anos.', 'Lei 8.112 art137'),
('Lei nº 11.340/2006 — Lei Maria da Penha. Cria mecanismos para coibir violência doméstica/familiar contra a mulher (art.226, §8º, CF; CADH; CEDAW). Formas de violência (art.7º): física, psicológica, sexual, patrimonial, moral. Medidas protetivas de urgência (art.22-24): afastamento do agressor do lar, proibição de aproximação/contato, entre outras — podem ser concedidas pelo juiz independentemente de audiência das partes ou manifestação do MP. Não se aplica a Lei 9.099/95 (JECRIM) aos crimes praticados com violência doméstica (art.41).',
 'Lei nº 11.340/2006 — Lei Maria da Penha. Formas de violência: física, psicológica, sexual, patrimonial e moral. Medidas protetivas podem ser concedidas independentemente de audiência das partes e de manifestação prévia do MP nas hipóteses legais. ATUALIZAÇÕES 2026: monitoração eletrônica do agressor como medida autônoma (Lei 15.383); ampliação do art. 12-C (Lei 15.411); medidas cíveis como título executivo judicial (Lei 15.412); e prazo decadencial de 12 meses para queixa/representação em crimes no âmbito doméstico e familiar contra a mulher (art. 16-A, Lei 15.438). Art. 41: não se aplica a Lei 9.099/95 aos crimes abrangidos.', 'Maria Penha geral 2026'),
('Art. 22, Lei 11.340/2006 — Medidas que obrigam o agressor incluem suspensão/restrição de armas, afastamento do lar, proibição de aproximação/contato/frequência a lugares e restrições/suspensão de visitas, entre outras providências legais.\\n\\n⚠ CEBRASPE — O rol permite cumulação e outras medidas; não exige sentença definitiva.',
 'Art. 22, Lei 11.340/2006 — Medidas que obrigam o agressor incluem suspensão/restrição de armas, afastamento do lar, proibições de aproximação/contato/frequência, restrições de visitas e MONITORAÇÃO ELETRÔNICA (inc. VIII, Lei 15.383/2026), com dispositivo/aplicação de alerta para a vítima. Lei 15.412/2026: medidas protetivas de natureza cível, inclusive alimentos provisionais/provisórios, constituem título executivo judicial de pleno direito e dispensam ação principal.\\n\\n⚠ CEBRASPE — Podem ser cumuladas e não dependem de sentença definitiva.', 'Maria Penha art22 2026')
]
for old,new,label in replacements: rep(old,new,label)

# Inserções de dispositivos atuais/relevantes sem substituir cartão existente.
anchor='"L8112 41":"Art. 41, Lei 8.112/1990 — REMUNERAÇÃO é o vencimento do cargo efetivo acrescido das vantagens pecuniárias permanentes estabelecidas em lei. §3º: o vencimento do cargo efetivo, acrescido das vantagens de caráter permanente, é irredutível. ⚠ Estágio probatório está no art. 20, não no art. 41.",'
if anchor not in s: raise SystemExit('anchor L8112 41 pós-correção não encontrado')
s=s.replace(anchor,'"L8112 20":"Art. 20, Lei 8.112/1990 — Ao entrar em exercício, o servidor efetivo fica sujeito a estágio probatório; o texto legal menciona 24 meses, mas a estabilidade constitucional é adquirida após 3 anos de efetivo exercício, devendo-se observar a disciplina constitucional e regulamentar vigente. Fatores legais: assiduidade, disciplina, capacidade de iniciativa, produtividade e responsabilidade.",'+anchor,1); changes.append('adiciona Lei 8.112 art20')

# As strings abaixo são inseridas junto a chaves já existentes, mantendo sintaxe do objeto DISP.
def insert_before(anchor_key, text, label):
    global s
    token='"'+anchor_key+'":'
    n=s.count(token)
    if n!=1: raise SystemExit(f'anchor {anchor_key}: {n}')
    s=s.replace(token,text+token,1); changes.append(label)

insert_before('L11340 18','"L11340 12D":"Art. 12-D, Lei 11.340/2006 (Lei 15.383/2026) — Havendo risco atual ou iminente à vida ou à integridade física ou psicológica da mulher ou de seus dependentes, o agressor será submetido imediatamente à monitoração eletrônica pela autoridade judicial ou, se o Município não for sede de comarca, pelo delegado, com comunicação ao juiz em 24 horas e decisão judicial em igual prazo.","L11340 16A":"Art. 16-A, Lei 11.340/2006 (Lei 15.438/2026) — Nos crimes praticados no âmbito de violência doméstica e familiar contra a mulher, a ofendida decai do direito de queixa ou de representação se não o exercer em 12 MESES, contado do conhecimento da autoria ou, na hipótese legal de ação subsidiária, do esgotamento do prazo da denúncia.",', 'adiciona LMP arts12D e16A')
insert_before('L11343 42','"L11343 40A":"Art. 40-A, Lei 11.343/2006 (Lei 15.358/2026) — As penas dos arts. 33 a 37 são aplicadas EM DOBRO se o crime for praticado por integrante de organização criminosa ultraviolenta, grupo paramilitar ou milícia privada no contexto das condutas do marco legal do combate ao crime organizado. O parágrafo único prevê concurso material com crime de arma de fogo na hipótese legal.",', 'adiciona Drogas art40A')
insert_before('L10826 16','"L10826 21A":"Art. 21-A, Lei 10.826/2003 (Lei 15.358/2026) — Nos crimes dos arts. 12, 14 e 16, a pena aumenta em 2/3 se o crime for praticado em concurso com crime da Lei de Drogas, estiver diretamente ligado ao comércio ilícito de entorpecentes ou a arma tiver sido utilizada para assegurar o sucesso da mercancia.",', 'adiciona Desarmamento art21A')
insert_before('L8069 18','"L8069 11A":"Art. 11-A, ECA (Lei 15.413/2026) — Crianças e adolescentes têm assegurado acesso, no SUS, a programas de saúde mental para prevenção e tratamento, com atenção psicossocial básica/especializada, urgência/emergência e atenção hospitalar, formação específica dos profissionais e acesso a recursos terapêuticos nas hipóteses legais.",', 'adiciona ECA art11A')
insert_before('CPP 319','"CPP 313":"Art. 313, CPP — Hipóteses legais de admissão da prisão preventiva. Desde a Lei 15.487/2026, o inciso VI inclui crimes contra a dignidade sexual praticados contra criança/adolescente e os crimes dos arts. 240 a 241-D e 244-A do ECA.",', 'adiciona CPP art313 2026')

# Validação mínima: nenhuma regra antiga crítica pode restar.
for banned in ['crime de perigo abstrato, dispensa lesão ou perigo concreto','contam-se os prazos incluindo o dia do começo','Art. 100, CPP — A decadência','40% (primário em hediondo/equiparado)','substituindo progressivamente a Lei 8.666/1993']:
    if banned in s: raise SystemExit('texto antigo ainda presente: '+banned)

P.write_text(s,encoding='utf-8')
Path('law-bank-fix-20260822.txt').write_text('\n'.join(['CORREÇÕES APLICADAS: '+str(len(changes))]+['- '+x for x in changes])+'\n',encoding='utf-8')
print('OK',len(changes),'correções/inserções; bytes',len(orig),'->',len(s))
