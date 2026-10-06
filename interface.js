/* PMAL — camada de cronograma próprio de masterização.
   O DSO permanece apenas como fonte externa de questões/comentários e como ciclo de lei seca.
   Esta camada não usa o cronograma DSO para decidir as matérias do dia. */
(function () {
  'use strict';

  const PLAN = {
    version: '2026.10.05-masterizacao-4',
    maxSubjects: 3,
    portugueseDaily: true,
    targetQuestions: 100,
    minQuestions: 80,
    examDate: '2027-01-17'
  };
  window.PMAL_MAINTENANCE_PLAN = PLAN;

  const norm = v => String(v || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const esc = v => String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  function style() {
    if (document.getElementById('masterizacao-css')) return;
    const s = document.createElement('style');
    s.id = 'masterizacao-css';
    s.textContent = `
      .master-banner{margin:0 0 18px;padding:18px 20px;border:1px solid var(--border,#dfe3ea);border-radius:16px;background:linear-gradient(135deg,rgba(47,108,229,.10),rgba(47,108,229,.02))}
      .master-banner h2{margin:0 0 6px;font-size:1.08rem}.master-banner p{margin:0;color:var(--muted,#667085);line-height:1.5}
      .master-badges{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.master-badge{padding:6px 9px;border-radius:999px;background:rgba(47,108,229,.10);font-size:.76rem;font-weight:700}
      .master-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:14px}.master-step{padding:11px 12px;border-radius:12px;background:var(--card,#fff);border:1px solid var(--border,#e4e7ec)}
      .master-step b{display:block;font-size:.82rem;margin-bottom:3px}.master-step span{font-size:.75rem;color:var(--muted,#667085);line-height:1.35}
      @media(max-width:720px){.master-grid{grid-template-columns:1fr}}
      .master-radar{margin-top:14px;padding:14px;border:1px solid var(--border,#e4e7ec);border-radius:14px;background:var(--card,#fff)}
      .master-radar-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:10px}
      .master-radar-head h3{margin:0 0 3px;font-size:.9rem}.master-radar-head p{margin:0;color:var(--muted,#667085);font-size:.74rem}
      .master-radar-head>strong{font-size:.78rem;white-space:nowrap}.radar-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:9px 0;border-top:1px solid var(--border,#eef0f3)}
      .radar-row b{display:block;font-size:.78rem}.radar-row small{display:block;color:var(--muted,#667085);font-size:.7rem;margin-top:2px}.radar-row>span{font-weight:800;font-size:.72rem}
      .master-empty{font-size:.75rem;color:var(--muted,#667085);margin:8px 0}
    
    `;
    document.head.appendChild(s);
  }

  function isAdaptive(t){ return t && t.type === 'adaptive' && t.item; }
  function isPortuguese(t){ return isAdaptive(t) && norm(t.title).includes('portugues'); }
  function isDso(t){ return isAdaptive(t) && (t.item.kind === 'dso' || t.item.dsoBlocks); }
  function isReview(t){ return isAdaptive(t) && ['combat','recent'].includes(t.item.kind); }
  function priority(t){
    if (!isAdaptive(t)) return 0;
    const k=t.item.kind;
    if (k==='combat') return 120;      // reincidência/combate
    if (k==='recent') return 108;      // erro/revisão recente
    if (k==='incidence') return 96;    // alta incidência
    if (k==='maintenance') return 68;  // manutenção
    if (k==='math') return 64;
    return 50;
  }
  function rotationBonus(t){
    // Rotação diária: quando várias prioridades são parecidas, evita repetir
    // sempre a mesma ordem de matérias sem sacrificar os assuntos críticos.
    const day=Math.floor(Date.now()/86400000);
    const key=norm(t.title||t.item.subject);
    let hash=0;
    for(let i=0;i<key.length;i++) hash=(hash*31+key.charCodeAt(i))%997;
    return (hash+day)%17;
  }

  // Seleção própria: cobertura + incidência + fraqueza/reincidência, sem usar dsoBlocks.
  function selectMaster(data){
    const all=(data.tasks||[]).filter(t=>isAdaptive(t)&&!isDso(t));
    const pending=all.filter(t=>!t.done);
    const pool=pending.length?pending:all;
    const chosen=[];
    const used=new Set();

    const port=pool.find(isPortuguese)||all.find(isPortuguese);
    if(port){ chosen.push(port); used.add(norm(port.title)); }

    const ranked=pool
      .filter(t=>!isPortuguese(t))
      .sort((a,b)=>(priority(b)+rotationBonus(b))-(priority(a)+rotationBonus(a)));

    for(const t of ranked){
      if(chosen.length>=PLAN.maxSubjects) break;
      const key=norm(t.title);
      if(!used.has(key)){ chosen.push(t); used.add(key); }
    }

    // Se não houver Português disponível no histórico, completa até 3 matérias.
    if(!port){
      for(const t of ranked){
        if(chosen.length>=PLAN.maxSubjects) break;
        const key=norm(t.title);
        if(!used.has(key)){ chosen.push(t); used.add(key); }
      }
    }
    return chosen;
  }


  /* Evolução 6 — radar real baseado no histórico efetivo de questões. */
  const TOPIC_WEIGHTS={combat:140,recent:118,incidence:104,maintenance:62,math:60};
  const INCIDENCE_HINTS={'lingua portuguesa':['sintaxe','concordancia','regencia','crase','pontuacao','pronomes','interpretacao'],'direito administrativo':['atos administrativos','poderes administrativos','agentes publicos','principios','licitacoes','responsabilidade civil'],'direito constitucional':['direitos fundamentais','organizacao do estado','administracao publica','controle de constitucionalidade','seguranca publica'],'direito penal':['teoria do crime','ilicitude','culpabilidade','concurso de pessoas','penas'],'direito processual penal':['inquerito','acao penal','provas','prisao','competencia'],'direito penal militar':['teoria do crime','estado de necessidade','excesso','concurso de pessoas'],'direito processual penal militar':['inquerito policial militar','acao penal','prisao','competencia','provas'],'direitos humanos':['sistema interamericano','pacto de san jose','tratados'],'legislacao penal especial':['lei de drogas','estatuto do desarmamento','maria da penha','abuso de autoridade'],'nocoes de informatica':['windows','seguranca da informacao','redes','internet','office','arquivos','forense computacional']};
  function topicName(t){const i=t&&t.item?t.item:t;return String((i&&(i.topic||i.subtopic||i.assunto))||(i&&i.study&&i.study.topics&&i.study.topics[0])||(t&&t.title)||'Assunto não identificado').trim();}
  function num(v){const n=Number(v);return Number.isFinite(n)?n:null;}
  function topicMetric(i,name){const v=i&&(i[name]!=null?i[name]:i.study&&i.study[name]);return num(v);}
  function topicKey(subject,topic){return norm(subject)+'▸'+norm(topic);}
  function actualTopicRadar(){const map=new Map(),logs=Array.isArray(window.S&&S.log)?S.log:[],now=Date.now();logs.forEach(q=>{if(!q||!q.m)return;const topic=String(q.a||'Assunto não identificado').trim(),key=topicKey(q.m,topic);if(!map.has(key))map.set(key,{subject:q.m,name:topic,total:0,errors:0,chutes:0,last:0,incidence:0});const x=map.get(key);x.total++;if(q.res==='erro')x.errors++;if(q.conf==='chute')x.chutes++;x.last=Math.max(x.last,num(q.ts)||0);const hints=INCIDENCE_HINTS[norm(q.m)]||[];if(hints.some(h=>norm(topic).includes(norm(h))))x.incidence=1;});return [...map.values()].map(x=>{const accuracy=x.total?100-(x.errors/x.total*100):100,recurrence=x.errors>=3?2:x.errors>=2?1:0,recent=x.last?Math.max(0,1-Math.min((now-x.last)/86400000,30)/30):0,chute=x.chutes>=2?10:0,score=50+(100-accuracy)*.9+recurrence*22+x.incidence*28+recent*12+chute;return {...x,accuracy:Math.round(accuracy),score,level:score>=145?'🔴 Crítico':score>=110?'🟠 Fraco':score>=80?'🟡 Instável':'🟢 Consolidado'};}).sort((a,b)=>b.score-a.score);}
  function topicScore(t,radar){const i=t.item||{},name=topicName(t),rec=radar.find(x=>norm(x.subject)===norm(i.subject||t.title)&&norm(x.name)===norm(name)),base=TOPIC_WEIGHTS[i.kind]||50,incidence=topicMetric(i,'incidence')??topicMetric(i,'incidencia')??0,recurrence=topicMetric(i,'recurrence')??topicMetric(i,'reincidencia')??0,accuracy=topicMetric(i,'accuracy')??topicMetric(i,'performance')??topicMetric(i,'aproveitamento'),weakness=accuracy==null?0:Math.max(0,100-accuracy),days=topicMetric(i,'daysSinceReview')??topicMetric(i,'diasDesdeRevisao')??0;return base+(rec?rec.score:0)*1.15+incidence*.35+recurrence*8+weakness*.55+Math.min(days,30)*1.2;}
  function buildTopicRadar(data){const actual=actualTopicRadar(),map=new Map(actual.map(x=>[topicKey(x.subject,x.name),x]));(data.tasks||[]).filter(isAdaptive).forEach(t=>{const name=topicName(t),subject=t.item&&t.item.subject||t.title,key=topicKey(subject,name);if(!map.has(key))map.set(key,{subject,name,total:0,errors:0,chutes:0,last:0,incidence:0,accuracy:null,score:topicScore(t,actual),level:'🟢 Consolidado'});});return [...map.values()].map(x=>({...x,items:x.total||0,done:0})).sort((a,b)=>b.score-a.score);}
  function selectMaster(data){const all=(data.tasks||[]).filter(t=>isAdaptive(t)&&!isDso(t)),pending=all.filter(t=>!t.done),pool=pending.length?pending:all,chosen=[],usedSubjects=new Set(),usedTopics=new Set(),port=pool.find(isPortuguese)||all.find(isPortuguese);if(port){chosen.push(port);usedSubjects.add(norm(port.title));usedTopics.add(norm(topicName(port)));}const radar=buildTopicRadar({tasks:pool});const ranked=pool.filter(t=>!isPortuguese(t)).sort((a,b)=>(topicScore(b,radar)+priority(b)+rotationBonus(b))-(topicScore(a,radar)+priority(a)+rotationBonus(a)));for(const t of ranked){if(chosen.length>=PLAN.maxSubjects)break;const tk=norm(topicName(t)),sk=norm(t.title);if(usedTopics.has(tk)||usedSubjects.has(sk))continue;chosen.push(t);usedTopics.add(tk);usedSubjects.add(sk);}for(const t of ranked){if(chosen.length>=PLAN.maxSubjects)break;const sk=norm(t.title);if(!usedSubjects.has(sk)){chosen.push(t);usedSubjects.add(sk);}}return chosen;}
  function radarMarkup(data){
    const radar=buildTopicRadar(data);
    const top=radar.slice(0,5);
    const total=radar.length, consolidated=radar.filter(x=>x.level==='🟢 Consolidado').length;
    const coverage=total?Math.round(consolidated/total*100):0;
    return '<section class="master-radar"><div class="master-radar-head"><div><h3>🎯 Radar de masterização</h3><p>O motor prioriza tópico + desempenho + reincidência + incidência.</p></div><strong>'+coverage+'% consolidados</strong></div>'+
      (top.length?top.map(x=>'<div class="radar-row"><div><b>'+esc(x.level)+' · '+esc(x.name)+'</b><small>'+x.items+' bloco(s)'+(x.accuracy!=null?' · '+x.accuracy+'% de aproveitamento':'')+'</small></div><span>'+Math.round(x.score)+'</span></div>').join(''):'<p class="master-empty">O radar será preenchido conforme o histórico gerar tópicos.</p>')+
      '</section>';
  }

  function render(){
    if(!window.PmalInterface || typeof window.PmalInterface.taskData!=='function') return;
    const home=document.getElementById('v-home');
    if(!home || !document.body.classList.contains('ui-ready')) return;
    style();

    let data;
    try { data=window.PmalInterface.taskData(); } catch(e) { return; }
    const selected=selectMaster(data);
    const reading=(data.tasks||[]).find(t=>t.type==='reading');

    let banner=home.querySelector('.master-banner');
    if(!banner){
      banner=document.createElement('section');
      banner.className='master-banner';
      const head=home.querySelector('.ui-page-head');
      if(head) head.after(banner); else home.prepend(banner);
    }

    const names=selected.map(t=>esc(t.title)).join(' + ') || 'Seleção adaptativa';
    banner.innerHTML=
      '<h2>🧠 Cronograma de masterização</h2>'+
      '<p>Este cronograma é independente do DSO: prioriza seus erros, reincidências, incidência da Cebraspe e cobertura do edital. O DSO entra como fonte de questões e comentários.</p>'+
      '<div class="master-badges">'+
        '<span class="master-badge">'+PLAN.targetQuestions+' questões/dia · meta</span>'+
        '<span class="master-badge">1–3 matérias</span>'+
        '<span class="master-badge">Português diário</span>'+
        '<span class="master-badge">Cebraspe prioritária</span>'+
      '</div>'+
      '<div class="master-grid">'+
        '<div class="master-step"><b>🔁 D-1</b><span>Erros e dúvidas do dia anterior primeiro.</span></div>'+
        '<div class="master-step"><b>🔥 Prioridade</b><span>Reincidência + fraqueza + incidência pesam mais.</span></div>'+
        '<div class="master-step"><b>📚 Cobertura</b><span>Assuntos consolidados entram em manutenção para abrir espaço ao edital.</span></div>'+
      '</div>'+radarMarkup(data)+readingHistoryMarkup();

    const title=home.querySelector('.ui-page-head h1');
    const sub=home.querySelector('.ui-page-head p');
    if(title) title.textContent='Sua preparação PMAL';
    if(sub) sub.textContent='Masterização diária · '+names;

    const heading=home.querySelector('.ui-section-heading');
    if(heading){
      const h=heading.querySelector('h2'); const sp=heading.querySelector('span');
      if(h) h.textContent='Plano de masterização de hoje';
      if(sp) sp.textContent=selected.length+' matéria(s) prioritária(s)';
    }

    // Reordena a lista principal para mostrar somente o núcleo da masterização + lei seca.
    const list=home.querySelector('ol.ui-task-list');
    if(list){
      const rows=Array.from(home.querySelectorAll('li.ui-task'));
      const byId=new Map();
      rows.forEach(r=>{const b=r.querySelector('[data-ui-task]'); if(b) byId.set(b.dataset.uiTask,r);});
      list.innerHTML='';
      let n=1;
      selected.forEach(t=>{
        const row=byId.get(t.id);
        if(row){ list.appendChild(row); n++; }
      });
      if(reading){
        const row=byId.get(reading.id);
        if(row) list.appendChild(row);
      }
      if(PLAN.portugueseDaily && !selected.some(isPortuguese)){
        const li=document.createElement('li');
        li.className='ui-task';
        li.innerHTML='<span class="ui-task-state">'+n+'</span><div class="ui-task-copy"><strong>Português diário</strong><small>15–20 questões · priorizar seus pontos fracos</small></div><button type="button" class="ui-task-action" data-ui-route="practice">Abrir</button>';
        list.appendChild(li);
      }
      const note=home.querySelector('.ui-note');
      if(note) note.innerHTML='📌 Meta: 80–100+ questões bem corrigidas · revisão D-1 · lei seca · 1–3 matérias. Sem dívida de estudo.';
    }
  }

  function enhanceCrono(){
    const crono=document.getElementById('v-crono');
    if(!crono || crono.querySelector('.master-crono')) return;
    style();
    const box=document.createElement('section');
    box.className='master-banner master-crono';
    box.innerHTML='<h2>🧠 Cronograma próprio de masterização</h2><p>O DSO não comanda esta área. A seleção é feita pelo desempenho do aluno, incidência Cebraspe, reincidências, pegadinhas e cobertura do edital. O ciclo de lei seca continua separado.</p><div class="master-badges"><span class="master-badge">Máx. 3 matérias/dia</span><span class="master-badge">Português diário</span><span class="master-badge">Simulado semanal</span><span class="master-badge">Sem dívida</span></div>';
    const anchor=crono.querySelector('.ui-page-head')||crono.firstElementChild;
    if(anchor) anchor.after(box); else crono.prepend(box);
  }

  /* Evolução 5 — persistência independente da Lei Seca.
     O estado original continua sendo a fonte de conclusão; esta camada mantém
     um histórico por data para que a virada do dia não apague o que já foi feito. */
  const READING_KEY='pmal_lei_seca_historico_v1';
  function readingToday(){
    const d=new Date();
    return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
  }
  function readHistory(){
    try{const x=JSON.parse(localStorage.getItem(READING_KEY)||'{}');return x&&typeof x==='object'?x:{}}catch(e){return {}}
  }
  function writeHistory(h){try{localStorage.setItem(READING_KEY,JSON.stringify(h));}catch(e){}}
  function markReadingDone(date){
    const h=readHistory();
    if(!h[date]){h[date]={done:true,completedAt:new Date().toISOString()};writeHistory(h);}
  }
  function readingHistoryMarkup(){
    const h=readHistory(), today=readingToday(), rows=[];
    for(let i=6;i>=0;i--){
      const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()-i);
      const key=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
      const label=i===0?'Hoje':d.toLocaleDateString('pt-BR',{weekday:'short'}).replace('.','');
      rows.push('<span class="master-badge">'+(h[key]?.done?'✓ ':'')+esc(label)+(key===today?' · hoje':'')+'</span>');
    }
    return '<div class="master-badges" aria-label="Histórico da lei seca">'+rows.join('')+'</div>';
  }
  function installReadingPersistence(){
    if(!window.PmalInterface || window.__readingPersistenceInstalled)return;
    const original=window.PmalInterface.taskData;
    if(typeof original!=='function')return;
    window.__readingPersistenceInstalled=true;
    window.PmalInterface.taskData=function(){
      const data=original.apply(this,arguments);
      const reading=(data.tasks||[]).find(t=>t.type==='reading');
      const today=readingToday();
      if(reading){
        // Captura a conclusão legítima do motor atual antes da virada do dia.
        if(reading.done)markReadingDone(today);
        const h=readHistory();
        if(h[today]?.done)reading.done=true;
      }
      return data;
    };
    // Guarda a posição de leitura e caixas marcadas por dia, sem criar dívida
    // para dias perdidos. Ao retornar no mesmo dia, o usuário continua de onde parou.
    const progressKey=()=>READING_KEY+'_progress_'+readingToday();
    const saveProgress=()=>{
      const card=document.getElementById('leitura-card');if(!card)return;
      const checks=Array.from(card.querySelectorAll('input[type="checkbox"]')).map(x=>!!x.checked);
      const scrolls=Array.from(card.querySelectorAll('*')).filter(x=>x.scrollHeight>x.clientHeight+8).slice(0,8).map(x=>x.scrollTop);
      try{localStorage.setItem(progressKey(),JSON.stringify({checks,scrolls,savedAt:Date.now()}));}catch(e){}
    };
    const restoreProgress=()=>{
      const card=document.getElementById('leitura-card');if(!card)return;
      try{
        const p=JSON.parse(localStorage.getItem(progressKey())||'null');if(!p)return;
        const checks=card.querySelectorAll('input[type="checkbox"]');
        (p.checks||[]).forEach((v,i)=>{if(checks[i])checks[i].checked=!!v;});
        const scrolls=Array.from(card.querySelectorAll('*')).filter(x=>x.scrollHeight>x.clientHeight+8).slice(0,8);
        (p.scrolls||[]).forEach((v,i)=>{if(scrolls[i])scrolls[i].scrollTop=v;});
      }catch(e){}
    };
    setTimeout(restoreProgress,300);
    document.addEventListener('change',e=>{if(e.target.closest('#leitura-card'))saveProgress();},true);
    document.addEventListener('scroll',e=>{if(e.target&&e.target.closest&&e.target.closest('#leitura-card'))saveProgress();},true);
    setInterval(()=>{if(document.getElementById('leitura-card'))saveProgress();},3000);
  }

  function afterCore(){
    style();
    installReadingPersistence();
    const oldSv=window.sv;
    if(typeof oldSv==='function' && !window.__masterSvWrapped){
      window.__masterSvWrapped=true;
      window.sv=function(id){
        const r=oldSv.apply(this,arguments);
        setTimeout(()=>{ if(id==='home') render(); if(id==='crono') enhanceCrono(); },60);
        return r;
      };
    }
    setTimeout(render,80);
    document.addEventListener('click',e=>{
      if(e.target.closest('[data-ui-route="crono"]')) setTimeout(enhanceCrono,80);
    });
    window.PMALMasterizacao={version:PLAN.version,render,selectMaster};
  }

  function loadCore(){
    const s=document.createElement('script');
    s.src='interface-core.js?v=20261005-masterizacao-lei-seca';
    s.onload=afterCore;
    s.onerror=()=>console.error('[PMAL] Falha ao carregar interface-core.js');
    document.head.appendChild(s);
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',loadCore,{once:true});
  else loadCore();
})();