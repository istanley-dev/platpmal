const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync(require('path').join(__dirname, '..', 'index.html'), 'utf8');
const source = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]).join('\n');

function fakeElement(id) {
  return {
    id,
    style: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    value: id === 'sel-qty' ? '20' : id === 'sel-niv' ? 'all' : '',
    textContent: '', innerHTML: '', disabled: false,
    addEventListener() {}, appendChild() {}, remove() {}, focus() {}, select() {},
    setSelectionRange() {}, scrollIntoView() {}, closest() { return fakeElement('closest'); },
    querySelectorAll() { return []; }, querySelector() { return fakeElement('child'); }
  };
}

function makeStorage(seed) {
  const data = new Map(Object.entries(seed || {}));
  return {
    get length() { return data.size; },
    key(i) { return [...data.keys()][i] || null; },
    getItem(k) {
      if (data.has(k)) return data.get(k);
      if (k === 'pmal26_cycle2_20260821_done') return '1';
      if (k.startsWith('pmal26_import_') && k !== 'pmal26_import_revisao_20260825_v1') return 'ok';
      return null;
    },
    setItem(k, v) { data.set(k, String(v)); },
    removeItem(k) { data.delete(k); },
    _data: data
  };
}

function boot(storage) {
  const elements = new Map();
  const element = (id) => { if (!elements.has(id)) elements.set(id, fakeElement(id)); return elements.get(id); };
  const document = {
    getElementById: element,
    querySelectorAll() { return []; },
    querySelector() { return fakeElement('query'); },
    createElement(tag) { return fakeElement(tag); },
    body: fakeElement('body')
  };
  const context = {
    console, document, localStorage: storage, navigator: { clipboard: { writeText: () => Promise.resolve() } },
    location: { reload() {} }, URL: { createObjectURL() { return 'blob:test'; }, revokeObjectURL() {} }, Blob,
    alert() {}, confirm() { return true; }, setTimeout() { return 1; }, clearTimeout() {}, setInterval() { return 1; }, clearInterval() {},
    Math, Date, JSON, Set, Map, Object, Array, String, Number, Boolean, RegExp, Promise, Error
  };
  context.window = context; context.globalThis = context;
  vm.createContext(context);
  const exportHook = `\n;globalThis.__app={S,QQ,REVIEW_QUESTIONS_20260823,REVIEW_QUESTIONS_20260824,REVIEW_QUESTIONS_20260825,buildAdaptiveDay,adaptiveItemDesc,adaptiveReviewQuestions,buildDailyPool,startQ,startSimulado,startWeekReview,findQuestionById,SS,LS,registerStudySubject,localDateKey,testMathAutoPool:function(){var old=dayPlan;dayPlan=function(){return {subs:['Matemática','Direito Administrativo'],target:12,primary:['Matemática','Direito Administrativo'],maintenance:['Matemática'],weak:null};};try{return buildDailyPool();}finally{dayPlan=old;}}};`;
  new vm.Script(source + exportHook, { filename: 'index.inline.js' }).runInContext(context, { timeout: 15000 });
  return context.__app;
}

const oldState = {
  ha: [{ id: 'legacy-answer', ok: true, ts: 123 }], eids: [], AS: {}, round: 7, log: [], metas: {}, xp: 11,
  streak: 2, lastDay: '2026-08-24', plan: { examDate: '' }, daily: { d: '', q: 0 }, bibLidos: {},
  leituraDia: { d: '', keys: [] }, flash: { cards: {} }, weekly: { lastDone: 0 },
  reviewSessions: { legacy: { title: 'preservar' } }, cycleId: 'ciclo2_20260821'
};
const storage = makeStorage({ pmal26: JSON.stringify(oldState) });
const app = boot(storage);

assert.equal(app.S.ha[0].id, 'legacy-answer', 'histórico antigo deve sobreviver');
assert.equal(app.S.reviewSessions.legacy.title, 'preservar', 'sessões antigas devem sobreviver');
assert.equal(app.S.reviewSessions['2026-08-25'].total, 52);
assert.equal(app.S.reviewSessions['2026-08-25'].net, 38);
assert.equal(app.S.reviewSessions['2026-08-25'].accuracy, 86.5);
assert.equal(app.S.studyHistory['2026-08-25'].subjects.find((x) => x.subject === 'Matemática').total, undefined, 'teoria não ganha estatística inventada');

const everyId = app.QQ.concat(app.REVIEW_QUESTIONS_20260823, app.REVIEW_QUESTIONS_20260824, app.REVIEW_QUESTIONS_20260825).map((q) => q.id);
assert.equal(new Set(everyId).size, everyId.length, 'IDs devem ser únicos');
assert.equal(app.REVIEW_QUESTIONS_20260825.length, 24);
assert.equal(app.REVIEW_QUESTIONS_20260825.filter((q) => q.reviewClass === 'erro').length, 7, 'sete itens prioritários acompanham os sete erros');
assert.equal(app.QQ.some((q) => q.reviewOnly || q.scope === 'review_only'), false, 'QQ não pode conter review_only');
assert.equal(app.REVIEW_QUESTIONS_20260825.every((q) => q.scope === 'review_only' && q.reviewOnly), true);
assert.equal(app.S.ha.some((x) => x.scope === 'review_only'), false, 'revisão exclusiva não entra nas métricas de respostas');
assert.equal(app.S.log.some((x) => x.scope === 'review_only'), false, 'revisão exclusiva não entra no log geral');

const d1 = app.buildAdaptiveDay('2026-08-26');
const d1Items = Object.values(d1.groups).flat();
assert.equal(d1Items.filter((x) => x.subject === 'Direito Administrativo').length, 1, 'Administrativo D+1 sem duplicação');
const mathD1 = d1Items.find((x) => x.subject === 'Matemática');
assert(mathD1 && mathD1.kind === 'd1');
assert.match(app.adaptiveItemDesc(mathD1), /Revisão teórica/);
assert.match(app.adaptiveItemDesc(mathD1), /papel\/caneta/);

const study25 = app.buildAdaptiveDay('2026-08-25').groups.study;
assert(study25.find((x) => x.subject === 'Direito Administrativo'), 'estudo do dia usa histórico real');
const mathStudy25 = study25.find((x) => x.subject === 'Matemática');
assert(mathStudy25, 'Matemática teórica aparece no estudo real do dia');
assert.match(app.adaptiveItemDesc(mathStudy25), /estudo teórico/i);

for (const date of ['2026-08-24', '2026-08-26', '2026-08-28']) {
  assert.equal(app.buildAdaptiveDay(date).groups.port.filter((x) => x.subject === 'Língua Portuguesa').length, 1, `Português fixo em ${date}`);
}
assert.equal(app.buildAdaptiveDay('2026-08-25').groups.port.length, 0, 'Português não é fixo na terça');

app.registerStudySubject('2026-08-25', { subject: 'Língua Portuguesa', mode: 'questions', topics: ['Sintaxe'] });
const mergedPort = app.buildAdaptiveDay('2026-08-26');
assert.equal(Object.values(mergedPort.groups).flat().filter((x) => x.subject === 'Língua Portuguesa').length, 1, 'Português fixo + D+1 deve virar um card');

const d7 = app.buildAdaptiveDay('2026-09-01');
const d7Items = Object.values(d7.groups).flat();
assert(d7Items.find((x) => x.subject === 'Direito Administrativo'));
assert.match(app.adaptiveItemDesc(d7Items.find((x) => x.subject === 'Matemática')), /Revisão teórica/);

const mathPool = app.testMathAutoPool();
assert.equal(mathPool.pool.some((q) => q.m === 'Matemática'), false, 'Matemática fora da bateria automática');

const mathQuestion = app.QQ.find((q) => q.m === 'Matemática');
const adminQuestion = app.QQ.find((q) => q.m === 'Direito Administrativo');
app.S.log = [
  { id: mathQuestion.id, m: mathQuestion.m, a: mathQuestion.a, res: 'acerto', ts: Date.now() },
  { id: adminQuestion.id, m: adminQuestion.m, a: adminQuestion.a, res: 'erro', ts: Date.now() }
];
app.startWeekReview();
assert.equal(app.S.sq.some((q) => q.m === 'Matemática'), false, 'Matemática fora da revisão semanal por questões');

app.S.mode = 'simulado'; app.S.qty = 10; app.startQ();
assert.equal(app.S.sq.some((q) => q.reviewOnly || q.scope === 'review_only'), false, 'simulado geral sem review_only');
app.startSimulado('equilibrado');
assert.equal(app.S.sq.some((q) => q.reviewOnly || q.scope === 'review_only'), false, 'Simulado Real sem review_only');

app.S.reviewSessions['2026-08-25'].attempts = app.REVIEW_QUESTIONS_20260825.map((q) => ({ id: q.id, ok: true, conf: 'certeza', ts: Date.now() }));
const admFuture = d7Items.find((x) => x.subject === 'Direito Administrativo');
assert(app.adaptiveReviewQuestions(admFuture).length <= 2, 'melhora deve reduzir a carga futura');

app.S.studyHistory.reloadProbe = { date: 'reloadProbe', subjects: [] }; app.SS();
app.S.studyHistory = {}; app.LS();
assert(app.S.studyHistory.reloadProbe, 'studyHistory deve sobreviver ao recarregamento');
assert.equal(app.findQuestionById('rev_20260825_adm_001').reviewDate, '2026-08-25', 'lookup deve localizar revisão exclusiva');

console.log('adaptive schedule tests: ok');
