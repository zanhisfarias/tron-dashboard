import re

with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ── 1. const → var inside DATA block ──────────────────────────────────────────
data_start = content.find('// DATA:START')
data_end   = content.find('// DATA:END')
assert data_start > 0 and data_end > 0, "DATA markers not found"

data_block    = content[data_start:data_end]
data_block_new = re.sub(r'\bconst\b', 'var', data_block)
content = content[:data_start] + data_block_new + content[data_end:]

# ── 2. IS_LIVE + POLL_INTERVAL after DATA:END ──────────────────────────────────
live_vars = (
    "\n"
    "// ---------------------------------------------------------\n"
    "// Modo ao vivo -- detecta se esta rodando no servidor Flask\n"
    "// ---------------------------------------------------------\n"
    "var IS_LIVE = (window.location.protocol !== 'file:');\n"
    "var POLL_INTERVAL = 15000;\n"
    "var _pollTimer = null;\n"
)
insert_after = '// DATA:END'
content = content.replace(insert_after, insert_after + '\n' + live_vars, 1)

# ── 3. Header: replace Atualizar button wrapper with live-mode version ─────────
old_btn_wrapper = (
    '    <div class="flex items-center gap-2 flex-shrink-0 ml-auto md:ml-0">\n'
    '      <div class="hidden md:block text-xs text-muted font-medium" id="headerDate"></div>\n'
    '      <button onclick="renderAll()" title="Atualizar dados" class="flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg transition-all" style="background:#1E2130;color:#9CA3AF;border:1px solid #2A2D3E" onmouseover="this.style.color=\'#fff\';this.style.borderColor=\'#6366F1\'" onmouseout="this.style.color=\'#9CA3AF\';this.style.borderColor=\'#2A2D3E\'">\n'
    '        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>\n'
    '        <span class="hidden md:inline">Atualizar</span>\n'
    '      </button>\n'
    '    </div>'
)

new_btn_wrapper = (
    '    <div class="flex items-center gap-2 flex-shrink-0 ml-auto md:ml-0">\n'
    '      <div class="hidden md:block text-xs text-muted font-medium" id="headerDate"></div>\n'
    '      <!-- Indicador ao vivo -->\n'
    '      <div id="liveIndicator" class="hidden items-center gap-1.5 text-[10px] font-semibold" style="color:#10B981">\n'
    '        <span class="live-dot" style="width:7px;height:7px;border-radius:50%;background:#10B981;display:inline-block;flex-shrink:0"></span>\n'
    '        <span class="hidden md:inline">AO VIVO</span>\n'
    '        <span id="liveCountdown" class="hidden md:inline text-muted font-normal"></span>\n'
    '      </div>\n'
    '      <div id="liveUpdatedAt" class="hidden text-[10px] text-muted font-normal"></div>\n'
    '      <button id="refreshBtn" onclick="triggerRefresh()" title="Atualizar dados" class="flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg transition-all" style="background:#1E2130;color:#9CA3AF;border:1px solid #2A2D3E" onmouseover="this.style.color=\'#fff\';this.style.borderColor=\'#6366F1\'" onmouseout="this.style.color=\'#9CA3AF\';this.style.borderColor=\'#2A2D3E\'">\n'
    '        <svg id="refreshIcon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>\n'
    '        <span class="hidden md:inline">Atualizar</span>\n'
    '      </button>\n'
    '    </div>'
)

if old_btn_wrapper in content:
    content = content.replace(old_btn_wrapper, new_btn_wrapper, 1)
    print("OK: button wrapper replaced")
else:
    print("WARN: button wrapper not found — skipping")

# ── 4. CSS: add keyframes before first @media ─────────────────────────────────
old_css_end = '    @media (min-width: 768px) {'
new_css_insert = (
    '    @keyframes pulse-dot {\n'
    '      0%, 100% { opacity: 1; transform: scale(1); }\n'
    '      50%       { opacity: 0.4; transform: scale(0.7); }\n'
    '    }\n'
    '    .live-dot { animation: pulse-dot 1.6s ease-in-out infinite; }\n'
    '    @keyframes spin-refresh { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }\n'
    '    .spin { animation: spin-refresh 0.8s linear infinite; }\n'
    '    @media (min-width: 768px) {'
)
if old_css_end in content:
    content = content.replace(old_css_end, new_css_insert, 1)
    print("OK: CSS keyframes added")
else:
    print("WARN: CSS @media not found")

# ── 5. JS live mode functions — insert before DOMContentLoaded ──────────────
live_js = (
    "\n"
    "// ---------------------------------------------------------\n"
    "// MODO AO VIVO\n"
    "// ---------------------------------------------------------\n"
    "\n"
    "function updateLiveUI(status) {\n"
    "  var ind = document.getElementById('liveIndicator');\n"
    "  var upd = document.getElementById('liveUpdatedAt');\n"
    "  var cd  = document.getElementById('liveCountdown');\n"
    "  if (!ind) return;\n"
    "  var dot = ind.querySelector('.live-dot');\n"
    "  var icon = document.getElementById('refreshIcon');\n"
    "  if (status.loading) {\n"
    "    ind.style.color = '#F59E0B';\n"
    "    if (dot) dot.style.background = '#F59E0B';\n"
    "    if (icon) icon.classList.add('spin');\n"
    "  } else {\n"
    "    ind.style.color = '#10B981';\n"
    "    if (dot) dot.style.background = '#10B981';\n"
    "    if (icon) icon.classList.remove('spin');\n"
    "  }\n"
    "  if (status.updated_at && upd) {\n"
    "    upd.textContent = 'Ult. atualizacao: ' + status.updated_at;\n"
    "  }\n"
    "  if (status.next_in_secs !== undefined && cd) {\n"
    "    var s = status.next_in_secs;\n"
    "    if (s > 0) {\n"
    "      var m = Math.floor(s / 60), r = s % 60;\n"
    "      cd.textContent = '(prox. em ' + (m > 0 ? m + 'min ' : '') + r + 's)';\n"
    "    } else {\n"
    "      cd.textContent = '';\n"
    "    }\n"
    "  }\n"
    "}\n"
    "\n"
    "function applyLiveData(json) {\n"
    "  var d = json.data;\n"
    "  if (!d) return;\n"
    "  if (d.campaigns)        CAMPAIGNS        = d.campaigns;\n"
    "  if (d.all_dates)        ALL_DATES        = d.all_dates;\n"
    "  if (d.all_data)         ALL_DATA         = d.all_data;\n"
    "  if (d.adsets_raw)       ADSETS_RAW       = d.adsets_raw;\n"
    "  if (d.adset_metrics)    ADSET_METRICS    = d.adset_metrics;\n"
    "  if (d.creatives)        CREATIVES        = d.creatives;\n"
    "  if (d.nectar_leadboard) NECTAR_LEADBOARD = d.nectar_leadboard;\n"
    "  renderAll();\n"
    "}\n"
    "\n"
    "function loadLiveData() {\n"
    "  fetch('/api/data')\n"
    "    .then(function(r){ return r.json(); })\n"
    "    .then(function(json){\n"
    "      updateLiveUI(json);\n"
    "      if (json.data && !json.loading) { applyLiveData(json); }\n"
    "    })\n"
    "    .catch(function(e){ console.warn('Erro ao buscar dados ao vivo:', e); });\n"
    "}\n"
    "\n"
    "function pollStatus() {\n"
    "  fetch('/api/status')\n"
    "    .then(function(r){ return r.json(); })\n"
    "    .then(function(status){\n"
    "      updateLiveUI(status);\n"
    "      if (!status.loading && status.updated_at) { loadLiveData(); }\n"
    "    })\n"
    "    .catch(function(e){ console.warn('Erro no poll de status:', e); });\n"
    "}\n"
    "\n"
    "function triggerRefresh() {\n"
    "  if (!IS_LIVE) { renderAll(); return; }\n"
    "  var icon = document.getElementById('refreshIcon');\n"
    "  if (icon) icon.classList.add('spin');\n"
    "  fetch('/api/refresh', { method: 'POST' })\n"
    "    .then(function(){ setTimeout(loadLiveData, 2000); })\n"
    "    .catch(function(e){ console.warn('Erro ao disparar refresh:', e); if(icon) icon.classList.remove('spin'); });\n"
    "}\n"
    "\n"
    "function startLiveMode() {\n"
    "  var ind = document.getElementById('liveIndicator');\n"
    "  if (ind) ind.style.display = 'flex';\n"
    "  var upd = document.getElementById('liveUpdatedAt');\n"
    "  if (upd) upd.style.display = 'block';\n"
    "  loadLiveData();\n"
    "  if (_pollTimer) clearInterval(_pollTimer);\n"
    "  _pollTimer = setInterval(pollStatus, POLL_INTERVAL);\n"
    "}\n"
    "\n"
)

dom_marker = "document.addEventListener('DOMContentLoaded', function() {"
if dom_marker in content:
    content = content.replace(dom_marker, live_js + dom_marker, 1)
    print("OK: live JS functions inserted")
else:
    print("WARN: DOMContentLoaded not found")

# ── 6. DOMContentLoaded: branch on IS_LIVE ──────────────────────────────────
old_dom_tail = (
    "  buildPeriodBar();\n"
    "  renderAll();\n"
    "});"
)
new_dom_tail = (
    "  buildPeriodBar();\n"
    "  if (IS_LIVE) {\n"
    "    startLiveMode();\n"
    "  } else {\n"
    "    renderAll();\n"
    "  }\n"
    "});"
)
if old_dom_tail in content:
    content = content.replace(old_dom_tail, new_dom_tail, 1)
    print("OK: DOMContentLoaded updated with IS_LIVE branch")
else:
    print("WARN: DOMContentLoaded tail not found")

# ── Validate & write ──────────────────────────────────────────────────────────
checks = ['IS_LIVE', 'startLiveMode', 'triggerRefresh', 'loadLiveData',
          'live-dot', 'liveIndicator', 'liveUpdatedAt', 'liveCountdown',
          'applyLiveData', 'pollStatus', 'pulse-dot', 'spin-refresh']
for c in checks:
    if c not in content:
        print(f"MISSING: {c}")
    else:
        print(f"CHECK OK: {c}")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone — {original_len} -> {len(content)} bytes")
