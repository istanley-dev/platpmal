/* Maintenance-mode bootstrap. Keeps the previous presentation layer intact. */
(function () {
  'use strict';

  const PLAN = {
    enabled: true,
    version: '2026.09.29-adaptive-2-3',
    minimumMinutes: 30,
    maximumCoreBlocks: 4,
    minimumSubjects: 2,
    maximumSubjects: 3,
    portugueseQuestions: '5–8 questões',
    note: 'Todos os dias: revisão dos erros do dia anterior + 2–3 matérias do cronograma. O restante do cronograma permanece ativo.'
  };
  window.PMAL_MAINTENANCE_PLAN = PLAN;

  const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const norm = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

  function injectStyles() {
    if (document.getElementById('maintenance-mode-css')) return;
    const style = document.createElement('style');
    style.id = 'maintenance-mode-css';
    style.textContent = `
      .maintenance-banner{margin:0 0 18px;padding:18px 20px;border:1px solid var(--border,#dfe3ea);border-radius:16px;background:linear-gradient(135deg,rgba(47,108,229,.10),rgba(47,108,229,.02));box-shadow:0 8px 28px rgba(15,23,42,.05)}
      .maintenance-banner h2{margin:0 0 6px;font-size:1.08rem}.maintenance-banner p{margin:0;color:var(--muted,#667085);line-height:1.55}
      .maintenance-badges{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.maintenance-badge{display:inline-flex;align-items:center;padding:6px 9px;border-radius:999px;background:rgba(47,108,229,.10);font-size:.78rem;font-weight:700}
      .maintenance-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:14px}.maintenance-step{padding:11px 12px;border-radius:12px;background:var(--card,#fff);border:1px solid var(--border,#e4e7ec)}
      .maintenance-step b{display:block;font-size:.84rem;margin-bottom:3px}.maintenance-step span{font-size:.76rem;color:var(--muted,#667085);line-height:1.35}
      .maintenance-optional{margin-top:14px}.maintenance-optional summary{cursor:pointer;font-weight:700;font-size:.86rem}.maintenance-optional .ui-task-list{margin-top:10px}
      .maintenance-synthetic{display:flex;align-items:center;gap:12px;padding:13px 0;border-bottom:1px solid var(--border,#e4e7ec)}.maintenance-synthetic .ui-task-state{flex:0 0 auto}.maintenance-synthetic .ui-task-copy{flex:1}.maintenance-synthetic .ui-task-copy strong,.maintenance-synthetic .ui-task-copy small{display:block}.maintenance-synthetic .ui-task-copy small{margin-top:3px;color:var(--muted,#667085)}
      .maintenance-crono{margin:0 0 18px}.maintenance-crono .maintenance-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
      @media(max-width:720px){.maintenance-grid,.maintenance-crono .maintenance-grid{grid-template-columns:1fr}.maintenance-banner{padding:15px}}
    `;
    document.head.appendChild(style);
  }

  function taskId(task) { return task && task.id; }
  function uniqueTasks(tasks) {
    const seen = new Set();
    return tasks.filter(task => task && taskId(task) && !seen.has(taskId(task)) && seen.add(taskId(task)));
  }
  function isPortuguese(task) {
    if (!task || task.type !== 'adaptive') return false;
    const subject = norm(task.title || (task.item && task.item.subject));
    return subject.includes('portugues') || (task.item && task.item.kind === 'port');
  }
  function isDSO(task) {
    return !!(task && task.type === 'adaptive' && task.item && (task.item.kind === 'dso' || task.item.dsoBlocks));
  }
  function isReview(task) {
    if (!task || task.type !== 'adaptive' || isPortuguese(task) || isDSO(task)) return false;
    const kind = task.item && task.item.kind;
    return ['combat','recent','maintenance'].includes(kind) || task.subtitle && norm(task.subtitle).includes('revis');
  }
  function pickMinimum(data) {
    const tasks = (data && data.tasks) || [];
    const pending = tasks.filter(task => !task.done);
    const source = pending.length ? pending : tasks;
    const port = source.find(isPortuguese) || tasks.find(isPortuguese);
    const review = source.find(isReview) || tasks.find(isReview);

    // Mantém Português frequente e seleciona mais 1–2 matérias do ciclo,
    // sem transformar o dia em uma lista interminável de tarefas.
    const subjects = [];
    if (port) subjects.push(port);

    const candidates = source.filter(task =>
      task.type === 'adaptive' &&
      !isPortuguese(task) &&
      !isReview(task) &&
      !isDSO(task)
    );
    for (const task of candidates) {
      if (subjects.length >= PLAN.maximumSubjects) break;
      const subject = norm(task.title);
      if (!subjects.some(item => norm(item.title) === subject)) subjects.push(task);
    }

    // Se Português não estiver disponível, o cronograma ainda entrega 2–3 matérias.
    if (!port) {
      for (const task of candidates) {
        if (subjects.length >= PLAN.maximumSubjects) break;
        const subject = norm(task.title);
        if (!subjects.some(item => norm(item.title) === subject)) subjects.push(task);
      }
    }

    const selected = uniqueTasks([review, ...subjects]);
    return selected.slice(0, PLAN.maximumCoreBlocks);
  }

  function syntheticRow(index, title, subtitle, route) {
    const li = document.createElement('li');
    li.className = 'ui-task maintenance-synthetic';
    li.innerHTML = '<span class="ui-task-state" aria-label="Pendente">'+index+'</span><div class="ui-task-copy"><strong>'+esc(title)+'</strong><small>'+esc(subtitle)+'</small></div><button type="button" class="ui-task-action" data-ui-route="'+esc(route)+'">Abrir</button>';
    return li;
  }

  let applying = false;
  let homeObserver = null;
  function applyMaintenanceHome() {
    if (applying || !PLAN.enabled || !window.PmalInterface || typeof window.PmalInterface.taskData !== 'function') return;
    const home = document.getElementById('v-home');
    if (!home || !document.body.classList.contains('ui-ready')) return;
    applying = true;
    try {
      injectStyles();
      const data = window.PmalInterface.taskData();
      const minimum = pickMinimum(data);
      const minIds = new Set(minimum.map(taskId));
      const minDone = minimum.filter(t => t.done).length;
      const pct = minimum.length ? Math.round(minDone / minimum.length * 100) : 0;

      let banner = home.querySelector('.maintenance-banner');
      if (!banner) {
        banner = document.createElement('section');
        banner.className = 'maintenance-banner';
        const head = home.querySelector('.ui-page-head');
        if (head) head.after(banner); else home.prepend(banner);
      }
      banner.innerHTML = '<h2>Plano adaptativo diário</h2><p>O cronograma completo continua ativo. A rotina diária combina a revisão dos erros do dia anterior com 2–3 matérias do ciclo.</p><div class="maintenance-badges"><span class="maintenance-badge">2–3 matérias por dia</span><span class="maintenance-badge">Revisão dos erros D+1</span><span class="maintenance-badge">Português com alta frequência</span></div><div class="maintenance-grid"><div class="maintenance-step"><b>1 · Revisão</b><span>Erros e dúvidas registrados no dia anterior.</span></div><div class="maintenance-step"><b>2 · Matérias</b><span>2–3 matérias previstas no cronograma do dia.</span></div><div class="maintenance-step"><b>3 · Questões</b><span>Priorizar CEBRASPE e reforçar assuntos de maior incidência.</span></div></div>';

      const pageHeadTitle = home.querySelector('.ui-page-head h1');
      const pageHeadSub = home.querySelector('.ui-page-head p');
      if (pageHeadTitle) pageHeadTitle.textContent = 'Seu estudo, em dia.';
      if (pageHeadSub) pageHeadSub.textContent = 'Revisão dos erros + 2–3 matérias do cronograma';

      const heading = home.querySelector('.ui-section-heading');
      if (heading) {
        const h2 = heading.querySelector('h2');
        const span = heading.querySelector('span');
        if (h2) h2.textContent = 'Mínimo do dia';
        if (span) span.textContent = minDone+' de '+Math.max(minimum.length,3)+' concluídos';
      }

      const allRows = Array.from(home.querySelectorAll('li.ui-task'));
      const rowById = new Map();
      allRows.forEach(row => {
        const button = row.querySelector('[data-ui-task]');
        if (button) rowById.set(button.dataset.uiTask, row);
      });
      const primaryList = home.querySelector('ol.ui-task-list');
      if (primaryList) {
        primaryList.innerHTML = '';
        let index = 1;
        minimum.forEach(task => {
          const row = rowById.get(task.id);
          if (row) { primaryList.appendChild(row); index += 1; }
        });
        if (!minimum.some(isPortuguese)) primaryList.appendChild(syntheticRow(index++, 'Português', PLAN.portugueseQuestions+' · revisão do tópico anterior', 'practice'));
        if (!minimum.some(isReview)) primaryList.appendChild(syntheticRow(index++, 'Revisão de erros', 'Abra o caderno de erros e faça uma revisão curta.', 'reviewhub'));
        if (!minimum.some(isDSO)) primaryList.appendChild(syntheticRow(index++, 'Matéria do ciclo', 'Faça apenas um bloco do cronograma DSO.', 'crono'));
      }

      const currentDetails = home.querySelector('.maintenance-optional');
      if (currentDetails) currentDetails.remove();
      const optionalRows = allRows.filter(row => {
        const button = row.querySelector('[data-ui-task]');
        return button && !minIds.has(button.dataset.uiTask);
      });
      if (primaryList && optionalRows.length) {
        const details = document.createElement('details');
        details.className = 'maintenance-optional';
        details.innerHTML = '<summary>Se der tempo · '+optionalRows.length+' blocos opcionais</summary><ol class="ui-task-list"></ol>';
        optionalRows.forEach(row => details.querySelector('ol').appendChild(row));
        primaryList.after(details);
      }
      Array.from(home.querySelectorAll('.ui-task-more')).forEach(el => el.remove());

      const note = home.querySelector('.ui-note');
      if (note) note.textContent = PLAN.note;
      const ring = home.querySelector('.ui-day-ring');
      if (ring) { ring.style.setProperty('--ui-pct', pct+'%'); ring.setAttribute('aria-label', pct+'% do mínimo diário concluído'); const s=ring.querySelector('span'); if(s)s.textContent=pct+'%'; }
      const dayPanel = home.querySelector('.ui-day-panel');
      if (dayPanel) {
        const strong = dayPanel.querySelector('.ui-day-progress strong');
        const small = dayPanel.querySelector('.ui-day-progress .ui-small');
        const estimate = dayPanel.querySelector('.ui-estimate');
        if (strong) strong.textContent = minDone+' de '+Math.max(minimum.length,3);
        if (small) small.textContent = 'blocos essenciais';
        if (estimate) estimate.innerHTML = minDone >= 3 ? 'Mínimo do dia concluído' : 'Meta-base: <b>~'+PLAN.minimumMinutes+' min</b>';
      }
      const nextMeta = home.querySelector('.ui-next-meta span:first-child');
      if (nextMeta && nextMeta.lastChild) nextMeta.lastChild.textContent = 'PMAL · CEBRASPE';
    } catch (error) {
      console.warn('[maintenance-mode] Falha ao adaptar a página Hoje:', error);
    } finally {
      applying = false;
    }
  }

  function enhanceCrono() {
    if (!PLAN.enabled) return;
    const crono = document.getElementById('v-crono');
    if (!crono || crono.querySelector('.maintenance-crono')) return;
    injectStyles();
    const box = document.createElement('section');
    box.className = 'maintenance-banner maintenance-crono';
    box.innerHTML = '<h2>Cronograma adaptativo</h2><p>O cronograma completo continua ativo. Cada dia trabalha 2–3 matérias, começando pela revisão dos erros e dúvidas do dia anterior.</p><div class="maintenance-grid"><div class="maintenance-step"><b>Revisão D+1</b><span>Erros e dúvidas do dia anterior antes de avançar.</span></div><div class="maintenance-step"><b>2–3 matérias</b><span>Conteúdo e questões conforme o ciclo previsto.</span></div><div class="maintenance-step"><b>Foco CEBRASPE</b><span>Maior exposição aos assuntos mais incidentes e aos pontos fracos.</span></div></div><div class="maintenance-badges"><span class="maintenance-badge">Edital completo</span><span class="maintenance-badge">Questões como base</span><span class="maintenance-badge">Revisões espaçadas mantidas</span></div>';
    const anchor = crono.querySelector('.ui-page-head') || crono.firstElementChild;
    if (anchor) anchor.after(box); else crono.prepend(box);
  }

  function afterCoreLoaded() {
    injectStyles();
    const coreSv = window.sv;
    if (typeof coreSv === 'function') {
      window.sv = function (id) {
        const result = coreSv.apply(this, arguments);
        queueMicrotask(() => {
          if (id === 'home') applyMaintenanceHome();
          if (id === 'crono') enhanceCrono();
        });
        return result;
      };
    }
    applyMaintenanceHome();
    const home = document.getElementById('v-home');
    if (home && !homeObserver) {
      let timer = null;
      homeObserver = new MutationObserver(() => {
        if (applying || home.querySelector('.maintenance-banner')) return;
        clearTimeout(timer);
        timer = setTimeout(applyMaintenanceHome, 80);
      });
      homeObserver.observe(home, {childList:true,subtree:true,characterData:true});
    }
    document.addEventListener('click', event => {
      const route = event.target.closest('[data-ui-route="crono"]');
      if (route) setTimeout(enhanceCrono, 50);
    });
    window.PMALMaintenance = {version:PLAN.version, apply:applyMaintenanceHome, enhanceCrono};
  }

  function loadCore() {
    const script = document.createElement('script');
    script.src = 'interface-core.js?v=2026091101';
    script.onload = afterCoreLoaded;
    script.onerror = function () { console.error('[maintenance-mode] Não foi possível carregar interface-core.js'); };
    document.head.appendChild(script);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', loadCore, {once:true});
  else loadCore();
})();