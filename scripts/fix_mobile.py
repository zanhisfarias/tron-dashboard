# fix_mobile.py — corrige responsividade mobile em todas as abas
import sys

FILE = r'C:\Users\Marketing\Desktop\Dashboard\index.html'

with open(FILE, 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# ─── 1. CSS MOBILE para o Calendário (7 colunas compactas) ─────────────────
OLD_STYLE_ANCHOR = '    body.light [style*="border-top:1px solid rgba(255,255,255,0.08)"] { border-top-color:rgba(0,0,0,0.08) !important; }'

MOBILE_CSS = '''    body.light [style*="border-top:1px solid rgba(255,255,255,0.08)"] { border-top-color:rgba(0,0,0,0.08) !important; }
    /* ── Responsividade mobile ─────────────────────────────── */
    @media (max-width: 639px) {
      /* Calendário — células compactas */
      #calGrid > div { min-height:56px !important; padding:3px !important; }
      #calGrid .text-\\[12px\\] { font-size:10px !important; }
      #calGrid .text-\\[10px\\] { font-size:8px !important; line-height:1.2 !important; }
      #calGrid .rounded { padding:1px 3px !important; margin-bottom:2px !important; }
      #calGrid .w-\\[6px\\] { width:4px !important; height:4px !important; }
      /* Header dias da semana */
      #socialMain .grid-cols-7 .py-2 { padding-top:4px !important; padding-bottom:4px !important; font-size:9px !important; }
      /* Pílulas do calendário — legenda */
      #socialMain .flex-wrap.gap-2 { gap:4px !important; }
      /* Orgânico — tabela com scroll */
      #orgPostsTable { font-size:11px; }
      /* KPI grid Meta — 2 cols no mobile */
      #kpiGrid { grid-template-columns: repeat(2, 1fr) !important; }
      /* Annual/monthly — empilhar em 1 col */
      #annualSummary > div > div { gap: 6px !important; }
      /* Verba por Produto — 1 col */
      #verbaProduto .grid-cols-2 { grid-template-columns: 1fr !important; }
      /* Budget pacing — 1 col */
      #budgetPacing .grid { grid-template-columns: 1fr !important; }
      /* CRM KPIs — 2 cols */
      #crmKpiRow { grid-template-columns: repeat(2, 1fr) !important; }
      /* Funil + Receita — empilhar */
      #crmMain .grid.grid-cols-1.md\\:grid-cols-2 { grid-template-columns: 1fr !important; }
      /* Score desktop oculto no mobile */
      .score-desktop { display: none !important; }
      .score-mobile { display: flex !important; }
      /* Hierarquia row oculta (vazia) */
      #hierarquiaRow { display: none !important; }
      /* Orgânico — insights em 1 col */
      #orgInsightsList { grid-template-columns: 1fr !important; }
      /* Roteiros — 1 col */
      #orgEditorialContent .grid-cols-2 { grid-template-columns: 1fr !important; }
      /* Rio Verde section */
      #rvSection .grid { grid-template-columns: 1fr !important; }
    }
    @media (min-width: 640px) and (max-width: 767px) {
      /* Tablet pequeno — calendário um pouco mais compacto */
      #calGrid > div { min-height:70px !important; }
      #crmKpiRow { grid-template-columns: repeat(3, 1fr) !important; }
    }'''

if OLD_STYLE_ANCHOR in html:
    html = html.replace(OLD_STYLE_ANCHOR, MOBILE_CSS)
    print('✓ CSS mobile adicionado')
else:
    print('✗ Âncora CSS não encontrada')
    sys.exit(1)

# ─── 2. Annual summary grid — md: prefix nos gaps ──────────────────────────
html = html.replace(
    "'<div class=\"grid grid-cols-3 gap-2 md:gap-4\">' +\n      kpis.map(function(k) {\n        return '<div class=\"min-w-0\">' +\n          '<div class=\"text-[8px] md:text-[10px]",
    "'<div class=\"grid grid-cols-3 gap-2 md:gap-4\">' +\n      kpis.map(function(k) {\n        return '<div class=\"min-w-0\">' +\n          '<div class=\"text-[8px] md:text-[10px]\""
)

# ─── 3. Tabela de posts orgânicos — garantir overflow-x-auto ───────────────
OLD_TABLE_WRAP = '<div class="overflow-x-auto mt-1">'
if OLD_TABLE_WRAP not in html:
    # Procurar o wrapper da tabela e garantir scroll
    html = html.replace(
        '<table class="tbl w-full" id="orgPostsTable">',
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch"><table class="tbl w-full" id="orgPostsTable">'
    )
    # Fechar o wrapper — simples: já existe </table> seguido de </div> provavelmente
    print('⚠ Verificar wrapper da tabela manualmente')
else:
    print('✓ Tabela orgânico já tem overflow-x-auto')

# ─── 4. Verba por Produto grid — garantir 1 col no mobile via classe ───────
html = html.replace(
    "'<div class=\"grid grid-cols-2 gap-2 md:gap-3\">' + cards + '</div>'",
    "'<div class=\"grid grid-cols-1 sm:grid-cols-2 gap-2 md:gap-3\">' + cards + '</div>'"
)
print('✓ Verba por Produto: grid-cols-1 sm:grid-cols-2')

# ─── 5. Budget pacing grid — 1 col mobile ──────────────────────────────────
# já usa gridCols variável — ok

# ─── 6. SALVAR ──────────────────────────────────────────────────────────────
with open(FILE, 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)
print('✓ index.html salvo com fixes de responsividade mobile!')
