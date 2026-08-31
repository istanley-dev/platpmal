#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'index.html'
s=p.read_text(encoding='utf-8')
START='<!-- PMAL_DSO_FULL_LAW_READER_V2_START -->'
END='<!-- PMAL_DSO_FULL_LAW_READER_V2_END -->'
if START in s:
    a=s.index(START); b=s.index(END,a)+len(END); s=s[:a]+s[b:]

block=r'''<!-- PMAL_DSO_FULL_LAW_READER_V2_START -->
<style>
#pmal-full-law-reader{margin:0 0 14px;border:1px solid var(--bdr);border-radius:14px;overflow:hidden;background:var(--card)}
#pmal-full-law-reader .pfl-head{padding:14px;background:linear-gradient(135deg,rgba(37,99,235,.10),rgba(16,185,129,.07));border-bottom:1px solid var(--bdr)}
#pmal-full-law-reader .pfl-title{font-size:15px;font-weight:900;line-height:1.35}
#pmal-full-law-reader .pfl-meta{font-size:11px;color:var(--mut);margin-top:5px;line-height:1.45}
#pmal-full-law-reader .pfl-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
#pmal-full-law-reader .pfl-body{display:none;padding:0 14px 14px}
#pmal-full-law-reader.open .pfl-body{display:block}
#pmal-full-law-reader .pfl-text{white-space:pre-wrap;word-break:normal;overflow-wrap:anywhere;font-family:inherit;font-size:14px;line-height:1.72;color:var(--txt);padding:16px 0 8px;margin:0}
#pmal-full-law-reader .pfl-done{border-top:1px solid var(--bdr);padding-top:12px;margin-top:8px}
#pmal-full-law-reader .pfl-ok{color:var(--sg);font-weight:800}
#pmal-fixacao-title{font-weight:900;font-size:13px;margin:10px 0 8px;color:var(--txt)}
@media(max-width:600px){#pmal-full-law-reader .pfl-text{font-size:15px;line-height:1.75}#pmal-full-law-reader .pfl-actions .btn{flex:1;min-width:135px}}
</style>
<script>
(function(){
'use strict';
var PMAL_FULL_MANIFEST=null,PMAL_FULL_MANIFEST_PROMISE=null,PMAL_FULL_TEXT_CACHE={};
function pmalFullEsc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function pmalFullToken(){return (typeof pmalDsoToken==='function'?pmalDsoToken():'');}
function pmalFullState(){if(!S.lawDsoIntegral||typeof S.lawDsoIntegral!=='object')S.lawDsoIntegral={};return S.lawDsoIntegral;}
function pmalFullDone(){var t=pmalFullToken(),st=pmalFullState();return !!(t&&st[t]&&st[t].done);}
function pmalLoadManifest(){
 if(PMAL_FULL_MANIFEST)return Promise.resolve(PMAL_FULL_MANIFEST);
 if(PMAL_FULL_MANIFEST_PROMISE)return PMAL_FULL_MANIFEST_PROMISE;
 PMAL_FULL_MANIFEST_PROMISE=fetch('law-reading/manifest.json?v=3',{cache:'no-cache'}).then(function(r){if(!r.ok)throw new Error('manifest '+r.status);return r.json();}).then(function(x){if(!x||x.totalDays!==65)throw new Error('manifest incompleto');PMAL_FULL_MANIFEST=x;return x;}).catch(function(e){PMAL_FULL_MANIFEST_PROMISE=null;throw e;});
 return PMAL_FULL_MANIFEST_PROMISE;
}
function pmalFullEntry(man){var st=typeof pmalDsoEnsure==='function'?pmalDsoEnsure():null;if(!st)return null;return (man.days||[]).find(function(x){return x.cycle===st.cycle&&x.day===st.day;})||null;}
function pmalLoadTodayText(entry){if(PMAL_FULL_TEXT_CACHE[entry.path])return Promise.resolve(PMAL_FULL_TEXT_CACHE[entry.path]);return fetch(entry.path+'?v=3',{cache:'force-cache'}).then(function(r){if(!r.ok)throw new Error('texto '+r.status);return r.text();}).then(function(t){if(!/\bArt\.?\s*\d+/i.test(t))throw new Error('texto legal inválido');PMAL_FULL_TEXT_CACHE[entry.path]=t;return t;});}
function pmalFullHost(){return document.getElementById('leitura-hoje');}
function pmalRenderFullReader(){
 var host=pmalFullHost();if(!host)return;var old=document.getElementById('pmal-full-law-reader');if(old)old.remove();var ft=document.getElementById('pmal-fixacao-title');if(ft)ft.remove();
 var box=document.createElement('div');box.id='pmal-full-law-reader';box.innerHTML='<div class="pfl-head"><div class="pfl-title">📖 LEITURA INTEGRAL DO DIA</div><div class="pfl-meta">Carregando a faixa completa prevista no plano DSO…</div></div><div class="pfl-body"><div class="pfl-text"></div><div class="pfl-done"></div></div>';
 host.parentNode.insertBefore(box,host);
 var fx=document.createElement('div');fx.id='pmal-fixacao-title';fx.innerHTML='🎯 FIXAÇÃO · DISPOSITIVOS-CHAVE E QUESTÕES CEBRASPE';host.parentNode.insertBefore(fx,host);
 pmalLoadManifest().then(function(man){var e=pmalFullEntry(man);if(!e)throw new Error('dia não localizado no manifesto');var meta=box.querySelector('.pfl-meta');var head=box.querySelector('.pfl-title');head.innerHTML='📖 LEITURA INTEGRAL · CICLO '+e.cycle+' · DIA '+e.day;meta.innerHTML='<b>'+pmalFullEsc(e.label)+'</b><br>'+e.articleCount+' dispositivo(s)/artigo(s) carregados na faixa integral. O plano DSO define a faixa; o arquivo de leitura contém o texto completo correspondente, separado da camada de fixação.';
 var actions=document.createElement('div');actions.className='pfl-actions';actions.innerHTML='<button class="btn" type="button" id="pfl-open">📚 Abrir leitura integral</button><button class="btn" type="button" id="pfl-reload">↻ Recarregar texto</button>';box.querySelector('.pfl-head').appendChild(actions);
 function load(open){var b1=document.getElementById('pfl-open');if(b1)b1.disabled=true;pmalLoadTodayText(e).then(function(txt){box.querySelector('.pfl-text').textContent=txt;box.classList.add('open');if(b1){b1.disabled=false;b1.textContent='📚 Leitura aberta';}pmalRenderFullDone(box,e);if(open)setTimeout(function(){box.scrollIntoView({behavior:'smooth',block:'start'});},50);}).catch(function(err){if(b1)b1.disabled=false;box.querySelector('.pfl-text').textContent='Não foi possível carregar a leitura integral. Recarregue a página. O dia NÃO será marcado como concluído sem esse conteúdo.\n\nDetalhe: '+err.message;box.classList.add('open');});}
 document.getElementById('pfl-open').onclick=function(){load(true);};document.getElementById('pfl-reload').onclick=function(){delete PMAL_FULL_TEXT_CACHE[e.path];load(false);};
 if(pmalFullDone())load(false);
 }).catch(function(err){box.querySelector('.pfl-meta').innerHTML='⚠️ Falha ao carregar o plano integral: '+pmalFullEsc(err.message)+'. A fixação permanece disponível, mas o dia não poderá ser concluído até o texto integral carregar.';});
}
function pmalRenderFullDone(box,e){var d=box.querySelector('.pfl-done');if(!d)return;if(pmalFullDone()){d.innerHTML='<div class="pfl-ok">✅ Leitura integral marcada como concluída.</div><div class="pfl-meta">Agora você pode fazer a fixação CEBRASPE e avançar o dia.</div>';return;}d.innerHTML='<div style="font-weight:800;margin-bottom:6px">Chegou ao fim da faixa?</div><div class="pfl-meta" style="margin-bottom:9px">Marque somente depois de ler a faixa integral acima. Isso substitui a antiga exigência de abrir apenas alguns cartões do DISP.</div><button class="btn" type="button" id="pfl-mark">✅ Li integralmente esta faixa</button>';var b=document.getElementById('pfl-mark');if(b)b.onclick=function(){var t=pmalFullToken(),st=pmalFullState();st[t]={done:true,ts:Date.now(),cycle:e.cycle,day:e.day,path:e.path,articleCount:e.articleCount};if(typeof SS==='function')SS();pmalRenderFullDone(box,e);if(typeof pmalDsoPanel==='function')pmalDsoPanel();if(typeof toast==='function')toast('📖 Leitura integral concluída. A fixação e as revisões continuam separadas.');};}
window.pmalRenderFullReader=pmalRenderFullReader;
window.pmalDsoIntegralDone=pmalFullDone;

if(typeof renderLeituraDia==='function'){
 var _pmalFullBaseRender=renderLeituraDia;
 window.renderLeituraDia=function(){var r=_pmalFullBaseRender.apply(this,arguments);setTimeout(pmalRenderFullReader,0);return r;};
}
if(typeof renderLeituraSub==='function'){
 var _pmalFullBaseSub=renderLeituraSub;
 window.renderLeituraSub=function(){var info=_pmalFullBaseSub.apply(this,arguments);var sub=document.getElementById('leitura-sub');if(sub&&info)sub.innerHTML='<b>Rodada '+info.round+' · Ciclo '+info.cycle+' · Dia '+info.day+'/'+info.cycleDays+'</b> — '+pmalFullEsc(info.label)+'<br><span class="tmut">📖 Leitura: <b>faixa integral do plano DSO</b> · 🎯 Fixação: '+info.todays.length+' cartão(ões)-chave disponíveis · revisões D+1/D+7/D+21: <b>'+info.dueReviews+'</b>.</span>';return info;};
}
window.leituraDoDiaFeita=function(){return pmalFullDone();};

window.completeDsoLawDay=function(){
 if(!pmalFullDone()){if(typeof toast==='function')toast('📖 Antes de avançar, abra a LEITURA INTEGRAL e marque a faixa como lida no fim do texto.');var b=document.getElementById('pmal-full-law-reader');if(b)b.scrollIntoView({behavior:'smooth',block:'start'});return;}
 if(typeof touchLeituraDia==='function')touchLeituraDia();var st=pmalDsoEnsure(),day=pmalDsoDay(),keys=(S.leituraDia&&S.leituraDia.keys)||[],token=pmalDsoToken();
 if(!st.history[token])st.history[token]={ts:Date.now(),round:st.round,cycle:st.cycle,day:st.day,label:day.label,keys:keys.slice(),reviews:{},integral:true};else st.history[token].integral=true;
 var c=pmalDsoCycle(st.cycle);if(st.day<c.days.length)st.day++;else if(st.cycle<PMAL_DSO_LAW_PLAN.length){st.cycle++;st.day=1;}else{st.round++;st.cycle=1;st.day=1;if(typeof toast==='function')toast('🏆 Os 3 ciclos foram concluídos. Iniciando nova rodada de manutenção.');}
 S.leituraDia=null;if(typeof SS==='function')SS();if(typeof renderLeituraDia==='function')renderLeituraDia();if(typeof toast==='function')toast('✅ Dia concluído. Próxima faixa integral carregada; D+1/D+7/D+21 permanecem ativos.');
};
setTimeout(pmalRenderFullReader,0);
})();
</script>
<!-- PMAL_DSO_FULL_LAW_READER_V2_END -->'''
pos=s.lower().rfind('</body>')
if pos<0: raise SystemExit('ERRO: </body> não encontrado')
s=s[:pos]+block+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
print('PMAL_DSO_FULL_LAW_READER_V2 aplicado')
