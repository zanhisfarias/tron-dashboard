import sys, json, urllib.request, urllib.parse
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

# Busca vendidas (status=2) para inspecionar campos de valor
url = f'{BASE}/qualificacoes/?api_token={TOKEN}&status=2&limit=5'
req = urllib.request.Request(url, headers={'Accept': 'application/json'})
data = json.loads(urllib.request.urlopen(req).read())

items = data if isinstance(data, list) else data.get('results', data.get('data', []))

if not items:
    print("Nenhuma venda encontrada ainda.")
    # Tenta buscar qualquer registro para ver a estrutura
    url2 = f'{BASE}/qualificacoes/?api_token={TOKEN}&status=1&limit=2'
    req2 = urllib.request.Request(url2, headers={'Accept': 'application/json'})
    data2 = json.loads(urllib.request.urlopen(req2).read())
    items2 = data2 if isinstance(data2, list) else data2.get('results', data2.get('data', []))
    if items2:
        print("\nCampos disponiveis (via status=1):")
        for k, v in items2[0].items():
            print(f"  {k}: {repr(v)[:80]}")
else:
    print(f"Vendas encontradas: {len(items)}\n")
    for item in items[:3]:
        print("--- VENDA ---")
        for k, v in item.items():
            if v is not None and v != '' and v != 0:
                print(f"  {k}: {repr(v)[:80]}")
        print()
