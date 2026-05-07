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

# Busca adsets ativos
url = (f'https://graph.facebook.com/{VERSION}/{ACCOUNT}/adsets'
       f'?fields=id,name,status,daily_budget&limit=100&access_token={TOKEN}')
data = json.loads(urllib.request.urlopen(url).read())
active = [a for a in data['data'] if a.get('status') == 'ACTIVE']

print(f"Ajustando {len(active)} adsets para R$50/dia...\n")

ok, erros = 0, 0
for a in active:
    budget_antes = int(a.get('daily_budget', 0)) / 100
    adset_id = a['id']

    # PATCH daily_budget (em centavos)
    patch_url = f'https://graph.facebook.com/{VERSION}/{adset_id}'
    body = urllib.parse.urlencode({'daily_budget': 5000, 'access_token': TOKEN}).encode()
    req  = urllib.request.Request(patch_url, data=body, method='POST')
    try:
        resp = json.loads(urllib.request.urlopen(req).read())
        if resp.get('success'):
            status = 'OK'
            ok += 1
        else:
            status = f'ERRO: {resp}'
            erros += 1
    except Exception as e:
        status = f'EXCECAO: {e}'
        erros += 1

    sinal = '+' if budget_antes < 50 else ('-' if budget_antes > 50 else '=')
    print(f'  [{status}] {sinal} {a["name"][:50]:<50}  R${budget_antes:.0f} -> R$50')

print(f'\nConcluido: {ok} OK | {erros} erros')
print(f'Nova verba diaria: R${50 * len(active):,}/dia')
print(f'Projecao mensal:   R${50 * len(active) * 31:,}/mes')
