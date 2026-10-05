/* PMAL — camada de cronograma próprio de masterização.
   O DSO permanece apenas como fonte externa de questões/comentários e como ciclo de lei seca.
   Esta camada não usa o cronograma DSO para decidir as matérias do dia. */
(function () {
  'use strict';

  const PLAN = {
    version: '2026.10.05-masterizacao-3',
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
      '</div>';

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

  function afterCore(){
    style();
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
    s.src='interface-core.js?v=20261005-masterizacao';
    s.onload=afterCore;
    s.onerror=()=>console.error('[PMAL] Falha ao carregar interface-core.js');
    document.head.appendChild(s);
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',loadCore,{once:true});
  else loadCore();
})();