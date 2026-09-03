from pathlib import Path

INDEX = Path('index.html')
MARK = 'PMAL_CPPM_REVIEW_NOTES_20260903_V1'

NOTES_HTML = r'''
  <!-- PMAL_CPPM_REVIEW_NOTES_20260903_V1 -->
  <div class="rh-section" id="rh-cppm-recent-notes">
    <div class="rh-section-h">
      <b>🧾 Caderno de Erros · CPPM</b>
      <span class="ts tmut">3 pegadinhas recentes</span>
    </div>
    <div class="rh-section-b">
      <div class="rh-saved">
        <div class="rh-action" id="cppm-note-pjm-delegacao" style="cursor:default">
          <strong>1. PJM — delegação</strong>
          <span><b>Regra:</b> delegação a oficial da ativa. <b>Exceção:</b> nas hipóteses legais, pode haver designação de oficial da reserva de posto mais elevado quando não houver oficial da ativa em condições de receber a delegação. <b>Pegadinha:</b> desconfie de “indelegável”.</span>
          <div style="margin-top:9px;display:flex;gap:6px;align-items:center;flex-wrap:wrap"><span class="ts tmut">CPPM · Polícia Judiciária Militar · lei seca</span><button class="rh-mini" id="cppm-btn-pjm-delegacao" onclick="toggleCppmReviewNote('pjm-delegacao')">✓ Marcar revisado</button></div>
        </div>
        <div class="rh-action" id="cppm-note-pjm-equivalencia" style="cursor:default">
          <strong>2. PJM — equivalência funcional</strong>
          <span>A Polícia Judiciária Militar exerce <b>função investigativa equivalente</b> à polícia judiciária comum, especializada na apuração de crimes militares. Mesma finalidade investigativa <b>não significa</b> mesma instituição ou mesma competência material.</span>
          <div style="margin-top:9px;display:flex;gap:6px;align-items:center;flex-wrap:wrap"><span class="ts tmut">CPPM · Polícia Judiciária Militar · conceito</span><button class="rh-mini" id="cppm-btn-pjm-equivalencia" onclick="toggleCppmReviewNote('pjm-equivalencia')">✓ Marcar revisado</button></div>
        </div>
        <div class="rh-action" id="cppm-note-desercao-estabilidade" style="cursor:default">
          <strong>3. Deserção — estabilidade da praça</strong>
          <span><b>Mais de 8 dias</b> de ausência sem licença. Praça <b>com estabilidade = agregação</b>; praça <b>sem estabilidade = exclusão</b>. No retorno: estável = <b>reversão</b>; sem estabilidade = <b>reinclusão</b>.</span>
          <div style="margin-top:9px;display:flex;gap:6px;align-items:center;flex-wrap:wrap"><span class="ts tmut">CPPM · Deserção · pegadinha CEBRASPE</span><button class="rh-mini" id="cppm-btn-desercao-estabilidade" onclick="toggleCppmReviewNote('desercao-estabilidade')">✓ Marcar revisado</button></div>
        </div>
      </div>
    </div>
  </div>
'''

RUNTIME = r'''
<script id="pmal-cppm-review-notes-runtime">/* PMAL_CPPM_REVIEW_NOTES_20260903_V1_RUNTIME */
(function(){
  var KEY='pmal26_cppm_review_notes_20260903_v1';
  function load(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')||{};}catch(e){return {};}}
  function save(x){try{localStorage.setItem(KEY,JSON.stringify(x));}catch(e){}}
  function paint(id){
    var s=load(), done=!!(s[id]&&s[id].done);
    var card=document.getElementById('cppm-note-'+id), btn=document.getElementById('cppm-btn-'+id);
    if(card){card.style.borderColor=done?'#31523d':'';card.style.background=done?'#152219':'';card.style.opacity=done?'.82':'1';}
    if(btn){btn.textContent=done?'✓ Revisado':'✓ Marcar revisado';btn.setAttribute('aria-pressed',done?'true':'false');}
  }
  window.toggleCppmReviewNote=function(id){
    var s=load(), was=!!(s[id]&&s[id].done);
    s[id]={done:!was,ts:Date.now()};save(s);paint(id);
    if(typeof toast==='function')toast(!was?'✅ Ponto marcado como revisado.':'↩️ Ponto voltou para revisão.');
  };
  function init(){['pjm-delegacao','pjm-equivalencia','desercao-estabilidade'].forEach(paint);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
</script>
'''


def main():
    txt = INDEX.read_text(encoding='utf-8')
    if MARK in txt:
        print('Notas CPPM já aplicadas.')
        return

    start = txt.find('<!-- PMAL_REVIEW_HUB_VIEW -->')
    quiz = txt.find('<!-- QUIZ -->', start)
    if start < 0 or quiz < 0:
        raise SystemExit('Central de Revisão não encontrada; abortando para não criar sistema paralelo.')

    close = txt.rfind('</div>', start, quiz)
    if close < 0:
        raise SystemExit('Fechamento da Central de Revisão não encontrado.')

    txt = txt[:close] + NOTES_HTML + '\n' + txt[close:]

    body = txt.rfind('</body>')
    if body < 0:
        raise SystemExit('Fechamento </body> não encontrado.')
    txt = txt[:body] + RUNTIME + '\n' + txt[body:]

    INDEX.write_text(txt, encoding='utf-8')
    print('OK: 3 erros recentes de CPPM adicionados à Central de Revisão.')


if __name__ == '__main__':
    main()
