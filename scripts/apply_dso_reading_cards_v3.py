#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
s = p.read_text(encoding="utf-8")

# Remove the previous full-text reader: it changed the original Meta de Leitura UX.
for start, end in [
    ("<!-- PMAL_DSO_FULL_LAW_READER_V2_START -->", "<!-- PMAL_DSO_FULL_LAW_READER_V2_END -->"),
    ("<!-- PMAL_DSO_READING_CARDS_V3_START -->", "<!-- PMAL_DSO_READING_CARDS_V3_END -->"),
]:
    if start in s and end in s:
        a = s.index(start)
        b = s.index(end, a) + len(end)
        s = s[:a] + s[b:]

block = r'''<!-- PMAL_DSO_READING_CARDS_V3_START -->
<style>
#leitura-hoje .dso-day-head{padding:11px 13px;margin:0 0 10px;border:1px solid var(--bdr);border-radius:12px;background:linear-gradient(135deg,rgba(37,99,235,.08),rgba(16,185,129,.05))}
#leitura-hoje .dso-day-title{font-weight:900;font-size:14px;line-height:1.4}
#leitura-hoje .dso-day-meta{font-size:11px;color:var(--mut);line-height:1.5;margin-top:4px}
#leitura-hoje .dso-section-title{font-weight:900;font-size:12px;margin:13px 2px 7px;color:var(--txt)}
#leitura-hoje .dso-article-text{font-size:14px;line-height:1.72;white-space:pre-wrap;overflow-wrap:anywhere;color:var(--txt)}
#leitura-hoje .dso-read-badge{font-size:11px;color:var(--mut);font-weight:700;flex:1;text-align:right}
#leitura-hoje .dso-read-badge.done{color:#166534}
#pmal-fixacao-hoje{margin-top:15px;padding-top:12px;border-top:1px dashed var(--bdr)}
#pmal-fixacao-hoje .dso-fix-title{font-weight:900;font-size:13px;margin-bottom:4px}
#pmal-fixacao-hoje .dso-fix-meta{font-size:10.5px;line-height:1.45;color:var(--mut);margin-bottom:9px}
#pmal-dso-law-mission .dso-mission-progress{font-weight:800}
@media(max-width:600px){#leitura-hoje .dso-article-text{font-size:15px;line-height:1.78}}
</style>
<script>
(function(){
'use strict';
var V3_MANIFEST=null,V3_MANIFEST_P=null,V3_TEXT_CACHE={},V3_CURRENT=null;

function escV3(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function planV3(){return window.PMAL_DSO_LAW_PLAN||[];}
function stateV3(){
 if(!S.lawDso||typeof S.lawDso!=='object')S.lawDso={version:1,cycle:1,day:1,round:1,history:{}};
 if(!S.lawDso.history)S.lawDso.history={};
 if(!S.lawDso.round)S.lawDso.round=1;
 return S.lawDso;
}
function cycleV3(c){var p=planV3();for(var i=0;i<p.length;i++)if(p[i].cycle===c)return p[i];return p[0]||null;}
function dayV3(){var st=stateV3(),c=cycleV3(st.cycle);return c&&c.days?c.days[st.day-1]:null;}
function tokenV3(){var st=stateV3();return st.round+'-'+st.cycle+'-'+st.day;}
function storeV3(){if(!S.lawDsoReadingV3||typeof S.lawDsoReadingV3!=='object')S.lawDsoReadingV3={};return S.lawDsoReadingV3;}
function recV3(token){var st=storeV3();if(!st[token])st[token]={read:{},done:false};if(!st[token].read)st[token].read={};return st[token];}
function saveV3(){if(typeof SS==='function')SS();}
function fixationKeysV3(){return (S.leituraDia&&Array.isArray(S.leituraDia.keys))?S.leituraDia.keys.slice():[];}

function loadManifestV3(){
 if(V3_MANIFEST)return Promise.resolve(V3_MANIFEST);
 if(V3_MANIFEST_P)return V3_MANIFEST_P;
 V3_MANIFEST_P=fetch('law-reading/manifest.json?v=4',{cache:'no-cache'}).then(function(r){if(!r.ok)throw new Error('manifest '+r.status);return r.json();}).then(function(m){if(!m||m.totalDays!==65||!Array.isArray(m.days))throw new Error('manifesto dos 65 dias incompleto');V3_MANIFEST=m;return m;}).catch(function(e){V3_MANIFEST_P=null;throw e;});
 return V3_MANIFEST_P;
}
function entryV3(man){var st=stateV3();return (man.days||[]).filter(function(x){return x.cycle===st.cycle&&x.day===st.day;})[0]||null;}
function loadTextV3(e){
 if(V3_TEXT_CACHE[e.path])return Promise.resolve(V3_TEXT_CACHE[e.path]);
 return fetch(e.path+'?v=4',{cache:'force-cache'}).then(function(r){if(!r.ok)throw new Error('texto '+r.status);return r.text();}).then(function(t){if(!t||t.length<20)throw new Error('texto legal vazio');V3_TEXT_CACHE[e.path]=t;return t;});
}
function parseSectionsV3(txt){
 var chunks=String(txt||'').split(/\n\s*━{8,}\s*\n/g),sections=[];
 chunks.forEach(function(raw,si){
  var chunk=raw.trim();if(!chunk)return;
  var cut=chunk.indexOf('\n\n');var header=cut>=0?chunk.slice(0,cut).trim():'Trecho legal';var body=cut>=0?chunk.slice(cut+2).trim():chunk;
  var re=/^(?:Art\.|Artigo)[ \t\r\n]*(\d+)(?:\.?[º°oO])?(?:[-–—‑]([A-Za-z]{1,3}))?/gmi,m,ms=[];
  while((m=re.exec(body))){ms.push({idx:m.index,key:m[1]+((m[2]||'').toUpperCase())});if(re.lastIndex===m.index)re.lastIndex++;}
  var cards=[];
  if(ms.length){
   ms.forEach(function(x,i){var end=i+1<ms.length?ms[i+1].idx:body.length;var text=body.slice(x.idx,end).trim();if(text.length>=10)cards.push({id:'s'+si+'a'+i+'k'+x.key,key:x.key,text:text});});
  }else if(body){cards.push({id:'s'+si+'a0',key:'trecho',text:body});}
  if(cards.length)sections.push({header:header,cards:cards});
 });
 return sections;
}
function flatCardsV3(sections){var out=[];(sections||[]).forEach(function(s){(s.cards||[]).forEach(function(c){out.push(c);});});return out;}
function countReadV3(){if(!V3_CURRENT)return {read:0,total:0};var r=recV3(V3_CURRENT.token),n=0;V3_CURRENT.cards.forEach(function(c){if(r.read[c.id])n++;});return {read:n,total:V3_CURRENT.cards.length};}
function dueStagesV3(){
 var st=stateV3(),now=Date.now(),DAY=86400000,o={1:0,7:0,21:0};
 Object.keys(st.history||{}).forEach(function(k){var x=st.history[k];if(!x||!x.ts)return;if(!x.reviews)x.reviews={};[1,7,21].forEach(function(d){if(!x.reviews['d'+d]&&now-x.ts>=d*DAY)o[d]++;});});return o;
}
function renderMissionV3(){
 var box=document.getElementById('pmal-dso-law-mission');if(!box)return;var st=stateV3(),d=dayV3(),c=cycleV3(st.cycle),due=dueStagesV3(),fix=fixationKeysV3(),cnt=countReadV3();
 var progress=cnt.total?cnt.read+'/'+cnt.total+' trechos abertos':'carregando trechos…';var can=cnt.total&&cnt.read===cnt.total;
 box.innerHTML='<div style="font-weight:900;font-size:15px;margin-bottom:5px">⚖️ MISSÃO LEGAL · CICLO '+st.cycle+' · DIA '+st.day+'</div>'+
  '<div style="font-weight:800;margin-bottom:9px">'+escV3(d?d.label:'Faixa do dia')+'</div>'+
  '<div class="tmut ts" style="line-height:1.55">📖 Meta de leitura: <span class="dso-mission-progress">'+progress+'</span> · os cartões abaixo correspondem à faixa definida no PDF do DSO.</div>'+
  '<div class="tmut ts" style="margin-top:7px">🎯 Fixação: <b>'+fix.length+'</b> cartão(ões)-chave do Banco de Leis · revisões pendentes: <b>D+1 '+due[1]+'</b> · <b>D+7 '+due[7]+'</b> · <b>D+21 '+due[21]+'</b>.</div>'+
  '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:11px"><button class="btn" onclick="startLeituraQuiz()">🎯 Treinar CEBRASPE</button><button class="btn" id="pmal-dso-complete-v3" onclick="completeDsoLawDay()"'+(can?'':' disabled')+'>✅ Concluir dia e avançar</button></div>'+
  '<div class="tmut" style="font-size:10px;margin-top:8px">Leitura e fixação são camadas separadas: a leitura segue integralmente o roteiro diário dos PDFs; os cartões de fixação continuam alimentando CEBRASPE, erros pessoais e D+1/D+7/D+21.</div>';
}
function ensureFixationV3(html){
 var host=document.getElementById('leitura-hoje');if(!host)return;var fx=document.getElementById('pmal-fixacao-hoje');if(!fx){fx=document.createElement('div');fx.id='pmal-fixacao-hoje';host.parentNode.insertBefore(fx,host.nextSibling);}var n=fixationKeysV3().length;
 fx.innerHTML='<div class="dso-fix-title">🎯 FIXAÇÃO · CEBRASPE E REVISÕES</div><div class="dso-fix-meta">'+n+' cartão(ões)-chave disponíveis. Esta parte não substitui os artigos da meta de leitura acima.</div><div class="dso-fix-cards">'+(html||'<div class="tmut ts">Nenhum cartão-chave disponível para esta faixa.</div>')+'</div>';
}
function renderCardsV3(e,sections){
 var host=document.getElementById('leitura-hoje');if(!host)return;var t=tokenV3(),r=recV3(t),cards=flatCardsV3(sections);V3_CURRENT={token:t,entry:e,sections:sections,cards:cards};
 var cnt={read:0,total:cards.length};cards.forEach(function(c){if(r.read[c.id])cnt.read++;});
 var html='<div class="dso-day-head"><div class="dso-day-title">📖 '+escV3(e.label)+'</div><div class="dso-day-meta">'+cnt.read+'/'+cnt.total+' trecho(s) já aberto(s). Leia os cartões desta faixa na ordem; eles substituem a antiga seleção aleatória de poucos dispositivos.</div></div>';
 sections.forEach(function(sec){html+='<div class="dso-section-title">'+escV3(sec.header)+'</div>';sec.cards.forEach(function(c){var done=!!r.read[c.id];html+='<details class="acc mb12 dso-law-card" data-rid="'+c.id+'" ontoggle="if(this.open)pmalDsoMarkArticleV3(this.dataset.rid)"><summary style="padding:11px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap"><span style="background:#2563eb;color:#fff;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:800;letter-spacing:.3px">Art. '+escV3(c.key)+'</span><span id="dso-v3-badge-'+c.id+'" class="dso-read-badge'+(done?' done':'')+'">'+(done?'✓ lido':'toque para ler')+'</span></summary><div class="accb"><div class="dso-article-text">'+escV3(c.text)+'</div></div></details>';});});
 host.innerHTML=html;renderMissionV3();
}
window.pmalDsoMarkArticleV3=function(id){if(!V3_CURRENT)return;var r=recV3(V3_CURRENT.token);if(!r.read[id]){r.read[id]=Date.now();saveV3();}var b=document.getElementById('dso-v3-badge-'+id);if(b){b.textContent='✓ lido';b.classList.add('done');}var cnt=countReadV3(),head=document.querySelector('#leitura-hoje .dso-day-meta');if(head)head.textContent=cnt.read+'/'+cnt.total+' trecho(s) já aberto(s). Leia os cartões desta faixa na ordem; eles substituem a antiga seleção aleatória de poucos dispositivos.';if(cnt.total&&cnt.read===cnt.total){r.done=true;saveV3();}renderMissionV3();};
function renderReadingV3(fixHtml){
 var host=document.getElementById('leitura-hoje');if(!host)return;ensureFixationV3(fixHtml);host.innerHTML='<div class="dso-day-head"><div class="dso-day-title">📖 Carregando a meta de leitura do DSO…</div><div class="dso-day-meta">A faixa será exibida aqui nos mesmos cartões de leitura usados anteriormente.</div></div>';V3_CURRENT=null;renderMissionV3();
 loadManifestV3().then(function(man){var e=entryV3(man);if(!e)throw new Error('dia atual não encontrado nos 65 dias');return loadTextV3(e).then(function(txt){var secs=parseSectionsV3(txt);var cards=flatCardsV3(secs);if(!cards.length)throw new Error('nenhum artigo reconhecido na faixa');if(e.articleCount&&cards.length!==e.articleCount)throw new Error('cobertura divergente: manifesto '+e.articleCount+' x cartões '+cards.length);renderCardsV3(e,secs);});}).catch(function(err){host.innerHTML='<div class="dso-day-head"><div class="dso-day-title">⚠️ Não foi possível carregar a meta de leitura</div><div class="dso-day-meta">'+escV3(err.message)+'. O dia não poderá ser concluído enquanto os trechos do DSO não estiverem disponíveis.</div></div>';renderMissionV3();});
}

if(typeof renderLeituraDia==='function'){
 var baseRenderV3=renderLeituraDia;
 window.renderLeituraDia=function(){var r=baseRenderV3.apply(this,arguments);var host=document.getElementById('leitura-hoje'),fixHtml=host?host.innerHTML:'';setTimeout(function(){renderReadingV3(fixHtml);},0);return r;};
}
if(typeof renderLeituraSub==='function'){
 var baseSubV3=renderLeituraSub;
 window.renderLeituraSub=function(){var info=baseSubV3.apply(this,arguments),st=stateV3(),d=dayV3(),c=cycleV3(st.cycle),sub=document.getElementById('leitura-sub');if(sub&&d&&c)sub.innerHTML='<b>Rodada '+st.round+' · Ciclo '+st.cycle+' · Dia '+st.day+'/'+c.days.length+'</b> — '+escV3(d.label)+'<br><span class="tmut">📖 Meta: <b>trechos integrais da faixa do PDF DSO</b> · 🎯 Fixação: '+fixationKeysV3().length+' cartão(ões)-chave.</span>';return info;};
}
window.leituraDoDiaFeita=function(){var cnt=countReadV3();return !!(cnt.total&&cnt.read===cnt.total);};
window.completeDsoLawDay=function(){
 var st=stateV3(),d=dayV3(),c=cycleV3(st.cycle),t=tokenV3();if(!V3_CURRENT||V3_CURRENT.token!==t){if(typeof toast==='function')toast('📖 A meta de leitura ainda não carregou.');return;}var cnt=countReadV3();if(!cnt.total||cnt.read<cnt.total){if(typeof toast==='function')toast('📖 Ainda faltam '+(cnt.total-cnt.read)+' trecho(s) desta faixa. Abra e leia antes de avançar.');var first=V3_CURRENT.cards.filter(function(x){return !recV3(t).read[x.id];})[0];if(first){var el=document.querySelector('[data-rid="'+first.id+'"]');if(el)el.scrollIntoView({behavior:'smooth',block:'center'});}return;}
 var keys=fixationKeysV3(),rr=recV3(t);rr.done=true;rr.completedAt=Date.now();rr.articleCount=cnt.total;if(!st.history[t])st.history[t]={ts:Date.now(),round:st.round,cycle:st.cycle,day:st.day,label:d?d.label:'',keys:keys,reviews:{},integral:true,readingCardsV3:true};else{st.history[t].integral=true;st.history[t].readingCardsV3=true;st.history[t].keys=keys;}
 if(st.day<c.days.length)st.day++;else if(st.cycle<planV3().length){st.cycle++;st.day=1;}else{st.round++;st.cycle=1;st.day=1;if(typeof toast==='function')toast('🏆 Os 3 ciclos foram concluídos. Iniciando nova rodada de manutenção.');}
 S.leituraDia=null;V3_CURRENT=null;saveV3();if(typeof renderLeituraDia==='function')renderLeituraDia();if(typeof toast==='function')toast('✅ Dia concluído. Próxima faixa do PDF DSO carregada.');
};
setTimeout(function(){if(typeof renderLeituraDia==='function')renderLeituraDia();},0);
})();
</script>
<!-- PMAL_DSO_READING_CARDS_V3_END -->'''

pos = s.lower().rfind("</body>")
if pos < 0:
    raise SystemExit("ERRO: </body> não encontrado")
s = s[:pos] + block + "\n" + s[pos:]
p.write_text(s, encoding="utf-8")
print("PMAL_DSO_READING_CARDS_V3 aplicado")
