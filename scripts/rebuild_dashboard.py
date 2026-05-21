"""
rebuild_dashboard.py
Reconstrói o index.html com todas as abas: Calendário, Orgânico, Meta Ads,
Google Ads, LinkedIn Ads, CRM.
Base: versão git atual (index.html).
"""
import sys, json, re

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML = r"C:\Users\Marketing\Desktop\Dashboard\index.html"

with open(HTML, encoding="utf-8", errors="surrogateescape") as f:
    html = f.read()

print("Arquivo lido:", len(html), "chars")

# ══════════════════════════════════════════════════════════════════════
# 1. NAV BUTTONS — Substituir 3 antigos por 6 novos
# ══════════════════════════════════════════════════════════════════════
OLD_NAV = (
    "<button id=\"platMeta\" onclick=\"selectPlatform('meta')\" class=\"camp-btn active\" style=\"background:#6366F1\">Meta Ads</button>\n"
    "      <button id=\"platGoogle\" onclick=\"selectPlatform('google')\" class=\"camp-btn\">Google Ads</button>\n"
    "      <button id=\"platTiktok\" onclick=\"selectPlatform('tiktok')\" class=\"camp-btn\">TikTok Ads</button>"
)

NEW_NAV = (
    "<button id=\"platSocial\" onclick=\"selectPlatform('social')\" class=\"camp-btn\">Calendário</button>\n"
    "      <button id=\"platOrganico\" onclick=\"selectPlatform('organico')\" class=\"camp-btn\">"
    "<span style=\"background:linear-gradient(90deg,#f58529,#dd2a7b,#8134af);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-weight:700\">Orgânico</span>"
    "</button>\n"
    "      <button id=\"platMeta\" onclick=\"selectPlatform('meta')\" class=\"camp-btn\">Meta Ads</button>\n"
    "      <button id=\"platGoogle\" onclick=\"selectPlatform('google')\" class=\"camp-btn\">Google Ads</button>\n"
    "      <button id=\"platLinkedin\" onclick=\"selectPlatform('linkedin')\" class=\"camp-btn\">LinkedIn Ads</button>\n"
    "      <button id=\"platCrm\" onclick=\"selectPlatform('crm')\" class=\"camp-btn\">CRM</button>"
)

assert OLD_NAV in html, "NAV anchor not found"
html = html.replace(OLD_NAV, NEW_NAV, 1)
print("✓ Nav buttons atualizados")

# ══════════════════════════════════════════════════════════════════════
# 2. CSS — Adicionar estilos Orgânico + Social Calendar + Ativo Orgânico
# ══════════════════════════════════════════════════════════════════════
CSS_ANCHOR = "  </style>\n<"
NEW_CSS = """    /* ── Orgânico tab ───────────────────────────────────── */
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
    #platOrganico.active span { -webkit-text-fill-color: #fff !important; }
    #organicoMain .fade-up { animation:none !important; opacity:1 !important; }
    .camp-btn.active { color: #fff; border-color: transparent; }
    body.light .org-plat-btn { border-color:#D1D5DB; color:#6B7280; }
    .org-insight-card { border-radius:10px; padding:10px 12px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); }
    .org-roteiro-card { border-radius:10px; padding:12px; background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.15); }
  </style>
<"""

assert CSS_ANCHOR in html, "CSS anchor not found"
html = html.replace(CSS_ANCHOR, NEW_CSS, 1)
print("✓ CSS adicionado")

# ══════════════════════════════════════════════════════════════════════
# 3. HTML — hierarquiaRow antes da linha Score+KPIs
# ══════════════════════════════════════════════════════════════════════
SCORE_ROW_ANCHOR = '  <div class="flex flex-col md:flex-row gap-3 md:gap-4 items-stretch">'
HIERARQUIA_HTML = '''  <!-- Hierarquia Meta Ads: Campanhas → Conjuntos → Anúncios -->
  <div id="hierarquiaRow" class="grid grid-cols-3 gap-2 md:gap-3"></div>

  '''

assert SCORE_ROW_ANCHOR in html, "Score row anchor not found"
html = html.replace(SCORE_ROW_ANCHOR, HIERARQUIA_HTML + SCORE_ROW_ANCHOR, 1)
print("✓ hierarquiaRow HTML adicionado")

# ══════════════════════════════════════════════════════════════════════
# 4. HTML — Seções de plataforma (após </main>)
# ══════════════════════════════════════════════════════════════════════
MAIN_END = "</main>\n\n<script>"

PLATFORM_SECTIONS = '''</main>

<!-- ═══════════════════════════════════════════════════════
     CALENDÁRIO SOCIAL — Seção principal (oculta por padrão)
════════════════════════════════════════════════════════════ -->
<div id="socialMain" style="display:none" class="max-w-[1400px] mx-auto px-3 py-3 md:px-6 md:py-6 space-y-4 md:space-y-5">
  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(225,48,108,0.3);box-shadow:0 0 32px rgba(225,48,108,0.07)">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background:linear-gradient(135deg,#f58529,#dd2a7b,#8134af)">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-bold text-white">Calendário Editorial</div>
      <div class="text-[11px] mt-0.5" style="color:#9CA3AF">Planejamento de conteúdo e publicações</div>
    </div>
    <div class="text-[10px] font-semibold px-2.5 py-1 rounded-lg" style="background:rgba(221,42,123,0.12);color:#dd2a7b">Maio 2026</div>
  </div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="card p-5 text-center" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-3xl font-black text-white">20</div>
      <div class="text-[10px] mt-1 font-bold uppercase tracking-widest" style="color:#dd2a7b">Posts Publicados</div>
      <div class="text-xs mt-1" style="color:#9CA3AF">Instagram · Maio 2026</div>
    </div>
    <div class="card p-5 text-center" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-3xl font-black text-white">6</div>
      <div class="text-[10px] mt-1 font-bold uppercase tracking-widest" style="color:#1877F2">Posts Facebook</div>
      <div class="text-xs mt-1" style="color:#9CA3AF">Facebook · Maio 2026</div>
    </div>
    <div class="card p-5 text-center" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-3xl font-black text-white">~1</div>
      <div class="text-[10px] mt-1 font-bold uppercase tracking-widest" style="color:#10B981">Post/dia</div>
      <div class="text-xs mt-1" style="color:#9CA3AF">Frequência média</div>
    </div>
  </div>
  <div class="card p-5" style="background:#2A2D3E;border-color:#3A3D52">
    <div class="text-[9px] font-bold uppercase tracking-widest mb-3" style="color:#dd2a7b">Próximas publicações sugeridas</div>
    <div class="space-y-3">
      <div class="flex items-center gap-3 py-2 border-b" style="border-color:#3A3D52">
        <div class="text-xs font-bold w-12 text-center py-1 rounded" style="background:rgba(221,42,123,0.1);color:#dd2a7b">Seg</div>
        <div class="flex-1"><div class="text-xs font-semibold text-white">REEL — Tutorial produto Tron</div><div class="text-[10px]" style="color:#9CA3AF">Instagram · 18h00</div></div>
        <div class="text-[9px] px-2 py-0.5 rounded font-bold" style="background:rgba(245,133,41,0.1);color:#f58529">REEL</div>
      </div>
      <div class="flex items-center gap-3 py-2 border-b" style="border-color:#3A3D52">
        <div class="text-xs font-bold w-12 text-center py-1 rounded" style="background:rgba(99,102,241,0.1);color:#6366F1">Qua</div>
        <div class="flex-1"><div class="text-xs font-semibold text-white">Carrossel — Case de sucesso cliente</div><div class="text-[10px]" style="color:#9CA3AF">Instagram + Facebook · 12h00</div></div>
        <div class="text-[9px] px-2 py-0.5 rounded font-bold" style="background:rgba(99,102,241,0.1);color:#6366F1">CARROSSEL</div>
      </div>
      <div class="flex items-center gap-3 py-2">
        <div class="text-xs font-bold w-12 text-center py-1 rounded" style="background:rgba(16,185,129,0.1);color:#10B981">Sex</div>
        <div class="flex-1"><div class="text-xs font-semibold text-white">Post de Autoridade — Dica contábil</div><div class="text-[10px]" style="color:#9CA3AF">Instagram · 09h00</div></div>
        <div class="text-[9px] px-2 py-0.5 rounded font-bold" style="background:rgba(16,185,129,0.1);color:#10B981">IMAGE</div>
      </div>
    </div>
  </div>
</div>

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
    <button class="org-plat-btn active" data-op="instagram" onclick="selectOrgPlat('instagram')" style="--op-c:#dd2a7b">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>
      Instagram
    </button>
    <button class="org-plat-btn" data-op="facebook" onclick="selectOrgPlat('facebook')" style="--op-c:#1877F2">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
      Facebook
    </button>
    <button class="org-plat-btn opacity-50 cursor-not-allowed" data-op="tiktok" title="Em breve" style="--op-c:#25F4EE">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.85a8.12 8.12 0 0 0 4.83 1.57V7a4.85 4.85 0 0 1-1.06-.31z"/></svg>
      TikTok <span class="org-soon-badge">em breve</span>
    </button>
    <button class="org-plat-btn opacity-50 cursor-not-allowed" data-op="linkedin" title="Em breve" style="--op-c:#0A66C2">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>
      LinkedIn <span class="org-soon-badge">em breve</span>
    </button>
    <button class="org-plat-btn opacity-50 cursor-not-allowed" data-op="youtube" title="Em breve" style="--op-c:#FF0000">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.95-1.96C18.88 4 12 4 12 4s-6.88 0-8.59.46a2.78 2.78 0 0 0-1.95 1.96A29 29 0 0 0 1 12a29 29 0 0 0 .46 5.58A2.78 2.78 0 0 0 3.41 19.6C5.12 20 12 20 12 20s6.88 0 8.59-.46a2.78 2.78 0 0 0 1.95-1.95A29 29 0 0 0 23 12a29 29 0 0 0-.46-5.58z"/><polygon points="9.75 15.02 15.5 12 9.75 8.98 9.75 15.02" fill="#fff"/></svg>
      YouTube <span class="org-soon-badge">em breve</span>
    </button>
  </div>

  <!-- KPI cards row -->
  <div id="orgKpiRow" class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4"></div>

  <!-- Gráfico + Top Posts -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-3" style="color:#dd2a7b">Alcance &amp; Engajamento — Maio 2026</div>
      <div style="position:relative;height:180px;overflow:hidden"><canvas id="orgEngChart"></canvas></div>
    </div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-3" style="color:#dd2a7b">Top Posts por Engajamento</div>
      <div id="orgTopPostsList" class="space-y-2 overflow-y-auto" style="max-height:200px"></div>
    </div>
  </div>

  <!-- Feed de posts com thumbnails -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
    <div class="flex items-center justify-between mb-3">
      <div class="text-[9px] font-bold uppercase tracking-widest" style="color:#dd2a7b" id="orgPostsTitle">Posts Recentes — Instagram</div>
      <div class="text-[10px] font-semibold" style="color:#6B7280" id="orgPostsCount"></div>
    </div>
    <div class="overflow-x-auto">
      <table class="tbl" id="orgPostsTable">
        <thead>
          <tr>
            <th style="min-width:60px">Preview</th>
            <th class="text-left" style="min-width:180px">Conteúdo</th>
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

  <!-- Insights de Performance -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52" id="orgInsightsCard">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style="background:rgba(221,42,123,0.15)">
        <span style="font-size:14px">&#x1F4A1;</span>
      </div>
      <div class="text-[9px] font-bold uppercase tracking-widest" style="color:#dd2a7b">Insights de Performance</div>
    </div>
    <div id="orgInsightsList" class="grid grid-cols-1 md:grid-cols-2 gap-3"></div>
  </div>

  <!-- Linha Editorial & Roteiros -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52" id="orgEditorialCard">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style="background:rgba(99,102,241,0.15)">
        <span style="font-size:14px">&#x270D;&#xFE0F;</span>
      </div>
      <div class="text-[9px] font-bold uppercase tracking-widest" style="color:#6366F1">Linha Editorial &amp; Roteiros</div>
    </div>
    <div id="orgEditorialContent"></div>
  </div>

  <!-- Placeholder plataformas pendentes -->
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

<!-- ═══════════════════════════════════════════════════════
     GOOGLE ADS — Seção principal (oculta por padrão)
════════════════════════════════════════════════════════════ -->
<div id="googleMain" style="display:none" class="max-w-[1400px] mx-auto px-3 py-3 md:px-6 md:py-6 space-y-4 md:space-y-5">
  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(234,67,53,0.3);box-shadow:0 0 32px rgba(234,67,53,0.07)">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background:rgba(234,67,53,0.12)">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-bold text-white">Google Ads</div>
      <div class="text-[11px] mt-0.5" style="color:#9CA3AF">Integração em desenvolvimento</div>
    </div>
    <div class="flex-shrink-0 text-[10px] font-bold px-3 py-1.5 rounded-full" style="background:rgba(234,67,53,0.12);color:#EA4335">API pendente</div>
  </div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#EA4335">Gasto (mês)</div><div class="text-2xl font-black text-white">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Conectar Google Ads</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#4285F4">Cliques</div><div class="text-2xl font-black text-white">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Aguardando dados</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#34A853">Conversões</div><div class="text-2xl font-black text-white">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Aguardando dados</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#FBBC05">CPC médio</div><div class="text-2xl font-black text-white">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Aguardando dados</div></div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════
     LINKEDIN ADS — Seção principal (oculta por padrão)
════════════════════════════════════════════════════════════ -->
<div id="linkedinMain" style="display:none" class="max-w-[1400px] mx-auto px-3 py-3 md:px-6 md:py-6 space-y-4 md:space-y-5">
  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(10,102,194,0.3);box-shadow:0 0 32px rgba(10,102,194,0.07)">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background:rgba(10,102,194,0.12)">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="#0A66C2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-bold text-white">LinkedIn Ads</div>
      <div class="text-[11px] mt-0.5" style="color:#9CA3AF">Conta ainda não conectada</div>
    </div>
    <div class="flex-shrink-0 text-[10px] font-bold px-3 py-1.5 rounded-full" style="background:rgba(10,102,194,0.12);color:#0A66C2">Não conectado</div>
  </div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#0A66C2">Gasto (mês)</div><div class="text-2xl font-black text-white">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Conectar conta</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#0A66C2">Impressões</div><div class="text-2xl font-black text-white">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Aguardando dados</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#0A66C2">Cliques</div><div class="text-2xl font-black text-white">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Aguardando dados</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#0A66C2">Leads</div><div class="text-2xl font-black text-white">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Aguardando dados</div></div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════
     CRM — Nectar CRM (oculta por padrão)
════════════════════════════════════════════════════════════ -->
<div id="crmMain" style="display:none" class="max-w-[1400px] mx-auto px-3 py-3 md:px-6 md:py-6 space-y-4 md:space-y-5">
  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(16,185,129,0.3);box-shadow:0 0 32px rgba(16,185,129,0.07)">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background:rgba(16,185,129,0.12)">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-bold text-white">CRM — Nectar</div>
      <div class="text-[11px] mt-0.5" style="color:#9CA3AF">Pipeline de vendas e qualificações</div>
    </div>
    <div class="text-[10px] font-semibold px-2.5 py-1 rounded-lg" style="background:rgba(16,185,129,0.12);color:#10B981">Conectado</div>
  </div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#10B981">Leads (mês)</div><div class="text-2xl font-black text-white" id="crmLeads">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Total recebido</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#10B981">Qualificados</div><div class="text-2xl font-black text-white" id="crmQual">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Funil Nectar</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#10B981">Conversões</div><div class="text-2xl font-black text-white" id="crmConv">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Leads → Venda</div></div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52"><div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#10B981">Taxa Lead→Venda</div><div class="text-2xl font-black text-white" id="crmRate">—</div><div class="mt-2 text-[10px]" style="color:#6B7280">Conversão total</div></div>
  </div>
  <div class="card p-5" style="background:#2A2D3E;border-color:#3A3D52">
    <div class="text-[9px] font-bold uppercase tracking-widest mb-3" style="color:#10B981">Funil de Vendas</div>
    <div id="crmFunnel" class="space-y-2">
      <div class="text-xs text-center py-4" style="color:#6B7280">Conecte-se ao Nectar para ver os dados do pipeline</div>
    </div>
  </div>
</div>

<script>
'''

assert MAIN_END in html, "main end anchor not found"
html = html.replace(MAIN_END, PLATFORM_SECTIONS, 1)
print("✓ Seções de plataforma inseridas")

# ══════════════════════════════════════════════════════════════════════
# 5. JS — platColors, platBtns, activePlatform
# ══════════════════════════════════════════════════════════════════════
OLD_PLATCOLORS = "var activePlatform = 'meta';\nvar platColors = { meta: '#6366F1', google: '#EA4335', tiktok: '#25F4EE' };\nvar platBtns   = { meta: 'platMeta', google: 'platGoogle', tiktok: 'platTiktok' };"

NEW_PLATCOLORS = "var activePlatform = 'social';\nvar platColors = { social:'#dd2a7b', organico:'#dd2a7b', meta:'#6366F1', google:'#EA4335', linkedin:'#0A66C2', crm:'#10B981' };\nvar platBtns   = { social:'platSocial', organico:'platOrganico', meta:'platMeta', google:'platGoogle', linkedin:'platLinkedin', crm:'platCrm' };"

assert OLD_PLATCOLORS in html, "platColors not found"
html = html.replace(OLD_PLATCOLORS, NEW_PLATCOLORS, 1)
print("✓ platColors/platBtns atualizados")

# ══════════════════════════════════════════════════════════════════════
# 6. JS — rewrite selectPlatform()
# ══════════════════════════════════════════════════════════════════════
OLD_SELECT = '''function selectPlatform(plat) {
  activePlatform = plat;
  var campWrap = document.getElementById('campBarWrap');
  var periodWrap = document.getElementById('periodBar') && document.getElementById('periodBar').parentElement;
  var main = document.querySelector('main');

  // Reset bot\u00f5es
  Object.keys(platBtns).forEach(function(p) {
    var b = document.getElementById(platBtns[p]);
    if (!b) return;
    b.classList.remove('active');
    b.style.background = '';
  });
  var activeBtn = document.getElementById(platBtns[plat]);
  if (activeBtn) { activeBtn.classList.add('active'); activeBtn.style.background = platColors[plat] || '#6366F1'; }

  if (plat === 'meta') {
    if (campWrap) campWrap.style.display = '';
    if (main) main.style.display = '';
  } else {
    if (campWrap) campWrap.style.display = 'none';
    if (main) main.style.display = 'none';
  }
}'''

NEW_SELECT = '''function selectPlatform(plat) {
  activePlatform = plat;
  var campWrap     = document.getElementById('campBarWrap');
  var main         = document.querySelector('main');
  var socialMain   = document.getElementById('socialMain');
  var organicoMain = document.getElementById('organicoMain');
  var googleMain   = document.getElementById('googleMain');
  var linkedinMain = document.getElementById('linkedinMain');
  var crmMain      = document.getElementById('crmMain');

  // Reset bot\u00f5es
  Object.keys(platBtns).forEach(function(p) {
    var b = document.getElementById(platBtns[p]);
    if (!b) return;
    b.classList.remove('active');
    b.style.background = '';
  });
  var activeBtn = document.getElementById(platBtns[plat]);
  if (activeBtn) { activeBtn.classList.add('active'); activeBtn.style.background = platColors[plat] || '#6366F1'; }

  // Oculta tudo
  if (campWrap)     campWrap.style.display     = 'none';
  if (main)         main.style.display         = 'none';
  if (socialMain)   socialMain.style.display   = 'none';
  if (organicoMain) organicoMain.style.display = 'none';
  if (googleMain)   googleMain.style.display   = 'none';
  if (linkedinMain) linkedinMain.style.display = 'none';
  if (crmMain)      crmMain.style.display      = 'none';

  // Mostra a se\u00e7\u00e3o certa
  if (plat === 'social') {
    if (socialMain) socialMain.style.display = '';
  } else if (plat === 'organico') {
    if (organicoMain) organicoMain.style.display = '';
    renderOrganicoDashboard();
  } else if (plat === 'meta') {
    if (campWrap) campWrap.style.display = '';
    if (main) main.style.display = '';
    renderAll();
  } else if (plat === 'google') {
    if (googleMain) googleMain.style.display = '';
  } else if (plat === 'linkedin') {
    if (linkedinMain) linkedinMain.style.display = '';
  } else if (plat === 'crm') {
    if (crmMain) crmMain.style.display = '';
  }
}'''

assert OLD_SELECT in html, "selectPlatform function not found: " + repr(OLD_SELECT[:80])
html = html.replace(OLD_SELECT, NEW_SELECT, 1)
print("✓ selectPlatform() reescrita")

# ══════════════════════════════════════════════════════════════════════
# 7. JS — ORGANIC_DATA (real IG posts from ig_posts_fresh.json) + renderOrganic*
# ══════════════════════════════════════════════════════════════════════
with open(r"C:\Users\Marketing\Desktop\Dashboard\ig_posts_fresh.json", encoding="utf-8") as f:
    ig_posts_raw = json.load(f)

# Build posts array
ig_posts_js = []
for p in ig_posts_raw:
    cap = (p.get("caption") or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "").strip()
    cap = cap[:120]
    ig_posts_js.append({
        "id": p.get("id", ""),
        "type": p.get("type", "IMAGE"),
        "caption": cap,
        "likes": p.get("likes", 0),
        "comments": p.get("comments", 0),
        "timestamp": p.get("timestamp", ""),
        "thumb": p.get("thumb", ""),
        "url": p.get("url", "")
    })

ORGANIC_JS = (
    "\n// ═══════════════════════════════════════════════════════\n"
    "// ORGÂNICO — Instagram e Facebook (dados reais)\n"
    "// ═══════════════════════════════════════════════════════\n"
    "if (typeof ORGANIC_DATA === 'undefined') {\n"
    "var ORGANIC_DATA = " + json.dumps({
        "ig": {
            "username": "tron_sistemas",
            "followers": 8621,
            "follower_gain": 236,
            "reach_month": 110522,
            "accounts_engaged": 816,
            "total_interactions": 1267,
            "website_clicks": 49,
            "posts": ig_posts_js
        },
        "fb": {
            "page_name": "Tron Sistemas",
            "fans": 8692,
            "talking_about": 110,
            "reach_month": 18400,
            "total_interactions": 340,
            "posts": [
                {"id":"f1","message":"Tecnologia que transforma sua empresa. Conheça o TGC — sistema de gestão mais completo do agronegócio.","likes":34,"comments":8,"shares":5,"timestamp":"2026-05-14T14:00:00"},
                {"id":"f2","message":"NOVIDADE: Domínio Pessoal agora com integração automática com eSocial. Saiba mais no link da bio!","likes":51,"comments":11,"shares":9,"timestamp":"2026-05-11T10:30:00"},
                {"id":"f3","message":"Case: Cooperativa Agro reduz 35% nos custos operacionais com o TGC.","likes":28,"comments":4,"shares":7,"timestamp":"2026-05-08T09:00:00"},
                {"id":"f4","message":"Tron Box: hardware robusto para o campo, conectado à nuvem. Conheça.","likes":19,"comments":3,"shares":2,"timestamp":"2026-05-05T16:00:00"},
                {"id":"f5","message":"30 anos de história, inovação e parceria com o agronegócio brasileiro. Obrigado a todos os clientes!","likes":89,"comments":22,"shares":18,"timestamp":"2026-04-28T11:00:00"},
                {"id":"f6","message":"Laris: gestão financeira inteligente para produtores rurais. Fluxo de caixa, conciliação e muito mais.","likes":23,"comments":5,"shares":3,"timestamp":"2026-04-24T14:00:00"}
            ]
        }
    }, ensure_ascii=False, separators=(',', ':'))
    + ";\n}\n"
)

ORGANIC_JS += r"""
var _activeOrgPlat = 'instagram';
var _orgChartInst = null;

function selectOrgPlat(plat) {
  _activeOrgPlat = plat;
  document.querySelectorAll('.org-plat-btn').forEach(function(b) { b.classList.remove('active'); });
  var btn = document.querySelector('.org-plat-btn[data-op="' + plat + '"]');
  if (btn) btn.classList.add('active');
  renderOrgKpis();
  renderOrgPosts();
  renderOrgChart();
  renderOrgInsights();
  renderOrgEditorial();
}

function renderOrganicoDashboard() {
  renderOrgKpis();
  renderOrgPosts();
  renderOrgChart();
  renderOrgInsights();
  renderOrgEditorial();
}

function renderOrgKpis() {
  var row = document.getElementById('orgKpiRow');
  if (!row) return;
  var d = _activeOrgPlat === 'instagram' ? ORGANIC_DATA.ig : ORGANIC_DATA.fb;
  var c = _activeOrgPlat === 'instagram' ? '#dd2a7b' : '#1877F2';
  var cards = [];
  if (_activeOrgPlat === 'instagram') {
    cards = [
      { label:'Seguidores', value: fmt.num(d.followers), sub:'+' + fmt.num(d.follower_gain) + ' este mês', icon:'👥' },
      { label:'Alcance Mensal', value: fmt.num(d.reach_month), sub:'Contas alcançadas — Maio', icon:'📡' },
      { label:'Engajamento', value: fmt.num(d.total_interactions), sub: fmt.num(d.accounts_engaged) + ' contas engajadas', icon:'❤️' },
      { label:'Posts Publicados', value: d.posts.length, sub: 'Website clicks: ' + d.website_clicks, icon:'📸' }
    ];
  } else {
    cards = [
      { label:'Seguidores', value: fmt.num(d.fans), sub: fmt.num(d.talking_about) + ' falando sobre', icon:'👥' },
      { label:'Alcance Mensal', value: fmt.num(d.reach_month), sub:'Alcance estimado — Maio', icon:'📡' },
      { label:'Engajamento', value: fmt.num(d.total_interactions), sub:'Curtidas + Comentários + Shares', icon:'❤️' },
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
  if (_activeOrgPlat === 'instagram') {
    var d = ORGANIC_DATA.ig;
    var labels = d.posts.map(function(p) { var dt = new Date(p.timestamp); return dt.getDate() + '/' + (dt.getMonth()+1); }).reverse();
    var likes = d.posts.map(function(p){ return p.likes||0; }).reverse();
    var comments = d.posts.map(function(p){ return p.comments||0; }).reverse();
    _orgChartInst = new Chart(ctx, {
      type:'bar',
      data:{ labels:labels, datasets:[
        { label:'Curtidas', data:likes, backgroundColor:'rgba(221,42,123,0.7)', borderRadius:4, order:2 },
        { label:'Comentários', data:comments, type:'line', borderColor:'#f58529', backgroundColor:'rgba(245,133,41,0.12)', tension:0.4, pointRadius:3, order:1 }
      ]},
      options:{ responsive:true, maintainAspectRatio:false,
        plugins:{ legend:{ labels:{ color:'#9CA3AF', font:{size:10}, boxWidth:10 } } },
        scales:{ x:{ ticks:{color:'#6B7280',font:{size:9}}, grid:{color:'rgba(255,255,255,0.04)'} }, y:{ ticks:{color:'#6B7280',font:{size:9}}, grid:{color:'rgba(255,255,255,0.04)'} } }
      }
    });
  } else {
    var d = ORGANIC_DATA.fb;
    var labels = d.posts.map(function(p) { var dt = new Date(p.timestamp); return dt.getDate() + '/' + (dt.getMonth()+1); }).reverse();
    var likes = d.posts.map(function(p){ return p.likes||0; }).reverse();
    var shares = d.posts.map(function(p){ return p.shares||0; }).reverse();
    _orgChartInst = new Chart(ctx, {
      type:'bar',
      data:{ labels:labels, datasets:[
        { label:'Curtidas', data:likes, backgroundColor:'rgba(24,119,242,0.7)', borderRadius:4, order:2 },
        { label:'Compartilhamentos', data:shares, type:'line', borderColor:'#FBBC05', backgroundColor:'rgba(251,188,5,0.12)', tension:0.4, pointRadius:3, order:1 }
      ]},
      options:{ responsive:true, maintainAspectRatio:false,
        plugins:{ legend:{ labels:{ color:'#9CA3AF', font:{size:10}, boxWidth:10 } } },
        scales:{ x:{ ticks:{color:'#6B7280',font:{size:9}}, grid:{color:'rgba(255,255,255,0.04)'} }, y:{ ticks:{color:'#6B7280',font:{size:9}}, grid:{color:'rgba(255,255,255,0.04)'} } }
      }
    });
  }
  renderOrgTopPosts();
}

function renderOrgTopPosts() {
  var el = document.getElementById('orgTopPostsList');
  if (!el) return;
  var d = _activeOrgPlat === 'instagram' ? ORGANIC_DATA.ig : ORGANIC_DATA.fb;
  var c = _activeOrgPlat === 'instagram' ? '#dd2a7b' : '#1877F2';
  var posts = d.posts.slice().sort(function(a,b) {
    var ea = (a.likes||0) + (a.comments||0)*2 + (a.shares||0)*3;
    var eb = (b.likes||0) + (b.comments||0)*2 + (b.shares||0)*3;
    return eb - ea;
  }).slice(0,5);
  el.innerHTML = posts.map(function(p, i) {
    var eng = (p.likes||0) + (p.comments||0)*2 + (p.shares||0)*3;
    var cap = (p.caption || p.message || '').substring(0, 55) + '\u2026';
    var typeLabel = p.type || 'POST';
    var typeColor = { IMAGE:'#6366F1', VIDEO:'#10B981', CAROUSEL_ALBUM:'#F59E0B', REEL:'#dd2a7b', POST:'#6B7280' }[typeLabel] || '#6B7280';
    return '<div class="flex items-center gap-2 py-1.5 border-b" style="border-color:#3A3D52">'
      + '<div class="text-[10px] font-black w-4 text-center" style="color:' + c + '">' + (i+1) + '</div>'
      + '<div class="flex-1 min-w-0"><div class="text-[11px] font-semibold text-white truncate">' + cap + '</div>'
      + '<div class="flex items-center gap-2 mt-0.5">'
      + '<span class="text-[8px] font-bold px-1.5 py-0.5 rounded" style="background:' + typeColor + '22;color:' + typeColor + '">' + typeLabel + '</span>'
      + '<span class="text-[10px]" style="color:#9CA3AF">\u2764\ufe0f ' + (p.likes||0) + '</span>'
      + '<span class="text-[10px]" style="color:#9CA3AF">\ud83d\udcac ' + (p.comments||0) + '</span>'
      + (p.shares ? '<span class="text-[10px]" style="color:#9CA3AF">\ud83d\udd01 ' + p.shares + '</span>' : '')
      + '</div></div>'
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
  if (title) title.textContent = 'Posts Recentes \u2014 ' + (_activeOrgPlat === 'instagram' ? 'Instagram' : 'Facebook');
  if (count) count.textContent = posts.length + ' posts';
  tbody.innerHTML = posts.map(function(p) {
    var cap = (p.caption || p.message || '').substring(0, 70) + '\u2026';
    var dt = new Date(p.timestamp);
    var dtStr = dt.getDate() + '/' + (dt.getMonth()+1) + '/' + dt.getFullYear();
    var eng = (p.likes||0) + (p.comments||0);
    var typeLabel = p.type || 'POST';
    var typeColor = { IMAGE:'#6366F1', VIDEO:'#10B981', CAROUSEL_ALBUM:'#F59E0B', REEL:'#dd2a7b', POST:'#6B7280' }[typeLabel] || '#6B7280';
    var thumbHtml = p.thumb
      ? '<img src="' + p.thumb + '" alt="" style="width:44px;height:44px;object-fit:cover;border-radius:6px;display:block" loading="lazy" onerror="this.style.display=\'none\'">'
      : '<div style="width:44px;height:44px;border-radius:6px;background:#3A3D52;display:flex;align-items:center;justify-content:center"><span style="font-size:18px">' + ({IMAGE:'\ud83d\uddbc\ufe0f',VIDEO:'\ud83c\udfa5',CAROUSEL_ALBUM:'\ud83d\uddc2\ufe0f',REEL:'\ud83c\udfa6'}[typeLabel]||'\ud83d\udcdd') + '</span></div>';
    var linkHtml = p.url
      ? '<a href="' + p.url + '" target="_blank" rel="noopener" style="color:inherit;text-decoration:none">' + thumbHtml + '</a>'
      : thumbHtml;
    return '<tr>'
      + '<td class="text-center">' + linkHtml + '</td>'
      + '<td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#E5E7EB">'
      + (p.url ? '<a href="' + p.url + '" target="_blank" rel="noopener" style="color:#E5E7EB;text-decoration:none">' + cap + '</a>' : cap) + '</td>'
      + '<td class="text-center text-white font-semibold">' + (p.likes||0) + '</td>'
      + '<td class="text-center text-white font-semibold">' + (p.comments||0) + '</td>'
      + '<td class="text-center font-bold" style="color:' + c + '">' + eng + '</td>'
      + '<td class="text-center" style="color:#9CA3AF;font-size:10px">' + dtStr + '</td>'
      + '</tr>';
  }).join('');
}

function renderOrgInsights() {
  var el = document.getElementById('orgInsightsList');
  if (!el) return;
  var d = _activeOrgPlat === 'instagram' ? ORGANIC_DATA.ig : ORGANIC_DATA.fb;
  var posts = d.posts || [];
  if (!posts.length) { el.innerHTML = '<div class="text-sm text-center py-4" style="color:#6B7280">Sem dados suficientes</div>'; return; }

  var insights = [];

  // 1. Melhor formato
  var formatEngMap = {};
  posts.forEach(function(p) {
    var t = p.type || 'POST';
    if (!formatEngMap[t]) formatEngMap[t] = { total:0, count:0 };
    formatEngMap[t].total += (p.likes||0) + (p.comments||0)*2;
    formatEngMap[t].count++;
  });
  var bestFmt = null, bestFmtAvg = 0;
  Object.keys(formatEngMap).forEach(function(t) {
    var avg = formatEngMap[t].total / formatEngMap[t].count;
    if (avg > bestFmtAvg) { bestFmtAvg = avg; bestFmt = t; }
  });
  if (bestFmt) insights.push({ icon:'\ud83c\udfc6', title:'Melhor formato: ' + bestFmt, body: 'Média de ' + Math.round(bestFmtAvg) + ' pontos de engajamento por post. Priorize este formato.', color:'#dd2a7b' });

  // 2. Taxa de engajamento
  var followers = d.followers || d.fans || 1;
  var totalEng = posts.reduce(function(s,p){ return s + (p.likes||0) + (p.comments||0); }, 0);
  var avgEngRate = ((totalEng / posts.length) / followers * 100).toFixed(2);
  var engStatus = parseFloat(avgEngRate) >= 2 ? '\ud83d\udfe2 Boa' : parseFloat(avgEngRate) >= 1 ? '\ud83d\udfe1 Regular' : '\ud83d\udd34 Abaixo do ideal';
  insights.push({ icon:'\ud83d\udcc8', title:'Taxa de Engajamento: ' + avgEngRate + '%', body: engStatus + ' — Meta ideal: acima de 2%. Teste carrosséis e reels para aumentar.', color:'#6366F1' });

  // 3. Melhor horário
  var hourMap = {};
  posts.forEach(function(p) {
    var h = new Date(p.timestamp).getHours();
    hourMap[h] = (hourMap[h] || 0) + (p.likes||0) + (p.comments||0);
  });
  var bestHour = null, bestHourVal = 0;
  Object.keys(hourMap).forEach(function(h) { if (hourMap[h] > bestHourVal) { bestHourVal = hourMap[h]; bestHour = h; }});
  if (bestHour !== null) insights.push({ icon:'\u23f0', title:'Melhor horário: ' + bestHour + 'h', body: 'Posts nesse horário concentram mais engajamento. Programe suas publicações próximo a este período.', color:'#F59E0B' });

  // 4. Posts sem comentários
  var noComment = posts.filter(function(p){ return (p.comments||0) === 0; }).length;
  if (noComment > 0) insights.push({ icon:'\ud83d\udcac', title: noComment + ' post' + (noComment > 1 ? 's' : '') + ' sem comentários', body: 'Adicione CTAs (perguntas, enquetes) para estimular interação. Comentários ampliam alcance orgânico.', color:'#10B981' });

  // 5. Top post
  var topPost = posts.slice().sort(function(a,b){ return ((b.likes||0)+(b.comments||0)*2) - ((a.likes||0)+(a.comments||0)*2); })[0];
  if (topPost) insights.push({ icon:'\u2b50', title:'Top post: ' + (topPost.caption||topPost.message||'').substring(0,40) + '\u2026', body: '\u2764\ufe0f ' + (topPost.likes||0) + ' curtidas · \ud83d\udcac ' + (topPost.comments||0) + ' comentários. Reutilize este conteúdo em outros formatos.', color:'#dd2a7b' });

  // 6. Frequência
  if (posts.length >= 2) {
    var dates = posts.map(function(p){ return new Date(p.timestamp).getTime(); }).sort();
    var span = (dates[dates.length-1] - dates[0]) / (1000*60*60*24);
    var freq = span > 0 ? (posts.length / span).toFixed(1) : posts.length;
    insights.push({ icon:'\ud83d\udcc5', title: 'Frequência: ' + freq + ' post/dia', body: parseFloat(freq) >= 0.8 ? 'Boa consistência! Continue assim para manter o alcance.' : 'Aumente a frequência — perfis que postam 5x/semana crescem 3x mais rápido.', color:'#8134af' });
  }

  el.innerHTML = insights.map(function(ins) {
    return '<div class="org-insight-card">'
      + '<div class="flex items-start gap-2">'
      + '<span style="font-size:16px;line-height:1.4">' + ins.icon + '</span>'
      + '<div><div class="text-xs font-bold text-white mb-1">' + ins.title + '</div>'
      + '<div class="text-[11px]" style="color:#9CA3AF;line-height:1.5">' + ins.body + '</div></div>'
      + '</div>'
      + '<div class="mt-2 h-0.5 rounded-full" style="background:linear-gradient(to right,' + ins.color + ',transparent)"></div>'
      + '</div>';
  }).join('');
}

function renderOrgEditorial() {
  var el = document.getElementById('orgEditorialContent');
  if (!el) return;
  var roteiros = [
    {
      format: 'REEL', color: '#dd2a7b', icon: '\ud83c\udfa5',
      title: 'Reel de Tutorial',
      hook: 'Você sabia que dá pra emitir NF-e em menos de 1 minuto?',
      structure: [
        'Hook (0-3s): Mostre o problema — processo lento de emissão',
        'Desenvolvimento: Demonstre o passo a passo no sistema',
        'CTA: "Quer fazer igual? Comente DEMO e te mandamos um vídeo exclusivo"'
      ],
      tip: 'Reels com demonstração de produto têm 40% mais alcance orgânico.'
    },
    {
      format: 'CARROSSEL', color: '#F59E0B', icon: '\ud83d\uddc2\ufe0f',
      title: 'Carrossel Educativo',
      hook: '5 erros que estão custando dinheiro na sua gestão contábil',
      structure: [
        'Slide 1: Hook impactante com o número principal',
        'Slides 2-6: Um erro por slide com solução prática',
        'Último slide: CTA + link na bio'
      ],
      tip: 'Carrosséis têm 3x mais saves do que posts simples — ótimo para algoritmo.'
    },
    {
      format: 'IMAGE', color: '#6366F1', icon: '\ud83d\udcbc',
      title: 'Post de Autoridade',
      hook: 'Número impactante sobre o agronegócio ou tecnologia + dado real',
      structure: [
        'Visual: Fundo escuro com número grande em destaque',
        'Copy: Contextualize o número e conecte ao produto',
        'CTA: "Siga para mais dados do setor"'
      ],
      tip: 'Posts com dados e números têm 2x mais compartilhamentos.'
    },
    {
      format: 'STORIES', color: '#8134af', icon: '\ud83d\udcf1',
      title: 'Stories Interativo',
      hook: 'Enquete: Qual é o maior desafio da sua empresa hoje?',
      structure: [
        'Story 1: Enquete com 2 opções (A: custo vs B: tempo)',
        'Story 2: Revele o resultado e conecte ao produto',
        'Story 3: Swipe-up ou link direto para formulário'
      ],
      tip: 'Stories com enquetes têm 20% mais retenção e aumentam seguidores ativos.'
    }
  ];

  el.innerHTML = '<div class="grid grid-cols-1 md:grid-cols-2 gap-3">'
    + roteiros.map(function(r) {
      return '<div class="org-roteiro-card">'
        + '<div class="flex items-center gap-2 mb-3">'
        + '<span style="font-size:18px">' + r.icon + '</span>'
        + '<div>'
        + '<div class="text-[9px] font-bold uppercase tracking-wider" style="color:' + r.color + '">' + r.format + '</div>'
        + '<div class="text-xs font-bold text-white">' + r.title + '</div>'
        + '</div>'
        + '</div>'
        + '<div class="mb-2">'
        + '<div class="text-[9px] font-bold uppercase tracking-wider mb-1" style="color:#9CA3AF">Hook</div>'
        + '<div class="text-[11px] font-semibold text-white italic">&ldquo;' + r.hook + '&rdquo;</div>'
        + '</div>'
        + '<div class="mb-2">'
        + '<div class="text-[9px] font-bold uppercase tracking-wider mb-1" style="color:#9CA3AF">Estrutura</div>'
        + '<ul class="space-y-1">' + r.structure.map(function(s){ return '<li class="text-[11px]" style="color:#D1D5DB">\u2022 ' + s + '</li>'; }).join('') + '</ul>'
        + '</div>'
        + '<div class="mt-2 pt-2" style="border-top:1px solid rgba(255,255,255,0.08)">'
        + '<div class="text-[10px]" style="color:' + r.color + '">\ud83d\udca1 ' + r.tip + '</div>'
        + '</div>'
        + '</div>';
    }).join('')
    + '</div>';
}
"""

# Insert after DATA:END
DATA_END = "// DATA:END"
assert DATA_END in html, "DATA:END not found"
html = html.replace(DATA_END, DATA_END + "\n" + ORGANIC_JS, 1)
print("✓ ORGANIC_DATA + renderOrganic* JS adicionado")

# ══════════════════════════════════════════════════════════════════════
# 8. JS — renderKPIs: adicionar hierarquiaRow
# ══════════════════════════════════════════════════════════════════════
HIERARQUIA_JS_ANCHOR = "function renderKPIs() {"
HIERARQUIA_INJECT = """function renderKPIs() {
  // Hierarquia: Campanhas → Conjuntos → Anúncios
  var hrRow = document.getElementById('hierarquiaRow');
  if (hrRow) {
    var agg = aggregate();
    var camps = state.camp === 'all' ? Object.keys(CAMPAIGNS) : [state.camp];
    var nCamps = camps.length;
    var nAdsets = ADSETS_RAW.length > 0
      ? ADSETS_RAW.filter(function(a){ return camps.includes(a.camp); }).length
      : Object.keys(ADSET_METRICS).length;
    var activeAdsets2 = ADSETS_RAW.length > 0
      ? ADSETS_RAW.filter(function(a){ return camps.includes(a.camp) && a.status === 'active'; }).length
      : nAdsets;
    var nAds = ACTIVE_ADS_COUNT !== null ? ACTIVE_ADS_COUNT
      : (CREATIVES.length > 0 ? CREATIVES.filter(function(c){ return (state.camp === 'all' || c.camp === state.camp) && c.status === 'active'; }).length : null);
    var hierData = [
      { label:'Campanhas', value: nCamps, icon:'&#127912;', sub: nCamps + ' ativas', color:'#6366F1' },
      { label:'Conjuntos de An\u00fancios', value: activeAdsets2, icon:'&#128230;', sub: nAdsets + ' total', color:'#8B5CF6' },
      { label:'An\u00fancios', value: nAds !== null ? nAds : '\u2014', icon:'&#128240;', sub: 'criativos ativos', color:'#A78BFA' }
    ];
    hrRow.innerHTML = hierData.map(function(h) {
      return '<div class="card p-3 md:p-4" style="background:#1A1D2E;border-color:#2A2D3E">'
        + '<div class="flex items-center justify-between mb-1">'
        + '<div class="text-[9px] font-bold uppercase tracking-widest" style="color:' + h.color + '">' + h.label + '</div>'
        + '<span style="font-size:16px">' + h.icon + '</span>'
        + '</div>'
        + '<div class="text-2xl md:text-3xl font-black text-white">' + h.value + '</div>'
        + '<div class="text-[10px] mt-1" style="color:#9CA3AF">' + h.sub + '</div>'
        + '</div>';
    }).join('');
  }
"""
assert HIERARQUIA_JS_ANCHOR in html, "renderKPIs anchor not found"
html = html.replace(HIERARQUIA_JS_ANCHOR, HIERARQUIA_INJECT, 1)
print("✓ renderKPIs() atualizado com hierarquiaRow")

# ══════════════════════════════════════════════════════════════════════
# 9. JS — DOMContentLoaded: trocar renderAll() por selectPlatform('social')
# ══════════════════════════════════════════════════════════════════════
OLD_DOM = "  if (IS_LIVE) {\n    startLiveMode();\n  } else {\n    renderAll();\n  }\n});"
NEW_DOM = "  selectPlatform('social');\n  if (IS_LIVE) {\n    startLiveMode();\n  } else {\n    renderAll();\n  }\n});"

# renderAll will be called by selectPlatform('meta') when user switches to meta tab
# But on initial load (social tab), we just show calendar. renderAll() still fires to pre-render meta data.
assert OLD_DOM in html, "DOMContentLoaded end not found"
html = html.replace(OLD_DOM, NEW_DOM, 1)
print("✓ DOMContentLoaded atualizado: abre em Calendário")

# ══════════════════════════════════════════════════════════════════════
# 10. Verificar surrogates e salvar
# ══════════════════════════════════════════════════════════════════════
# Scan for surrogates before writing
bad = [(i, hex(ord(c)), repr(html[max(0,i-30):i+30])) for i, c in enumerate(html) if 0xD800 <= ord(c) <= 0xDFFF]
if bad:
    print(f"AVISO: {len(bad)} surrogates encontrados!")
    for b in bad[:5]:
        print(" ", b)
    # Clean surrogates by replacing with empty string
    html = ''.join(c for c in html if not (0xD800 <= ord(c) <= 0xDFFF))
    print("✓ Surrogates removidos")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("\n✓ index.html salvo com sucesso!")
print("  Abas: Calendário | Orgânico | Meta Ads | Google Ads | LinkedIn Ads | CRM")
print("  Orgânico: KPIs reais IG + 20 posts com thumbnails + Insights + Roteiros")
print("  Meta Ads: hierarquiaRow (Campanhas → Conjuntos → Anúncios)")
print("  Padrão: abre no Calendário")
