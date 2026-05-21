import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

env = {}
with open(r'C:\Users\Marketing\.claude\meta_ads_config.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

TOKEN = env['NECTAR_API_TOKEN']
BASE  = 'https://app.nectarcrm.com.br/crm/api/1'

from datetime import date
today   = date.today()
mes_ini = today.strftime('%Y-%m-01')
mes_fim = today.isoformat()

print(f'Periodo: {mes_ini} a {mes_fim}')
print()

# ── Status 1: abertas (pipeline atual) ───────────────────────────────────────
print('=== PIPELINE ATUAL (status=1 - abertas) ===')
url = f'{BASE}/qualificacoes/?api_token={TOKEN}&status=1&displayLength=200'
req = urllib.request.Request(url, headers={'Accept': 'application/json'})
data = json.loads(urllib.request.urlopen(req).read())
items = data if isinstance(data, list) else data.get('data', [])

etapas = {}
for o in items:
    ea  = o.get('etapaAtual') or {}
    seq = ea.get('sequencia', 0)
    nom = ea.get('nome', f'seq{seq}')
    etapas[nom] = etapas.get(nom, 0) + 1

for e, n in sorted(etapas.items(), key=lambda x: x[0]):
    print(f'  {e}: {n}')
print(f'  TOTAL abertas: {len(items)}')

# ── Status 2: vendidas ────────────────────────────────────────────────────────
print()
print('=== VENDIDAS (status=2) ===')
url2 = f'{BASE}/qualificacoes/?api_token={TOKEN}&status=2&displayLength=200'
req2 = urllib.request.Request(url2, headers={'Accept': 'application/json'})
data2 = json.loads(urllib.request.urlopen(req2).read())
items2 = data2 if isinstance(data2, list) else data2.get('data', [])

vendidas_mes = 0
por_mes = {}
for o in items2:
    dc = (o.get('dataConclusao') or o.get('dataAtualizacao') or '')[:10]
    mes = dc[:7]
    por_mes[mes] = por_mes.get(mes, 0) + 1
    if mes_ini[:7] == mes:
        vendidas_mes += 1
        print(f'  Vendida em {dc}: {(o.get("etapaAtual") or {}).get("nome","?")} | cliente: {o.get("cliente",{}).get("nome","?")}')

print(f'\n  Total vendidas este mes ({mes_ini[:7]}): {vendidas_mes}')
print(f'\n  Historico por mes:')
for m, n in sorted(por_mes.items()):
    print(f'    {m}: {n} vendas')

# ── Status 3: perdidas ────────────────────────────────────────────────────────
print()
print('=== PERDIDAS (status=3) ===')
url3 = f'{BASE}/qualificacoes/?api_token={TOKEN}&status=3&displayLength=200'
req3 = urllib.request.Request(url3, headers={'Accept': 'application/json'})
data3 = json.loads(urllib.request.urlopen(req3).read())
items3 = data3 if isinstance(data3, list) else data3.get('data', [])

perdidas_mes = 0
for o in items3:
    dc = (o.get('dataConclusao') or o.get('dataAtualizacao') or '')[:10]
    if dc[:7] == mes_ini[:7]:
        perdidas_mes += 1
print(f'  Perdidas este mes: {perdidas_mes}')
print(f'  Total perdidas: {len(items3)}')

# ── O que está no dashboard ───────────────────────────────────────────────────
print()
print('=== O QUE ESTA SENDO INJETADO NO DASHBOARD ===')
import re
with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    html = f.read()
m = re.search(r'var NECTAR_LEADBOARD = ({.*?});', html)
if m:
    nectar = json.loads(m.group(1))
    print(json.dumps(nectar, indent=2, ensure_ascii=False))
else:
    print('  NECTAR_LEADBOARD nao encontrado no HTML')
