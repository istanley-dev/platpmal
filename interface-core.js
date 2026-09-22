/* Presentation layer only: existing question engines, IDs and storage remain authoritative. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const safe = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const glyphs = {
    shield:'<path d="M12 3 4 6v6c0 5 8 9 8 9s8-4 8-9V6z"/>',
    home:'<path d="m3 10 9-7 9 7v11h-6v-8H9v8H3z"/>',
    questions:'<path d="m3 6 2 2 4-4M12 6h9M3 13h6M12 13h9M3 20h6M12 20h9"/>',
    review:'<path d="M3 10a9 9 0 1 1 2 8M3 4v6h6M12 7v5l3 2"/>',
    calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 11h18M7 15h3M14 15h3"/>',
    book:'<path d="M12 6C8 3 3 4 3 4v16s5-1 9 2c4-3 9-2 9-2V4s-5-1-9 2v16"/>',
    chart:'<path d="M4 3v18h18M8 16v-4M13 16V8M18 16V5"/>',
    clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    arrow:'<path d="M4 12h16m-6-6 6 6-6 6"/>',
    more:'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    settings:'<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="3"/><circle cx="15" cy="17" r="3"/>',
    pen:'<path d="m16 3 5 5-12 12-6 1 1-6zM13 6l5 5"/>',
    target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    sparkle:'<path d="m12 3 2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6z"/>'
  };
  const icon = name => '<svg class="ui-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+(glyphs[name]||glyphs.book)+'</svg>';
  const routes = {home:'Hoje',practice:'Questões',reviewhub:'Revisões',more:'Mais recursos',settings:'Configurações',crono:'Cronograma',stats:'Progresso',biblio:'Biblioteca',assuntos:'Radar de assuntos',redacao:'Redação',metas:'Metas de leitura',res:'Resultado da sessão',sim:'Simulado',simres:'Resultado do simulado',quiz:'Questões',fb:'Comentário da questão',flash:'Flashcards','adaptive-theory':'Revisão teórica',miniaula:'Mini-aula',gen:'Questões com IA'};
  const state = {active:'home',resume:null,items:[],tasks:[],date:null,focus:false,formSession:null};
  let baseNav, baseView;
  const navButton = (route,label,glyph) => '<button type="button" data-ui-route="'+route+'">'+icon(glyph)+'<span>'+label+'</span></button>';
  const head = (title,sub) => '<div class="ui-page-head"><div><h1>'+title+'</h1>'+(sub?'<p>'+sub+'</p>':'')+'</div></div>';
  function view(id,html) {const el=document.createElement('section');el.id='v-'+id;el.className='view';el.innerHTML=html;return el;}
  function brand(){return '<span class="ui-brand-mark">'+icon('shield')+'</span><div><div class="ui-brand-name">PMAL</div><div class="ui-brand-label">CENTRAL TÁTICA</div></div>';}
  function navigate(route){
    if(route==='practice'){
      // Editing a future session must not change an active exam's clock or score mode.
      if(state.active!=='practice')state.formSession=canResume()?{mode:S.mode,subs:(S.subs||[]).slice(),niv:S.niv,qty:S.qty,sim:S.sim}:null;
      window.sv('practice');
    } else if(route==='reviewhub') {window.openReviewHub();syncNavigation('reviewhub');}
    else if(route==='more'||route==='settings'){window.sv(route);}
    else if(route==='sim-selector'){window.openSimuladoSelector();}
    else {baseNav(route);syncNavigation(state.active);}
  }
  function syncNavigation(id){
    const group=['practice','quiz','fb','sim','simres','res'].includes(id)?'practice':id==='reviewhub'?'reviewhub':id==='home'?'home':'more';
    document.querySelectorAll('.ui-side-nav [data-ui-route]').forEach(b=>{
      const selected=b.dataset.uiRoute===id||(b.dataset.uiRoute==='practice'&&group==='practice');
      if(selected)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');
    });
    document.querySelectorAll('.bnav .nb').forEach(b=>{const selected=b.dataset.n===group;b.classList.toggle('act',selected);if(selected)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
    $('ui-current-page').textContent=routes[id]||'Estudo';
    const focusAllowed=['quiz','fb','adaptive-theory','flash'].includes(id);
    document.body.classList.toggle('ui-focus',state.focus&&focusAllowed);
    document.querySelectorAll('[data-ui-focus]').forEach(el=>el.checked=state.focus);
  }
  function installNavigation(){
    const sidebar=document.createElement('aside');sidebar.className='ui-sidebar';sidebar.setAttribute('aria-label','Navegação da plataforma');
    sidebar.innerHTML='<div class="ui-brand">'+brand()+'</div><div><div class="ui-nav-label">Área de estudos</div><nav class="ui-side-nav" aria-label="Estudar">'+navButton('home','Hoje','home')+navButton('practice','Questões','questions')+navButton('reviewhub','Revisões','review')+navButton('crono','Cronograma','calendar')+navButton('sim-selector','Simulados','target')+navButton('biblio','Biblioteca','book')+navButton('stats','Progresso','chart')+navButton('more','Mais recursos','more')+'</nav></div><div class="ui-side-bottom"><nav class="ui-side-nav" aria-label="Preferências">'+navButton('settings','Configurações','settings')+'</nav><div class="ui-side-footer">PMAL · CEBRASPE<br>Preparação 2026</div></div>';
    document.body.prepend(sidebar);
    const hi=document.querySelector('.hi');
    hi.insertAdjacentHTML('afterbegin','<div class="ui-breadcrumb">Área de estudos <span aria-hidden="true">/</span> <strong id="ui-current-page">Hoje</strong></div><div class="ui-brand ui-mobile-brand">'+brand()+'</div>');
    document.querySelector('.bnav').setAttribute('aria-label','Navegação principal');
    document.querySelector('.bnav').innerHTML=[['home','Hoje','home'],['practice','Questões','questions'],['reviewhub','Revisões','review'],['more','Mais','more']].map(([route,label,glyph])=>'<button type="button" class="nb" data-n="'+route+'" data-ui-route="'+route+'">'+icon(glyph)+'<span>'+label+'</span></button>').join('');
    baseNav=window.gN;baseView=window.sv;
    window.gN=navigate;
    window.sv=function(id){
      if(['quiz','fb','sim','flash','adaptive-theory'].includes(id))state.resume=id;
      if(['res','simres'].includes(id))state.resume=null;
      baseView(id);state.active=id;
      if(id==='home')renderToday();
      if(id==='reviewhub')renderReviewSummary();
      syncNavigation(id);
      window.scrollTo({top:0,behavior:'instant'});
    };
  }
  function splitHome(){
    const previous=$('v-home');previous.id='v-practice';previous.classList.remove('active');
    const container=document.querySelector('.container');
    const today=view('home','');today.classList.add('active');container.prepend(today);
    const settings=view('settings',head('Configurações e backup','Suas preferências e seu progresso, em um só lugar.'));
    const more=view('more',head('Seu espaço de estudo.','Todos os recursos da sua preparação.')+'<div class="ui-resources" id="ui-resources"></div>');
    container.append(more,settings);
    // Move live nodes so every existing listener and import control is preserved.
    const backup=$('home-imp-file').closest('.card');settings.append(backup);
    const api=$('apicard');settings.append(api);
    settings.insertAdjacentHTML('beforeend','<div class="ui-settings-links"><button class="ui-secondary" type="button" id="ui-api-toggle">Configurar chave de IA</button><button class="ui-secondary" type="button" data-ui-route="crono">Data da prova e cronograma</button></div>');
    backup.querySelector('.slbl').textContent='Backup do progresso';
    const legacySummary=previous.querySelector('.hcard');$('v-stats').prepend(legacySummary);
    legacySummary.querySelector('h2').textContent='Seu desempenho';
    $('v-stats').insertBefore($('home-gam'),$('stats-bd'));
    previous.prepend(document.createRange().createContextualFragment(head('Questões','Monte uma sessão com as matérias e fontes que você precisa.')));
    const ops=previous.querySelector('.tiles');const sourceButtons=Array.from(ops.querySelectorAll('button')).concat($('btn-gen-manual'));
    const resources=[['btn-crono','Cronograma','Plano diário e organização da semana','calendar'],['btn-sim','Simulados','Treino completo no formato CEBRASPE','target'],['btn-red','Redação','Discursiva e autoavaliação','pen'],['btn-metas','Metas de leitura','Dispositivos ligados aos seus erros','book'],['btn-cruel','CEBRASPE Cruel','Questões de maior dificuldade','target'],['btn-gen-manual','Questões com IA','Prática adicional por assunto','sparkle']];
    resources.forEach(([id,title,sub,glyph])=>{const b=sourceButtons.find(el=>el.id===id);b.className='ui-resource';b.innerHTML=icon(glyph)+'<span><strong>'+title+'</strong><small>'+sub+'</small></span>';if(id==='btn-crono'){const desc=b.querySelector('small');desc.id='btn-crono-sub';} $('ui-resources').append(b);});
    // Keep this existing hook in the review page for scripts that refresh its subtitle.
    const reviewButton=$('btn-review-hub');reviewButton.hidden=true;$('v-reviewhub').append(reviewButton);
    ops.remove();previous.querySelectorAll('.sec-k').forEach(el=>{if(el.textContent.trim()==='Operações')el.remove();else el.textContent='Sua sessão';});
    $('btn-start').textContent='Iniciar questões';
    const filters=document.createElement('details');filters.className='ui-practice-advanced';filters.innerHTML='<summary>Ajustar dificuldade e fonte</summary>';
    const difficulty=$('sel-niv').closest('.fg'),source=$('sel-source').closest('.fg');filters.append(difficulty,source);
    const controls=$('btn-start').parentElement;controls.insertBefore(filters,$('btn-start'));
    [['sel-niv','Dificuldade'],['sel-qty','Quantidade de questões'],['sel-source','Fonte das questões'],['rh-subject','Matéria da revisão'],['rh-topic','Assunto da revisão']].forEach(([id,label])=>$(id).setAttribute('aria-label',label));
    previous.querySelectorAll('label').forEach(label=>{const select=label.parentElement.querySelector('select');if(select)label.htmlFor=select.id;});
    function keyboardChips(){document.querySelectorAll('#ch-mode .chip,#ch-sub .chip').forEach(el=>{el.setAttribute('role','button');el.tabIndex=0;el.setAttribute('aria-pressed',String(el.classList.contains('sel')));});}
    function restoreSessionSettings(){if(state.formSession)Object.assign(S,state.formSession);}
    keyboardChips();previous.addEventListener('click',e=>{if(e.target.closest('.chip')){keyboardChips();restoreSessionSettings();}});
    previous.addEventListener('change',restoreSessionSettings);
    previous.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.classList.contains('chip')){e.preventDefault();e.target.click();}});
    const direct=[['biblio','Biblioteca','Leis e dispositivos organizados','book'],['assuntos','Radar de assuntos','Pontos fortes e prioridades','target'],['stats','Progresso','Seu desempenho e histórico','chart'],['res','Último resultado','Retomar a correção da última sessão','questions'],['settings','Configurações e backup','Preferências, exportação e importação','settings']];
    direct.forEach(([route,title,sub,glyph])=>$('ui-resources').insertAdjacentHTML('beforeend','<button class="ui-resource" type="button" data-ui-route="'+route+'">'+icon(glyph)+'<span><strong>'+title+'</strong><small>'+sub+'</small></span></button>'));
  }
  function taskData(){
    const status=dailyStatus(),date=status.adaptive.date;
    const ordered=['combat','recent','maintenance','incidence','math'].flatMap(group=>status.adaptive.groups[group]||[]);
    const tasks=ordered.map((item,index)=>{
      const done=isAdaptiveDone(item,date)||(item.kind==='dso'&&studySubjects(date).some(r=>r.subject===item.subject));
      const isLesson=!!item.dsoBlocks;
      const kind=item.subject==='Matemática'?'Teoria':'Revisão adaptativa';
      const minutes=isLesson?item.dsoBlocks.reduce((sum,b)=>sum+(b.minutes||0),0):18;
      const topic=item.topic||(item.study&&item.study.topics||[]).slice(0,2).join(' · ');
      return {id:'adaptive-'+index,title:item.subject,subtitle:(topic?topic+' · ':'')+kind,detail:adaptiveItemDesc(item),minutes,done,item,index,type:'adaptive'};
    });
    tasks.push({id:'reading',title:'Leitura de lei seca',subtitle:'Meta diária do Banco de Leis',minutes:25,done:leituraDoDiaFeita(),type:'reading'});
    if(status.p.extra==='sim')tasks.push({id:'sim',title:'Simulado CEBRASPE',subtitle:'Treino completo',minutes:0,done:!!S.daily.sim,type:'sim'});
    if(status.p.extra==='red'||status.p.pendingEssay)tasks.push({id:'essay',title:'Redação',subtitle:status.p.pendingEssay?'Discursiva pendente':'Prática de escrita',minutes:0,done:!!S.daily.red,type:'essay'});
    return {status,date,ordered,tasks};
  }
  function readableMinutes(value){return value>=60?Math.floor(value/60)+'h'+String(value%60).padStart(2,'0'):value+' min';}
  function row(task,index,next){return '<li class="ui-task'+(task.done?' done':'')+(task.id===next?' next':'')+'"><span class="ui-task-state" aria-label="'+(task.done?'Concluído':'Pendente')+'">'+(task.done?'✓':index+1)+'</span><div class="ui-task-copy"><strong>'+safe(task.title)+'</strong><small>'+safe(task.subtitle)+'</small></div><button type="button" class="ui-task-action" data-ui-task="'+task.id+'" aria-label="'+(task.done?'Reabrir':'Abrir')+' '+safe(task.title)+'">'+(task.done?'Reabrir':task.type==='adaptive'&&task.item.dsoBlocks?'Ver aula':'Abrir')+'</button></li>';}
  function canResume(){
    if(!state.resume)return false;
    if(state.resume==='adaptive-theory')return !!S._theoryContext;
    if(state.resume==='flash')return !!(S._flashQueue&&S._flashIdx<S._flashQueue.length);
    if(state.resume==='sim')return !!(S.sim&&S.sq&&S.ci<S.sq.length);
    return !!(S.sq&&S.sq.length&&S.ci<S.sq.length);
  }
  function renderToday(){
    const home=$('v-home');if(!home||!document.body.classList.contains('ui-ready'))return;
    const data=taskData();state.items=data.ordered;state.tasks=data.tasks;state.date=data.date;
    const done=data.tasks.filter(t=>t.done).length,total=data.tasks.length,pct=total?Math.round(done/total*100):0;
    const next=data.tasks.find(t=>!t.done),resume=canResume();
    const title=resume?'Continue de onde parou.':next?next.title:'Plano de hoje concluído.';
    const subtitle=resume?routes[state.resume]:next?next.subtitle:'Você pode seguir treinando ou consultar seu progresso.';
    const action=resume?'data-ui-resume':next?'data-ui-task="'+next.id+'"':'data-ui-route="stats"';
    const pendingReviews=data.tasks.filter(t=>t.type==='adaptive'&&!t.done&&t.item.kind!=='dso');
    const remaining=data.tasks.filter(t=>!t.done).reduce((sum,t)=>sum+t.minutes,0);
    const hasUntimed=data.tasks.some(t=>!t.done&&!t.minutes);
    const dateLabel=new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'numeric',month:'long'});
    const visible=data.tasks.slice(0,6),extra=data.tasks.slice(6);
    const expanded=home.querySelector('.ui-task-more')?.open||false;
    home.innerHTML=head('Seu estudo, em dia.',safe(dateLabel))+'<div class="ui-today-grid"><div><section class="ui-next"><div class="ui-eyebrow">'+(resume?'Sua sessão em andamento':'Seu próximo passo')+'</div><h2>'+safe(title)+'</h2><p>'+safe(subtitle)+'</p><div class="ui-next-meta"><span>'+icon('book')+'PMAL · CEBRASPE</span>'+(next&&next.minutes&&!resume?'<span>'+icon('clock')+'~'+readableMinutes(next.minutes)+'</span>':'')+'</div><button class="ui-primary" type="button" '+action+'>'+(resume?'Retomar sessão':next?'Continuar estudo':'Ver meu progresso')+icon('arrow')+'</button></section><div class="ui-section-heading"><h2>Roteiro de hoje</h2><span>'+done+' de '+total+' concluídos</span></div><ol class="ui-task-list">'+visible.map((t,i)=>row(t,i,next?.id)).join('')+'</ol>'+(extra.length?'<details class="ui-task-more"'+(expanded?' open':'')+'><summary>Ver mais '+extra.length+' blocos</summary><ol class="ui-task-list">'+extra.map((t,i)=>row(t,i+6,next?.id)).join('')+'</ol></details>':'')+'<div class="ui-note">'+icon('calendar')+'Plano DSO + revisões do seu histórico</div></div><aside class="ui-aside" aria-label="Resumo do dia"><section class="ui-panel ui-day-panel"><h2>Seu ritmo hoje</h2><div class="ui-day-progress"><div class="ui-day-ring" style="--ui-pct:'+pct+'%" role="img" aria-label="'+pct+'% do plano concluído"><span>'+pct+'%</span></div><div><strong>'+done+' de '+total+'</strong><span class="ui-small">blocos feitos</span></div></div><div class="ui-estimate">'+(remaining?'Restam cerca de <b>'+readableMinutes(remaining)+'</b>'+(hasUntimed?' + atividades extras':''):done===total?'Plano concluído':'Atividades extras pendentes')+'</div></section><section class="ui-panel ui-review-panel"><div class="ui-panel-title"><h2>Para revisar</h2><span class="ui-count">'+pendingReviews.length+' blocos</span></div>'+(pendingReviews.length?pendingReviews.slice(0,3).map(t=>'<div class="ui-subject-line"><span>'+safe(t.title)+'</span></div>').join(''):'<p class="ui-small">Nenhum bloco de revisão pendente hoje.</p>')+'<button type="button" class="ui-text-button" data-ui-route="reviewhub">Abrir revisões →</button></section><section class="ui-panel ui-week-panel"><div class="ui-panel-title"><h2>Sua semana</h2><button type="button" class="ui-text-button" data-ui-route="crono">Ver plano</button></div><div class="ui-week" id="ui-week"></div><div id="ui-week-detail" class="ui-week-detail" hidden></div></section></aside></div>';
    const monday=shiftDateKey(data.date,-((new Date().getDay()+6)%7));
    $('ui-week').innerHTML=['SEG','TER','QUA','QUI','SEX','SÁB','DOM'].map((label,i)=>{const key=shiftDateKey(monday,i);return '<button type="button" data-ui-day="'+key+'"'+(key===data.date?' aria-current="date"':'')+' aria-label="Plano de '+key+'"><span>'+label+'</span><b>'+Number(key.slice(8))+'</b></button>';}).join('');
  }
  function runTask(id){
    // Use the same array as the displayed task, independent of Cronograma's ordering.
    const task=state.tasks.find(t=>t.id===id);if(!task)return;
    if(state.date!==localDateKey(new Date())){renderToday();toast('O plano foi atualizado para hoje.');return;}
    if(task.type==='adaptive'){
      if(task.item.dsoBlocks){navigate('crono');$('adaptive-card').scrollIntoView({block:'start',behavior:'smooth'});return;}
      S._adaptiveDisplay={date:state.date,items:state.items};
      S._adaptiveContext=null;S._theoryContext=null;
      runAdaptiveItem(task.index);
    } else if(task.type==='reading'){navigate('crono');$('leitura-card').scrollIntoView({block:'start',behavior:'smooth'});}
    else if(task.type==='essay')navigate('redacao');
    else if(task.type==='sim')openSimuladoSelector();
  }
  function renderReviewSummary(){
    const data=taskData(),pending=data.tasks.filter(t=>t.type==='adaptive'&&!t.done&&t.item.kind!=='dso');
    $('ui-review-summary').innerHTML='<div><div class="ui-eyebrow">Revisões de hoje</div><h2>'+pending.length+' '+(pending.length===1?'bloco para revisar.':'blocos para revisar.')+'</h2><p>'+(pending.length?safe(pending.slice(0,3).map(t=>t.title).join(' · ')):'As revisões salvas e o histórico continuam disponíveis abaixo.')+'</p></div><button class="ui-primary" type="button" data-ui-route="crono">Ver plano de revisão '+icon('arrow')+'</button>';
  }
  function installStudyTools(){
    ['quiz','fb','adaptive-theory','flash'].forEach(id=>{
      const toolbar=document.createElement('div');toolbar.className='ui-quiz-tools';toolbar.innerHTML='<button type="button" class="ui-text-button" data-ui-route="'+(id==='fb'?'practice':'home')+'">← '+(id==='fb'?'Questões':'Hoje')+'</button><label class="ui-focus-label"><input type="checkbox" data-ui-focus>Modo foco</label>';
      $('v-'+id).prepend(toolbar);
    });
    const extra=document.createElement('details');extra.className='ui-feedback-extra';extra.innerHTML='<summary>Origem da questão e sinalização</summary>';
    const source=$('fb-source-panel');source.before(extra);extra.append(source);
    const sub=document.querySelector('#v-reviewhub .rh-sub');sub.textContent='Revisões de hoje, erros e sessões salvas.';
    const summary=document.createElement('section');summary.id='ui-review-summary';summary.className='ui-panel ui-review-today';document.querySelector('#v-reviewhub .rh-head').after(summary);
    // A new ordinary hub session must not inherit a previous exclusive review context.
    ['reviewHubStartCurrentErrors','reviewHubStartHistoricalErrors','reviewHubStartGroup'].forEach(name=>{
      const original=window[name];window[name]=function(){S.reviewActive=null;S._adaptiveContext=null;S._theoryContext=null;return original.apply(this,arguments);};
    });
    ['generateQuestionsAI','corrigirRedacaoAI'].forEach(name=>{
      const original=window[name];window[name]=function(){
        if(!apiKey){navigate('settings');$('apicard').style.display='block';$('inp-key').focus();toast('Insira sua chave de API para usar este recurso.');return Promise.resolve();}
        return original.apply(this,arguments);
      };
    });
    // The existing button listener resolves startQ at initialization. Clear abandoned
    // adaptive contexts in capture phase before it launches a new manual session.
    $('btn-start').addEventListener('click',()=>{
      state.formSession=null;
      S.mode=document.querySelector('#ch-mode .chip.sel')?.dataset.mode||'simulado';
      S.subs=Array.from(document.querySelectorAll('#ch-sub .chip.sel')).map(el=>el.dataset.s).filter(s=>s!=='all');
      S._adaptiveContext=null;S._theoryContext=null;S.sim=false;
      if(typeof simTimer!=='undefined'&&simTimer){clearInterval(simTimer);simTimer=null;}
    },true);
  }
  function bindActions(){
    document.addEventListener('click',event=>{
      const button=event.target.closest('[data-ui-route],[data-ui-task],[data-ui-resume],[data-ui-day]');if(!button)return;
      if(button.dataset.uiRoute)navigate(button.dataset.uiRoute);
      else if(button.dataset.uiTask)runTask(button.dataset.uiTask);
      else if(button.hasAttribute('data-ui-resume')){if(canResume())window.sv(state.resume);else renderToday();}
      else if(button.dataset.uiDay){const plan=scheduleForDate(button.dataset.uiDay);$('ui-week-detail').hidden=false;$('ui-week-detail').textContent=new Date(button.dataset.uiDay+'T12:00:00').toLocaleDateString('pt-BR',{weekday:'long',day:'numeric'})+' · '+(plan.subs||[]).join(' + ');}
    });
    document.addEventListener('change',event=>{if(event.target.matches('[data-ui-focus]')){state.focus=event.target.checked;syncNavigation(state.active);}});
    $('ui-api-toggle').addEventListener('click',()=>{const card=$('apicard');card.style.display=card.style.display==='none'?'block':'none';if(card.style.display==='block')$('inp-key').focus();});
    document.addEventListener('visibilitychange',()=>{if(!document.hidden&&state.active==='home')renderToday();});
    // The legal reader updates asynchronously; refresh completion without recreating it.
    let timer;
    new MutationObserver(()=>{clearTimeout(timer);timer=setTimeout(()=>{if(state.active==='home')renderToday();},100);}).observe($('leitura-sub'),{childList:true,subtree:true,characterData:true});
  }
  function init(){
    if(document.body.classList.contains('ui-ready'))return;
    splitHome();installNavigation();installStudyTools();bindActions();document.body.classList.add('ui-ready');
    renderToday();syncNavigation('home');
    window.PmalInterface={version:'2026.09.08',navigate,renderToday,taskData};
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
