import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

env = {}
with open(r'C:\Users\Marketing\.claude\meta_ads_config.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

TOKEN   = env['META_ACCESS_TOKEN']
VERSION = env['META_API_VERSION']
ACCOUNT = env['META_AD_ACCOUNT_TRON']

# Adsets ativos
url = f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/adsets?fields=id,name,status,daily_budget&limit=100&access_token={TOKEN}'
data = json.loads(urllib.request.urlopen(url).read())
active = [a for a in data['data'] if a.get('status') == 'ACTIVE']

# Insights do mês atual
from datetime import date
today = date.today()
since = f'{today.year}-{today.month:02d}-01'
until = today.isoformat()

url2 = (
    f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/insights'
    f'?fields=spend,actions'
    f'&time_range=%7B%22since%22%3A%22{since}%22%2C%22until%22%3A%22{until}%22%7D'
    f'&level=account&access_token={TOKEN}'
)
ins = json.loads(urllib.request.urlopen(url2).read())
ins_data = ins.get('data', [{}])[0]

spend = float(ins_data.get('spend', 0))
leads = 0
for act in ins_data.get('actions', []):
    if act['action_type'] == 'lead':
        leads += float(act.get('value', 0))

cpl = spend / leads if leads > 0 else 0

# Cálculos
n = len(active)
budget_atual = sum(int(a.get('daily_budget', 0)) / 100 for a in active)
dias = 31

gasto_mes_atual = budget_atual * dias
gasto_mes_50    = 50 * n * dias
leads_mes_50    = gasto_mes_50 / cpl if cpl > 0 else 0

print('=== SITUACAO ATUAL ===')
print(f'Adsets ativos:      {n}')
print(f'Verba diaria atual: R${budget_atual:,.0f}/dia')
print(f'Projecao mensal:    R${gasto_mes_atual:,.0f}/mes')
print()
print('=== PERFORMANCE MAIO 2026 ===')
print(f'Gasto realizado:    R${spend:,.2f}')
print(f'Leads gerados:      {int(leads)}')
print(f'CPL medio:          R${cpl:.2f}')
print()
print('=== SIMULACAO: R$50/adset/dia ===')
print(f'Verba diaria:       R${50*n:,.0f}/dia  ({n} adsets x R$50)')
print(f'Projecao mensal:    R${gasto_mes_50:,.0f}/mes  ({n} x R$50 x {dias} dias)')
print(f'Expectativa leads:  {int(leads_mes_50)} leads/mes  (CPL R${cpl:.2f})')
print()
print(f'Limite desejado:    R$44.000/mes')
print(f'Diferenca:          R${gasto_mes_50 - 44000:+,.0f} em relacao ao limite')
print()

# Budget maximo por adset para caber em 44k
budget_max_por_adset = 44000 / dias / n
print(f'Para caber em R$44k: R${budget_max_por_adset:.0f}/adset/dia')
leads_44k = 44000 / cpl if cpl > 0 else 0
print(f'Expectativa leads em R$44k: {int(leads_44k)} leads/mes')
