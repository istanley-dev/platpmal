#!/usr/bin/env python3
import re
from pathlib import Path

P = Path('index.html')
src = P.read_text(encoding='utf-8')
MARKER = 'PMAL_CYCLE_FIX_V1'

if MARKER in src:
    print('Correção de ciclo já instalada.')
    raise SystemExit(0)

pattern = re.compile(
    r"function activateCycle2IfNeeded\(\)\{.*?\}\s*function startNewCycleManual\(\)\{.*?\}\s*function refreshLawBankLabels",
    re.S,
)
m = pattern.search(src)
if not m:
    raise SystemExit('ABORTADO: fluxo antigo de ciclo não encontrado exatamente como esperado.')

old = m.group(0)
# Guardas para não trocar um trecho errado do HTML gigante.
required = [
    "pmal26_cycle2_20260821_done",
    "pmal26_archive_",
    "Não foi possível iniciar novo ciclo.",
    "S.cycleId='ciclo_'+Date.now()",
]
for token in required:
    if token not in old:
        raise SystemExit(f'ABORTADO: marcador esperado ausente no fluxo antigo: {token}')

new = r'''/* PMAL_CYCLE_FIX_V1 — novo ciclo robusto, histórico preservado e sem regressão de cycleId */
function activateCycle2IfNeeded(){
  var flag='pmal26_cycle2_20260821_done';
  // Se a migração já ocorreu, NÃO sobrescreva o cycleId carregado do storage.
  // Isso permite que ciclos manuais posteriores sobrevivam ao reload.
  if(localStorage.getItem(flag)==='1')return;
  try{
    var raw=localStorage.getItem('pmal26')||'{}',snap=JSON.parse(raw);
    try{localStorage.setItem('pmal26_archive_ciclo1_20260821',raw);}catch(archiveErr){console.warn('Arquivo completo do ciclo 1 não coube no storage:',archiveErr);}
    var sig=collectLegacySignals(snap),oldHa=Array.isArray(snap.ha)?snap.ha:[],oldOk=oldHa.filter(function(x){return x&&x.ok;}).length;
    S.legacyEids=sig.eids;
    S.legacyTopics=sig.topics;
    S.legacySummary={cycleId:snap.cycleId||'ciclo1',total:oldHa.length,ok:oldOk,err:oldHa.length-oldOk,accuracy:oldHa.length?Math.round(oldOk/oldHa.length*100):0,archivedAt:'2026-08-21'};
    var keepPlan=S.plan||{examDate:''};
    S.ha=[];S.eids=new Set();S.AS={};S.round=0;S.log=[];S.metas={};S.xp=0;S.streak=0;S.lastDay='';S.plan=keepPlan;
    S.daily={d:'',q:0,rev:false,sim:false,red:false,metas:0,bonus:false,diaAnterior:false,leisFeitas:false};
    S.bibLidos={};S.leituraDia={d:'',keys:[],inReview:false};S.flash={cards:{}};S.weekly={lastDone:0};
    S.coverageQueue=[];S.weeklyAdjust=[];S.cycleId='ciclo2_20260821';
    SS();localStorage.setItem(flag,'1');
  }catch(e){console.warn('Falha ao ativar Ciclo 2:',e);}
}

function cycleArchiveSummary(snap,archiveKey){
  snap=snap||{};
  var ha=Array.isArray(snap.ha)?snap.ha:[],ok=ha.filter(function(x){return x&&x.ok;}).length;
  return {
    archiveKey:archiveKey,
    cycleId:snap.cycleId||S.cycleId||'ciclo_anterior',
    total:ha.length,
    ok:ok,
    err:ha.length-ok,
    accuracy:ha.length?Math.round(ok/ha.length*100):0,
    archivedAt:new Date().toISOString()
  };
}

function appendCycleHistory(summary){
  try{
    var k='pmal26_cycle_history',arr=JSON.parse(localStorage.getItem(k)||'[]');
    if(!Array.isArray(arr))arr=[];
    if(!arr.some(function(x){return x&&x.archiveKey===summary.archiveKey;}))arr.push(summary);
    // Resumos são pequenos; 30 ciclos é mais que suficiente e evita crescimento indefinido.
    localStorage.setItem(k,JSON.stringify(arr.slice(-30)));
  }catch(e){console.warn('Não foi possível gravar o resumo histórico do ciclo:',e);}
}

function saveFullOrCompactCycleArchive(key,raw,summary){
  try{
    localStorage.setItem(key,raw);
    return 'completo';
  }catch(fullErr){
    // Se o navegador estiver perto da cota, guarda apenas os dados necessários
    // para reconstruir desempenho/erros do ciclo, em vez de bloquear o novo ciclo.
    try{
      var snap=JSON.parse(raw||'{}');
      var compact={
        _type:'PMAL_CYCLE_ARCHIVE_COMPACT_V1',
        cycleId:snap.cycleId||summary.cycleId,
        archivedAt:summary.archivedAt,
        summary:summary,
        ha:Array.isArray(snap.ha)?snap.ha:[],
        eids:Array.isArray(snap.eids)?snap.eids:[],
        AS:snap.AS||{},
        log:Array.isArray(snap.log)?snap.log.slice(-500):[]
      };
      localStorage.setItem(key,JSON.stringify(compact));
      return 'compacto';
    }catch(compactErr){
      console.warn('Arquivo detalhado do ciclo não coube no storage:',compactErr);
      return 'resumo';
    }
  }
}

function startNewCycleManual(){
  if(!confirm('Arquivar o ciclo atual e iniciar outro com estatísticas e leitura zeradas? O histórico será preservado no navegador.'))return;
  try{
    var raw=localStorage.getItem('pmal26')||'{}',snap;
    try{snap=JSON.parse(raw);}catch(parseErr){
      // Estado salvo corrompido não deve impedir o usuário de começar um ciclo novo.
      snap={ha:S.ha||[],eids:[...(S.eids||new Set())],AS:S.AS||{},log:S.log||[],cycleId:S.cycleId||'ciclo_anterior'};
      raw=JSON.stringify(snap);
    }

    var archiveKey='pmal26_archive_'+new Date().toISOString().slice(0,10)+'_'+Date.now();
    var summary=cycleArchiveSummary(snap,archiveKey);

    // Tenta arquivar antes do reset. Se a cota estiver cheia, repetiremos depois que
    // o estado ativo for reduzido, liberando espaço — esse era o ponto que travava o botão.
    var archiveMode='pendente';
    try{localStorage.setItem(archiveKey,raw);archiveMode='completo';}catch(quotaErr){console.warn('Storage cheio; arquivo será tentado após o reset:',quotaErr);}

    var sig=collectLegacySignals(snap);
    if(!(S.legacyEids instanceof Set))S.legacyEids=new Set(Array.isArray(S.legacyEids)?S.legacyEids:[]);
    if(!S.legacyTopics||typeof S.legacyTopics!=='object')S.legacyTopics={};
    Array.from(sig.eids).forEach(function(id){S.legacyEids.add(id);});
    Object.keys(sig.topics).forEach(function(k){S.legacyTopics[k]=(S.legacyTopics[k]||0)+sig.topics[k];});
    S.legacySummary=summary;

    // Zera somente o que pertence às métricas do ciclo. Preferências, data da prova,
    // redações e itens sinalizados continuam preservados.
    S.ha=[];S.eids=new Set();S.AS={};S.log=[];S.round=0;S.metas={};S.xp=0;S.streak=0;S.lastDay='';
    S.daily={d:'',q:0,rev:false,sim:false,red:false,metas:0,bonus:false,diaAnterior:false,leisFeitas:false};
    S.bibLidos={};S.leituraDia={d:'',keys:[],inReview:false};S.flash={cards:{}};S.weekly={lastDone:0};
    S.coverageQueue=[];S.weeklyAdjust=[];
    S.cycleId='ciclo_'+Date.now();
    var newCycleId=S.cycleId;

    SS();
    var saved=JSON.parse(localStorage.getItem('pmal26')||'{}');
    if(saved.cycleId!==newCycleId)throw new Error('O novo estado não foi persistido no navegador.');

    // Se a primeira cópia falhou por cota, o reset acima tornou pmal26 muito menor.
    if(archiveMode==='pendente')archiveMode=saveFullOrCompactCycleArchive(archiveKey,raw,summary);
    summary.archiveMode=archiveMode;
    appendCycleHistory(summary);

    toast('✅ Novo ciclo iniciado · histórico '+(archiveMode==='completo'?'arquivado':'preservado em modo '+archiveMode)+'.');
    setTimeout(function(){location.reload();},450);
  }catch(e){
    console.error('Falha ao iniciar novo ciclo:',e);
    toast('❌ Não foi possível iniciar novo ciclo: '+(e&&e.message?e.message:'erro de armazenamento'));
  }
}

function refreshLawBankLabels'''

patched = src[:m.start()] + new + src[m.end():]

# Validações estáticas essenciais.
checks = [
    'PMAL_CYCLE_FIX_V1',
    "if(localStorage.getItem(flag)==='1')return;",
    "S.cycleId='ciclo_'+Date.now()",
    'saveFullOrCompactCycleArchive',
    'appendCycleHistory',
    "saved.cycleId!==newCycleId",
]
for token in checks:
    if token not in patched:
        raise SystemExit(f'ABORTADO: correção incompleta; faltou {token}')

P.write_text(patched, encoding='utf-8')
print('Fluxo de novo ciclo corrigido com preservação de histórico e fallback de cota.')
