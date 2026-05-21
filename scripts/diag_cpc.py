import sys, json, urllib.request, urllib.parse
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

from datetime import date
today = date.today()
since = f'{today.year}-{today.month:02d}-01'
until = today.isoformat()

# Insights por adset — mês atual
url = (
    f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/insights'
    f'?fields=adset_name,campaign_name,spend,clicks,impressions,actions,cpc,cpm,ctr'
    f'&time_range=%7B%22since%22%3A%22{since}%22%2C%22until%22%3A%22{until}%22%7D'
    f'&level=adset&limit=100&access_token={TOKEN}'
)
data = json.loads(urllib.request.urlopen(url).read())
rows = data.get('data', [])

# Também pega targeting de cada adset
url_adsets = (
    f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/adsets'
    f'?fields=id,name,targeting,status&limit=100&access_token={TOKEN}'
)
adsets_data = json.loads(urllib.request.urlopen(url_adsets).read())
targeting_map = {}
for a in adsets_data.get('data', []):
    if a.get('status') == 'ACTIVE':
        t = a.get('targeting', {})
        ages = f"{t.get('age_min','?')}-{t.get('age_max','?')}"
        geos = [g.get('name','?') for g in t.get('geo_locations',{}).get('regions',[])]
        geos += [g.get('name','?') for g in t.get('geo_locations',{}).get('cities',[]) if isinstance(g, dict)]
        if not geos:
            geos = [c.get('name','?') for c in t.get('geo_locations',{}).get('countries',[]) if isinstance(c, dict)]
        targeting_map[a['name']] = {'ages': ages, 'geos': geos[:3]}

# Ordena por CPC decrescente
def get_cpc(r):
    clicks = int(r.get('clicks', 0))
    spend  = float(r.get('spend', 0))
    return spend / clicks if clicks > 0 else 0

rows_with_data = [r for r in rows if int(r.get('clicks', 0)) > 0]
rows_with_data.sort(key=get_cpc, reverse=True)

# Totais
total_spend   = sum(float(r.get('spend', 0)) for r in rows)
total_clicks  = sum(int(r.get('clicks', 0)) for r in rows)
total_impr    = sum(int(r.get('impressions', 0)) for r in rows)
total_leads   = sum(float(a['value']) for r in rows for a in r.get('actions', []) if a['action_type'] == 'lead')
cpc_medio     = total_spend / total_clicks if total_clicks > 0 else 0
ctr_medio     = total_clicks / total_impr * 100 if total_impr > 0 else 0
cpm_medio     = total_spend / total_impr * 1000 if total_impr > 0 else 0

print(f'=== RESUMO MAIO {today.year} (01/{today.month:02d} a {today.day:02d}/{today.month:02d}) ===')
print(f'Gasto:      R${total_spend:,.2f}')
print(f'Cliques:    {total_clicks:,}')
print(f'Impressoes: {total_impr:,}')
print(f'Leads:      {int(total_leads)}')
print(f'CPC medio:  R${cpc_medio:.2f}')
print(f'CTR medio:  {ctr_medio:.2f}%')
print(f'CPM medio:  R${cpm_medio:.2f}')
print()

print(f'{"Adset":<45} {"Gasto":>8} {"Cliques":>8} {"CPC":>7} {"CTR":>6} {"CPM":>7} {"Leads":>6}')
print('-' * 95)
for r in rows_with_data[:20]:
    name   = r.get('adset_name', '')[:44]
    spend  = float(r.get('spend', 0))
    clicks = int(r.get('clicks', 0))
    impr   = int(r.get('impressions', 0))
    leads  = sum(float(a['value']) for a in r.get('actions', []) if a['action_type'] == 'lead')
    cpc    = spend / clicks if clicks > 0 else 0
    ctr    = clicks / impr * 100 if impr > 0 else 0
    cpm    = spend / impr * 1000 if impr > 0 else 0
    flag   = ' <<' if cpc > cpc_medio * 1.5 else ''
    print(f'{name:<45} {spend:>8.2f} {clicks:>8} {cpc:>7.2f} {ctr:>6.2f}% {cpm:>7.2f} {int(leads):>6}{flag}')

print()
print(f'<< = CPC acima de 1.5x a media (R${cpc_medio*1.5:.2f})')
print()

# Diagnóstico de causas
print('=== DIAGNOSTICO ===')
high_cpm  = [r for r in rows_with_data if float(r.get('spend',0))/max(int(r.get('impressions',0)),1)*1000 > 50]
low_ctr   = [r for r in rows_with_data if int(r.get('clicks',0))/max(int(r.get('impressions',0)),1)*100 < 0.5]
print(f'Adsets com CPM > R$50 (audiencia cara):  {len(high_cpm)}')
print(f'Adsets com CTR < 0.5% (criativos fracos): {len(low_ctr)}')
