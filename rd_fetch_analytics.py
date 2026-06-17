"""
rd_fetch_analytics.py
Fetches email open/click/bounce analytics for recent RD Station campaigns.
Uses campaign_ids already collected to call emails_by_campaign_analytics.
"""
import sys, json, time, urllib.request as _ureq
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import date, timedelta

MCP_URL = 'https://mcp.rdstationmentor.com/marketing/mcp?key=019ed0a8-caf5-7310-a309-b6f69187aaf3'
CACHE   = 'rd_data_cache.json'
HTML    = 'index.html'

def mcp_text(name, args):
    payload = json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/call',
                          'params':{'name':name,'arguments':args}}).encode()
    req = _ureq.Request(MCP_URL, data=payload,
        headers={'Content-Type':'application/json',
                 'Accept':'application/json, text/event-stream'})
    try:
        with _ureq.urlopen(req, timeout=30) as r:
            raw = r.read().decode('utf-8', errors='replace')
        for line in raw.splitlines():
            if line.startswith('data:'):
                parsed = json.loads(line[5:].strip())
                if parsed.get('result',{}).get('isError', False):
                    txt = parsed.get('result',{}).get('content',[{}])[0].get('text','')
                    if '429' in txt:
                        print('  429 rate limit')
                    return None
                text = parsed.get('result',{}).get('content',[{}])[0].get('text','')
                try: return json.loads(text)
                except: return None
    except Exception as e:
        print(f'  Error: {e}')
    return None

today = date.today()

# Email ID -> campaign_id mapping (pre-collected to avoid rate limits)
email_campaigns = [
    (22703095, 19706421, '[CRM][ORDIX] Estrategia de Junho 2026',                    '2026-06-12', 11179),
    (22682682, 19688614, '[CRM][EXTERNO] Live - Checklist ECD 2026 2',               '2026-06-10', 5513),
    (22678373, 19684922, '[CRM][EXTERNO] Checklist ECD 2026',                        '2026-06-09', None),
    (22683744, 19689519, 'DP Fora da Caixa - W2 - Lembrete 2 (dup)',                 '2026-06-09', None),
    (22552379, 19573862, 'DP Fora da Caixa - W2 - Lembrete 2',                       '2026-06-08', None),
    (22552359, 19573845, 'DP Fora da Caixa - W2 - Lembrete 1',                       '2026-06-05', None),
    (22645141, 19655302, '[CRM][EXTERNO] Calendario de Treinamentos - Junho',        '2026-06-03', None),
    (22643383, 19653744, '[CRM][EXTERNO] Feriado de Corpus Christi',                 '2026-06-03', None),
    (22643215, 19653596, '[CRM][EXTERNO] Novo menu TGC Eos D+14',                    '2026-06-02', None),
    (22552492, 19573962, 'DP Fora da Caixa - Email convite 4',                       '2026-06-02', None),
    (22614760, 19628693, '[CRM][EXTERNO] Tron flow #5 - Automacao EFD-Reinf - 2',   '2026-05-29', None),
    (22613424, 19627518, '[CRM][EXTERNO] Tron flow #5 - Automacao EFD-Reinf',       '2026-05-28', None),
]

email_metrics = []
seen_cids = set()

for i, (eid, cid, name, send_at, leads) in enumerate(email_campaigns):
    if cid in seen_cids:
        continue
    seen_cids.add(cid)

    if i > 0:
        time.sleep(1.5)

    try: sd = date.fromisoformat(send_at)
    except: sd = today
    start_d = (sd - timedelta(days=1)).isoformat()
    end_d   = min(sd + timedelta(days=7), today).isoformat()

    analytics = mcp_text('emails_by_campaign_analytics', {
        'start_date':  start_d,
        'end_date':    end_d,
        'campaign_id': [cid],
    })

    if analytics and analytics.get('emails'):
        em = analytics['emails'][0]
        entry = {
            'campaign_id':    cid,
            'email_id':       eid,
            'name':           em.get('campaign_name', name),
            'send_at':        send_at,
            'contacts_count': em.get('contacts_count', leads or 0),
            'delivered':      em.get('email_delivered_count', 0),
            'delivered_rate': round(em.get('email_delivered_rate', 0), 1),
            'bounced':        em.get('email_bounced_count', 0),
            'opened':         em.get('email_opened_count', 0),
            'open_rate':      round(em.get('email_opened_rate', 0), 1),
            'clicked':        em.get('email_clicked_count', 0),
            'click_rate':     round(em.get('email_clicked_rate', 0), 2),
            'unsubscribed':   em.get('email_unsubscribed_count', 0),
            'spam_reported':  em.get('email_spam_reported_count', 0),
            'spam_rate':      round(em.get('email_spam_reported_rate', 0), 3),
        }
        email_metrics.append(entry)
        print(f'  [{i+1}] {name[:40]}: open={entry["open_rate"]}% '
              f'click={entry["click_rate"]}% bounce={entry["bounced"]}')
    else:
        print(f'  [{i+1}] {name[:40]}: no analytics')

print(f'\nCollected {len(email_metrics)} analytics entries')

# Aggregate
valid = [m for m in email_metrics if m.get('open_rate') is not None]
if valid:
    avg_open  = round(sum(m['open_rate'] for m in valid) / len(valid), 1)
    avg_click = round(sum(m['click_rate'] for m in valid) / len(valid), 2)
    avg_del   = round(sum(m['delivered_rate'] for m in valid) / len(valid), 1)
    total_del     = sum(m.get('delivered', 0) for m in valid)
    total_bounced = sum(m.get('bounced',   0) for m in valid)
    total_opened  = sum(m.get('opened',    0) for m in valid)
    total_clicked = sum(m.get('clicked',   0) for m in valid)
    bounce_rates  = [(m.get('bounced', 0)) / max(m.get('contacts_count', 1), 1) * 100
                     for m in valid if m.get('bounced')]
    avg_bounce = round(sum(bounce_rates) / len(bounce_rates), 1) if bounce_rates else 0
else:
    avg_open = avg_click = avg_del = avg_bounce = None
    total_del = total_bounced = total_opened = total_clicked = 0

print(f'Avg open: {avg_open}% | click: {avg_click}% | '
      f'bounce: {avg_bounce}% | delivered: {avg_del}%')

# Update cache
with open(CACHE, encoding='utf-8') as f:
    cache = json.load(f)

cache.update({
    'email_metrics':      email_metrics,
    'avg_open_rate':      avg_open,
    'avg_click_rate':     avg_click,
    'avg_bounce_rate':    avg_bounce,
    'avg_delivered_rate': avg_del,
    'total_delivered':    total_del,
    'total_bounced':      total_bounced,
    'total_opened':       total_opened,
    'total_clicked':      total_clicked,
    '_updated_date':      today.isoformat(),
})

with open(CACHE, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)
print('Cache saved.')

# Update HTML
with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

rd_data = {
    'auth_ok':            True,
    'total_campaigns':    cache.get('total_campaigns', 372),
    'total_workflows':    cache.get('total_workflows', 25),
    'workflows_enabled':  cache.get('workflows_enabled', 14),
    'total_lps':          cache.get('total_lps', 20),
    'lps_published':      cache.get('lps_published', 17),
    'recent_campaigns':   cache.get('recent_campaigns', []),
    'workflows':          cache.get('workflows', []),
    'mes_stats':          cache.get('mes_stats', {}),
    'funnel':             {},
    'email_metrics':      email_metrics,
    'avg_open_rate':      avg_open,
    'avg_click_rate':     avg_click,
    'avg_bounce_rate':    avg_bounce,
    'avg_delivered_rate': avg_del,
    'total_delivered':    total_del,
    'total_bounced':      total_bounced,
    'total_opened':       total_opened,
    'total_clicked':      total_clicked,
}

rd_js = 'var RD_STATION_DATA = ' + json.dumps(
    rd_data, ensure_ascii=False, separators=(',', ':')) + ';'

idx = html.find('var RD_STATION_DATA = ')
if idx == -1:
    print('ERROR: RD_STATION_DATA not found in HTML')
    sys.exit(1)
end = html.find(';\n', idx) + 2
new_html = html[:idx] + rd_js + '\n' + html[end:]

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(new_html)
print('HTML updated successfully!')
