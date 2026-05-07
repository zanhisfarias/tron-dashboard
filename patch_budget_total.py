import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── 1. update_dashboard.py: fetch_adsets busca também nível de conta ──────────
with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', encoding='utf-8') as f:
    ud = f.read()

# Adiciona função fetch_total_budget logo após calc_budgets
old_after_calc = '''def calc_budgets(adsets):
    budgets = {code: 0 for code in CAMPAIGN_IDS}
    for a in adsets:
        if a["status"] == "active":
            budgets[a["camp"]] += a["budget"]
    return budgets'''

new_after_calc = '''def calc_budgets(adsets):
    budgets = {code: 0 for code in CAMPAIGN_IDS}
    for a in adsets:
        if a["status"] == "active":
            budgets[a["camp"]] += a["budget"]
    return budgets


def fetch_total_daily_budget():
    """Soma o daily_budget de TODOS os adsets ativos da conta (nível de conta)."""
    try:
        resp = api_get(f"{AD_ACCOUNT}/adsets", {
            "fields": "daily_budget,status",
            "limit": "200",
        })
        total = 0
        for a in resp.get("data", []):
            if a.get("status") == "ACTIVE":
                total += int(a.get("daily_budget", 0)) // 100
        print(f"  → Verba diária total (conta): R${total}/dia")
        return total
    except Exception as e:
        print(f"  AVISO: erro ao buscar budget total: {e}")
        return 0'''

if old_after_calc in ud:
    ud = ud.replace(old_after_calc, new_after_calc, 1)
    print("OK: fetch_total_daily_budget() added to update_dashboard.py")
else:
    print("FAIL: calc_budgets not found")

# Adiciona chamada de fetch_total_daily_budget em build_js_block e main()
# Primeiro: adiciona total_budget ao parâmetro de build_js_block
old_build_sig = 'def build_js_block(all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar=None):'
new_build_sig = 'def build_js_block(all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar=None, total_budget=0):'

if old_build_sig in ud:
    ud = ud.replace(old_build_sig, new_build_sig, 1)
    print("OK: build_js_block signature updated")
else:
    print("WARN: build_js_block signature not found")

# Adiciona TOTAL_DAILY_BUDGET no bloco JS gerado
old_nectar_js = '    nectar_js = f"""var NECTAR_LEADBOARD'
if old_nectar_js in ud:
    insert_before = '    nectar_js = f"""var NECTAR_LEADBOARD'
    budget_js = (
        '    budget_total_js = f"var TOTAL_DAILY_BUDGET = {total_budget};\\n"\n'
        '    '
    )
    ud = ud.replace(insert_before, budget_js + insert_before, 1)
    print("OK: TOTAL_DAILY_BUDGET var added to JS block")
else:
    # Tenta outra abordagem: busca onde nectar_js é concatenado ao bloco
    print("WARN: nectar_js insertion point not found, trying alternate...")
    idx = ud.find('nectar_js')
    print(f"  nectar_js found at: {idx}")
    print(repr(ud[idx:idx+200]))

# Adiciona budget_total_js ao bloco retornado
old_return_block = '    return "\\n".join(['
if old_return_block in ud:
    # Encontra o return e adiciona budget_total_js
    idx = ud.find(old_return_block)
    snippet = ud[idx:idx+400]
    print("Return block:")
    print(repr(snippet[:300]))
else:
    print("WARN: return block not found")

with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(ud)

print("\nDone step 1.")
