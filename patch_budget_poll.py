with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    html = f.read()

# Adiciona pollBudget() e inicia o polling na startLiveMode()
old_start_live = (
    "function startLiveMode() {\n"
    "  var ind = document.getElementById('liveIndicator');\n"
    "  if (ind) ind.style.display = 'flex';\n"
    "  var upd = document.getElementById('liveUpdatedAt');\n"
    "  if (upd) upd.style.display = 'block';\n"
    "  loadLiveData();\n"
    "  if (_pollTimer) clearInterval(_pollTimer);\n"
    "  _pollTimer = setInterval(pollStatus, POLL_INTERVAL);\n"
    "}"
)

new_start_live = (
    "function pollBudget() {\n"
    "  fetch('/api/budget')\n"
    "    .then(function(r){ return r.json(); })\n"
    "    .then(function(json){\n"
    "      if (json.ok && json.total_daily_budget !== undefined) {\n"
    "        TOTAL_DAILY_BUDGET = json.total_daily_budget;\n"
    "        renderKPIs();\n"
    "      }\n"
    "    })\n"
    "    .catch(function(){});\n"
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
    "  // Polling de verba a cada 60s — reflete ajustes sem esperar refresh completo\n"
    "  setInterval(pollBudget, 60000);\n"
    "}"
)

if old_start_live in html:
    html = html.replace(old_start_live, new_start_live, 1)
    print("OK: pollBudget() added and started in startLiveMode()")
else:
    print("FAIL: startLiveMode not found")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done.")
