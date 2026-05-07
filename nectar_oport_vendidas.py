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

# Oportunidades vendidas (status=2) de QUALQUER funil, com valores
url = f'{BASE}/oportunidades/?api_token={TOKEN}&status=2&limit=50'
req = urllib.request.Request(url, headers={'Accept': 'application/json'})
data = json.loads(urllib.request.urlopen(req).read())
items = data if isinstance(data, list) else data.get('results', data.get('data', []))

print(f"Total vendidas: {len(items)}")
print()

total_avulso  = 0
total_mensal  = 0
por_funil = {}

for item in items:
    funil = item.get('pipeline', 'N/A')
    va = float(item.get('valorAvulso', 0) or 0)
    vm = float(item.get('valorMensal', 0) or 0)
    total_avulso += va
    total_mensal += vm

    if funil not in por_funil:
        por_funil[funil] = {'count': 0, 'avulso': 0, 'mensal': 0}
    por_funil[funil]['count']  += 1
    por_funil[funil]['avulso'] += va
    por_funil[funil]['mensal'] += vm

    if va > 0 or vm > 0:
        nome = item.get('nome', item.get('cliente', {}).get('nome', '?'))
        dc = item.get('dataConclusao') or item.get('dataAtualizacao', '')[:10]
        print(f"  [{funil}] {nome[:40]:<40} avulso=R${va:.0f}  mensal=R${vm:.0f}  data={dc[:10]}")

print()
print("=== POR FUNIL ===")
for funil, v in por_funil.items():
    print(f"  {funil}: {v['count']} vendas | avulso=R${v['avulso']:,.0f} | mensal=R${v['mensal']:,.0f}/mes")

print()
print(f"TOTAL avulso:  R${total_avulso:,.2f}")
print(f"TOTAL mensal:  R${total_mensal:,.2f}/mes (MRR)")
