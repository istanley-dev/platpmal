/* Run with jsdom@26.1.0 available via NODE_PATH. No production dependencies. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, ResourceLoader, VirtualConsole } = require('jsdom');
const root = path.resolve(__dirname, '..');
const original = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const runtimeErrors = [];
const logs = new VirtualConsole();
logs.on('jsdomError', e => { if (e.type !== 'css parsing') runtimeErrors.push(e.message); });
logs.on('error', (...args) => runtimeErrors.push(args.map(String).join(' ')));
const state = {
  ha: [{ id: 'kept-history', ok: true, ts: 100 }], eids: [], AS: {}, round: 4,
  log: [], metas: {}, xp: 11, streak: 2, lastDay: '2026-08-24', plan: { examDate: '2026-11-29' },
  daily: { d: '', q: 0 }, bibLidos: {}, leituraDia: { d: '', keys: [] }, flash: { cards: {} },
  weekly: {}, reviewSessions: { keep: { title: 'Minha revisão' } },
  studyHistory: {}, adaptiveReview: { completed: {}, deferred: {} }, cycleId: 'ciclo2_20260821'
};
function localPath(url) {
  const parsed = new URL(url, 'https://istanley-dev.github.io/platpmal/');
  assert.equal(parsed.origin, 'https://istanley-dev.github.io', 'No remote requests in UI checks');
  const filename = path.resolve(root, decodeURIComponent(parsed.pathname.replace(/^\/platpmal\//, '')));
  assert(filename.startsWith(root + path.sep));
  return filename;
}
class LocalResources extends ResourceLoader {
  fetch(url) { return Promise.resolve(fs.readFileSync(localPath(url))); }
}
const dom = new JSDOM(original, {
  url: 'https://istanley-dev.github.io/platpmal/', runScripts: 'dangerously',
  resources: new LocalResources(), pretendToBeVisual: true, virtualConsole: logs,
  beforeParse(w) {
    w.scrollTo = () => {};
    w.HTMLElement.prototype.scrollIntoView = () => {};
    w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
    w.alert = () => {}; w.confirm = () => true;
    w.URL.createObjectURL = () => 'blob:backup'; w.URL.revokeObjectURL = () => {};
    w.HTMLAnchorElement.prototype.click = function () {};
    w.fetch = async url => ({ ok: true, status: 200, json: async () => JSON.parse(fs.readFileSync(localPath(url), 'utf8')), text: async () => fs.readFileSync(localPath(url), 'utf8') });
    w.localStorage.setItem('pmal26', JSON.stringify(state));
    w.localStorage.setItem('pmal26_key', 'test-key-never-export');
    w.localStorage.setItem('pmal26_cycle2_20260821_done', '1');
    w.localStorage.setItem('pmal26_cppm_review_notes_20260903_v1', JSON.stringify({ preserved: true }));
    // Avoid re-importing historical migrations; those are covered by the engine suite.
    const get = w.Storage.prototype.getItem;
    w.Storage.prototype.getItem = function (key) {
      const value = get.call(this, key);
      return value !== null ? value : key.startsWith('pmal26_import_') ? 'ok' : null;
    };
  }
});
const w = dom.window, d = w.document;
const $ = id => d.getElementById(id);
const visibleView = () => d.querySelector('.view.active')?.id;
const click = selector => { const element = d.querySelector(selector); assert(element, 'Missing action: '+selector); element.click(); };
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
  await new Promise(resolve => w.addEventListener('load', resolve, { once: true }));
  await sleep(350);
  assert.deepEqual(runtimeErrors, [], 'No runtime errors at boot');
  assert(w.PmalInterface, 'New UI initialized');
  assert.equal(visibleView(), 'v-home');
  const ids = [...d.querySelectorAll('[id]')].map(el => el.id);
  assert.equal(ids.length, new Set(ids).size, 'No duplicated DOM IDs');
  assert.equal($('hs-t').closest('.view').id, 'v-stats');
  assert.equal($('apicard').closest('.view').id, 'v-settings');
  assert.equal($('home-imp-file').closest('.view').id, 'v-settings');
  assert.equal($('btn-start').closest('.view').id, 'v-practice');
  assert.equal(w.S.ha[0].id, 'kept-history');
  assert.equal(w.S.reviewSessions.keep.title, 'Minha revisão');
  const bankIds = w.QQ.map(q => q.id).join('|');
  const beforeNavigation = JSON.stringify(w.S.ha);
  for (const route of ['more','settings','practice','reviewhub','stats','assuntos','biblio','crono','home']) {
    w.PmalInterface.navigate(route);
    assert.equal(visibleView(), 'v-'+route, 'Route '+route);
  }
  assert.equal(JSON.stringify(w.S.ha), beforeNavigation, 'Navigation never writes answers');
  assert.equal(w.QQ.map(q => q.id).join('|'), bankIds, 'Question IDs unchanged');
  assert.equal(w.localStorage.getItem('pmal26_cppm_review_notes_20260903_v1'), '{"preserved":true}');
  assert($('ui-week').children.length === 7);
  click('#ui-week button'); assert.equal($('ui-week-detail').hidden, false);

  // The selected displayed task is resolved independently of Cronograma's index order.
  const today = w.PmalInterface.taskData();
  const target = today.tasks.find(t => t.type==='adaptive' && !t.item.dsoBlocks);
  if (target) {
    let called;
    const old = w.runAdaptiveItem;
    w.runAdaptiveItem = i => { called = w.S._adaptiveDisplay.items[i]; };
    click('[data-ui-task="'+target.id+'"]');
    assert.equal(called.subject, target.item.subject);
    assert.equal(called.kind, target.item.kind);
    w.runAdaptiveItem = old;
  }
  w.PmalInterface.navigate('practice');
  assert.equal(d.querySelector('.bnav [aria-current="page"]').dataset.n, 'practice');
  $('sel-source').value = 'all'; $('sel-qty').value = '5'; $('sel-niv').value = 'all';
  const ordinaryMode = d.querySelector('#ch-mode .chip[data-mode="simulado"]'); ordinaryMode.click();
  w.S._adaptiveContext = { item: { subject: 'do not complete' } };
  $('btn-start').click();
  assert.equal(visibleView(), 'v-quiz');
  assert.equal(w.S._adaptiveContext, null);
  assert(w.S.sq.length > 0);
  assert(w.S.sq.every(q => !q.reviewOnly && q.scope !== 'review_only'));
  const beforeAnswer = w.S.ha.length;
  const activeQuestion = w.S.sq[w.S.ci];
  $(activeQuestion.g === 'CERTO' ? 'btn-c' : 'btn-e').click();
  assert.equal(w.S.ha.length, beforeAnswer, 'Choice waits for confidence');
  assert.equal($('ar-conf').style.display, 'block');
  click('#ar-conf .bconf');
  assert.equal(visibleView(), 'v-fb');
  assert.equal(w.S.ha.length, beforeAnswer + 1);
  assert($('fb-co').textContent.length > 0);
  click('#v-fb [data-ui-focus]');
  assert(d.body.classList.contains('ui-focus'));
  w.PmalInterface.navigate('home');
  assert(!d.body.classList.contains('ui-focus'));
  click('[data-ui-resume]'); assert.equal(visibleView(), 'v-fb');
  assert(d.body.classList.contains('ui-focus'));
  $('btn-nx').click(); assert.equal(visibleView(), 'v-quiz');
  while(visibleView()==='v-quiz'){
    const q=w.S.sq[w.S.ci];$(q.g==='CERTO'?'btn-c':'btn-e').click();click('#ar-conf .bconf');$('btn-nx').click();
  }
  assert.equal(visibleView(), 'v-res', 'A completed session reaches its result');
  assert.equal(d.querySelector('.bnav [aria-current="page"]').dataset.n, 'practice');

  w.startSimulado('equilibrado');
  const deadline=w.S.simDeadline;
  w.PmalInterface.navigate('practice');
  click('#ch-mode .chip[data-mode="materia"]');
  $('sel-qty').value='20';$('sel-qty').dispatchEvent(new w.Event('change',{bubbles:true}));
  assert.equal(w.S.mode,'cebraspe','Editing the next session preserves the running exam');
  assert.equal(w.S.simDeadline,deadline);
  w.PmalInterface.navigate('home');click('[data-ui-resume]');
  assert.equal(visibleView(),'v-sim');
  assert.equal(w.S.mode,'cebraspe');
  w.tickSim();assert($('sim-timer').textContent.includes('⏳'));
  w.ansSim('CERTO');w.finishSim();
  assert.equal(visibleView(),'v-simres');
  assert($('v-simres').textContent.includes('P1/P2'));

  w.S._theoryContext={item:{kind:'dso',subject:'Matemática'},target:w.localDateKey(new Date())};
  w.sv('adaptive-theory');w.completeTheoryReview();w.PmalInterface.navigate('home');
  assert.equal(d.querySelector('[data-ui-resume]'),null,'Completed theory is not offered as resumable');
  w.S._flashQueue=[];w.S._flashIdx=0;w.sv('flash');w.PmalInterface.navigate('home');
  assert.equal(d.querySelector('[data-ui-resume]'),null,'Empty flashcard catalog is not a study session');

  // Exclusive review remains isolated, even after visiting the new home.
  const count = w.S.ha.length;
  w.startReview20260823();
  const review = w.S.sq[w.S.ci];
  assert(review.reviewOnly || review.scope === 'review_only');
  $(review.g === 'CERTO' ? 'btn-c' : 'btn-e').click();
  click('#ar-conf .bconf');
  assert.equal(w.S.ha.length, count);
  assert.equal(w.S.reviewSessions['2026-08-23'].attempts.at(-1).id, review.id);
  // Launch a regular error review after an exclusive one: no inherited scope.
  const ordinary = w.QQ.find(q => !q.reviewOnly && !q.missingContext);
  w.S.eids.add(ordinary.id);
  w.PmalInterface.navigate('reviewhub');
  w.reviewHubStartCurrentErrors();
  assert.equal(w.S.reviewActive, null);
  assert.equal(w.S._adaptiveContext, null);
  const regular = w.S.sq[w.S.ci];
  $(regular.g === 'CERTO' ? 'btn-c' : 'btn-e').click(); click('#ar-conf .bconf');
  assert.equal(w.S.ha.length, count+1);

  w.SS();
  const saved=JSON.parse(w.localStorage.getItem('pmal26'));
  assert.equal(saved.ha[0].id, 'kept-history');
  assert.equal(saved.reviewSessions.keep.title, 'Minha revisão');
  assert.equal(w.localStorage.getItem('pmal26_key'), 'test-key-never-export');
  w.eval('apiKey=""');
  await w.generateQuestionsAI(true);
  assert.equal(visibleView(),'v-settings');
  assert.equal(d.activeElement.id,'inp-key');
  w.PmalInterface.navigate('redacao');await w.corrigirRedacaoAI();
  assert.equal(visibleView(),'v-settings');
  assert.equal(d.activeElement.id,'inp-key');
  assert.deepEqual(runtimeErrors, [], 'No runtime errors across study flows');
  console.log('OK: Today, all routes, real task mapping, answer/confidence, focus/resume, exclusive reviews, regular error reviews and stored progress.');
  dom.window.close();
})().catch(error => { console.error(error); dom.window.close(); process.exitCode=1; });
