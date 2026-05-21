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

from datetime import date
today     = date.today()
since_mes = today.strftime('%Y-%m-01')
since_abr = '2026-04-01'
until_abr = '2026-04-30'
until     = today.isoformat()

def fetch_insights(s, u):
    tr = f'%7B%22since%22%3A%22{s}%22%2C%22until%22%3A%22{u}%22%7D'
    url = (f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/insights'
           f'?fields=campaign_id,campaign_name,spend,clicks,impressions,actions,reach'
           f'&time_range={tr}&level=campaign&limit=100&access_token={TOKEN}')
    return json.loads(urllib.request.urlopen(url).read()).get('data', [])

def parse_rows(rows):
    out = {}
    for r in rows:
        nome  = r.get('campaign_name', '?')
        spend = float(r.get('spend', 0))
        clk   = int(r.get('clicks', 0))
        impr  = int(r.get('impressions', 0))
        reach = int(r.get('reach', 0))
        leads = sum(float(a['value']) for a in r.get('actions', []) if a['action_type'] == 'lead')
        out[nome] = {
            'id': r.get('campaign_id', ''),
            'spend': spend, 'clicks': clk, 'impr': impr, 'reach': reach, 'leads': leads,
            'cpc': spend / clk   if clk  else 0,
            'ctr': clk / impr * 100 if impr else 0,
            'cpm': spend / impr * 1000 if impr else 0,
            'cpl': spend / leads if leads else 0,
        }
    return out

def brl(v):  return 'R$' + f'{v:,.2f}'
def pct(v):  return f'{v:.2f}%'
def delta(now, prev):
    if prev == 0: return '   n/a'
    d = (now - prev) / prev * 100
    return (('+' if d >= 0 else '') + f'{d:.0f}%').rjust(6)

# Adsets ativos
url_a = (f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/adsets'
         f'?fields=campaign_id,status,daily_budget&limit=100&access_token={TOKEN}')
adsets_raw = json.loads(urllib.request.urlopen(url_a).read()).get('data', [])
camp_budget = {}
camp_count  = {}
for a in adsets_raw:
    if a.get('status') == 'ACTIVE':
        cid = a.get('campaign_id', '')
        camp_budget[cid] = camp_budget.get(cid, 0) + int(a.get('daily_budget', 0)) // 100
        camp_count[cid]  = camp_count.get(cid, 0) + 1

maio = parse_rows(fetch_insights(since_mes, until))
abr  = parse_rows(fetch_insights(since_abr, until_abr))

print('PANORAMA DE CAMPANHAS — ' + today.strftime('%d/%m/%Y') + ' vs Abril completo')
print('=' * 76)

tot_m = dict(spend=0, clicks=0, impr=0, leads=0)
tot_a = dict(spend=0, clicks=0, impr=0, leads=0)

for nome, m in sorted(maio.items(), key=lambda x: -x[1]['spend']):
    a   = abr.get(nome, {})
    cid = m['id']
    n   = camp_count.get(cid, 0)
    b   = camp_budget.get(cid, 0)
    for k in tot_m: tot_m[k] += m.get(k, 0)
    for k in tot_a: tot_a[k] += a.get(k, 0)

    sp_a  = a.get('spend', 0);  ld_a  = a.get('leads', 0)
    cpc_a = a.get('cpc', 0);    ctr_a = a.get('ctr', 0)
    cpm_a = a.get('cpm', 0);    cpl_a = a.get('cpl', 0)

    ctr_m_s  = pct(m['ctr']);   ctr_a_s  = pct(ctr_a)
    cpl_m_s  = brl(m['cpl']) if m['leads'] else '--'
    cpl_a_s  = brl(cpl_a)   if ld_a        else '--'
    cpl_delta = delta(m['cpl'], cpl_a) if m['leads'] and ld_a else '   n/a'

    print()
    print(nome)
    print(f'  Adsets ativos: {n}  |  Verba: R${b}/dia  |  Alcance: {m["reach"]:,}')
    print(f'  {"Metrica":<10} {"MAIO MTD":>12}  {"ABRIL":>12}  {"VAR":>6}')
    print(f'  {"Gasto":<10} {brl(m["spend"]):>12}  {brl(sp_a):>12}  {delta(m["spend"], sp_a)}')
    print(f'  {"Leads":<10} {int(m["leads"]):>12}  {int(ld_a):>12}  {delta(m["leads"], ld_a)}')
    print(f'  {"CPC":<10} {brl(m["cpc"]):>12}  {brl(cpc_a):>12}  {delta(m["cpc"], cpc_a)}')
    print(f'  {"CTR":<10} {ctr_m_s:>12}  {ctr_a_s:>12}  {delta(m["ctr"], ctr_a)}')
    print(f'  {"CPM":<10} {brl(m["cpm"]):>12}  {brl(cpm_a):>12}  {delta(m["cpm"], cpm_a)}')
    print(f'  {"CPL":<10} {cpl_m_s:>12}  {cpl_a_s:>12}  {cpl_delta}')

print()
print('=' * 76)
print('TOTAL GERAL')
cpc_m = tot_m['spend'] / tot_m['clicks'] if tot_m['clicks'] else 0
cpc_a = tot_a['spend'] / tot_a['clicks'] if tot_a['clicks'] else 0
cpl_m = tot_m['spend'] / tot_m['leads']  if tot_m['leads']  else 0
cpl_a = tot_a['spend'] / tot_a['leads']  if tot_a['leads']  else 0
proj  = tot_m['spend'] / today.day * 31
print(f'  {"Gasto":<10} {brl(tot_m["spend"]):>12}  {brl(tot_a["spend"]):>12}  {delta(tot_m["spend"], tot_a["spend"])}')
print(f'  {"Leads":<10} {int(tot_m["leads"]):>12}  {int(tot_a["leads"]):>12}  {delta(tot_m["leads"], tot_a["leads"])}')
print(f'  {"CPC":<10} {brl(cpc_m):>12}  {brl(cpc_a):>12}  {delta(cpc_m, cpc_a)}')
print(f'  {"CPL":<10} {brl(cpl_m) if tot_m["leads"] else "--":>12}  {brl(cpl_a):>12}')
print()
print(f'  Dias decorridos: {today.day}/31  |  Projecao mensal: {brl(proj)}')
