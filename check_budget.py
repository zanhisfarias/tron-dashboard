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

url = (f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/adsets'
       f'?fields=id,name,status,daily_budget,campaign_id&limit=100&access_token={TOKEN}')
data = json.loads(urllib.request.urlopen(url).read())
active = [a for a in data['data'] if a.get('status') == 'ACTIVE']

total = 0
print(f'{"Adset":<55} {"R$/dia":>8}')
print('-' * 65)
for a in sorted(active, key=lambda x: -int(x.get('daily_budget', 0))):
    b = int(a.get('daily_budget', 0)) / 100
    total += b
    print(f'{a["name"][:55]:<55} {b:>8.0f}')
print('-' * 65)
print(f'{"TOTAL":<55} {total:>8.0f}')
print(f'\nAdsets ativos: {len(active)}')
