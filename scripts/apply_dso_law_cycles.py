#!/usr/bin/env python3
from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
START='<!-- PMAL_DSO_LAW_CYCLES_V1_START -->'
END='<!-- PMAL_DSO_LAW_CYCLES_V1_END -->'
if START in s and END in s:
    a=s.index(START); b=s.index(END,a)+len(END)
    s=s[:a]+s[b:]

block=r'''<!-- PMAL_DSO_LAW_CYCLES_V1_START -->
<script id="pmal-dso-law-cycles-v1">
(function(){
/* PMAL_DSO_LAW_CYCLES_V1
   Ordem de leitura: planos DSO pós-edital, ciclos 1, 2 e 3.
   O plano define a ORDEM. O conteúdo jurídico exibido continua vindo do Banco de Leis atualizado da plataforma.
*/
var PMAL_DSO_LAW_PLAN=[
 {cycle:1,title:'Ciclo 1 — Base constitucional, penal, administrativa e legislação especial',days:[
  {n:1,label:'CF/88 — art. 5º',seg:[['CF','5','5']]},
  {n:2,label:'CF/88 — arts. 6º a 11',seg:[['CF','6','11']]},
  {n:3,label:'CF/88 — arts. 12 a 17',seg:[['CF','12','17']]},
  {n:4,label:'CF/88 — arts. 18 a 36',seg:[['CF','18','36']]},
  {n:5,label:'Código Penal — arts. 1º a 28',seg:[['CP','1','28']]},
  {n:6,label:'CF/88 — arts. 136 a 144',seg:[['CF','136','144']]},
  {n:7,label:'Lei 14.133/2021 — arts. 1º a 44',seg:[['L14133','1','44']]},
  {n:8,label:'Lei 14.133/2021 — arts. 45 a 71',seg:[['L14133','45','71']]},
  {n:9,label:'Lei 14.133/2021 — arts. 72 a 114',seg:[['L14133','72','114']]},
  {n:10,label:'Lei 14.133/2021 — arts. 115 a 150',seg:[['L14133','115','150']]},
  {n:11,label:'Lei 14.133/2021 — arts. 151 a 194',seg:[['L14133','151','194']]},
  {n:12,label:'CADH — arts. 1º a 40',seg:[['CADH','1','40']]},
  {n:13,label:'CADH — arts. 41 a 82',seg:[['CADH','41','82']]},
  {n:14,label:'CPP — arts. 4º a 23',seg:[['CPP','4','23']]},
  {n:15,label:'CPP — arts. 24 a 62',seg:[['CPP','24','62']]},
  {n:16,label:'Lei 14.751/2023 — Lei Orgânica Nacional das PMs/CBMs',seg:[['LO','*','*']]},
  {n:17,label:'Lei 7.716/1989 + Lei 8.072/1990 — racismo e crimes hediondos',seg:[['L7716','*','*'],['L8072','*','*']]},
  {n:18,label:'Lei 13.869/2019 — Abuso de Autoridade',seg:[['L13869','*','*']]},
  {n:19,label:'Lei 10.826/2003 — Estatuto do Desarmamento',seg:[['L10826','*','*']]},
  {n:20,label:'Lei 12.850/2013 — Organização Criminosa',seg:[['L12850','*','*']]},
  {n:21,label:'Lei 9.605/1998 — Crimes Ambientais',seg:[['L9605','*','*']]},
  {n:22,label:'Lei 11.340/2006 — Maria da Penha',seg:[['L11340','*','*']]},
  {n:23,label:'Lei 9.455/1997 + Lei 7.960/1989 — Tortura e Prisão Temporária',seg:[['L9455','*','*'],['L7960','*','*']]},
  {n:24,label:'Lei 9.099/1995 — arts. 1º a 59',seg:[['L9099','1','59']]},
  {n:25,label:'Lei 9.099/1995 — arts. 60 a 97',seg:[['L9099','60','97']]},
  {n:26,label:'Lei 11.343/2006 — arts. 1º a 47',seg:[['L11343','1','47']]},
  {n:27,label:'Lei 11.343/2006 — arts. 48 a 75',seg:[['L11343','48','75']]},
  {n:28,label:'Lei 10.259/2001 — Juizados Especiais Federais',seg:[['L10259','*','*']]}
 ]},
 {cycle:2,title:'Ciclo 2 — Penal Militar, Processo Penal Militar, ECA e CTB',days:[
  {n:1,label:'CPM — arts. 1º a 12',seg:[['CPM','1','12']]},
  {n:2,label:'CPPM — arts. 1º a 28',seg:[['CPPM','1','28']]},
  {n:3,label:'CPM — arts. 13 a 25',seg:[['CPM','13','25']]},
  {n:4,label:'CPPM — arts. 29 a 46',seg:[['CPPM','29','46']]},
  {n:5,label:'CPM — arts. 26 a 29 e 48 a 68',seg:[['CPM','26','29'],['CPM','48','68']]},
  {n:6,label:'CPPM — arts. 243 a 271',seg:[['CPPM','243','271']]},
  {n:7,label:'CPM — arts. 69 a 108',seg:[['CPM','69','108']]},
  {n:8,label:'CPPM — arts. 451 a 460',seg:[['CPPM','451','460']]},
  {n:9,label:'CPM — arts. 109 a 135',seg:[['CPM','109','135']]},
  {n:10,label:'ECA — arts. 1º a 32',seg:[['L8069','1','32']]},
  {n:11,label:'ECA — arts. 33 a 73',seg:[['L8069','33','73']]},
  {n:12,label:'CPM — arts. 136 a 194',seg:[['CPM','136','194']]},
  {n:13,label:'CTB — arts. 1º a 73',seg:[['L9503','1','73']]},
  {n:14,label:'CPM — arts. 195 a 253',seg:[['CPM','195','253']]},
  {n:15,label:'CPM — arts. 254 a 310',seg:[['CPM','254','310']]},
  {n:16,label:'CPM — arts. 311 a 354',seg:[['CPM','311','354']]},
  {n:17,label:'ECA — arts. 74 a 109',seg:[['L8069','74','109']]},
  {n:18,label:'CTB — arts. 74 a 129-B',seg:[['L9503','74','129B']]},
  {n:19,label:'CTB — arts. 130 a 200',seg:[['L9503','130','200']]},
  {n:20,label:'ECA — arts. 110 a 163',seg:[['L8069','110','163']]},
  {n:21,label:'ECA — arts. 194 a 197',seg:[['L8069','194','197']]},
  {n:22,label:'ECA — arts. 197-A a 224',seg:[['L8069','197A','224']]},
  {n:23,label:'ECA — arts. 225 a 244-C',seg:[['L8069','225','244C']]},
  {n:24,label:'CTB — arts. 201 a 268-A',seg:[['L9503','201','268A']]},
  {n:25,label:'CTB — arts. 269 a 341',seg:[['L9503','269','341']]},
  {n:26,label:'ECA — arts. 245 a 267',seg:[['L8069','245','267']]}
 ]},
 {cycle:3,title:'Ciclo 3 — Legislação Institucional PMAL',days:[
  {n:1,label:'Lei Estadual 5.346/1992 — arts. 1º a 14',seg:[['Lei5346','1','14']]},
  {n:2,label:'Lei Estadual 5.346/1992 — arts. 15 a 30',seg:[['Lei5346','15','30']]},
  {n:3,label:'Lei Estadual 5.346/1992 — arts. 31 a 52',seg:[['Lei5346','31','52']]},
  {n:4,label:'Lei Estadual 5.346/1992 — arts. 53 a 88',seg:[['Lei5346','53','88']]},
  {n:5,label:'Lei Estadual 5.346/1992 — arts. 89 a 104',seg:[['Lei5346','89','104']]},
  {n:6,label:'Lei Estadual 5.346/1992 — arts. 105 a 135',seg:[['Lei5346','105','135']]},
  {n:7,label:'Decreto Estadual 37.042/1996 — arts. 1º a 25',seg:[['RD','1','25']]},
  {n:8,label:'Decreto Estadual 37.042/1996 — arts. 26 a 38',seg:[['RD','26','38']]},
  {n:9,label:'Decreto Estadual 37.042/1996 — arts. 39 a 66',seg:[['RD','39','66']]},
  {n:10,label:'Decreto Estadual 37.042/1996 — arts. 67 a 81',seg:[['RD','67','81']]},
  {n:11,label:'Decreto Estadual 37.042/1996 — arts. 82 a 107',seg:[['RD','82','107']]}
 ]}
];
window.PMAL_DSO_LAW_PLAN=PMAL_DSO_LAW_PLAN;
var PMAL_DSO_TOTAL_DAYS=65;
function pmalDsoCycle(c){return PMAL_DSO_LAW_PLAN.filter(function(x){return x.cycle===c;})[0]||PMAL_DSO_LAW_PLAN[0];}
function pmalDsoEnsure(){
 if(!S.lawDso||S.lawDso.version!==1){S.lawDso={version:1,cycle:1,day:1,round:1,history:{}};if(typeof SS==='function')SS();}
 if(!S.lawDso.history)S.lawDso.history={};
 if(!S.lawDso.round)S.lawDso.round=1;
 var c=pmalDsoCycle(S.lawDso.cycle);if(!c){S.lawDso.cycle=1;c=pmalDsoCycle(1);}
 if(S.lawDso.day<1||S.lawDso.day>c.days.length)S.lawDso.day=1;
 return S.lawDso;
}
function pmalDsoDay(){var st=pmalDsoEnsure(),c=pmalDsoCycle(st.cycle);return c.days[st.day-1];}
function pmalDsoToken(){var st=pmalDsoEnsure();return st.round+'-'+st.cycle+'-'+st.day;}
function pmalDsoArticleCode(v){
 v=String(v||'').replace(/[-‐‑–—\.\sº°]/g,'').toUpperCase();var m=v.match(/^(\d+)([A-Z]*)$/);if(!m)return null;
 var suf=0;for(var i=0;i<m[2].length;i++)suf=suf*27+(m[2].charCodeAt(i)-64);
 return parseInt(m[1],10)*1000+suf;
}
function pmalDsoKeyParts(k){
 if(k==='Lei 5.346')return {p:'Lei5346',art:null};
 var p=k.split(' ')[0],rest=k.slice(p.length).trim();
 if(p==='Lei5346')return {p:p,art:rest||null};
 return {p:p,art:rest||null};
}
function pmalDsoKeysForDay(day){
 var all=Object.keys(DISP||{}),out=[],used={};
 (day.seg||[]).forEach(function(seg){
  var p=seg[0],lo=seg[1],hi=seg[2],matches=[];
  all.forEach(function(k){
   var kp=pmalDsoKeyParts(k);if(kp.p!==p)return;
   if(lo==='*'){matches.push(k);return;}
   if(!kp.art)return;
   var a=pmalDsoArticleCode(kp.art),l=pmalDsoArticleCode(lo),h=pmalDsoArticleCode(hi);
   if(a!==null&&l!==null&&h!==null&&a>=l&&a<=h)matches.push(k);
  });
  matches.sort(function(a,b){return (pmalDsoArticleCode(pmalDsoKeyParts(a).art)||-1)-(pmalDsoArticleCode(pmalDsoKeyParts(b).art)||-1);});
  if(!matches.length){
   var base=all.filter(function(k){var x=pmalDsoKeyParts(k);return x.p===p&&!x.art;})[0];if(base)matches=[base];
  }
  matches.forEach(function(k){if(!used[k]){used[k]=1;out.push(k);}});
 });
 return out;
}
function pmalDsoCurrentRoundDone(){var st=pmalDsoEnsure(),n=0;Object.keys(st.history).forEach(function(k){var r=st.history[k];if(r&&r.round===st.round)n++;});return n;}
function pmalDsoDueReviews(){
 var st=pmalDsoEnsure(),now=Date.now(),DAY=86400000,due=[];
 Object.keys(st.history).forEach(function(k){var r=st.history[k];if(!r||!r.ts)return;if(!r.reviews)r.reviews={};
  [1,7,21].forEach(function(d){var stage='d'+d;if(!r.reviews[stage]&&now-r.ts>=d*DAY)due.push({histKey:k,rec:r,stage:stage,days:d,keys:r.keys||[]});});
 });
 due.sort(function(a,b){return a.days-b.days||a.rec.ts-b.rec.ts;});return due;
}
function pmalDsoReviewKeys(entries){var o={},r=[];(entries||pmalDsoDueReviews()).forEach(function(e){(e.keys||[]).forEach(function(k){if(DISP[k]&&!o[k]){o[k]=1;r.push(k);}});});return r;}
function pmalDsoMarkReviews(entries){var st=pmalDsoEnsure();(entries||[]).forEach(function(e){if(!st.history[e.histKey])return;if(!st.history[e.histKey].reviews)st.history[e.histKey].reviews={};st.history[e.histKey].reviews[e.stage]=Date.now();});if(typeof SS==='function')SS();}

/* Camada de cobertura exclusiva do Banco de Leis: não entra em QQ.filter/simulados gerais. */
var PMAL_LAW_COVERAGE_CACHE=null;
function pmalLawCovId(k){return 'lawcov_'+String(k).toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'')+'_v1';}
function pmalLawArticleFmt(a){a=String(a||'');return a.replace(/^(\d+)([A-Za-z]+)$/,'$1-$2');}
function pmalLawFoundation(k){
 var x=pmalDsoKeyParts(k),a=x.art?(', art. '+pmalLawArticleFmt(x.art)+'.'):'.';
 var m={CF:'CF/88',CP:'CP',CPP:'CPP',CPM:'CPM',CPPM:'CPPM',CADH:'CADH',Lei5346:'Lei 5.346/1992',RD:'Decreto 37.042/1996',LO:'Lei 14.751/2023',L14133:'Lei 14.133/2021',L11343:'Lei 11.343/2006',L8069:'Lei 8.069/1990',L8072:'Lei 8.072/1990',L13869:'Lei 13.869/2019',L11340:'Lei 11.340/2006',L10826:'Lei 10.826/2003',L9503:'Lei 9.503/1997',L12850:'Lei 12.850/2013',L9455:'Lei 9.455/1997',L7716:'Lei 7.716/1989',L9605:'Lei 9.605/1998',L7960:'Lei 7.960/1989',L9099:'Lei 9.099/1995',L10259:'Lei 10.259/2001',L8429:'Lei 8.429/1992',L8987:'Lei 8.987/1995',L9784:'Lei 9.784/1999',L8112:'Lei 8.112/1990',L4717:'Lei 4.717/1965',L13300:'Lei 13.300/2016',LEP:'Lei 7.210/1984',L12016:'Lei 12.016/2009',L9474:'Lei 9.474/1997',L12830:'Lei 12.830/2013',L12037:'Lei 12.037/2009',L9507:'Lei 9.507/1997',L9296:'Lei 9.296/1996'};
 return (m[x.p]||x.p)+a;
}
function pmalLawSubject(k){var p=pmalDsoKeyParts(k).p;if(p==='CF')return 'Direito Constitucional';if(p==='CP')return 'Direito Penal';if(p==='CPP')return 'Direito Processual Penal';if(p==='CPM')return 'Direito Penal Militar';if(p==='CPPM')return 'Direito Processual Penal Militar';if(p==='CADH')return 'Direitos Humanos';if(p==='Lei5346'||p==='RD'||p==='LO')return 'Legislação Institucional PMAL';if(['L14133','L8429','L8987','L9784','L8112','L4717','L13300','L12016'].indexOf(p)>=0)return 'Direito Administrativo';return 'Legislação Penal Especial';}
function lawCoverageQuestions(){
 if(PMAL_LAW_COVERAGE_CACHE)return PMAL_LAW_COVERAGE_CACHE;
 PMAL_LAW_COVERAGE_CACHE=Object.keys(DISP||{}).map(function(k){
  var txt=String(DISP[k]||''),parts=txt.split(/\n\n⚠/),core=parts[0].trim(),warn=parts.length>1?('⚠ '+parts.slice(1).join('\n\n⚠').trim()):'';
  return {id:pmalLawCovId(k),e:'Julgue o item à luz da legislação indicada. '+core,g:'CERTO',m:pmalLawSubject(k),a:'Lei seca — '+(typeof labelFromDispKey==='function'?labelFromDispKey(k):k),c:'CERTO. O item reproduz o conteúdo do dispositivo indicado. '+core+(warn?' '+warn:''),p:warn||'Atenção à literalidade, às exceções, aos sujeitos, aos prazos e às competências do dispositivo.',f:pmalLawFoundation(k),d:'Cobertura exclusiva da Biblioteca Legal',n:'medio',ce:'lei seca',lawOnly:true,lawKey:k,reviewOnly:true,scope:'review_only',reviewClass:'lei_seca'};
 });return PMAL_LAW_COVERAGE_CACHE;
}
window.lawCoverageQuestions=lawCoverageQuestions;
if(typeof QQ!=='undefined'&&!QQ.__lawCoverageFindV1){
 QQ.__lawCoverageFindV1=true;
 QQ.find=function(cb,thisArg){var r=Array.prototype.find.call(QQ,cb,thisArg);if(r!==undefined)return r;return Array.prototype.find.call(lawCoverageQuestions(),cb,thisArg);};
}
if(typeof buildKeyToQids==='function'){
 var pmalDsoBaseBuildKeyToQids=buildKeyToQids;
 window.buildKeyToQids=function(){var map=pmalDsoBaseBuildKeyToQids();Object.keys(DISP||{}).forEach(function(k){if(!map[k]||!map[k].length)map[k]=[pmalLawCovId(k)];});return map;};
}

window.computeTodaysArticles=function(){var day=pmalDsoDay(),keys=pmalDsoKeysForDay(day);return {N:PMAL_DSO_TOTAL_DAYS,remaining:PMAL_DSO_TOTAL_DAYS-pmalDsoCurrentRoundDone(),perDay:keys.length,todays:keys,inReview:false};};
window.touchLeituraDia=function(){
 var st=pmalDsoEnsure(),token=pmalDsoToken(),day=pmalDsoDay(),keys=pmalDsoKeysForDay(day),due=pmalDsoDueReviews(),reviewKeys=pmalDsoReviewKeys(due),changed=false;
 if(!S.leituraDia||S.leituraDia.planToken!==token||!S.leituraDia.dsoPlanV1){S.leituraDia={d:(typeof todayStr==='function'?todayStr():''),keys:keys,reviewKeys:reviewKeys,planToken:token,dsoPlanV1:true,inReview:false};changed=true;}
 else{S.leituraDia.keys=keys;S.leituraDia.reviewKeys=reviewKeys;S.leituraDia.d=(typeof todayStr==='function'?todayStr():S.leituraDia.d);}
 if(changed&&typeof SS==='function')SS();
};
window.readingPlanInfo=function(){
 touchLeituraDia();var st=pmalDsoEnsure(),c=pmalDsoCycle(st.cycle),day=pmalDsoDay(),done=pmalDsoCurrentRoundDone(),due=pmalDsoDueReviews();
 return {N:PMAL_DSO_TOTAL_DAYS,lidos:done,todays:S.leituraDia.keys||[],inReview:false,cycle:st.cycle,day:st.day,cycleDays:c.days.length,round:st.round,label:day.label,dueReviews:due.length,reviewKeys:S.leituraDia.reviewKeys||[]};
};
window.renderLeituraSub=function(){
 var info=readingPlanInfo(),pct=Math.round(info.lidos/info.N*100),bar=document.getElementById('leitura-bar'),sub=document.getElementById('leitura-sub');if(bar)bar.style.width=pct+'%';
 if(sub)sub.innerHTML='<b>Rodada '+info.round+' · Ciclo '+info.cycle+' · Dia '+info.day+'/'+info.cycleDays+'</b> — '+esc(info.label)+'<br><span class="tmut">Progresso do plano: <b>'+info.lidos+'/'+info.N+' dias</b> ('+pct+'%) · '+info.todays.length+' dispositivo(s) disponível(is) no banco · revisões vencidas D+1/D+7/D+21: <b>'+info.dueReviews+'</b>.</span>';
 return info;
};
window.leituraDoDiaFeita=function(){touchLeituraDia();var ks=S.leituraDia.keys||[];return ks.every(function(k){return !!S.bibLidos[k];});};
function pmalDsoPanel(){
 var hoje=document.getElementById('leitura-hoje');if(!hoje)return;var old=document.getElementById('pmal-dso-law-mission');if(old)old.remove();var info=readingPlanInfo(),due=pmalDsoDueReviews();
 var stages={1:0,7:0,21:0};due.forEach(function(x){stages[x.days]=(stages[x.days]||0)+1;});
 var html='<div id="pmal-dso-law-mission" class="card mb16" style="border:1px solid var(--bdr);padding:14px;background:linear-gradient(135deg,rgba(37,99,235,.08),rgba(245,158,11,.06))">'+
 '<div style="font-weight:900;font-size:15px;margin-bottom:5px">⚖️ MISSÃO LEGAL · CICLO '+info.cycle+' · DIA '+info.day+'</div><div style="font-weight:800;margin-bottom:9px">'+esc(info.label)+'</div>'+
 '<div class="tmut ts" style="line-height:1.55">📖 Leitura guiada: <b>'+info.todays.length+'</b> cartão(ões) do banco · 🎯 treino CEBRASPE com troca de conceitos/literalidade · ⏱️ prazos e números · 🔀 não confunda · ⚖️ jurisprudência quando houver · 🔥 erros anteriores.</div>'+
 '<div class="tmut ts" style="margin-top:7px">Revisão espaçada pendente: <b>D+1 '+stages[1]+'</b> · <b>D+7 '+stages[7]+'</b> · <b>D+21 '+stages[21]+'</b>. O ciclo só avança quando os dispositivos disponíveis deste dia forem lidos.</div>'+
 '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:11px"><button class="btn" onclick="startLeituraQuiz()">🎯 Treinar CEBRASPE</button><button class="btn" onclick="completeDsoLawDay()">✅ Concluir dia e avançar</button></div>'+ 
 '<div class="tmut" style="font-size:10px;margin-top:8px">A sequência segue os planos DSO. A plataforma usa o conteúdo jurídico atualizado do Banco de Leis; o PDF serve como roteiro de ordem e faixas.</div></div>';
 hoje.insertAdjacentHTML('beforebegin',html);
}
if(typeof renderLeituraDia==='function'){
 var pmalDsoBaseRenderLeituraDia=renderLeituraDia;
 window.renderLeituraDia=function(){var r=pmalDsoBaseRenderLeituraDia.apply(this,arguments);pmalDsoPanel();return r;};
}
if(typeof ldRead==='function'){
 var pmalDsoBaseLdRead=ldRead;
 window.ldRead=function(k){var r=pmalDsoBaseLdRead.apply(this,arguments);pmalDsoPanel();return r;};
}
window.completeDsoLawDay=function(){
 touchLeituraDia();var st=pmalDsoEnsure(),day=pmalDsoDay(),keys=S.leituraDia.keys||[],unread=keys.filter(function(k){return !S.bibLidos[k];});
 if(unread.length){toast('📖 Ainda faltam '+unread.length+' dispositivo(s) deste dia. Abra e leia antes de avançar.');return;}
 var token=pmalDsoToken();if(!st.history[token])st.history[token]={ts:Date.now(),round:st.round,cycle:st.cycle,day:st.day,label:day.label,keys:keys.slice(),reviews:{}};
 var c=pmalDsoCycle(st.cycle);if(st.day<c.days.length)st.day++;else if(st.cycle<PMAL_DSO_LAW_PLAN.length){st.cycle++;st.day=1;}else{st.round++;st.cycle=1;st.day=1;toast('🏆 Os 3 ciclos foram concluídos. Iniciando nova rodada de manutenção.');}
 S.leituraDia=null;if(typeof SS==='function')SS();if(typeof renderLeituraDia==='function')renderLeituraDia();toast('✅ Dia concluído. Próxima faixa carregada sem depender do calendário.');
};
function pmalDsoQClass(q){var s=((q&&q.e)||'')+' '+((q&&q.p)||'')+' '+((q&&q.c)||'');if(/\b(STF|STJ|súmula|sumula|tema|jurisprud)/i.test(s))return 'jurisprudência';if(/\b\d+\s*(dias?|horas?|meses?|anos?|%|por cento)|prazo|percentual|maior de|menor de/i.test(s))return 'prazos/números';if(/\b(somente|apenas|exclusivamente|sempre|nunca|obrigatoriamente|vedad[oa]|facultad[oa]|pode|deve)\b/i.test(s))return 'troca de conceitos';return 'lei seca';}
function pmalDsoDiversify(arr){var buckets={},out=[];(arr||[]).forEach(function(q){var c=pmalDsoQClass(q);if(!buckets[c])buckets[c]=[];buckets[c].push(q);});Object.keys(buckets).forEach(function(k){buckets[k].sort(function(){return Math.random()-.5;});});var names=['troca de conceitos','prazos/números','jurisprudência','lei seca'],go=true;while(go){go=false;names.forEach(function(n){if(buckets[n]&&buckets[n].length){out.push(buckets[n].shift());go=true;}});}return out;}
window.startLeituraQuiz=function(){
 touchLeituraDia();var newKeys=S.leituraDia.keys||[],dueEntries=pmalDsoDueReviews(),reviewKeys=pmalDsoReviewKeys(dueEntries),errObj=(typeof lawErrorKeys==='function'?lawErrorKeys():{}),errKeys=Object.keys(errObj||{}).filter(function(k){return DISP[k];}),map=buildKeyToQids(),poolAll=QQ.concat(lawCoverageQuestions()),byId={};poolAll.forEach(function(q){byId[q.id]=q;});
 function fromKeys(keys){var ids={},r=[];(keys||[]).forEach(function(k){(map[k]||[]).forEach(function(id){ids[id]=1;});});Object.keys(ids).forEach(function(id){if(byId[id])r.push(byId[id]);});return pmalDsoDiversify(r);}
 var fresh=fromKeys(newKeys),rev=fromKeys(reviewKeys),errs=fromKeys(errKeys),chosen=[],seen={};function take(arr,n){for(var i=0;i<arr.length&&n>0;i++){var q=arr[i];if(!seen[q.id]){seen[q.id]=1;chosen.push(q);n--;}}}
 take(fresh,12);take(rev,5);take(errs,3);take(fresh.concat(rev,errs),20-chosen.length);
 if(!chosen.length){toast('Ainda não há questão utilizável para esta faixa do ciclo. Leia os cartões e conclua o dia.');return;}
 if(rev.length)pmalDsoMarkReviews(dueEntries);
 chosen.sort(function(){return Math.random()-.5;});S.round++;S.sq=chosen.slice(0,20);S.ci=0;S.sa=[];S._lawDsoSession={token:pmalDsoToken(),fresh:fresh.length,review:rev.length,errors:errs.length};var h=document.getElementById('hsc');if(h)h.style.display='none';sv('quiz');renderQ();document.querySelectorAll('.nb').forEach(function(b){b.classList.remove('act');});
 var cc={};chosen.forEach(function(q){var c=pmalDsoQClass(q);cc[c]=(cc[c]||0)+1;});toast('⚖️ Treino legal: '+chosen.length+' itens · '+(cc['troca de conceitos']||0)+' troca de conceitos · '+(cc['prazos/números']||0)+' prazos/números · '+(cc['jurisprudência']||0)+' jurisprudência.');
};
pmalDsoEnsure();
})();
</script>
<!-- PMAL_DSO_LAW_CYCLES_V1_END -->'''

pos=s.lower().rfind('</body>')
if pos<0:
    raise SystemExit('ERRO: </body> não encontrado')
s=s[:pos]+block+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
print('PMAL_DSO_LAW_CYCLES_V1 aplicado')
