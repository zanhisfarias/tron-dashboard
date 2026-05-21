import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', encoding='utf-8') as f:
    ud = f.read()

# Corrige a chamada em main() — tem uma linha só sem quebra
old = 'js_block = build_js_block(all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar)'
new = (
    'total_budget = fetch_total_daily_budget()\n'
    '    js_block = build_js_block(all_dates, all_data, adsets, adset_metrics, budgets, creatives, nectar,\n'
    '                               total_budget=total_budget)'
)

if old in ud:
    ud = ud.replace(old, new, 1)
    print("OK: main() updated")
else:
    print("FAIL")

with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(ud)

# Também adiciona no data dict do server.py
with open(r'C:\Users\Marketing\Desktop\server.py', encoding='utf-8') as f:
    srv = f.read()

# O server.py usa _merge_campaigns e build_js_block separadamente
# Verifica se total_budget já está sendo passado
print("server.py TOTAL_DAILY_BUDGET:", 'total_budget' in srv)
print("server.py fetch_total_daily_budget:", 'fetch_total_daily_budget' in srv)

# Adiciona total_budget ao payload do /api/data
old_data_payload = '''        data = {
            "campaigns":        _merge_campaigns(budgets),
            "all_dates":        all_dates,
            "all_data":         all_data,
            "adsets_raw":       adsets,
            "adset_metrics":    adset_metrics,
            "creatives":        creatives,
            "nectar_leadboard": nectar,
        }'''
new_data_payload = '''        total_budget = ud.fetch_total_daily_budget()
        data = {
            "campaigns":          _merge_campaigns(budgets),
            "all_dates":          all_dates,
            "all_data":           all_data,
            "adsets_raw":         adsets,
            "adset_metrics":      adset_metrics,
            "creatives":          creatives,
            "nectar_leadboard":   nectar,
            "total_daily_budget": total_budget,
        }'''

if old_data_payload in srv:
    srv = srv.replace(old_data_payload, new_data_payload, 1)
    print("OK: server.py data payload includes total_daily_budget")
else:
    print("FAIL: data payload not found in server.py")

with open(r'C:\Users\Marketing\Desktop\server.py', 'w', encoding='utf-8') as f:
    f.write(srv)

print("Done.")
