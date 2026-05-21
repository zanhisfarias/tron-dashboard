"""
Exporta toda a base de leads do Nectar CRM (Leadboard) para CSV.
Busca status 1 (Abertos), 2 (Vendidos) e 3 (Perdidos).
Saída: Desktop\leads_nectar_YYYYMMDD.csv
"""

import sys, csv, time, json, datetime, os
import urllib.request, urllib.parse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Configuração ──────────────────────────────────────────
ENV_FILE = r'C:\Users\Marketing\.claude\meta_ads_config.env'
OUTPUT   = rf'C:\Users\Marketing\Desktop\leads_nectar_{datetime.date.today().strftime("%Y%m%d")}_v2.csv'
BASE     = 'https://app.nectarcrm.com.br/crm/api/1'
PAGE_SIZE  = 15
PAGE_DELAY = 0.4   # segundos entre páginas

# ── Lê token ─────────────────────────────────────────────
env = {}
with open(ENV_FILE, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

TOKEN = env.get('NECTAR_API_TOKEN', '')
if not TOKEN:
    print("ERRO: NECTAR_API_TOKEN não encontrado no .env")
    sys.exit(1)

# ── Helpers ───────────────────────────────────────────────
def get_page(status, pg):
    params = urllib.parse.urlencode({
        'api_token':     TOKEN,
        'displayLength': PAGE_SIZE,
        'page':          pg,
        'status':        status,
    })
    url = f'{BASE}/qualificacoes/?{params}'
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    for attempt in range(4):
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            return json.loads(resp.read())
        except Exception as e:
            if attempt == 3:
                print(f"  ERRO (status={status} pg={pg}): {e}")
                return None
            time.sleep((attempt + 1) * 3)

def safe(val):
    if val is None:
        return ''
    return str(val).replace('\n', ' ').replace('\r', '').strip()

def parse_lead(o, status_num):
    cli       = o.get('cliente') or {}
    etapa     = o.get('etapaAtual') or {}
    funil     = o.get('funilVenda') or {}
    responsavel = o.get('responsavel') or {}

    status_label = {1: 'Aberto', 2: 'Vendido', 3: 'Perdido'}.get(status_num, str(status_num))

    # Tags/listas — junta os nomes separados por " | "
    listas = o.get('listas') or []
    tags = ' | '.join(lst.get('nome', '') for lst in listas if lst.get('nome'))

    # Produto via campo RDStation ID nos camposPersonalizados
    campos_p = o.get('camposPersonalizados') or {}
    produto_rd = safe(campos_p.get('RDStation ID') or campos_p.get('RDStationId') or '')

    # Produto inferido das tags (segmento contábil, ordix, tgc, box, etc.)
    tags_lower = tags.lower()
    if 'contábil' in tags_lower or 'contabilidade' in tags_lower or 'escrita' in tags_lower:
        segmento = 'Contábil'
    elif 'ordix' in tags_lower:
        segmento = 'Ordix'
    elif 'tgc' in tags_lower:
        segmento = 'TGC'
    elif 'box' in tags_lower or 'backup' in tags_lower:
        segmento = 'Box'
    elif 'medicina' in tags_lower:
        segmento = 'Medicina'
    elif 'empresarial' in tags_lower:
        segmento = 'Empresarial'
    elif produto_rd:
        rd = produto_rd.lower()
        if 'ordix' in rd:
            segmento = 'Ordix'
        elif 'box' in rd:
            segmento = 'Box'
        elif 'tgc' in rd:
            segmento = 'TGC'
        elif 'contab' in rd or 'escrita' in rd:
            segmento = 'Contábil'
        else:
            segmento = produto_rd
    else:
        segmento = ''

    return {
        'id':                safe(o.get('id')),
        'status':            status_label,
        'segmento':          segmento,
        'tags':              tags,
        'produto_rdstation': produto_rd,
        'etapa':             safe(etapa.get('nome')),
        'etapa_seq':         safe(etapa.get('sequencia')),
        'funil':             safe(funil.get('nome')),
        'nome_lead':         safe(o.get('nome') or cli.get('nome')),
        'empresa':           safe(cli.get('empresa') or cli.get('nomeEmpresa')),
        'email':             safe(cli.get('email')),
        'telefone':          safe(cli.get('telefone') or cli.get('celular')),
        'cidade':            safe(cli.get('cidade')),
        'estado':            safe(cli.get('estado')),
        'origem':            safe(cli.get('origem')),
        'responsavel':       safe(responsavel.get('nome') or responsavel.get('login')),
        'data_cadastro':     safe(o.get('dataCadastro') or o.get('dataInclusao')),
        'data_atualizacao':  safe(o.get('dataAtualizacao')),
        'data_conclusao':    safe(o.get('dataConclusao') or o.get('dataConversao')),
        'valor':             safe(o.get('valor') or o.get('valorTotal')),
        'motivo_perda':      safe(o.get('motivoPerda') or o.get('motivo')),
        'observacoes':       safe(o.get('observacoes') or o.get('descricao')),
    }

# ── Coleta todos os leads ──────────────────────────────────
CAMPOS = [
    'id', 'status', 'segmento', 'tags', 'produto_rdstation',
    'etapa', 'etapa_seq', 'funil',
    'nome_lead', 'empresa', 'email', 'telefone', 'cidade', 'estado',
    'origem', 'responsavel',
    'data_cadastro', 'data_atualizacao', 'data_conclusao',
    'valor', 'motivo_perda', 'observacoes',
]

todos = []

for status_num in [1, 2, 3]:
    label = {1: 'Abertos', 2: 'Vendidos', 3: 'Perdidos'}[status_num]
    print(f'\n[{label}] Buscando...')
    seen_ids = set()
    pg = 1

    while True:
        data = get_page(status_num, pg)
        if data is None:
            break

        items = data if isinstance(data, list) else data.get('data', [])
        if not items:
            break

        # detecta loop de paginação
        page_ids = [o.get('id') for o in items]
        if all(i in seen_ids for i in page_ids):
            break
        seen_ids.update(page_ids)

        for o in items:
            todos.append(parse_lead(o, status_num))

        print(f'  pg {pg:3d} → {len(items)} registros (total acum.: {len(todos)})')
        time.sleep(PAGE_DELAY)
        pg += 1

print(f'\nTotal coletado: {len(todos)} leads')

# ── Exporta CSV ───────────────────────────────────────────
with open(OUTPUT, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(todos)

print(f'Exportado: {OUTPUT}')
