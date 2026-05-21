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

# CPL de abril (mais representativo que maio com 1 dia)
url_abr = (
    f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/insights'
    f'?fields=spend,actions'
    f'&time_range=%7B%22since%22%3A%222026-04-01%22%2C%22until%22%3A%222026-04-30%22%7D'
    f'&level=account&access_token={TOKEN}'
)
ins = json.loads(urllib.request.urlopen(url_abr).read())
d = ins.get('data', [{}])[0]
spend_abr = float(d.get('spend', 0))
leads_abr = sum(float(a['value']) for a in d.get('actions', []) if a['action_type'] == 'lead')
cpl_abr = spend_abr / leads_abr if leads_abr > 0 else 0

print(f'=== CPL DE REFERENCIA (Abril 2026) ===')
print(f'Gasto:   R${spend_abr:,.2f}')
print(f'Leads:   {int(leads_abr)}')
print(f'CPL:     R${cpl_abr:.2f}')
print()

# Meta exige 50 conversoes/semana por adset para sair do aprendizado
# 50 conv/semana = ~7,14 conv/dia
META_CONV_SEMANA = 50
conv_dia = META_CONV_SEMANA / 7

# Budget necessario por adset para 50 conv/semana
budget_necesario_dia = conv_dia * cpl_abr
budget_necesario_semana = META_CONV_SEMANA * cpl_abr

# Com R$50/dia por adset — quantas conversoes por semana?
conv_por_semana_com_50 = (50 * 7) / cpl_abr if cpl_abr > 0 else 0

# Adsets ativos
url = (f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/adsets'
       f'?fields=id,name,status,daily_budget&limit=100&access_token={TOKEN}')
data = json.loads(urllib.request.urlopen(url).read())
active = [a for a in data['data'] if a.get('status') == 'ACTIVE']
n = len(active)

print(f'=== REGRA DO META: 50 CONVERSOES/SEMANA POR ADSET ===')
print(f'Para sair do aprendizado, cada adset precisa de:')
print(f'  50 conversoes/semana = {conv_dia:.1f} leads/dia')
print(f'  Com CPL de R${cpl_abr:.2f} = R${budget_necesario_dia:,.0f}/dia por adset')
print(f'  (R${budget_necesario_semana:,.0f}/semana por adset)')
print()
print(f'=== COM R$50/ADSET/DIA ===')
print(f'  Leads por semana por adset: {conv_por_semana_com_50:.2f}')
print(f'  Atingiria a meta de 50?    NAO — ficaria {(conv_por_semana_com_50/50)*100:.1f}% da meta')
print()

# Quantos adsets podemos ter para cada um atingir 50 conv/semana dentro de R$44k/mes?
# 50 conv/semana = budget_necesario_dia por adset
# n_adsets_ideal = 44000 / 31 / budget_necesario_dia
n_ideal = int((44000 / 31) / budget_necesario_dia) if budget_necesario_dia > 0 else 0
budget_por_adset_44k = (44000 / 31) / n if n > 0 else 0

print(f'=== PARA CABER EM R$44K E ATINGIR 50 CONV/SEMANA ===')
print(f'  Budget disponivel/dia:   R${44000/31:,.0f}')
print(f'  Budget necesario/adset:  R${budget_necesario_dia:,.0f}/dia')
print(f'  Max adsets viaveis:      {n_ideal} adsets')
print()
print(f'=== RESUMO ===')
print(f'  Adsets ativos hoje:      {n}')
print(f'  Adsets viaveis (44k):    {n_ideal}')
print(f'  R$50/adset entrega:      {conv_por_semana_com_50:.1f} leads/semana/adset (precisa de 50)')
print(f'  Recomendacao: consolidar adsets para no maximo {n_ideal} e dar mais verba a cada um')
