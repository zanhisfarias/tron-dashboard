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

# Busca vendidas e imprime TUDO (incluindo camposPersonalizados e camposListagem)
url = f'{BASE}/qualificacoes/?api_token={TOKEN}&status=2&limit=3'
req = urllib.request.Request(url, headers={'Accept': 'application/json'})
data = json.loads(urllib.request.urlopen(req).read())
items = data if isinstance(data, list) else data.get('results', data.get('data', []))

for item in items[:2]:
    print(f"=== ID {item['id']} ===")
    # Campos personalizados
    cp = item.get('camposPersonalizados', {})
    print(f"camposPersonalizados: {json.dumps(cp, ensure_ascii=False)}")
    # Campos listagem completo
    cl = item.get('camposListagem', [])
    print(f"camposListagem:")
    for c in cl:
        print(f"  {c}")
    # Todos os campos com 'valor' ou 'mrr' ou 'receita' no nome
    print("Campos com valor/mrr/receita:")
    for k, v in item.items():
        if any(x in k.lower() for x in ['valor', 'mrr', 'receita', 'preco', 'price', 'amount']):
            print(f"  {k}: {v}")
    print()

# Tenta endpoint de oportunidades para ver se tem valor lá
print("\n=== Verificando /oportunidades/ para campos de valor ===")
url2 = f'{BASE}/oportunidades/?api_token={TOKEN}&limit=2'
req2 = urllib.request.Request(url2, headers={'Accept': 'application/json'})
try:
    data2 = json.loads(urllib.request.urlopen(req2).read())
    items2 = data2 if isinstance(data2, list) else data2.get('results', data2.get('data', []))
    if items2:
        for k, v in items2[0].items():
            if any(x in k.lower() for x in ['valor', 'mrr', 'receita', 'preco', 'amount']):
                print(f"  {k}: {v}")
        print("\nTodos os campos de oportunidades:")
        for k in items2[0].keys():
            print(f"  {k}: {repr(items2[0][k])[:60]}")
except Exception as e:
    print(f"Erro: {e}")
