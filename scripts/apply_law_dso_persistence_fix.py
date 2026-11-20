#!/usr/bin/env python3
from pathlib import Path

P = Path("index.html")
src = P.read_text(encoding="utf-8")
MARKER = "PMAL_LAW_DSO_PERSISTENCE_V1"

if MARKER in src:
    print("Persistência lateral do Banco de Leis já instalada.")
    raise SystemExit(0)

required = [
    "window.completeDsoLawDay=function",
    "lawDsoReadingV3",
    "function pmalDsoEnsure",
]
missing = [token for token in required if token not in src]
if missing:
    raise SystemExit("ABORTADO: estrutura atual do Banco de Leis não confere: " + ", ".join(missing))

snippet = r"""
<!-- PMAL_LAW_DSO_PERSISTENCE_V1 -->
<script>
(function () {
  'use strict';
  var KEY = 'pmal26_law_dso_persistence_v1';
  var installed = false;

  function currentState() {
    try { return typeof S !== 'undefined' && S && typeof S === 'object' ? S : null; }
    catch (e) { return null; }
  }

  function persistLawState() {
    var state = currentState();
    if (!state) return;
    var payload = {
      version: 1,
      savedAt: Date.now(),
      lawDso: state.lawDso || null,
      lawDsoReadingV3: state.lawDsoReadingV3 || null,
      leituraDia: state.leituraDia || null
    };
    try { localStorage.setItem(KEY, JSON.stringify(payload)); }
    catch (e) { console.warn('Não foi possível salvar o progresso do Banco de Leis:', e); }
  }

  function restoreLawState() {
    var state = currentState();
    if (!state) return false;
    try {
      var saved = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (!saved || saved.version !== 1) return false;
      if (saved.lawDso && typeof saved.lawDso === 'object') state.lawDso = saved.lawDso;
      if (saved.lawDsoReadingV3 && typeof saved.lawDsoReadingV3 === 'object') state.lawDsoReadingV3 = saved.lawDsoReadingV3;
      if (saved.leituraDia && typeof saved.leituraDia === 'object') state.leituraDia = saved.leituraDia;
      return true;
    } catch (e) {
      console.warn('Não foi possível recuperar o progresso do Banco de Leis:', e);
      return false;
    }
  }

  if (installed) return;
  installed = true;

  // O estado principal já foi inicializado neste ponto; restaura antes do render
  // agendado da Meta de Leitura e mantém um espelho independente do salvamento geral.
  restoreLawState();

  if (typeof SS === 'function' && !SS.__lawDsoPersistenceWrapped) {
    var originalSS = SS;
    var wrappedSS = function () {
      var result = originalSS.apply(this, arguments);
      persistLawState();
      return result;
    };
    wrappedSS.__lawDsoPersistenceWrapped = true;
    SS = wrappedSS;
  }

  window.addEventListener('pagehide', persistLawState);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') persistLawState();
  });

  // Atualiza o espelho após restaurar, sem modificar o histórico recuperado.
  persistLawState();
})();
</script>
<!-- /PMAL_LAW_DSO_PERSISTENCE_V1 -->
"""

pos = src.lower().rfind("</body>")
if pos < 0:
    raise SystemExit("ABORTADO: </body> não encontrado; nenhum arquivo foi alterado.")

patched = src[:pos] + snippet + "\n" + src[pos:]
if patched.count(MARKER) != 2 or "SS.__lawDsoPersistenceWrapped" not in patched:
    raise SystemExit("ABORTADO: verificação estática da persistência falhou.")

P.write_text(patched, encoding="utf-8")
print("Espelho persistente do ciclo e dos cartões de leitura do Banco de Leis instalado.")
