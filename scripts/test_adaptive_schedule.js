const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const source = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]).join('\n');

function fakeElement(id) {
  return {
    id, style: {}, className: '', dataset: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    value: id === 'sel-qty' ? '20' : id === 'sel-niv' ? 'all' : '',
    textContent: '', innerHTML: '', disabled: false,
    addEventListener() {}, appendChild() {}, insertAdjacentHTML() {}, remove() {}, focus() {}, select() {},
    setSelectionRange() {}, scrollIntoView() {}, closest() { return fakeElement('closest'); },
    querySelectorAll() { return []; }, querySelector() { return fakeElement('child'); }
  };
}

function makeStorage(seed) {
  const data = new Map(Object.entries(seed || {}));
  return {
    get length() { return data.size; }, key(i) { return [...data.keys()][i] || null; },
    getItem(k) {
      if (data.has(k)) return data.get(k);
      if (k === 'pmal26_cycle2_20260821_done') return '1';
      if (k.startsWith('pmal26_import_') && k !== 'pmal26_import_revisao_20260825_v1') return 'ok';
      return null;
    },
    setItem(k, v) { data.set(k, String(v)); }, removeItem(k) { data.delete(k); }, _data: data
  };
}

function boot(storage) {
  const elements = new Map();
  const element = (id) => { if (!elements.has(id)) elements.set(id, fakeElement(id)); return elements.get(id); };
  const document = {
    getElementById: element, querySelectorAll() { return []; }, querySelector() { return fakeElement('query'); },
    createElement(tag) { return fakeElement(tag); }, body: fakeElement('body')
  };
  const context = {
    console, document, localStorage: storage, navigator: { clipboard: { writeText: () => Promise.resolve() } },
    location: { protocol: 'https:', reload() {} }, URL: { createObjectURL() { return 'blob:test'; }, revokeObjectURL() {} }, Blob,
    alert() {}, confirm() { return true; }, setTimeout() { return 1; }, clearTimeout() {}, setInterval() { return 1; }, clearInterval() {},
    Math, Date, JSON, Set, Map, Object, Array, String, Number, Boolean, RegExp, Promise, Error
  };
  context.window = context; context.globalThis = context;
  vm.createContext(context);
  const exportHook = `
;globalThis.__app={S,QQ,WEEK,QUESTION_TEXTS,REVIEW_QUESTIONS_20260823,REVIEW_QUESTIONS_20260824,REVIEW_QUESTIONS_20260825,
buildAdaptiveDay,adaptiveItemDesc,adaptiveReviewQuestions,buildDailyPool,startQ,startSimulado,startWeekReview,
findQuestionById,SS,LS,registerStudySubject,localDateKey,studyClass,studySubjects,errorCombatItems,
lawDailySelection,computeTodaysArticles,touchLeituraDia,recordLawMemory,lawMemoryRec,prepareQuestionContexts,questionUsable,getPool,
phaseInfo,dayPlan,renderCrono,MAX_ADAPTIVE_ITEMS,DATA_ALVO_PROVA,
testMathAutoPool:function(){var old=dayPlan;dayPlan=function(){return {subs:['Matemática','Direito Administrativo'],target:12,primary:['Matemática','Direito Administrativo'],maintenance:['Matemática'],weak:null};};try{return buildDailyPool();}finally{dayPlan=old;}}};`;
  new vm.Script(source + exportHook, { filename: 'index.inline.js' }).runInContext(context, { timeout: 20000 });
  return context.__app;
}

const oldState = {
  ha: [{ id: 'legacy-answer', ok: true, ts: 123 }], eids: [], AS: {}, round: 7, log: [], metas: {}, xp: 11,
  streak: 2, lastDay: '2026-08-24', plan: { examDate: '' }, daily: { d: '', q: 0 }, bibLidos: {},
  leituraDia: { d: '', keys: [] }, flash: { cards: {} }, weekly: { lastDone: Date.now() },
  reviewSessions: { legacy: { title: 'preservar' } }, cycleId: 'ciclo2_20260821'
};
const storage = makeStorage({ pmal26: JSON.stringify(oldState) });
const app = boot(storage);

// Compatibilidade, importações e IDs.
assert.equal(app.S.ha[0].id, 'legacy-answer');
assert.equal(app.S.reviewSessions.legacy.title, 'preservar');
assert.equal(app.S.plan.examDate, '2026-11-29');
assert.equal(app.S.reviewSessions['2026-08-25'].total, 52);
assert.equal(app.S.reviewSessions['2026-08-25'].accuracy, 86.5);
assert.equal(app.S.studyHistory['2026-08-25'].subjects.find((x) => x.subject === 'Matemática').total, undefined);
const everyId = app.QQ.concat(app.REVIEW_QUESTIONS_20260823, app.REVIEW_QUESTIONS_20260824, app.REVIEW_QUESTIONS_20260825).map((q) => q.id);
assert.equal(new Set(everyId).size, everyId.length, 'IDs devem continuar únicos');

// DSO-base solicitado e estudo previsto != estudo concluído.
assert.deepEqual(Array.from(app.WEEK[1].subs), ['Direito Constitucional', 'Noções de Informática']);
assert.deepEqual(Array.from(app.WEEK[2].subs), ['Direito Administrativo', 'Matemática']);
assert.deepEqual(Array.from(app.WEEK[3].subs), ['Direito Penal', 'Direito Processual Penal']);
const emptyFuture = app.buildAdaptiveDay('2026-08-31');
assert(emptyFuture.groups.dso.some((x) => x.subject === 'Direito Constitucional'));
assert.equal(app.studySubjects('2026-08-31').length, 0, 'planejamento não vira estudo real');

// D+1 de 25/08 em 26/08, sem duplicação; Português fixo; Matemática teórica.
const d1 = app.buildAdaptiveDay('2026-08-26');
const d1Items = Object.values(d1.groups).flat();
assert.equal(d1Items.filter((x) => x.subject === 'Direito Administrativo').length, 1);
const admD1 = d1Items.find((x) => x.subject === 'Direito Administrativo');
assert(admD1.offsets.includes(1));
const mathD1 = d1Items.find((x) => x.subject === 'Matemática');
assert(mathD1 && mathD1.offsets.includes(1));
assert.match(app.adaptiveItemDesc(mathD1), /Revisão teórica/);
assert.match(app.adaptiveItemDesc(mathD1), /papel\/caneta/);
assert.equal(d1Items.filter((x) => x.subject === 'Língua Portuguesa').length, 1);

// Classificação e cadências variáveis.
app.registerStudySubject('2026-08-01', { subject: 'Direito Constitucional', mode: 'questions', topics: ['Direitos Fundamentais'], total: 20, correct: 19, errors: 0, accuracy: 95 });
app.registerStudySubject('2026-08-02', { subject: 'Direitos Humanos', mode: 'questions', topics: ['Tortura'], total: 10, correct: 6, errors: 4, accuracy: 60 });
app.registerStudySubject('2026-08-03', { subject: 'Legislação Penal Especial', mode: 'questions', topics: ['Lei de Drogas'], total: 20, correct: 15, errors: 5, accuracy: 75 });
assert.equal(app.studyClass(app.studySubjects('2026-08-01')[0]).label, 'MANUTENÇÃO');
assert.equal(app.studyClass(app.studySubjects('2026-08-02')[0]).label, 'CRÍTICO');
assert.equal(app.studyClass(app.studySubjects('2026-08-03')[0]).label, 'CRÍTICO');
assert(Object.values(app.buildAdaptiveDay('2026-08-09').groups).flat().some((x) => x.subject === 'Direitos Humanos' && (x.offsets || []).includes(7)));
assert.equal(Object.values(app.buildAdaptiveDay('2026-08-22').groups).flat().some((x) => x.subject === 'Direito Constitucional' && (x.offsets || []).includes(21)), false);
assert(Object.values(app.buildAdaptiveDay('2026-08-31').groups).flat().some((x) => x.subject === 'Direito Constitucional' && (x.offsets || []).includes(30)));
assert(Object.values(app.buildAdaptiveDay('2026-08-23').groups).flat().some((x) => x.subject === 'Direitos Humanos' && (x.offsets || []).includes(21)));

// Português seg/qua/sex e fusão com revisão.
for (const date of ['2026-08-24', '2026-08-26', '2026-08-28']) {
  assert.equal(Object.values(app.buildAdaptiveDay(date).groups).flat().filter((x) => x.subject === 'Língua Portuguesa').length, 1);
}
assert.equal(Object.values(app.buildAdaptiveDay('2026-08-25').groups).flat().filter((x) => x.subject === 'Língua Portuguesa').length, 0);
app.registerStudySubject('2026-08-25', { subject: 'Língua Portuguesa', mode: 'questions', topics: ['Sintaxe'] });
assert.equal(Object.values(app.buildAdaptiveDay('2026-08-26').groups).flat().filter((x) => x.subject === 'Língua Portuguesa').length, 1);

// Carga limitada, erros e manutenção antiga.
const capped = app.buildAdaptiveDay('2026-08-26');
assert(Object.values(capped.groups).flat().length <= app.MAX_ADAPTIVE_ITEMS);
assert(capped.summary.deferred >= 0);
assert(app.errorCombatItems('2026-08-26').length <= 3);
assert(Object.values(app.buildAdaptiveDay('2026-08-31').groups).flat().some((x) => x.kind === 'advanced'));

// Matemática nunca entra automaticamente em bateria mobile.
const mathPool = app.testMathAutoPool();
assert.equal(mathPool.pool.some((q) => q.m === 'Matemática'), false);
const mathQuestion = app.QQ.find((q) => q.m === 'Matemática');
const adminQuestion = app.QQ.find((q) => q.m === 'Direito Administrativo');
app.S.log = [
  { id: mathQuestion.id, m: mathQuestion.m, a: mathQuestion.a, res: 'acerto', ts: Date.now() },
  { id: adminQuestion.id, m: adminQuestion.m, a: adminQuestion.a, res: 'erro', ts: Date.now() }
];
app.startWeekReview();
assert.equal(app.S.sq.some((q) => q.m === 'Matemática'), false);

// Banco de Leis diário e memória espaçada.
const weekdayLaw = app.computeTodaysArticles();
assert(weekdayLaw.todays.length >= 5 && weekdayLaw.todays.length <= 8);
const legacyFive = weekdayLaw.todays.slice(0, 5);
app.S.leituraDia = { d: app.localDateKey(new Date()), keys: Array.from(legacyFive), inReview: false };
app.touchLeituraDia();
assert.equal(app.S.leituraDia.keys.length, 7, 'rotina antiga do mesmo dia deve migrar de 5 para 7 dispositivos');
assert(legacyFive.every((key) => app.S.leituraDia.keys.includes(key)), 'migração deve preservar os dispositivos já exibidos');
const law = app.lawDailySelection('2026-08-26');
assert(law.deadlines.length > 0 && law.deadlines.length <= 5);
assert(law.juris.length > 0 && law.juris.length <= 3);
assert(law.traps.length > 0 && law.traps.length <= 4);
const before = Date.now();app.recordLawMemory('deadline:test', 'error');
assert.equal(Math.round((app.lawMemoryRec('deadline:test').due - before) / 86400000), 1);

// review_only isolado dos simulados e do banco principal.
assert.equal(app.QQ.some((q) => q.reviewOnly || q.scope === 'review_only'), false);
assert(app.REVIEW_QUESTIONS_20260825.every((q) => q.reviewOnly && q.scope === 'review_only'));
app.S.mode = 'simulado'; app.S.qty = 10; app.startQ();
assert.equal(app.S.sq.some((q) => q.reviewOnly || q.scope === 'review_only'), false);
app.startSimulado('equilibrado');
assert.equal(app.S.sq.some((q) => q.reviewOnly || q.scope === 'review_only'), false);

// Contextos de Português: texto único por textId e bloqueio quando faltar.
const p1 = { id: 'ctx1', m: 'Língua Portuguesa', tx: 'Texto-base compartilhado.', e: 'Item 1.' };
const p2 = { id: 'ctx2', m: 'Língua Portuguesa', tx: 'Texto-base compartilhado.', e: 'Item 2.' };
const missing = { id: 'ctx3', m: 'Língua Portuguesa', textId: 'revtxt_ausente', e: 'Conforme o texto precedente.' };
app.prepareQuestionContexts([p1, p2, missing]);
assert.equal(p1.textId, p2.textId);
assert.equal(app.QUESTION_TEXTS[p1.textId], 'Texto-base compartilhado.');
assert.equal(missing.missingContext, true);
assert.equal(app.questionUsable(missing), false);

// Fases simuladas e mobile-first.
assert.equal(app.phaseInfo('2026-09-27').ph, 1);
assert.equal(app.phaseInfo('2026-09-28').ph, 2);
assert.equal(app.phaseInfo('2026-10-26').ph, 3);
assert.equal(app.phaseInfo('2026-11-16').ph, 4);
assert.match(html, /@media\(max-width:430px\)[\s\S]*\.adaptive-list,\.law-memory-grid\{grid-template-columns:1fr\}/);

// Persistência, reload e renderização básica.
app.S.studyHistory.reloadProbe = { date: 'reloadProbe', subjects: [] };app.S.lawMemory.cards.reloadProbe = { due: 123 };app.SS();
assert.equal(JSON.parse(storage.getItem('pmal26')).lawMemory.cards.reloadProbe.due, 123, 'SS deve persistir lawMemory');
const reloaded = boot(storage);
assert(reloaded.S.studyHistory.reloadProbe);
assert.equal(reloaded.S.lawMemory.cards.reloadProbe.due, 123);
assert.equal(app.findQuestionById('rev_20260825_adm_001').reviewDate, '2026-08-25');
assert.doesNotThrow(() => app.renderCrono());

console.log('adaptive PMAL schedule tests: ok');
