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

origens = {}

for status in [1, 2, 3]:
    label = {1: 'abertos', 2: 'vendidos', 3: 'perdidos'}[status]
    url = f'{BASE}/qualificacoes/?api_token={TOKEN}&status={status}&displayLength=200'
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    data = json.loads(urllib.request.urlopen(req).read())
    items = data if isinstance(data, list) else data.get('data', [])

    for item in items:
        # Verifica camposListagem para campo Origem
        for campo in (item.get('camposListagem') or []):
            if campo and campo.get('label', '').lower() == 'origem':
                origem = campo.get('value', '') or 'vazio'
                origens[origem] = origens.get(origem, 0) + 1

        # Verifica camposPersonalizados
        cp = item.get('camposPersonalizados') or {}
        for k, v in cp.items():
            if 'origem' in k.lower() or 'source' in k.lower() or 'ads' in str(v).lower():
                print(f"  [{label}] Campo: {k} = {v}")

print("=== ORIGENS ENCONTRADAS EM camposListagem ===")
for o, cnt in sorted(origens.items(), key=lambda x: -x[1]):
    print(f"  {cnt:>4}x  {o}")
