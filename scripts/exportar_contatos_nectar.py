"""
Exporta todos os contatos do Nectar (/contatos/) e compara com o Leadboard
já exportado para identificar duplicatas (por email e telefone).

Saídas:
  contatos_nectar_YYYYMMDD.csv   — base completa de contatos (sem duplicatas internas)
  leadboard_nectar_YYYYMMDD.csv  — leadboard já existente (renomeado para clareza)
  relatorio_duplicados.txt        — resumo de registros que aparecem nos dois lados
"""

import sys, csv, time, json, datetime, urllib.request, urllib.parse, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Config ────────────────────────────────────────────────
ENV_FILE      = r'C:\Users\Marketing\.claude\meta_ads_config.env'
LEADBOARD_CSV = rf'C:\Users\Marketing\Desktop\leads_nectar_{datetime.date.today().strftime("%Y%m%d")}_v2.csv'
OUT_CONTATOS  = rf'C:\Users\Marketing\Desktop\contatos_nectar_{datetime.date.today().strftime("%Y%m%d")}.csv'
OUT_RELATORIO = rf'C:\Users\Marketing\Desktop\relatorio_duplicados_{datetime.date.today().strftime("%Y%m%d")}.txt'
BASE          = 'https://app.nectarcrm.com.br/crm/api/1'
PAGE_SIZE     = 50
PAGE_DELAY    = 0.25

# ── Token ─────────────────────────────────────────────────
env = {}
with open(ENV_FILE, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

TOKEN = env.get('NECTAR_API_TOKEN', '')
if not TOKEN:
    print("ERRO: NECTAR_API_TOKEN não encontrado")
    sys.exit(1)

# ── Helpers ───────────────────────────────────────────────
def safe(val):
    if val is None:
        return ''
    return str(val).replace('\n', ' ').replace('\r', '').strip()

def normaliza_telefone(tel):
    """Remove tudo que não é dígito."""
    return re.sub(r'\D', '', str(tel or ''))

def normaliza_email(email):
    return str(email or '').strip().lower()

def get_page(path, pg, extra={}):
    params = {'api_token': TOKEN, 'displayLength': PAGE_SIZE, 'page': pg}
    params.update(extra)
    url = f'{BASE}/{path}?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    for attempt in range(4):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:
            if attempt == 3:
                print(f"  ERRO pg{pg}: {e}")
                return None
            time.sleep((attempt + 1) * 3)

def parse_contato(c):
    telefones = c.get('telefones') or []
    tel_principal = c.get('telefonePrincipal') or (telefones[0] if telefones else '')
    emails = c.get('emails') or []
    email_principal = c.get('emailPrincipal') or c.get('email') or (emails[0] if emails else '')
    responsavel = c.get('responsavel') or {}
    return {
        'id':               safe(c.get('id')),
        'nome':             safe(c.get('nome')),
        'empresa':          safe(c.get('nomeEmpresa') or c.get('empresa')),
        'email':            safe(email_principal),
        'telefone':         safe(tel_principal),
        'cidade':           safe(c.get('cidade')),
        'estado':           safe(c.get('estado')),
        'origem':           safe(c.get('origem')),
        'responsavel':      safe(responsavel.get('nome') or responsavel.get('login')),
        'data_cadastro':    safe(c.get('dataCriacao') or c.get('dataCadastro')),
        'data_atualizacao': safe(c.get('dataAtualizacao')),
        'ativo':            'Sim' if c.get('ativo') else 'Não',
        'is_empresa':       'Sim' if c.get('isEmpresa') or c.get('empresa') == True else 'Não',
    }

CAMPOS_CONTATO = [
    'id', 'nome', 'empresa', 'email', 'telefone',
    'cidade', 'estado', 'origem', 'responsavel',
    'data_cadastro', 'data_atualizacao', 'ativo', 'is_empresa',
]

# ─────────────────────────────────────────────────────────
# 1. Carrega Leadboard já exportado
# ─────────────────────────────────────────────────────────
print("=== CARREGANDO LEADBOARD ===")
try:
    with open(LEADBOARD_CSV, encoding='utf-8-sig') as f:
        lb_rows = list(csv.DictReader(f))
    print(f"  Leadboard carregado: {len(lb_rows)} registros")
except FileNotFoundError:
    print(f"  AVISO: arquivo não encontrado: {LEADBOARD_CSV}")
    lb_rows = []

# Índices do leadboard por email e telefone normalizados
lb_emails  = {normaliza_email(r['email']): r for r in lb_rows if r.get('email')}
lb_tels    = {normaliza_telefone(r['telefone']): r for r in lb_rows if r.get('telefone')}

print(f"  Emails únicos no leadboard:    {len(lb_emails)}")
print(f"  Telefones únicos no leadboard: {len(lb_tels)}")

# ─────────────────────────────────────────────────────────
# 2. Baixa todos os contatos
# ─────────────────────────────────────────────────────────
print("\n=== BAIXANDO CONTATOS (/contatos/) ===")
contatos = []
seen_ids = set()
pg = 1

while True:
    data = get_page('contatos/', pg)
    if data is None:
        break

    items = data if isinstance(data, list) else data.get('data', [])
    if not items:
        break

    page_ids = [str(c.get('id', '')) for c in items]
    if all(i in seen_ids for i in page_ids):
        break
    seen_ids.update(page_ids)

    for c in items:
        contatos.append(parse_contato(c))

    if pg % 100 == 0:
        print(f"  pg {pg:4d} → {len(contatos):,} contatos...")
    time.sleep(PAGE_DELAY)
    pg += 1

print(f"  Download concluído: {len(contatos):,} contatos")

# ─────────────────────────────────────────────────────────
# 3. Remove duplicatas internas nos contatos (mesmo email ou telefone)
# ─────────────────────────────────────────────────────────
print("\n=== DEDUPLICAÇÃO INTERNA (contatos) ===")
seen_emails = set()
seen_tels   = set()
unicos = []
dup_internos = 0

for c in contatos:
    em  = normaliza_email(c['email'])
    tel = normaliza_telefone(c['telefone'])
    is_dup = False
    if em and em in seen_emails:
        is_dup = True
    if tel and len(tel) >= 8 and tel in seen_tels:
        is_dup = True
    if is_dup:
        dup_internos += 1
        continue
    if em:
        seen_emails.add(em)
    if tel and len(tel) >= 8:
        seen_tels.add(tel)
    unicos.append(c)

print(f"  Duplicatas internas removidas: {dup_internos:,}")
print(f"  Contatos únicos:               {len(unicos):,}")

# ─────────────────────────────────────────────────────────
# 4. Cruza contatos com leadboard
# ─────────────────────────────────────────────────────────
print("\n=== CRUZAMENTO CONTATOS × LEADBOARD ===")
cruzados = []

for c in unicos:
    em  = normaliza_email(c['email'])
    tel = normaliza_telefone(c['telefone'])
    match_email = lb_emails.get(em) if em else None
    match_tel   = lb_tels.get(tel) if tel and len(tel) >= 8 else None
    if match_email or match_tel:
        cruzados.append({
            'contato_id':   c['id'],
            'contato_nome': c['nome'],
            'email':        c['email'],
            'telefone':     c['telefone'],
            'match_por':    'email' if match_email else 'telefone',
            'lb_id':        (match_email or match_tel)['id'],
            'lb_status':    (match_email or match_tel)['status'],
            'lb_etapa':     (match_email or match_tel)['etapa'],
        })

print(f"  Contatos que também estão no leadboard: {len(cruzados):,}")

# ─────────────────────────────────────────────────────────
# 5. Exporta CSV de contatos
# ─────────────────────────────────────────────────────────
print("\n=== EXPORTANDO ===")
with open(OUT_CONTATOS, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=CAMPOS_CONTATO, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(unicos)
print(f"  Contatos: {OUT_CONTATOS}")

# ─────────────────────────────────────────────────────────
# 6. Relatório de duplicados
# ─────────────────────────────────────────────────────────
with open(OUT_RELATORIO, 'w', encoding='utf-8') as f:
    f.write(f"RELATÓRIO DE DUPLICADOS — {datetime.date.today()}\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Leadboard (qualificacoes): {len(lb_rows):,} registros\n")
    f.write(f"Contatos (base geral):     {len(contatos):,} registros brutos\n")
    f.write(f"  Duplicatas internas:     {dup_internos:,}\n")
    f.write(f"  Contatos únicos:         {len(unicos):,}\n\n")
    f.write(f"Cruzamento (contatos presentes no leadboard): {len(cruzados):,}\n\n")
    f.write("-" * 60 + "\n")
    f.write("DETALHES DOS CRUZADOS\n")
    f.write("-" * 60 + "\n")
    for r in cruzados[:500]:
        f.write(f"  Contato {r['contato_id']} ({r['contato_nome']}) "
                f"| match por {r['match_por']} "
                f"| LB id={r['lb_id']} status={r['lb_status']} etapa={r['lb_etapa']}\n")
    if len(cruzados) > 500:
        f.write(f"  ... e mais {len(cruzados)-500} registros\n")
print(f"  Relatório: {OUT_RELATORIO}")

print("\n=== RESUMO FINAL ===")
print(f"  Leadboard:          {len(lb_rows):,}")
print(f"  Contatos únicos:    {len(unicos):,}")
print(f"  Presentes nos dois: {len(cruzados):,}")
print(f"  Exclusivos contatos: {len(unicos) - len(cruzados):,}")
print("Concluído.")
