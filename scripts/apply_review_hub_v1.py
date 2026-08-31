#!/usr/bin/env python3
import re
from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='PMAL_REVIEW_HUB_V1'
if MARK in s:
    print('Review Hub V1 already applied')
    raise SystemExit(0)

# 1) Limpa a Home: remove revisões avulsas e Patrulha da grade Operações.
for bid in ['btn-review-20260830','btn-review-20260825','btn-review-20260824','btn-review-20260823','btn-smart']:
    s,n=re.subn(r'\s*<button\b(?=[^>]*\bid="'+re.escape(bid)+r'")[\s\S]*?</button>', '', s, count=1, flags=re.I)
    if n!=1:
        print('WARN: button not found/removed:',bid)

hub_tile='''\n    <button class="tile t-vio" id="btn-review-hub" onclick="openReviewHub()"><span class="ic">🔁</span><span class="tt">Central de Revisão</span><span class="tsub" id="review-hub-home-sub">Erros, matérias, assuntos e revisões programadas em um só lugar</span></button>'''
anchor='<button class="tile t-grn" id="btn-crono"'
pos=s.find(anchor)
if pos<0: raise SystemExit('Anchor btn-crono not found')
s=s[:pos]+hub_tile+'\n    '+s[pos:]

# 2) Estilos próprios, sem alterar o tema global.
css=f'''\n<style id="pmal-review-hub-style">/* {MARK} */
#v-reviewhub .rh-head{{display:flex;gap:10px;align-items:center;justify-content:space-between;margin-bottom:12px}}
#v-reviewhub .rh-title{{font-size:18px;font-weight:900;letter-spacing:.2px}}
#v-reviewhub .rh-sub{{font-size:12px;color:var(--mut);margin-top:3px}}
#v-reviewhub .rh-back{{border:1px solid var(--bd);background:var(--cardb);color:var(--ink);border-radius:10px;padding:9px 12px;font-weight:800}}
.rh-kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px}}
.rh-kpi{{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:11px;text-align:center}}
.rh-kpi .n{{font-size:22px;font-weight:900;line-height:1.1}}
.rh-kpi .l{{font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:.7px;margin-top:4px}}
.rh-section{{background:var(--card);border:1px solid var(--bd);border-radius:14px;margin-bottom:12px;overflow:hidden}}
.rh-section-h{{padding:12px 13px;border-bottom:1px solid var(--bd);display:flex;align-items:center;justify-content:space-between;gap:8px}}
.rh-section-h b{{font-size:13px}}
.rh-section-b{{padding:12px}}
.rh-actions{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}}
.rh-action{{text-align:left;border:1px solid var(--bd);background:var(--cardb);color:var(--ink);border-radius:11px;padding:11px;min-height:66px}}
.rh-action strong{{display:block;font-size:12.5px;margin-bottom:4px}}
.rh-action span{{display:block;color:var(--mut);font-size:10.5px;line-height:1.35}}
.rh-action.primary{{border-color:#4d8f66;background:#13251a}}
.rh-filter{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:9px}}
.rh-filter select{{width:100%;min-width:0}}
.rh-cta-row{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}}
.rh-cta{{border:0;border-radius:10px;padding:10px 8px;font-weight:900;font-size:11px}}
.rh-cta.err{{background:#4b1f24;color:#ffd8dc;border:1px solid #6f3038}}
.rh-cta.hist{{background:#1c2b22;color:#dff6e6;border:1px solid #31523d}}
.rh-list{{display:flex;flex-direction:column;gap:7px}}
.rh-row{{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 10px;background:var(--cardb);border:1px solid var(--bd);border-radius:10px}}
.rh-row-main{{min-width:0}}
.rh-row-mat{{font-size:11.5px;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.rh-row-topic{{font-size:10.5px;color:var(--mut);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.rh-row-right{{display:flex;align-items:center;gap:7px;flex:0 0 auto}}
.rh-count{{font-size:10px;font-weight:900;color:#f2a9a9;background:#35191d;border:1px solid #57262c;border-radius:999px;padding:4px 7px}}
.rh-mini{{border:1px solid var(--bd);background:#172019;color:var(--ink);border-radius:8px;padding:6px 8px;font-size:10px;font-weight:900}}
.rh-weak{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--bd)}}
.rh-weak:last-child{{border-bottom:0}}
.rh-bar{{height:5px;background:#202722;border-radius:999px;overflow:hidden;margin-top:5px}}
.rh-bar>i{{display:block;height:100%;background:#8c5c60;border-radius:999px}}
.rh-empty{{padding:13px;text-align:center;color:var(--mut);font-size:11px;border:1px dashed var(--bd);border-radius:10px}}
.rh-saved{{display:grid;grid-template-columns:1fr;gap:7px}}
@media(max-width:520px){{.rh-kpis{{grid-template-columns:repeat(3,1fr)}}.rh-actions,.rh-cta-row{{grid-template-columns:1fr 1fr}}.rh-filter{{grid-template-columns:1fr}}}}
</style>'''
head=s.find('</head>')
if head<0: raise SystemExit('</head> not found')
s=s[:head]+css+'\n'+s[head:]

# 3) View dedicada.
view='''\n<!-- PMAL_REVIEW_HUB_VIEW -->
<div id="v-reviewhub" class="view">
  <div class="rh-head">
    <div><div class="rh-title">🔁 Central de Revisão</div><div class="rh-sub">Revisar deixa de ocupar a Home e passa a ter um espaço próprio.</div></div>
    <button class="rh-back" onclick="gN('home')">← Início</button>
  </div>

  <div class="rh-kpis">
    <div class="rh-kpi"><div class="n" id="rh-kpi-pending">0</div><div class="l">erros pendentes</div></div>
    <div class="rh-kpi"><div class="n" id="rh-kpi-critical">0</div><div class="l">assuntos críticos</div></div>
    <div class="rh-kpi"><div class="n" id="rh-kpi-history">0</div><div class="l">erros históricos</div></div>
  </div>

  <div class="rh-section">
    <div class="rh-section-h"><b>📅 Revisões programadas</b><span class="ts tmut">ciclos e manutenção</span></div>
    <div class="rh-section-b"><div class="rh-actions">
      <button class="rh-action primary" onclick="startYesterdayReview()"><strong>🌅 Revisão de ontem</strong><span>Cartões dos conteúdos registrados no dia anterior.</span></button>
      <button class="rh-action" onclick="startWeekReview()"><strong>📆 Revisão semanal</strong><span>Retoma os tópicos trabalhados nos últimos dias.</span></button>
      <button class="rh-action" onclick="revisaoInteligente()"><strong>🧠 Patrulha inteligente</strong><span>50% críticos · 30% instáveis · 20% manutenção.</span></button>
      <button class="rh-action" onclick="gN('crono')"><strong>🗓️ Cronograma</strong><span>Veja a Operação do Dia e as revisões previstas.</span></button>
    </div></div>
  </div>

  <div class="rh-section">
    <div class="rh-section-h"><b>❌ Questões erradas</b><span class="ts tmut" id="rh-filter-count">0 encontradas</span></div>
    <div class="rh-section-b">
      <div class="rh-filter">
        <select id="rh-subject" onchange="reviewHubSubjectChanged()"><option value="">Todas as matérias</option></select>
        <select id="rh-topic" onchange="renderReviewHub()"><option value="">Todos os assuntos</option></select>
      </div>
      <div class="rh-cta-row">
        <button class="rh-cta err" onclick="reviewHubStartCurrentErrors()">❌ Refazer pendentes</button>
        <button class="rh-cta hist" onclick="reviewHubStartHistoricalErrors()">↻ Refazer histórico</button>
      </div>
      <div id="rh-error-groups" class="rh-list"></div>
    </div>
  </div>

  <div class="rh-section">
    <div class="rh-section-h"><b>📊 Matérias e assuntos para priorizar</b><span class="ts tmut">baseado no seu histórico</span></div>
    <div class="rh-section-b" id="rh-weaknesses"></div>
  </div>

  <div class="rh-section">
    <div class="rh-section-h"><b>🗂️ Revisões salvas</b><span class="ts tmut">rodadas anteriores</span></div>
    <div class="rh-section-b"><div class="rh-saved">
      <button class="rh-action" onclick="startReview20260830()"><strong>📝 Simulado 30/08</strong><span>120 questões · revisão exclusiva da rodada.</span></button>
      <button class="rh-action" onclick="startReview20260825()"><strong>📚 Revisão 25/08</strong><span>Administrativo + Matemática teórica.</span></button>
      <button class="rh-action" onclick="startReview20260824()"><strong>📚 Revisão 24/08</strong><span>73 questões da sessão registrada.</span></button>
      <button class="rh-action" onclick="startReview20260823()"><strong>📚 Revisão 23/08</strong><span>Simulado antigo e itens revisáveis.</span></button>
    </div></div>
  </div>
</div>
'''
quiz='<!-- QUIZ -->'
if quiz not in s: raise SystemExit('QUIZ marker not found')
s=s.replace(quiz,view+'\n'+quiz,1)

# 4) Runtime: usa os mesmos S, QQ, topico, sv e renderQ da plataforma.
js=r'''\n<script id="pmal-review-hub-runtime">
(function(){
  function arr(v){if(!v)return[];if(v instanceof Set)return Array.from(v);if(Array.isArray(v))return v.slice();return Object.keys(v).filter(function(k){return v[k];});}
  function allQ(){return (typeof QQ!=='undefined'&&Array.isArray(QQ))?QQ:[];}
  function qById(id){var q=allQ().find(function(x){return x.id===id;});return q||null;}
  function tp(q){try{return (typeof topico==='function'?topico(q.a):q.a)||'Sem assunto';}catch(e){return q.a||'Sem assunto';}}
  function selected(){return {m:(document.getElementById('rh-subject')||{}).value||'',t:(document.getElementById('rh-topic')||{}).value||''};}
  function match(q,f){return q&&(!f.m||q.m===f.m)&&(!f.t||tp(q)===f.t);}
  function currentErrorIds(){return arr(window.S&&S.eids);}
  function historicalErrorIds(){var ids=[],seen={};((window.S&&S.ha)||[]).forEach(function(h){if(!h.ok&&h.id&&!seen[h.id]){seen[h.id]=1;ids.push(h.id);}});return ids;}
  function criticalCount(){var n=0;try{Object.values((S&&S.AS)||{}).forEach(function(r){if(typeof statusOf==='function'&&statusOf(r)==='vermelho')n++;});}catch(e){}return n;}
  function setTxt(id,v){var e=document.getElementById(id);if(e)e.textContent=v;}
  function escRh(x){return String(x==null?'':x).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function fillSubjects(){var el=document.getElementById('rh-subject');if(!el)return;var cur=el.value;var mats=Array.from(new Set(allQ().map(function(q){return q.m;}).filter(Boolean))).sort();var html='<option value="">Todas as matérias</option>'+mats.map(function(m){return '<option value="'+escRh(m)+'">'+escRh(m)+'</option>';}).join('');if(el.innerHTML!==html)el.innerHTML=html;if(mats.indexOf(cur)>=0)el.value=cur;}
  function fillTopics(){var sub=document.getElementById('rh-subject'),el=document.getElementById('rh-topic');if(!el)return;var cur=el.value,m=sub?sub.value:'';var qs=allQ().filter(function(q){return !m||q.m===m;});var topics=Array.from(new Set(qs.map(tp).filter(Boolean))).sort();el.innerHTML='<option value="">Todos os assuntos</option>'+topics.map(function(t){return '<option value="'+escRh(t)+'">'+escRh(t)+'</option>';}).join('');if(topics.indexOf(cur)>=0)el.value=cur;}
  function filteredIds(ids){var f=selected();return ids.filter(function(id){return match(qById(id),f);});}
  function start(ids,label){var seen={},qs=[];ids.forEach(function(id){var q=qById(id);if(q&&!seen[id]&&!q.missingContext){seen[id]=1;qs.push(q);}});if(!qs.length){if(typeof toast==='function')toast('Nenhuma questão disponível para este filtro.');return;}S.mode='review';S.sim=false;S.sq=qs.slice();S.ci=0;S.sa=[];S.round=(S.round||0)+1;if(typeof sv==='function')sv('quiz');if(typeof renderQ==='function')renderQ();document.querySelectorAll('.nb').forEach(function(b){b.classList.remove('act');});if(typeof toast==='function')toast('🔁 '+label+': '+qs.length+' questão(ões).');}
  window.reviewHubStartCurrentErrors=function(){start(filteredIds(currentErrorIds()),'Erros pendentes');};
  window.reviewHubStartHistoricalErrors=function(){start(filteredIds(historicalErrorIds()),'Histórico de erros');};
  window.reviewHubStartGroup=function(m,t){var ids=currentErrorIds().filter(function(id){var q=qById(id);return q&&q.m===m&&tp(q)===t;});start(ids,m+' · '+t);};
  window.reviewHubSubjectChanged=function(){var t=document.getElementById('rh-topic');if(t)t.value='';fillTopics();renderReviewHub();};
  window.renderReviewHub=function(){
    fillSubjects();fillTopics();var f=selected();var cur=filteredIds(currentErrorIds()),hist=filteredIds(historicalErrorIds());
    setTxt('rh-kpi-pending',currentErrorIds().length);setTxt('rh-kpi-critical',criticalCount());setTxt('rh-kpi-history',historicalErrorIds().length);setTxt('rh-filter-count',cur.length+' encontrada'+(cur.length===1?'':'s'));
    var groups={};cur.forEach(function(id){var q=qById(id);if(!q)return;var t=tp(q),k=q.m+'|||'+t;if(!groups[k])groups[k]={m:q.m,t:t,n:0};groups[k].n++;});
    var rows=Object.values(groups).sort(function(a,b){return b.n-a.n||a.m.localeCompare(b.m);});var box=document.getElementById('rh-error-groups');if(box)box.innerHTML=rows.length?rows.map(function(g){return '<div class="rh-row"><div class="rh-row-main"><div class="rh-row-mat">'+escRh(g.m)+'</div><div class="rh-row-topic">'+escRh(g.t)+'</div></div><div class="rh-row-right"><span class="rh-count">'+g.n+' erro'+(g.n===1?'':'s')+'</span><button class="rh-mini" data-m="'+escRh(g.m)+'" data-t="'+escRh(g.t)+'">Resolver</button></div></div>';}).join(''):'<div class="rh-empty">Nenhum erro pendente neste filtro. Quando você errar uma questão, ela aparecerá aqui automaticamente.</div>';
    if(box)box.querySelectorAll('.rh-mini').forEach(function(b){b.onclick=function(){reviewHubStartGroup(b.getAttribute('data-m'),b.getAttribute('data-t'));};});
    var ag={};((S&&S.ha)||[]).forEach(function(h){var q=qById(h.id);if(!match(q,f))return;var t=tp(q),k=q.m+'|||'+t;if(!ag[k])ag[k]={m:q.m,t:t,total:0,err:0};ag[k].total++;if(!h.ok)ag[k].err++;});
    var weak=Object.values(ag).filter(function(x){return x.err>0;}).sort(function(a,b){var ra=a.err/a.total,rb=b.err/b.total;return rb-ra||b.err-a.err;}).slice(0,12);var w=document.getElementById('rh-weaknesses');if(w)w.innerHTML=weak.length?weak.map(function(x){var pct=Math.round(x.err/x.total*100);return '<div class="rh-weak"><div><div class="rh-row-mat">'+escRh(x.m)+'</div><div class="rh-row-topic">'+escRh(x.t)+' · '+x.err+' erro(s) em '+x.total+' resposta(s)</div><div class="rh-bar"><i style="width:'+Math.max(4,pct)+'%"></i></div></div><span class="rh-count">'+pct+'%</span></div>';}).join(''):'<div class="rh-empty">Ainda não há histórico suficiente para priorizar assuntos.</div>';
    var hs=document.getElementById('review-hub-home-sub');if(hs){var n=currentErrorIds().length;hs.textContent=n?n+' erro'+(n===1?'':'s')+' pendente'+(n===1?'':'s')+' · toque para revisar':'Erros, matérias, assuntos e revisões programadas em um só lugar';}
  };
  window.openReviewHub=function(){if(typeof sv==='function')sv('reviewhub');document.querySelectorAll('.nb').forEach(function(b){b.classList.remove('act');});renderReviewHub();};
  document.addEventListener('DOMContentLoaded',function(){try{renderReviewHub();}catch(e){console.warn('review hub init',e);}});
})();
</script>'''
body=s.rfind('</body>')
if body<0: raise SystemExit('</body> not found')
s=s[:body]+js+'\n'+s[body:]

p.write_text(s,encoding='utf-8')
print('OK: PMAL Review Hub V1 applied')
