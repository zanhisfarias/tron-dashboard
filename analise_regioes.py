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
from collections import defaultdict

today     = date.today()
since_mai = today.strftime('%Y-%m-01')
since_abr = '2026-04-01'
until_abr = '2026-04-30'
until     = today.isoformat()

def fetch_insights(s, u):
    tr = urllib.parse.quote(json.dumps({'since': s, 'until': u}, separators=(',', ':')))
    url = (
        'https://graph.facebook.com/' + VERSION + '/' + ACCOUNT + '/insights'
        '?fields=adset_id,adset_name,campaign_name,spend,actions,impressions,clicks'
        '&time_range=' + tr + '&level=adset&limit=200&access_token=' + TOKEN
    )
    data = json.loads(urllib.request.urlopen(url).read())
    rows = data.get('data', [])
    while data.get('paging', {}).get('next'):
        data = json.loads(urllib.request.urlopen(data['paging']['next']).read())
        rows += data.get('data', [])
    return rows

def get_leads(r):
    for a in r.get('actions') or []:
        if a.get('action_type') == 'lead':
            return int(float(a['value']))
    # fallback: native form leads
    for a in r.get('actions') or []:
        if 'lead' in a.get('action_type', ''):
            return int(float(a['value']))
    return 0

# Targeting por adset ativo
url_t = (
    'https://graph.facebook.com/' + VERSION + '/' + ACCOUNT + '/adsets'
    '?fields=id,name,campaign_id,status,daily_budget,targeting&limit=200&access_token=' + TOKEN
)
adsets_raw = json.loads(urllib.request.urlopen(url_t).read()).get('data', [])

targeting = {}
for a in adsets_raw:
    if a.get('status') != 'ACTIVE':
        continue
    t   = a.get('targeting', {})
    geo = t.get('geo_locations', {})
    regioes = [r.get('name', '?') for r in geo.get('regions', [])]
    cidades = [c.get('name', '?') for c in geo.get('cities', []) if isinstance(c, dict)]
    paises  = [p.get('name', '?') for p in geo.get('countries', []) if isinstance(p, dict)]
    locs = regioes or cidades or paises or ['Brasil']
    targeting[a['id']] = {
        'name':   a['name'],
        'budget': int(a.get('daily_budget', 0)) // 100,
        'locs':   locs,
        'n_locs': len(locs),
    }

rows_mai = {r['adset_id']: r for r in fetch_insights(since_mai, until)}
rows_abr = {r['adset_id']: r for r in fetch_insights(since_abr, until_abr)}

def get_spend(r):
    return float(r.get('spend', 0))

def get_cpl(r):
    l = get_leads(r)
    s = get_spend(r)
    return s / l if l else 0

print('Adset'.ljust(40) + ' Reg  Vba  Lds-Mai  Lds-Abr  CPL-Mai  CPL-Abr')
print('-' * 90)

tot_mai = tot_abr = 0
all_rows = []
for aid, t in targeting.items():
    m  = rows_mai.get(aid, {})
    a  = rows_abr.get(aid, {})
    lm = get_leads(m)
    la = get_leads(a)
    tot_mai += lm
    tot_abr += la
    all_rows.append((aid, t, m, a, lm, la))

for aid, t, m, a, lm, la in sorted(all_rows, key=lambda x: -(x[4] + x[5])):
    if lm == 0 and la == 0:
        continue
    nr   = t['n_locs']
    cplm = 'R$' + str(int(get_cpl(m))) if lm else '--'
    cpla = 'R$' + str(int(get_cpl(a))) if la else '--'
    line = (
        t['name'][:39].ljust(40) +
        str(nr).rjust(4) +
        str(t['budget']).rjust(5) +
        str(lm).rjust(9) +
        str(la).rjust(9) +
        cplm.rjust(9) +
        cpla.rjust(9)
    )
    print(line)

print('-' * 90)
var = (tot_mai - tot_abr) / tot_abr * 100 if tot_abr else 0
print('TOTAL'.ljust(40) + ' ' * 9 + str(tot_mai).rjust(9) + str(tot_abr).rjust(9) + (('%+.0f%%' % var).rjust(9)))

# Resumo por numero de regioes
print()
print('=== VERBA VS LEADS POR NUMERO DE REGIOES POR ADSET ===')
buckets = defaultdict(lambda: {'budget': 0, 'leads_mai': 0, 'leads_abr': 0, 'count': 0})
for aid, t, m, a, lm, la in all_rows:
    nr = t['n_locs']
    buckets[nr]['budget']    += t['budget']
    buckets[nr]['leads_mai'] += lm
    buckets[nr]['leads_abr'] += la
    buckets[nr]['count']     += 1

for nr, b in sorted(buckets.items()):
    cpl_mai = '--'
    cpl_abr = '--'
    print(
        '  ' + str(nr) + ' regiao(oes): ' +
        str(b['count']) + ' adsets | ' +
        'R$' + str(b['budget']) + '/dia | ' +
        'leads mai=' + str(b['leads_mai']) + ' abr=' + str(b['leads_abr'])
    )

# Resumo campanha x campanha
print()
print('=== LEADS POR CAMPANHA ===')
camp_mai = defaultdict(int)
camp_abr = defaultdict(int)
for r in fetch_insights(since_mai, until):
    camp_mai[r.get('campaign_name', '?')] += get_leads(r)
for r in fetch_insights(since_abr, until_abr):
    camp_abr[r.get('campaign_name', '?')] += get_leads(r)

camps = sorted(set(list(camp_mai.keys()) + list(camp_abr.keys())))
for c in camps:
    lm = camp_mai.get(c, 0)
    la = camp_abr.get(c, 0)
    var_c = (lm - la) / la * 100 if la else 0
    print('  ' + c[:50] + ': mai=' + str(lm) + ' abr=' + str(la) + ' var=' + ('%+.0f%%' % var_c))
