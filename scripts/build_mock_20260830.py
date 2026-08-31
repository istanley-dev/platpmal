"""Build the isolated 30/08/2026 review dataset from the user's PDF."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


PDF = Path(sys.argv[1])
OUT = Path(sys.argv[2])


def clean(value: str) -> str:
    value = value.replace("\u00a0", " ").replace("–", "–")
    value = re.sub(r"\s*-\s*", "-", value)
    value = re.sub(r"\s+", " ", value).strip()
    fixes = {
        "injust iça": "injustiça", "parág rafo": "parágrafo", "q ualificada": "qualificada",
        "substantivo s": "substantivos", "equivalesse m": "equivalessem", "neura stênicos": "neurastênicos",
        "refl ete": "reflete", "v erbal": "verbal", "de sencadear": "desencadear", "inci dente": "incidente",
        "mesm o": "mesmo", "aguardam": "aguardam", "aplicá-la": "aplicá-la", "Falta-lhe": "Falta-lhe",
        "operam-se": "operam-se", "exigindo-lhe": "exigindo-lhe", "vê-la": "vê-la", "exija-lhe": "exija-lhe",
        "Hércules-Quasímodo": "Hércules-Quasímodo",
        "tudo a guardam": "tudo aguardam", "juros si mples": "juros simples",
        "a a legação": "a alegação", "corpo ração": "corporação", "milita res": "militares",
        "const itucional": "constitucional", "ef eitos": "efeitos", "admini strativa": "administrativa",
        "Trib unal": "Tribunal", "administrati vo": "administrativo", "fuga o u": "fuga ou",
        "absolu ta": "absoluta", "in formações": "informações", "Naciona l": "Nacional",
        "o s elementos": "os elementos", "ci rcunstanciada": "circunstanciada", "15.43 8/2026": "15.438/2026",
        "Constituiçã o": "Constituição", "n as mesmas": "nas mesmas", "Có digo": "Código",
        "d uração": "duração", "diminuí da": "diminuída", "m ilitar": "militar", "mil itar": "militar",
        "quare nta": "quarenta", "julgam ento": "julgamento", "catálo go": "catálogo", "aciona r": "acionar",
    }
    for old, new in fixes.items():
        value = value.replace(old, new)
    return value


reader = PdfReader(PDF)
pages = [p.extract_text() or "" for p in reader.pages]

# The two Portuguese bases are stored once and referenced by textId.
p2 = pages[1]
text1 = clean(p2.split("CONHECIMENTOS BÁSICOS", 1)[1].split("Rui Barbosa.", 1)[0])
text1 += "\n\nRui Barbosa. Oração aos moços. Rio de Janeiro, 1921 (com adaptações)."
text2 = "O sertanejo é" + p2.split("O sertanejo é", 1)[1].split("Euclides da Cunha.", 1)[0]
text2 = clean(text2) + "\n\nEuclides da Cunha. Os sertões. Rio de Janeiro, 1902 (com adaptações)."

raw_questions: dict[int, str] = {}
for page in pages[1:8]:
    matches = list(re.finditer(r"(?m)^\s*(\d{1,3})\.\s+", page))
    for idx, match in enumerate(matches):
        number = int(match.group(1))
        if not 1 <= number <= 120:
            continue
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(page)
        raw_questions[number] = clean(page[match.end():end])

cuts = {
    11: "O sertanejo é", 20: "Julgue os itens a seguir, relativos a divisão proporcional",
    30: "Julgue os itens a seguir, relativos a sistema operacional", 40: "Com relação à formação histórica",
    50: "Espaço Livre", 54: "Julgue os itens seguintes", 57: "Julgue os itens subsequentes",
    60: "A respeito dos atos administrativos", 66: "Acerca do controle", 70: "Acerca dos direitos",
    76: "No que se refere à organização", 80: "Acerca do inquérito", 85: "A respeito da ação penal",
    90: "Com base na Parte Geral", 96: "Julgue os itens subsequentes", 100: "Quanto à polícia judiciária militar",
    105: "A respeito das medidas cautelares", 110: "Acerca da teoria geral",
    114: "Com base na Convenção Americana", 120: "Espaço Livre",
}
for number, marker in cuts.items():
    if marker in raw_questions[number]:
        raw_questions[number] = raw_questions[number].split(marker, 1)[0].strip()

if sorted(raw_questions) != list(range(1, 121)):
    missing = sorted(set(range(1, 121)) - set(raw_questions))
    raise SystemExit(f"Expected 120 questions; missing {missing}")

answers = """
E C E E E E E E C E C E C E E E C C E E
C E E E E E C E C E E C C E C E E E E C
C E C C E E C C E C C E E C E C E E E C
C E C E E C C C E E C C E C E E C C C E
C C E C E C C C E E C E E C E E E C E C
E C C E C C C E C C C E E C C E C C C E
""".split()

responses = """
E C E C E C E BRANCO E E BRANCO E E E E E C C E C
E E E E E B B C C B C E C E E E E E C E
E C C C E C C C E C C E C C E C E E E E
C C C C E E C C E E C E E C E E C C C E
C E C C E C C C E E C C E E B E E E E C
C C C E E E C E C C C E E C C C C E C E
""".split()

if len(answers) != 120 or len(responses) != 120:
    raise SystemExit("Answer/response list length mismatch")


def matter(n: int) -> str:
    if n <= 20: return "Língua Portuguesa"
    if n <= 30: return "Matemática"
    if n <= 40: return "Noções de Informática"
    if n <= 50: return "Conhecimentos de Alagoas"
    if n <= 54 or n == 60: return "Legislação Institucional PMAL"
    if n <= 59: return "Legislação Penal Especial"
    if n <= 70: return "Direito Administrativo"
    if n <= 80: return "Direito Constitucional"
    if n <= 90: return "Direito Processual Penal"
    if n <= 100: return "Direito Penal Militar"
    if n <= 110: return "Direito Processual Penal Militar"
    return "Direitos Humanos"


topics = [
    "Interpretação — tese central", "Interpretação — inferência", "Interpretação — igualdade material", "Sintaxe — sujeito",
    "Sintaxe — predicativo", "Semântica — senão", "Conectivos — valor causal", "Sintaxe — pronome relativo",
    "Regência nominal e crase", "Coesão referencial", "Orações comparativas", "Interpretação — aparência e resistência",
    "Interpretação — contraste", "Concordância verbal", "Sintaxe — aposto", "Voz passiva sintética",
    "Funções do pronome oblíquo", "Pronome com valor possessivo", "Substantivação do infinitivo", "Colocação pronominal",
    "Porcentagem", "Porcentagem", "Porcentagem", "Porcentagem", "Porcentagem", "Divisão proporcional",
    "Divisão proporcional", "Divisão proporcional", "Divisão proporcional", "Divisão proporcional",
    "Windows 11 — Explorador", "Windows 11 — arquivos", "Windows 11 — atalhos", "Windows 11 — Lixeira",
    "Segurança da informação", "Segurança da informação", "Navegadores", "Redes de computadores", "Redes de computadores", "Redes de computadores",
    "História de Alagoas — Quilombo dos Palmares", "História de Alagoas — Palmares", "Geografia de Alagoas — clima", "Geografia de Alagoas — relevo",
    "Geografia de Alagoas — hidrografia", "Geografia de Alagoas — economia", "Geografia de Alagoas — população", "Geografia de Alagoas — urbanização",
    "Geografia de Alagoas — municípios", "Atualidades de Alagoas", "Estatuto da PMAL", "Estatuto da PMAL", "Estatuto da PMAL", "Estatuto da PMAL",
    "Lei de Tortura", "Crimes Ambientais", "Crimes Ambientais", "CTB", "CTB", "Lei Orgânica Nacional das PMs",
    "Atos administrativos", "Atos administrativos", "Atos administrativos", "Atos administrativos", "Atos administrativos", "Atos administrativos",
    "Controle da Administração", "Controle da Administração", "Controle da Administração", "Controle da Administração",
    "Direitos fundamentais", "Direitos fundamentais", "Direitos fundamentais", "Direitos fundamentais", "Direitos fundamentais", "Direitos fundamentais",
    "Organização do Estado", "Organização do Estado", "Organização do Estado", "Organização do Estado",
    "Inquérito policial", "Inquérito policial", "Inquérito policial", "Inquérito policial", "Inquérito policial",
    "Ação penal", "Ação penal", "Ação penal", "Ação penal", "Ação penal",
    "Aplicação da lei penal militar", "Aplicação da lei penal militar", "Aplicação da lei penal militar", "Aplicação da lei penal militar", "Aplicação da lei penal militar", "Aplicação da lei penal militar",
    "Crime militar", "Crime militar", "Crime militar", "Crime militar",
    "Polícia judiciária militar", "Polícia judiciária militar", "Polícia judiciária militar", "Polícia judiciária militar", "Polícia judiciária militar",
    "Medidas cautelares no CPPM", "Medidas cautelares no CPPM", "Medidas cautelares no CPPM", "Medidas cautelares no CPPM", "Medidas cautelares no CPPM",
    "Teoria geral dos direitos humanos", "Teoria geral dos direitos humanos", "Teoria geral dos direitos humanos", "Teoria geral dos direitos humanos",
    "Convenção Americana de Direitos Humanos", "Convenção Americana de Direitos Humanos", "Convenção Americana de Direitos Humanos", "Convenção Americana de Direitos Humanos", "Convenção Americana de Direitos Humanos", "Convenção Americana de Direitos Humanos",
]

rules = [
    "O texto desloca a eficácia das leis para a qualidade de quem as executa; não atribui a inefetividade à imperfeição legal.",
    "A demora ilegal é chamada de injustiça qualificada e manifesta, portanto vai além de falha administrativa.",
    "O último parágrafo defende igualdade material: tratar desigualmente os desiguais na medida de suas diferenças.",
    "O sujeito posposto de “faltassem” é composto: “mãos firmes e consciências retas”; “lhe” é objeto indireto.",
    "“Estéril” atribui estado a “a esperança” por meio de verbo de ligação e exerce função de predicativo do sujeito.",
    "No contexto, “senão” significa “mas sim”; escrever “se não” criaria outra estrutura e alteraria a correção e o sentido.",
    "“Porquanto” tem valor causal/explicativo, equivalente a “porque”, e não conclusivo como “portanto”.",
    "O “que” retoma “culpados” e introduz oração adjetiva; não é conjunção integrante.",
    "“Obediência” e “submissão” regem a preposição a; com os artigos femininos de “lei” e “letra”, ocorre crase.",
    "O pronome “as” retoma “as partes”, objeto direto de “lesa”, e não “mãos”.",
    "A construção “como se” seleciona o imperfeito do subjuntivo e expressa comparação hipotética.",
    "A aparência cansada engana; o texto afirma que ela não corresponde à resistência efetiva do sertanejo.",
    "O sertanejo é contraposto aos mestiços neurastênicos do litoral, apresentados como organicamente debilitados.",
    "Com sujeito composto posposto, o singular pode concordar por atração com o núcleo mais próximo; não há violação obrigatória da norma.",
    "“Hércules-Quasímodo” renomeia/caracteriza o sertanejo e funciona como aposto, não vocativo.",
    "Em “operam-se transmutações”, há voz passiva sintética; “transmutações completas” é sujeito paciente.",
    "Em construção causativa/perceptiva, “la” é objeto de “ver” e sujeito semântico do infinitivo “desaparecer”.",
    "O dativo “lhe” equivale a “dele/no sertanejo”, exprimindo posse das energias desencadeadas.",
    "O artigo em “o desencadear” substantiva o infinitivo; ele passa a funcionar como substantivo nuclear.",
    "Com pronome átono depois de palavra atrativa (“que”), exige-se próclise: “que lhe exija”, não “que exija-lhe”.",
]

specific_rules = [
    "Os pesos são 4/2, 5/1 e 8/4, isto é, 2, 5 e 2; a segunda parte recebe 5/9 de R$ 45.000,00, ou R$ 25.000,00.",
    "A distância é proporcional a viaturas × dias × horas: a nova operação reúne 216 viatura-horas contra 240 da primeira e não alcança 1.800 km.",
    "Se o lucro é 25% do preço de venda, P − 90 = 0,25P; logo, P = R$ 120,00, e não R$ 112,50.",
    "Nos juros simples, J = 24.000 × 0,15 × 73/360 = R$ 730,00.",
    "A raiz quarta fornecida corresponde a 4,88% por trimestre, taxa inferior a 5%.",
    "O desconto comercial é R$ 1.100,00; o racional é R$ 1.000,00. O racional é R$ 100,00 menor, não maior.",
    "A taxa real é (1,26/1,20) − 1 = 0,05, exatamente 5%.",
    "Após o primeiro ano há R$ 22.000,00; retirados R$ 4.000,00, os R$ 18.000,00 rendem para R$ 19.800,00.",
    "Os fatores 0,80 e 0,90 produzem 0,72; a redução equivalente é de 28%.",
    "A produtividade é 5 veículos por policial-hora; para 120 veículos em 2 horas são necessários 12 policiais.",
    "Quando permissões NTFS e de compartilhamento coexistem no acesso pela rede, prevalece a combinação mais restritiva.",
    "Ao copiar de C2 para D3, A$1 avança para B$1 e $B2 mantém a coluna B, mas avança a linha para $B3.",
    "O CONT.SE compara cada valor com a média, e a concatenação “>”&MÉDIA(...) forma corretamente o critério.",
    "O PROCV pesquisa na primeira coluna e só retorna colunas à direita; índice negativo não habilita busca à esquerda.",
    "HTTPS usa normalmente a porta 443; o TLS autentica e negocia material de chave para cifragem simétrica da sessão.",
    "Assinatura digital garante autenticidade, integridade e não repúdio, mas não cifra necessariamente o conteúdo nem assegura confidencialidade.",
    "Os conceitos foram invertidos: backdoor oferece acesso oculto; rootkit procura esconder presença e manter privilégios.",
    "Em IaaS, o provedor protege a infraestrutura; sistema operacional da instância e acessos do cliente permanecem sob responsabilidade do cliente.",
    "RPO mede a perda de dados tolerável; RTO mede o tempo tolerável para restabelecimento. O item inverteu os indicadores.",
    "O incremental tende a ser menor e mais rápido, mas a restauração exige o backup completo e cada incremental subsequente.",
    "A emancipação política ocorreu em 1817, e a instalação do governo da capitania em 1819 com Melo e Póvoas está historicamente correta.",
    "A criação da comarca ampliou a estrutura judicial, mas não rompeu a dependência político-administrativa de Pernambuco.",
    "A força econômica do porto de Jaraguá foi central na transferência da capital para Maceió em 1839.",
    "O acordo de Ganga Zumba previa Cucaú e liberdade nos termos indicados; Zumbi o rejeitou e continuou a resistência.",
    "A queda do Cerca do Macaco em 1694 liga-se à expedição de Domingos Jorge Velho e Bernardo Vieira de Melo, não ao comando de Fernão Carrilho.",
    "A Cabanada reuniu forte componente restaurador e monarquista; classificá-la como movimento abolicionista e republicano distorce sua natureza.",
    "O desastre socioambiental em Maceió foi associado à mineração de sal-gema e provocou evacuação e interdição de bairros.",
    "Piaçabuçu, Penedo e Xingó/Piranhas estão corretamente posicionados ao longo do baixo São Francisco alagoano.",
    "O item inverte as unidades: os tabuleiros costeiros ficam na faixa litorânea, enquanto a influência da Borborema aparece no interior.",
    "Guerreiro, pastoril e reisado integram tradições natalinas, e o filé é característico das comunidades da lagoa Mundaú.",
    "O militar com mais de dez anos candidato fica agregado; a situação funcional indicada permanece até a diplomação ou retorno, conforme o Estatuto.",
    "Demissão aplica-se ao oficial e licenciamento à praça; o item inverte os destinatários e ainda generaliza a autoridade competente.",
    "Causa de justificação exclui a transgressão/punição; ela não serve apenas para reduzir a sanção ao mínimo.",
    "A progressão e o rebaixamento das classificações de comportamento descritos reproduzem a disciplina estatutária cobrada no item.",
    "A recusa ao etilômetro não impede prova do crime por outros meios, como sinais de alteração psicomotora, testemunhos ou exame clínico.",
    "O STF reconheceu a constitucionalidade do crime de afastar-se do local do acidente para fugir à responsabilidade.",
    "A PM só executa fiscalização de trânsito e autua quando houver a atribuição legal ou convênio; o poder de polícia corporativo não basta por si.",
    "Manter arma irregular em casa configura posse; portá-la em via pública configura porte. São tipos penais distintos.",
    "O afastamento policial da Lei Maria da Penha depende também dos requisitos territoriais e da indisponibilidade das autoridades previstas; não basta faltar delegado.",
    "A Lei 14.751/2023 prevê estabilidade após três anos e disciplina o afastamento do militar com menos de dez anos que registra candidatura.",
    "Mesmo quando a motivação não era obrigatória, os motivos declarados vinculam o ato; sua falsidade pode invalidá-lo.",
    "A jurisprudência admite delegação de consentimento, fiscalização e sanção a certas entidades privadas estatais; o item erra ao vedar a sanção em absoluto.",
    "Anulação por ilegalidade tem efeitos retroativos; revogação por mérito produz efeitos prospectivos e respeita direitos adquiridos.",
    "No processo administrativo federal, o prazo decadencial geral para anular ato favorável é de cinco anos, salvo má-fé, e não dez.",
    "Atos normativos e decisões de recursos não podem ser delegados; a avocação também é excepcional, temporária e motivada.",
    "A autorização de uso é unilateral, discricionária e precária, normalmente voltada ao interesse do particular e sem licitação ou lei específica.",
    "A Lei 14.230/2021 eliminou a improbidade culposa e passou a exigir dolo para os tipos legais, não mera voluntariedade.",
    "A omissão estatal é em regra examinada pela falta do serviço; em custódia ou dever específico de proteção, incide responsabilidade objetiva.",
    "Pela tese da dupla garantia, a ação indenizatória deve ser dirigida contra o Estado, que pode depois exercer regresso contra o agente com dolo ou culpa.",
    "Em contrato administrativo, a sustação cabe inicialmente ao Congresso; o Tribunal de Contas comunica a irregularidade e observa o rito constitucional.",
    "O ingresso sem mandado exige fundadas razões de flagrante, justificadas depois; sem isso, há nulidade e possível responsabilização.",
    "A Súmula Vinculante 11 admite algemas por resistência, risco de fuga ou perigo à integridade, sempre com justificativa escrita.",
    "O sigilo telefônico não é absoluto: a CF admite interceptação judicial, nas hipóteses legais, para investigação ou instrução penal.",
    "Militar da ativa não pode sindicalizar-se, fazer greve ou filiar-se a partido; candidato com menos de dez anos afasta-se da atividade.",
    "A jurisprudência exige pretensão resistida ou prévio requerimento para caracterizar interesse de agir em habeas data.",
    "A vedação de habeas corpus contra punição disciplinar não impede controle judicial da legalidade, competência e devido processo.",
    "Estado de defesa é decretado e submetido depois ao Congresso; estado de sítio depende de autorização prévia do Congresso Nacional.",
    "O estado de defesa dura até trinta dias e admite uma única prorrogação por igual período.",
    "A intervenção é apreciada em 24 horas, mas a CF dispensa a apreciação quando basta suspender o ato impugnado para restaurar a normalidade.",
    "Cabe à União editar normas gerais sobre organização e material das polícias militares; não há competência privativa estadual nos termos amplos do item.",
    "O indiciamento é ato fundamentado e privativo do delegado; juiz e Ministério Público não podem ordená-lo.",
    "A SV 14 garante acesso defensivo aos elementos já documentados e relacionados à defesa, sem alcançar diligências sigilosas ainda em curso.",
    "A cadeia de custódia começa com a preservação do local ou detecção do vestígio, antes de sua apreensão pelo perito.",
    "Do indeferimento de instauração cabe recurso ao chefe de polícia, sem eliminar o direito de queixa nos crimes de ação privada.",
    "O prazo do inquérito com indiciado preso é de dez dias e não se prorroga pela regra geral; a afirmação de prorrogação em ambos os casos é falsa.",
    "O art. 28 do CPP prevê comunicações e revisão ministerial, e permite à vítima provocar a revisão no prazo legal.",
    "O ANPP exige confissão formal e circunstanciada, ausência de violência ou grave ameaça e pena mínima inferior a quatro anos, computadas majorantes e minorantes.",
    "O item reproduz o prazo decadencial especial de doze meses indicado pela Lei 15.438/2026 para o contexto nela previsto.",
    "A ação privada subsidiária exige inércia do Ministério Público; arquivamento promovido tempestivamente não a autoriza.",
    "Perempção é sanção própria da ação penal privada, não da ação pública condicionada à representação.",
    "O art. 9.º do CPM também alcança crimes da legislação comum quando presentes as circunstâncias militares, inclusive entre militares da ativa.",
    "A ressalva legal de ação militar refere-se às Forças Armadas; para militar estadual contra civil, o crime doloso contra a vida vai ao júri.",
    "Civis podem submeter-se à Justiça Militar da União nas hipóteses constitucionais e legais; a vedação absoluta afirmada não existe.",
    "O rol de penas principais do CPM inclui morte, reclusão, detenção, prisão e impedimento; as antigas penas funcionais mencionadas foram revogadas.",
    "Os prazos e as exclusões do sursis militar não coincidem integralmente com a formulação do item; a generalização torna-o errado.",
    "A perda do posto e da patente do oficial depende do julgamento constitucionalmente competente; não decorre automaticamente da condenação.",
    "Deserção e dormir em serviço são propriamente militares; furto e peculato, por existirem também no direito comum, são impropriamente militares.",
    "No peculato culposo, a reparação anterior à sentença irrecorrível extingue a punibilidade tanto no CP quanto no CPM.",
    "Lei excepcional ou temporária tem ultratividade: rege o fato praticado durante sua vigência mesmo depois de cessada, independentemente de ser mais benéfica.",
    "No CPM, a tentativa sofre redução de um a dois terços, com possibilidade excepcional de aplicação da pena do consumado pela gravidade.",
    "Polícia judiciária militar é exercida pelas autoridades militares do CPPM; não se delega essa função ao representante do Ministério Público Militar.",
    "A delegação do IPM deve recair em oficial superior ao indiciado ou, se impossível, em oficial do mesmo posto mais antigo.",
    "O IPM termina em vinte dias com indiciado preso e quarenta dias com indiciado solto, prorrogáveis por mais vinte nesta última hipótese.",
    "A autoridade militar não pode arquivar IPM; ainda que conclua pela inexistência de crime, deve remeter os autos à autoridade competente.",
    "A ação penal militar é pública e do MPM, mas a garantia constitucional admite ação privada subsidiária diante de inércia.",
    "O CPPM admite decretação de prisão preventiva pelo auditor ou Conselho, inclusive de ofício, além de requerimento ou representação.",
    "A menagem cabe no limite legal e cessa com a sentença condenatória, mesmo que ainda exista recurso.",
    "O CPPM não estrutura liberdade provisória por fiança arbitrada pelo encarregado do IPM como afirma o item.",
    "Consumada a deserção, o oficial é agregado e a praça sem estabilidade é excluída, antes do processo especial correspondente.",
    "O Conselho Especial julga oficiais e dissolve-se ao final; o Permanente julga praças e tem composição renovada periodicamente.",
    "Historicidade descreve a construção progressiva dos direitos humanos por lutas e transformações sociais.",
    "A dependência entre a realização dos direitos traduz interdependência/indivisibilidade, não inalienabilidade.",
    "Embora seja declaração, a DUDH possui forte relevância normativa e interpretativa e influenciou costumes e tratados; não é meramente política.",
    "Direitos de terceira dimensão são difusos ou coletivos, como paz, desenvolvimento, meio ambiente e autodeterminação.",
    "A CADH proíbe pena de morte por delitos políticos/conexos, para menores de 18 ou maiores de 70 no fato e para gestantes.",
    "A exceção ao trabalho forçado exige decisão de autoridade judicial competente; resolução administrativa não basta.",
    "A CADH admite suspensão em emergência, mas preserva um núcleo inderrogável que inclui vida, integridade, personalidade e direitos políticos.",
    "Indivíduos não submetem casos diretamente à Corte; somente Estados-Partes e a Comissão possuem essa legitimidade.",
    "A sentença vincula o Estado que aceitou a competência, e a indenização pode ser executada internamente contra a Fazenda Pública.",
    "O esgotamento dos recursos internos admite exceções, entre elas demora injustificada e inexistência de devido processo ou acesso efetivo.",
]


def technical_comment(n: int, statement: str, answer: str) -> str:
    if n <= 20:
        return rules[n - 1]
    return specific_rules[n - 21]


def reference(n: int) -> str:
    m = matter(n)
    return {
        "Língua Portuguesa": "Textos-base do simulado e gramática normativa.",
        "Matemática": "Porcentagem e divisão proporcional.",
        "Noções de Informática": "Windows 11, segurança, navegadores e redes.",
        "Conhecimentos de Alagoas": "História e Geografia de Alagoas.",
        "Legislação Institucional PMAL": "Lei estadual 5.346/1992 e Lei 14.751/2023.",
        "Legislação Penal Especial": "Lei 9.455/1997, Lei 9.605/1998 e CTB.",
        "Direito Administrativo": "Teoria dos atos e do controle administrativo.",
        "Direito Constitucional": "Constituição Federal de 1988.",
        "Direito Processual Penal": "Código de Processo Penal.",
        "Direito Penal Militar": "Código Penal Militar.",
        "Direito Processual Penal Militar": "Código de Processo Penal Militar.",
        "Direitos Humanos": "Teoria geral e Convenção Americana sobre Direitos Humanos.",
    }[m]


questions = []
for i in range(1, 121):
    user = "BRANCO" if responses[i - 1] == "B" else responses[i - 1]
    g = answers[i - 1]
    blank = user == "BRANCO"
    ok = not blank and user == g
    classification = "recuperado" if ok else ("chute_lacuna" if blank else "erro_persistente")
    comment = technical_comment(i, raw_questions[i], g)
    questions.append({
        "id": f"sim_20260830_{i:03d}", "m": matter(i), "a": topics[i - 1],
        "n": "dificil" if ok else "cruel", "e": raw_questions[i], "g": "CERTO" if g == "C" else "ERRADO",
        "c": comment,
        "p": "Ponto decisivo da pegadinha: " + comment,
        "f": reference(i), "d": "Compare a afirmação com a regra central e justifique o C/E em uma frase.",
        "ce": "CEBRASPE · certo/errado", "src": "Simulado PMAL — 30/08/2026",
        "scope": "review_only", "reviewOnly": True, "reviewDate": "2026-08-30",
        "reviewClass": classification, "originalNumber": i, "userAnswer": user,
        "originalCorrect": ok, "originalBlank": blank, "gabaritoStatus": "provisorio",
        **({"textId": "sim_20260830_texto_1"} if i <= 11 else ({"textId": "sim_20260830_texto_2"} if i <= 20 else {})),
    })

correct = sum(q["originalCorrect"] for q in questions)
blank = sum(q["originalBlank"] for q in questions)
errors = 120 - correct - blank
if (correct, errors, blank) != (83, 31, 6):
    raise SystemExit(f"Unexpected score: {(correct, errors, blank)}")

essay = {
    "id": "sim_20260830_redacao", "title": "A violência estrutural contra a população negra no Brasil",
    "source": "Simulado PMAL — 30/08/2026", "date": "2026-08-30", "status": "pending",
    "scope": "review_only", "prompt": clean(pages[8]),
}

payload = (
    "/* Gerado de pdf_simulados_15355.pdf por scripts/build_mock_20260830.py. */\n"
    + "var SIM_TEXTS_20260830=" + json.dumps({
        "sim_20260830_texto_1": {"title": "Texto I — Rui Barbosa", "body": text1},
        "sim_20260830_texto_2": {"title": "Texto II — Euclides da Cunha", "body": text2},
    }, ensure_ascii=False, separators=(",", ":")) + ";\n"
    + "var SIM_ESSAY_20260830=" + json.dumps(essay, ensure_ascii=False, separators=(",", ":")) + ";\n"
    + "var REVIEW_QUESTIONS_20260830=" + json.dumps(questions, ensure_ascii=False, separators=(",", ":")) + ";\n"
)
OUT.write_text(payload, encoding="utf-8")
print(json.dumps({"questions": len(questions), "correct": correct, "errors": errors, "blank": blank, "output": str(OUT)}, ensure_ascii=False))
