import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ══════════════════════════════════════════════════════════════════
# 1. update_dashboard.py
# ══════════════════════════════════════════════════════════════════
with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', encoding='utf-8') as f:
    ud = f.read()

# 1a. const → var em campaigns_js dentro de build_js_block
ud = ud.replace(
    '"const CAMPAIGNS = {\\n"',
    '"var CAMPAIGNS = {\\n"',
    1
)
print("OK: campaigns_js usa var")

# 1b. Adiciona TOTAL_DAILY_BUDGET ao bloco JS gerado
old_block_template = '''    block = f"""// ─────────────────────────────────────────────────────────
// 1. DADOS — atualizado automaticamente pelo update_dashboard.py
// DATA:START
// Última atualização: {updated_at}
// ─────────────────────────────────────────────────────────

{campaigns_js}

{dates_js}
{all_data_js}

{adsets_js}

{metrics_js}

{creatives_js}

{nectar_js}

// DATA:END"""'''

new_block_template = '''    total_budget_js = f"var TOTAL_DAILY_BUDGET = {total_budget};"

    block = f"""// ─────────────────────────────────────────────────────────
// 1. DADOS — atualizado automaticamente pelo update_dashboard.py
// DATA:START
// Última atualização: {updated_at}
// ─────────────────────────────────────────────────────────

{campaigns_js}

{dates_js}
{all_data_js}

{adsets_js}

{metrics_js}

{creatives_js}

{nectar_js}

{total_budget_js}

// DATA:END"""'''

if old_block_template in ud:
    ud = ud.replace(old_block_template, new_block_template, 1)
    print("OK: TOTAL_DAILY_BUDGET added to JS block")
else:
    print("FAIL: block template not found")

# 1c. Adiciona fetch_total_daily_budget() na função main()
old_main_build = 'js_block = build_js_block(\n            all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar\n        )'
new_main_build = (
    'total_budget = fetch_total_daily_budget()\n'
    '        js_block = build_js_block(\n'
    '            all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar,\n'
    '            total_budget=total_budget\n'
    '        )'
)
if old_main_build in ud:
    ud = ud.replace(old_main_build, new_main_build, 1)
    print("OK: main() calls fetch_total_daily_budget")
else:
    print("WARN: main() build call not found — checking pattern...")
    idx = ud.find('js_block = build_js_block(')
    print(f"  found at: {idx}")
    print(repr(ud[idx:idx+200]))

with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(ud)
print("update_dashboard.py saved.\n")

# ══════════════════════════════════════════════════════════════════
# 2. server.py — adiciona fetch_total_daily_budget em do_refresh()
# ══════════════════════════════════════════════════════════════════
with open(r'C:\Users\Marketing\Desktop\server.py', encoding='utf-8') as f:
    srv = f.read()

old_srv_build = '''        js_block = ud.build_js_block(
            all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar
        )'''
new_srv_build = '''        total_budget = ud.fetch_total_daily_budget()
        js_block = ud.build_js_block(
            all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar,
            total_budget=total_budget
        )'''

if old_srv_build in srv:
    srv = srv.replace(old_srv_build, new_srv_build, 1)
    print("OK: server.py calls fetch_total_daily_budget")
else:
    print("WARN: server.py build call not found")
    idx = srv.find('ud.build_js_block(')
    print(repr(srv[idx:idx+200]))

with open(r'C:\Users\Marketing\Desktop\server.py', 'w', encoding='utf-8') as f:
    f.write(srv)
print("server.py saved.\n")

# ══════════════════════════════════════════════════════════════════
# 3. dashboard.html — usa TOTAL_DAILY_BUDGET no KPI Verba Diária
# ══════════════════════════════════════════════════════════════════
with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    html = f.read()

# 3a. Adiciona placeholder TOTAL_DAILY_BUDGET no DATA block
old_data_end = '\n// DATA:END'
new_data_end = '\nvar TOTAL_DAILY_BUDGET = 0;\n\n// DATA:END'

# Só adiciona se ainda não existir
if 'TOTAL_DAILY_BUDGET' not in html:
    html = html.replace(old_data_end, new_data_end, 1)
    print("OK: TOTAL_DAILY_BUDGET placeholder added to DATA block")
else:
    print("OK: TOTAL_DAILY_BUDGET already in DATA block")

# 3b. Corrige dailyBudget em renderKPIs para usar TOTAL_DAILY_BUDGET quando camp='all'
old_daily = "  var dailyBudget  = camps.reduce(function(s, c) { return s + CAMPAIGNS[c].budget; }, 0);"
new_daily  = (
    "  // Verba diária: total da conta (todos adsets) quando 'all', ou soma da campanha filtrada\n"
    "  var dailyBudget = state.camp === 'all'\n"
    "    ? (TOTAL_DAILY_BUDGET || camps.reduce(function(s, c) { return s + (CAMPAIGNS[c] ? CAMPAIGNS[c].budget : 0); }, 0))\n"
    "    : camps.reduce(function(s, c) { return s + (CAMPAIGNS[c] ? CAMPAIGNS[c].budget : 0); }, 0);"
)

if old_daily in html:
    html = html.replace(old_daily, new_daily, 1)
    print("OK: dailyBudget uses TOTAL_DAILY_BUDGET")
else:
    print("FAIL: dailyBudget line not found")
    idx = html.find('dailyBudget')
    print(repr(html[idx:idx+150]))

# 3c. Mesmo fix em renderBudgetPacing se usar dailyBudget por campanha
# (Budget pacing usa CAMPAIGNS[code].budget diretamente, não precisa mudar)

# ── Checks ─────────────────────────────────────────────────────────────────
for c in ['TOTAL_DAILY_BUDGET', 'fetch_total_daily_budget', 'var CAMPAIGNS']:
    in_html = c in html
    in_ud   = c in ud
    in_srv  = c in srv
    print(f"CHECK {c}: html={in_html} ud={in_ud} srv={in_srv}")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\nDone.")
