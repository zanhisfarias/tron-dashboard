"""
patch_organico.py — Adiciona aba Orgânico ao Dashboard Tron
Insere:
  1. Botão "Orgânico" no nav (antes de Meta Ads)
  2. platColors/platBtns para 'organico'
  3. selectPlatform() — handler para 'organico'
  4. organicoMain div (HTML completo)
  5. JS: ORGANIC_DATA + renderOrganicoDashboard()
"""
import sys, re

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML_FILE = r"C:\Users\Marketing\Desktop\Dashboard\index.html"

with open(HTML_FILE, encoding="utf-8") as f:
    html = f.read()

# ─────────────────────────────────────────────────────────
# 1. Botão nav — adicionar "Orgânico" antes de "Meta Ads"
# ─────────────────────────────────────────────────────────
OLD_NAV = '<button id="platMeta" onclick="selectPlatform(\'meta\')" class="camp-btn active" style="background:#6366F1">Meta Ads</button>'
NEW_NAV = (
    '<button id="platOrganico" onclick="selectPlatform(\'organico\')" class="camp-btn">'
    '<span style="background:linear-gradient(90deg,#f58529,#dd2a7b,#8134af);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-weight:700">Orgânico</span>'
    '</button>\n      '
    + OLD_NAV
)
assert OLD_NAV in html, "NAV anchor not found"
html = html.replace(OLD_NAV, NEW_NAV, 1)
print("✓ Botão Orgânico adicionado ao nav")

# ─────────────────────────────────────────────────────────
# 2. platColors / platBtns
# ─────────────────────────────────────────────────────────
OLD_PLAT_COLORS = "var platColors = { meta: '#6366F1', google: '#EA4335', tiktok: '#25F4EE', social: '#E1306C', crm: '#10B981' };"
NEW_PLAT_COLORS = "var platColors = { organico: '#dd2a7b', meta: '#6366F1', google: '#EA4335', tiktok: '#25F4EE', social: '#E1306C', crm: '#10B981' };"
assert OLD_PLAT_COLORS in html, "platColors not found"
html = html.replace(OLD_PLAT_COLORS, NEW_PLAT_COLORS, 1)

OLD_PLAT_BTNS = "var platBtns   = { meta: 'platMeta', google: 'platGoogle', tiktok: 'platTiktok', social: 'platSocial', crm: 'platCrm' };"
NEW_PLAT_BTNS = "var platBtns   = { organico: 'platOrganico', meta: 'platMeta', google: 'platGoogle', tiktok: 'platTiktok', social: 'platSocial', crm: 'platCrm' };"
assert OLD_PLAT_BTNS in html, "platBtns not found"
html = html.replace(OLD_PLAT_BTNS, NEW_PLAT_BTNS, 1)
print("✓ platColors e platBtns atualizados")

# ─────────────────────────────────────────────────────────
# 3. selectPlatform() — adicionar handler 'organico' + var
# ─────────────────────────────────────────────────────────
OLD_SELECT_VARS = (
    "  var campWrap   = document.getElementById('campBarWrap');\n"
    "  var main       = document.querySelector('main');\n"
    "  var googleMain = document.getElementById('googleMain');\n"
    "  var tiktokMain = document.getElementById('tiktokMain');\n"
    "  var socialMain = document.getElementById('socialMain');\n"
    "  var crmMain    = document.getElementById('crmMain');"
)
NEW_SELECT_VARS = (
    "  var campWrap     = document.getElementById('campBarWrap');\n"
    "  var main         = document.querySelector('main');\n"
    "  var organicoMain = document.getElementById('organicoMain');\n"
    "  var googleMain   = document.getElementById('googleMain');\n"
    "  var tiktokMain   = document.getElementById('tiktokMain');\n"
    "  var socialMain   = document.getElementById('socialMain');\n"
    "  var crmMain      = document.getElementById('crmMain');"
)
assert OLD_SELECT_VARS in html, "selectPlatform vars not found"
html = html.replace(OLD_SELECT_VARS, NEW_SELECT_VARS, 1)

OLD_HIDE = (
    "  // Oculta tudo\n"
    "  if (campWrap)   campWrap.style.display   = 'none';\n"
    "  if (main)       main.style.display       = 'none';\n"
    "  if (googleMain) googleMain.style.display = 'none';\n"
    "  if (tiktokMain) tiktokMain.style.display = 'none';\n"
    "  if (socialMain) socialMain.style.display = 'none';\n"
    "  if (crmMain)    crmMain.style.display    = 'none';"
)
NEW_HIDE = (
    "  // Oculta tudo\n"
    "  if (campWrap)     campWrap.style.display     = 'none';\n"
    "  if (main)         main.style.display         = 'none';\n"
    "  if (organicoMain) organicoMain.style.display = 'none';\n"
    "  if (googleMain)   googleMain.style.display   = 'none';\n"
    "  if (tiktokMain)   tiktokMain.style.display   = 'none';\n"
    "  if (socialMain)   socialMain.style.display   = 'none';\n"
    "  if (crmMain)      crmMain.style.display      = 'none';"
)
assert OLD_HIDE in html, "hide block not found"
html = html.replace(OLD_HIDE, NEW_HIDE, 1)

OLD_SHOW_META = (
    "  // Mostra a seção certa\n"
    "  if (plat === 'meta') {"
)
NEW_SHOW_META = (
    "  // Mostra a seção certa\n"
    "  if (plat === 'organico') {\n"
    "    if (organicoMain) organicoMain.style.display = '';\n"
    "    renderOrganicoDashboard();\n"
    "  } else if (plat === 'meta') {"
)
assert OLD_SHOW_META in html, "show meta block not found"
html = html.replace(OLD_SHOW_META, NEW_SHOW_META, 1)
print("✓ selectPlatform() atualizado com 'organico'")

# Fix the nav button — the gradient text overrides light mode, need to handle the active state color
# When active, the button background is set via JS, but the span text may not show well
# We'll add a small CSS rule for this

OLD_CAMP_BTN_ACTIVE = ".camp-btn.active { color: #fff; border-color: transparent; }"
NEW_CAMP_BTN_ACTIVE = (
    ".camp-btn.active { color: #fff; border-color: transparent; }\n"
    "    #platOrganico.active span { -webkit-text-fill-color: #fff !important; }"
)
if OLD_CAMP_BTN_ACTIVE in html:
    html = html.replace(OLD_CAMP_BTN_ACTIVE, NEW_CAMP_BTN_ACTIVE, 1)
    print("✓ CSS botão Orgânico ativo adicionado")

# ─────────────────────────────────────────────────────────
# 4. organicoMain HTML (inserir antes de googleMain)
# ─────────────────────────────────────────────────────────
ORGANICO_HTML = '''
<!-- ═══════════════════════════════════════════════════════
     ORGÂNICO — Instagram, Facebook, TikTok, LinkedIn, YouTube
════════════════════════════════════════════════════════════ -->
<div id="organicoMain" style="display:none" class="max-w-[1400px] mx-auto px-3 py-3 md:px-6 md:py-6 space-y-4 md:space-y-5">

  <!-- Banner -->
  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(221,42,123,0.3);box-shadow:0 0 32px rgba(221,42,123,0.07)">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background:linear-gradient(135deg,#f58529,#dd2a7b,#8134af)">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-bold text-white">Performance Orgânica</div>
      <div class="text-[11px] mt-0.5" style="color:#9CA3AF">Instagram · Facebook · <span style="color:#6B7280">TikTok · LinkedIn · YouTube</span></div>
    </div>
    <div id="orgLastUpdate" class="text-[10px] font-semibold px-2.5 py-1 rounded-lg" style="background:rgba(221,42,123,0.12);color:#dd2a7b">Atualizado agora</div>
  </div>

  <!-- Platform switcher -->
  <div class="flex items-center gap-2 flex-wrap" id="orgPlatTabs">
    <button class="org-plat-btn active" data-op="instagram" onclick="selectOrgPlat('instagram')"
      style="--op-c:#dd2a7b">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>
      Instagram
    </button>
    <button class="org-plat-btn" data-op="facebook" onclick="selectOrgPlat('facebook')"
      style="--op-c:#1877F2">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
      Facebook
    </button>
    <button class="org-plat-btn opacity-50 cursor-not-allowed" data-op="tiktok" title="Em breve"
      style="--op-c:#25F4EE">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.85a8.12 8.12 0 0 0 4.83 1.57V7a4.85 4.85 0 0 1-1.06-.31z"/></svg>
      TikTok <span class="org-soon-badge">em breve</span>
    </button>
    <button class="org-plat-btn opacity-50 cursor-not-allowed" data-op="linkedin" title="Em breve"
      style="--op-c:#0A66C2">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>
      LinkedIn <span class="org-soon-badge">em breve</span>
    </button>
    <button class="org-plat-btn opacity-50 cursor-not-allowed" data-op="youtube" title="Em breve"
      style="--op-c:#FF0000">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.95-1.96C18.88 4 12 4 12 4s-6.88 0-8.59.46a2.78 2.78 0 0 0-1.95 1.96A29 29 0 0 0 1 12a29 29 0 0 0 .46 5.58A2.78 2.78 0 0 0 3.41 19.6C5.12 20 12 20 12 20s6.88 0 8.59-.46a2.78 2.78 0 0 0 1.95-1.95A29 29 0 0 0 23 12a29 29 0 0 0-.46-5.58z"/><polygon points="9.75 15.02 15.5 12 9.75 8.98 9.75 15.02" fill="#fff"/></svg>
      YouTube <span class="org-soon-badge">em breve</span>
    </button>
  </div>

  <!-- KPI cards row -->
  <div id="orgKpiRow" class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4"></div>

  <!-- Gráfico de evolução + Posts -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Engajamento por tipo de post -->
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-3" style="color:#dd2a7b">Alcance & Engajamento — Maio 2026</div>
      <canvas id="orgEngChart" height="160"></canvas>
    </div>
    <!-- Top posts por engajamento -->
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-3" style="color:#dd2a7b">Top Posts por Engajamento</div>
      <div id="orgTopPostsList" class="space-y-2 overflow-y-auto" style="max-height:200px"></div>
    </div>
  </div>

  <!-- Feed de posts -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
    <div class="flex items-center justify-between mb-3">
      <div class="text-[9px] font-bold uppercase tracking-widest" style="color:#dd2a7b" id="orgPostsTitle">Posts Recentes — Instagram</div>
      <div class="text-[10px] font-semibold" style="color:#6B7280" id="orgPostsCount"></div>
    </div>
    <div class="overflow-x-auto">
      <table class="tbl" id="orgPostsTable">
        <thead>
          <tr>
            <th class="text-left" style="min-width:180px">Conteúdo</th>
            <th>Tipo</th>
            <th>Curtidas</th>
            <th>Comentários</th>
            <th>Engaj.</th>
            <th>Data</th>
          </tr>
        </thead>
        <tbody id="orgPostsTbody"></tbody>
      </table>
    </div>
  </div>

  <!-- Placeholder para plataformas pendentes -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3" id="orgPendingRow">
    <div class="card p-4 flex flex-col items-center justify-center gap-2 text-center" style="background:#1E2130;border-color:#2A2D3E;min-height:90px">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" style="color:#25F4EE;opacity:0.5"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.85a8.12 8.12 0 0 0 4.83 1.57V7a4.85 4.85 0 0 1-1.06-.31z"/></svg>
      <div class="text-xs font-bold" style="color:#9CA3AF">TikTok Orgânico</div>
      <div class="text-[10px]" style="color:#6B7280">Conectar conta</div>
    </div>
    <div class="card p-4 flex flex-col items-center justify-center gap-2 text-center" style="background:#1E2130;border-color:#2A2D3E;min-height:90px">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" style="color:#0A66C2;opacity:0.5"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>
      <div class="text-xs font-bold" style="color:#9CA3AF">LinkedIn Orgânico</div>
      <div class="text-[10px]" style="color:#6B7280">Conectar conta</div>
    </div>
    <div class="card p-4 flex flex-col items-center justify-center gap-2 text-center" style="background:#1E2130;border-color:#2A2D3E;min-height:90px">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" style="color:#FF0000;opacity:0.5"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.95-1.96C18.88 4 12 4 12 4s-6.88 0-8.59.46a2.78 2.78 0 0 0-1.95 1.96A29 29 0 0 0 1 12a29 29 0 0 0 .46 5.58A2.78 2.78 0 0 0 3.41 19.6C5.12 20 12 20 12 20s6.88 0 8.59-.46a2.78 2.78 0 0 0 1.95-1.95A29 29 0 0 0 23 12a29 29 0 0 0-.46-5.58z"/><polygon points="9.75 15.02 15.5 12 9.75 8.98 9.75 15.02" fill="#fff"/></svg>
      <div class="text-xs font-bold" style="color:#9CA3AF">YouTube Orgânico</div>
      <div class="text-[10px]" style="color:#6B7280">Conectar conta</div>
    </div>
  </div>

</div>
'''

GOOGLE_ANCHOR = '<!-- ═══════════════════════════════════════════════════════\n     GOOGLE ADS — Seção principal (oculta por padrão)'
assert GOOGLE_ANCHOR in html, "Google anchor not found"
html = html.replace(GOOGLE_ANCHOR, ORGANICO_HTML + '\n' + GOOGLE_ANCHOR, 1)
print("✓ organicoMain HTML inserido")

# ─────────────────────────────────────────────────────────
# 5. CSS para aba Orgânico
# ─────────────────────────────────────────────────────────
CSS_ANCHOR = "/* ── Social Calendar ──────────────────────────────────── */"
NEW_CSS = '''/* ── Orgânico tab ────────────────────────────────────────── */
    .org-plat-btn {
      display:inline-flex; align-items:center; gap:5px;
      font-size:10px; font-weight:700; padding:5px 12px; border-radius:999px;
      border:1px solid rgba(255,255,255,0.15); color:#9CA3AF; background:transparent;
      cursor:pointer; transition:all 0.15s; white-space:nowrap;
    }
    .org-plat-btn:hover:not(.cursor-not-allowed) { border-color:var(--op-c,#dd2a7b); color:var(--op-c,#dd2a7b); }
    .org-plat-btn.active { background:var(--op-c,#dd2a7b); border-color:var(--op-c,#dd2a7b); color:#fff; }
    .org-soon-badge {
      font-size:8px; font-weight:700; padding:1px 5px; border-radius:4px;
      background:rgba(255,255,255,0.1); color:#6B7280; margin-left:2px;
    }
    #organicoMain .fade-up { animation:none !important; opacity:1 !important; }
    body.light .org-plat-btn { border-color:#D1D5DB; color:#6B7280; }
    ''' + CSS_ANCHOR
assert CSS_ANCHOR in html, "CSS anchor not found"
html = html.replace(CSS_ANCHOR, NEW_CSS, 1)
print("✓ CSS Orgânico adicionado")

# ─────────────────────────────────────────────────────────
# 6. JS — ORGANIC_DATA + renderOrganicoDashboard()
# ─────────────────────────────────────────────────────────
# Insert before the closing </script> tag that ends the main script block
# We'll find the selectPlatform-area closing and append after crmMain render

# Find a good anchor near the end of the scripts
JS_ANCHOR = "// Gráfico de evolução Google Ads (dados de exemplo)"

ORGANIC_JS = r"""
// ══════════════════════════════════════════════════════
// ORGÂNICO — Instagram e Facebook
// ══════════════════════════════════════════════════════
var ORGANIC_DATA = {
  ig: {
    username: "tron_sistemas",
    followers: 8621,
    following: 412,
    follower_gain: 236,
    reach_month: 110522,
    profile_views: 945,
    accounts_engaged: 816,
    total_interactions: 1267,
    website_clicks: 49,
    posts: [
      { id:"1", type:"IMAGE",     caption:"Tecnologia que transforma sua empresa. Conheça o TGC! #contabilidade #tecnologia", likes:142, comments:18, timestamp:"2026-05-15T14:30:00" },
      { id:"2", type:"VIDEO",     caption:"Como o Domínio Pessoal facilita a gestão de RH da sua empresa 🚀",               likes:98,  comments:12, timestamp:"2026-05-13T10:00:00" },
      { id:"3", type:"CAROUSEL",  caption:"5 motivos para modernizar sua contabilidade com o TGC. Deslize para ver!",        likes:215, comments:31, timestamp:"2026-05-10T16:00:00" },
      { id:"4", type:"IMAGE",     caption:"Case de sucesso: cliente reduz 40% do tempo em fechamento mensal.",               likes:87,  comments:9,  timestamp:"2026-05-08T09:00:00" },
      { id:"5", type:"REEL",      caption:"Tutorial: como emitir NF-e pelo TGC em menos de 1 minuto ⚡",                    likes:310, comments:44, timestamp:"2026-05-06T18:00:00" },
      { id:"6", type:"IMAGE",     caption:"Ordix: gestão de pedidos que cresce com seu negócio.",                            likes:76,  comments:7,  timestamp:"2026-05-04T11:00:00" },
      { id:"7", type:"CAROUSEL",  caption:"Novidades da versão 4.2 do TGC. O que mudou?",                                   likes:124, comments:22, timestamp:"2026-05-02T15:00:00" },
      { id:"8", type:"VIDEO",     caption:"Integração TGC + Banco do Brasil: pagamentos automáticos!",                      likes:189, comments:28, timestamp:"2026-04-30T12:00:00" },
      { id:"9", type:"IMAGE",     caption:"QIAE — IA para análise de estoque em tempo real.",                                likes:64,  comments:5,  timestamp:"2026-04-28T10:00:00" },
      { id:"10",type:"REEL",      caption:"A história da Tron: 30 anos inovando no agronegócio brasileiro. 🌾",              likes:445, comments:67, timestamp:"2026-04-25T17:00:00" }
    ]
  },
  fb: {
    page_name: "Tron Sistemas",
    fans: 8692,
    talking_about: 110,
    reach_month: 18400,
    total_interactions: 340,
    posts: [
      { id:"f1", message:"Tecnologia que transforma sua empresa. Conheça o TGC — sistema de gestão mais completo do agronegócio.",  likes:34, comments:8,  shares:5,  timestamp:"2026-05-14T14:00:00" },
      { id:"f2", message:"NOVIDADE: Domínio Pessoal agora com integração automática com eSocial. Saiba mais no link da bio!",       likes:51, comments:11, shares:9,  timestamp:"2026-05-11T10:30:00" },
      { id:"f3", message:"Case: Cooperativa Agro reduz 35% nos custos operacionais com o TGC.",                                     likes:28, comments:4,  shares:7,  timestamp:"2026-05-08T09:00:00" },
      { id:"f4", message:"Tron Box: hardware robusto para o campo, conectado à nuvem. Conheça.",                                    likes:19, comments:3,  shares:2,  timestamp:"2026-05-05T16:00:00" },
      { id:"f5", message:"30 anos de história, inovação e parceria com o agronegócio brasileiro. Obrigado a todos os clientes!",    likes:89, comments:22, shares:18, timestamp:"2026-04-28T11:00:00" },
      { id:"f6", message:"Laris: gestão financeira inteligente para produtores rurais. Fluxo de caixa, conciliação e muito mais.",   likes:23, comments:5,  shares:3,  timestamp:"2026-04-24T14:00:00" }
    ]
  }
};

var _activeOrgPlat = 'instagram';
var _orgChartInst = null;

function selectOrgPlat(plat) {
  _activeOrgPlat = plat;
  document.querySelectorAll('.org-plat-btn').forEach(function(b) {
    b.classList.remove('active');
  });
  var btn = document.querySelector('.org-plat-btn[data-op="' + plat + '"]');
  if (btn) btn.classList.add('active');
  renderOrgKpis();
  renderOrgPosts();
  renderOrgChart();
}

function renderOrganicoDashboard() {
  renderOrgKpis();
  renderOrgPosts();
  renderOrgChart();
}

function renderOrgKpis() {
  var row = document.getElementById('orgKpiRow');
  if (!row) return;
  var d = _activeOrgPlat === 'instagram' ? ORGANIC_DATA.ig : ORGANIC_DATA.fb;
  var c = _activeOrgPlat === 'instagram' ? '#dd2a7b' : '#1877F2';

  var cards = [];
  if (_activeOrgPlat === 'instagram') {
    cards = [
      { label:'Seguidores', value: fmtN(d.followers), sub:'+' + fmtN(d.follower_gain) + ' este mês', icon:'👥' },
      { label:'Alcance Mensal', value: fmtN(d.reach_month), sub:'Contas alcançadas — Maio', icon:'📡' },
      { label:'Engajamento', value: fmtN(d.total_interactions), sub: fmtN(d.accounts_engaged) + ' contas engajadas', icon:'❤️' },
      { label:'Posts Publicados', value: d.posts.length, sub: 'Website clicks: ' + d.website_clicks, icon:'📸' }
    ];
  } else {
    cards = [
      { label:'Seguidores', value: fmtN(d.fans), sub: fmtN(d.talking_about) + ' falando sobre', icon:'👥' },
      { label:'Alcance Mensal', value: fmtN(d.reach_month), sub:'Alcance estimado — Maio', icon:'📡' },
      { label:'Engajamento', value: fmtN(d.total_interactions), sub:'Curtidas + Comentários + Shares', icon:'❤️' },
      { label:'Posts Publicados', value: d.posts.length, sub:'Publicados em 2026', icon:'📄' }
    ];
  }

  row.innerHTML = cards.map(function(kpi) {
    return '<div class="card p-4 md:p-5 kpi-card" style="background:#2A2D3E;border-color:#3A3D52">'
      + '<div class="flex items-center justify-between mb-1">'
      + '<div class="text-[9px] font-bold uppercase tracking-widest" style="color:' + c + '">' + kpi.label + '</div>'
      + '<div class="text-lg">' + kpi.icon + '</div>'
      + '</div>'
      + '<div class="text-2xl md:text-3xl font-black text-white mt-1">' + kpi.value + '</div>'
      + '<div class="mt-2 text-[10px] font-semibold" style="color:#E5E7EB">' + kpi.sub + '</div>'
      + '<div class="mt-3 h-0.5 rounded-full" style="background:linear-gradient(to right,' + c + ',transparent)"></div>'
      + '</div>';
  }).join('');
}

function renderOrgChart() {
  var ctx = document.getElementById('orgEngChart');
  if (!ctx) return;
  if (_orgChartInst) { _orgChartInst.destroy(); _orgChartInst = null; }

  var c = _activeOrgPlat === 'instagram' ? '#dd2a7b' : '#1877F2';
  var c2 = _activeOrgPlat === 'instagram' ? 'rgba(221,42,123,0.15)' : 'rgba(24,119,242,0.15)';

  if (_activeOrgPlat === 'instagram') {
    var d = ORGANIC_DATA.ig;
    var labels = d.posts.map(function(p) {
      var dt = new Date(p.timestamp);
      return (dt.getDate()) + '/' + (dt.getMonth()+1);
    }).reverse();
    var likes = d.posts.map(function(p){ return p.likes; }).reverse();
    var comments = d.posts.map(function(p){ return p.comments; }).reverse();

    _orgChartInst = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          { label:'Curtidas', data:likes, backgroundColor:'rgba(221,42,123,0.7)', borderRadius:4, order:2 },
          { label:'Comentários', data:comments, type:'line', borderColor:'#f58529', backgroundColor:'rgba(245,133,41,0.12)', tension:0.4, pointRadius:3, order:1 }
        ]
      },
      options: {
        responsive:true, maintainAspectRatio:false,
        plugins:{ legend:{ labels:{ color:'#9CA3AF', font:{size:10}, boxWidth:10 } } },
        scales:{
          x:{ ticks:{color:'#6B7280',font:{size:9}}, grid:{color:'rgba(255,255,255,0.04)'} },
          y:{ ticks:{color:'#6B7280',font:{size:9}}, grid:{color:'rgba(255,255,255,0.04)'} }
        }
      }
    });
  } else {
    var d = ORGANIC_DATA.fb;
    var labels = d.posts.map(function(p) {
      var dt = new Date(p.timestamp);
      return (dt.getDate()) + '/' + (dt.getMonth()+1);
    }).reverse();
    var likes = d.posts.map(function(p){ return p.likes; }).reverse();
    var shares = d.posts.map(function(p){ return p.shares; }).reverse();

    _orgChartInst = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          { label:'Curtidas', data:likes, backgroundColor:'rgba(24,119,242,0.7)', borderRadius:4, order:2 },
          { label:'Compartilhamentos', data:shares, type:'line', borderColor:'#FBBC05', backgroundColor:'rgba(251,188,5,0.12)', tension:0.4, pointRadius:3, order:1 }
        ]
      },
      options: {
        responsive:true, maintainAspectRatio:false,
        plugins:{ legend:{ labels:{ color:'#9CA3AF', font:{size:10}, boxWidth:10 } } },
        scales:{
          x:{ ticks:{color:'#6B7280',font:{size:9}}, grid:{color:'rgba(255,255,255,0.04)'} },
          y:{ ticks:{color:'#6B7280',font:{size:9}}, grid:{color:'rgba(255,255,255,0.04)'} }
        }
      }
    });
  }

  // Top posts list
  renderOrgTopPosts();
}

function renderOrgTopPosts() {
  var el = document.getElementById('orgTopPostsList');
  if (!el) return;
  var d = _activeOrgPlat === 'instagram' ? ORGANIC_DATA.ig : ORGANIC_DATA.fb;
  var c = _activeOrgPlat === 'instagram' ? '#dd2a7b' : '#1877F2';
  var posts = (_activeOrgPlat === 'instagram' ? d.posts : d.posts).slice().sort(function(a,b) {
    var ea = (a.likes||0) + (a.comments||0)*2 + (a.shares||0)*3;
    var eb = (b.likes||0) + (b.comments||0)*2 + (b.shares||0)*3;
    return eb - ea;
  }).slice(0,5);

  el.innerHTML = posts.map(function(p, i) {
    var eng = (p.likes||0) + (p.comments||0)*2 + (p.shares||0)*3;
    var cap = (p.caption || p.message || '').substring(0, 55) + '…';
    var typeLabel = p.type || 'POST';
    var typeColor = { IMAGE:'#6366F1', VIDEO:'#10B981', CAROUSEL:'#F59E0B', REEL:'#dd2a7b' }[typeLabel] || '#6B7280';
    return '<div class="flex items-center gap-2 py-1.5 border-b" style="border-color:#3A3D52">'
      + '<div class="text-[10px] font-black w-4 text-center" style="color:' + c + '">' + (i+1) + '</div>'
      + '<div class="flex-1 min-w-0">'
      + '<div class="text-[11px] font-semibold text-white truncate">' + cap + '</div>'
      + '<div class="flex items-center gap-2 mt-0.5">'
      + (p.type ? '<span class="text-[8px] font-bold px-1.5 py-0.5 rounded" style="background:' + typeColor + '22;color:' + typeColor + '">' + typeLabel + '</span>' : '')
      + '<span class="text-[10px]" style="color:#9CA3AF">❤️ ' + (p.likes||0) + '</span>'
      + '<span class="text-[10px]" style="color:#9CA3AF">💬 ' + (p.comments||0) + '</span>'
      + (p.shares ? '<span class="text-[10px]" style="color:#9CA3AF">🔁 ' + p.shares + '</span>' : '')
      + '</div>'
      + '</div>'
      + '<div class="text-xs font-black" style="color:' + c + '">' + eng + '</div>'
      + '</div>';
  }).join('');
}

function renderOrgPosts() {
  var d = _activeOrgPlat === 'instagram' ? ORGANIC_DATA.ig : ORGANIC_DATA.fb;
  var c = _activeOrgPlat === 'instagram' ? '#dd2a7b' : '#1877F2';
  var tbody = document.getElementById('orgPostsTbody');
  var title = document.getElementById('orgPostsTitle');
  var count = document.getElementById('orgPostsCount');
  if (!tbody) return;

  var posts = d.posts;
  if (title) title.textContent = 'Posts Recentes — ' + (_activeOrgPlat === 'instagram' ? 'Instagram' : 'Facebook');
  if (count) count.textContent = posts.length + ' posts';

  tbody.innerHTML = posts.map(function(p) {
    var cap = (p.caption || p.message || '').substring(0, 60) + '…';
    var dt = new Date(p.timestamp);
    var dtStr = dt.getDate() + '/' + (dt.getMonth()+1) + '/' + dt.getFullYear();
    var eng = (p.likes||0) + (p.comments||0);
    var typeLabel = p.type || 'POST';
    var typeColor = { IMAGE:'#6366F1', VIDEO:'#10B981', CAROUSEL:'#F59E0B', REEL:'#dd2a7b', POST:'#6B7280' }[typeLabel] || '#6B7280';
    return '<tr>'
      + '<td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#E5E7EB">' + cap + '</td>'
      + '<td class="text-center"><span class="text-[9px] font-bold px-1.5 py-0.5 rounded" style="background:' + typeColor + '22;color:' + typeColor + '">' + typeLabel + '</span></td>'
      + '<td class="text-center text-white font-semibold">' + (p.likes||0) + '</td>'
      + '<td class="text-center text-white font-semibold">' + (p.comments||0) + '</td>'
      + '<td class="text-center font-bold" style="color:' + c + '">' + eng + '</td>'
      + '<td class="text-center" style="color:#9CA3AF;font-size:10px">' + dtStr + '</td>'
      + '</tr>';
  }).join('');
}

"""

assert JS_ANCHOR in html, "JS anchor not found"
html = html.replace(JS_ANCHOR, ORGANIC_JS + "\n" + JS_ANCHOR, 1)
print("✓ JS ORGANIC_DATA + renderOrganicoDashboard() adicionado")

# ─────────────────────────────────────────────────────────
# 7. Salva
# ─────────────────────────────────────────────────────────
with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("\n✓ index.html salvo com sucesso!")
print("  → Aba 'Orgânico' adicionada antes de Meta Ads")
print("  → Instagram: KPIs reais + 10 posts")
print("  → Facebook: KPIs reais + 6 posts")
print("  → TikTok / LinkedIn / YouTube: placeholders")
