"""
fix_tabs.py — Corrige 3 problemas:
1. DOMContentLoaded: renderAll() ANTES de selectPlatform('social') — fix charts Meta Ads
2. Calendário: mês real com posts do ORGANIC_DATA por data
3. CRM: renderCRM() usando NECTAR_LEADBOARD real
"""
import sys
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML = r"C:\Users\Marketing\Desktop\Dashboard\index.html"
with open(HTML, encoding="utf-8") as f:
    html = f.read()
print("Lido:", len(html), "chars")

# ══════════════════════════════════════════════════════════════════════
# 1. FIX DOMContentLoaded — renderAll() antes de selectPlatform
# ══════════════════════════════════════════════════════════════════════
OLD_DOM = (
    "  buildPeriodBar();\n"
    "  selectPlatform('social');\n"
    "  if (IS_LIVE) {\n"
    "    startLiveMode();\n"
    "  } else {\n"
    "    renderAll();\n"
    "  }\n"
    "});"
)
NEW_DOM = (
    "  buildPeriodBar();\n"
    "  if (IS_LIVE) {\n"
    "    startLiveMode();\n"
    "  } else {\n"
    "    renderAll();\n"
    "  }\n"
    "  selectPlatform('social');\n"
    "});"
)
assert OLD_DOM in html, "DOMContentLoaded anchor not found"
html = html.replace(OLD_DOM, NEW_DOM, 1)
print("✓ DOMContentLoaded: renderAll() antes de selectPlatform()")

# ══════════════════════════════════════════════════════════════════════
# 2. CALENDÁRIO — substituir socialMain pelo calendário com posts reais
# ══════════════════════════════════════════════════════════════════════
OLD_SOCIAL_INNER = '''  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(225,48,108,0.3);box-shadow:0 0 32px rgba(225,48,108,0.07)">
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
  </div>'''

NEW_SOCIAL_INNER = '''  <!-- Banner Calendário -->
  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(221,42,123,0.3);box-shadow:0 0 32px rgba(221,42,123,0.07)">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background:linear-gradient(135deg,#f58529,#dd2a7b,#8134af)">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-bold text-white">Calendário Editorial</div>
      <div class="text-[11px] mt-0.5" style="color:#9CA3AF">Posts publicados — Instagram &amp; Facebook</div>
    </div>
    <div id="calMonthLabel" class="text-[10px] font-semibold px-2.5 py-1 rounded-lg" style="background:rgba(221,42,123,0.12);color:#dd2a7b">Maio 2026</div>
  </div>

  <!-- KPIs rápidos -->
  <div id="calKpiRow" class="grid grid-cols-3 gap-3"></div>

  <!-- Grade do calendário -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
    <div class="text-[9px] font-bold uppercase tracking-widest mb-4" style="color:#dd2a7b">Maio 2026 — Posts por Dia</div>
    <div id="calGrid"></div>
  </div>

  <!-- Lista de posts do mês -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
    <div class="flex items-center justify-between mb-3">
      <div class="text-[9px] font-bold uppercase tracking-widest" style="color:#dd2a7b">Todos os Posts — Maio 2026</div>
      <div id="calPostCount" class="text-[10px] font-semibold" style="color:#6B7280"></div>
    </div>
    <div id="calPostList" class="space-y-2"></div>
  </div>'''

assert OLD_SOCIAL_INNER in html, "socialMain inner not found"
html = html.replace(OLD_SOCIAL_INNER, NEW_SOCIAL_INNER, 1)
print("✓ Calendário HTML atualizado")

# ══════════════════════════════════════════════════════════════════════
# 3. CRM — substituir placeholder por KPIs reais do NECTAR_LEADBOARD
# ══════════════════════════════════════════════════════════════════════
OLD_CRM_INNER = '''  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(16,185,129,0.3);box-shadow:0 0 32px rgba(16,185,129,0.07)">
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
  </div>'''

NEW_CRM_INNER = '''  <!-- Banner CRM -->
  <div class="card p-3 md:p-4 flex items-center gap-3" style="border-color:rgba(16,185,129,0.3);box-shadow:0 0 32px rgba(16,185,129,0.07)">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background:rgba(16,185,129,0.12)">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-bold text-white">CRM — Nectar</div>
      <div class="text-[11px] mt-0.5" style="color:#9CA3AF">Pipeline de vendas e qualificações — Maio 2026</div>
    </div>
    <div class="text-[10px] font-semibold px-2.5 py-1 rounded-lg" style="background:rgba(16,185,129,0.12);color:#10B981">Conectado</div>
  </div>

  <!-- KPIs CRM -->
  <div id="crmKpiRow" class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4"></div>

  <!-- Funil + Receita -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-4" style="color:#10B981">Funil de Vendas — Nectar</div>
      <div id="crmFunnelNew" class="space-y-2"></div>
    </div>
    <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-4" style="color:#10B981">Receita — Maio 2026</div>
      <div id="crmReceita" class="space-y-3"></div>
    </div>
  </div>

  <!-- Histórico mensal -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">
    <div class="text-[9px] font-bold uppercase tracking-widest mb-4" style="color:#10B981">Histórico Mensal</div>
    <div id="crmHistorico" class="space-y-2"></div>
  </div>'''

assert OLD_CRM_INNER in html, "crmMain inner not found"
html = html.replace(OLD_CRM_INNER, NEW_CRM_INNER, 1)
print("✓ CRM HTML atualizado")

# ══════════════════════════════════════════════════════════════════════
# 4. JS — renderCalendario() + renderCRM() + chamadas no selectPlatform
# ══════════════════════════════════════════════════════════════════════

NEW_JS = r"""
// ═══════════════════════════════════════════════════════
// CALENDÁRIO EDITORIAL
// ═══════════════════════════════════════════════════════
function renderCalendario() {
  var posts = (typeof ORGANIC_DATA !== 'undefined' && ORGANIC_DATA.ig && ORGANIC_DATA.ig.posts) ? ORGANIC_DATA.ig.posts : [];
  var fbPosts = (typeof ORGANIC_DATA !== 'undefined' && ORGANIC_DATA.fb && ORGANIC_DATA.fb.posts) ? ORGANIC_DATA.fb.posts : [];

  // KPIs rápidos
  var kpiRow = document.getElementById('calKpiRow');
  if (kpiRow) {
    kpiRow.innerHTML = [
      { label:'Posts IG (mês)', value: posts.length, color:'#dd2a7b' },
      { label:'Posts FB (mês)', value: fbPosts.length, color:'#1877F2' },
      { label:'Freq. IG', value: posts.length > 1 ? (posts.length / 20).toFixed(1) + '/dia' : '—', color:'#10B981' }
    ].map(function(k) {
      return '<div class="card p-4" style="background:#2A2D3E;border-color:#3A3D52">'
        + '<div class="text-[9px] font-bold uppercase tracking-widest mb-1" style="color:' + k.color + '">' + k.label + '</div>'
        + '<div class="text-2xl md:text-3xl font-black text-white">' + k.value + '</div>'
        + '</div>';
    }).join('');
  }

  // Grade do calendário — maio 2026 (1=sex)
  var grid = document.getElementById('calGrid');
  if (grid) {
    var days = ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];
    var firstDay = 4; // 1 maio 2026 = quinta-feira (0=dom, 4=qui)
    var totalDays = 31;

    // Mapear posts por dia
    var postsByDay = {};
    posts.forEach(function(p) {
      var d = new Date(p.timestamp);
      if (d.getMonth() === 4) { // maio
        var day = d.getDate();
        if (!postsByDay[day]) postsByDay[day] = [];
        postsByDay[day].push({ type: p.type, caption: (p.caption||'').substring(0,35), url: p.url||'' });
      }
    });
    fbPosts.forEach(function(p) {
      var d = new Date(p.timestamp);
      if (d.getMonth() === 4) {
        var day = d.getDate();
        if (!postsByDay[day]) postsByDay[day] = [];
        postsByDay[day].push({ type: 'FB', caption: (p.message||'').substring(0,35), url:'' });
      }
    });

    var typeColor = { IMAGE:'#6366F1', VIDEO:'#10B981', CAROUSEL_ALBUM:'#F59E0B', REEL:'#dd2a7b', FB:'#1877F2' };

    var html = '<div class="grid grid-cols-7 gap-1 mb-2">'
      + days.map(function(d){ return '<div class="text-center text-[9px] font-bold uppercase tracking-widest py-1" style="color:#6B7280">' + d + '</div>'; }).join('')
      + '</div>';
    html += '<div class="grid grid-cols-7 gap-1">';

    // Células vazias antes do dia 1
    for (var i = 0; i < firstDay; i++) {
      html += '<div class="rounded-lg p-1" style="min-height:50px;background:rgba(255,255,255,0.02)"></div>';
    }

    for (var d = 1; d <= totalDays; d++) {
      var ps = postsByDay[d] || [];
      var isToday = d === 20; // 20 maio 2026
      var hasPosts = ps.length > 0;
      var borderStyle = isToday ? 'border:1.5px solid #dd2a7b' : (hasPosts ? 'border:1px solid rgba(99,102,241,0.3)' : 'border:1px solid rgba(255,255,255,0.05)');
      html += '<div class="rounded-lg p-1.5 cursor-pointer" style="min-height:50px;background:' + (hasPosts ? 'rgba(99,102,241,0.07)' : 'rgba(255,255,255,0.02)') + ';' + borderStyle + '">';
      html += '<div class="text-[10px] font-bold mb-1" style="color:' + (isToday ? '#dd2a7b' : (hasPosts ? '#E5E7EB' : '#4B5563')) + '">' + d + '</div>';
      ps.slice(0,2).forEach(function(p) {
        var c = typeColor[p.type] || '#6B7280';
        var postHtml = '<div class="text-[8px] font-semibold truncate mb-0.5 rounded px-1" style="background:' + c + '22;color:' + c + ';max-width:100%">'
          + (p.url ? '<a href="' + p.url + '" target="_blank" rel="noopener" style="color:' + c + ';text-decoration:none">' : '')
          + (p.type === 'CAROUSEL_ALBUM' ? 'Carrossel' : p.type)
          + (p.url ? '</a>' : '')
          + '</div>';
        html += postHtml;
      });
      if (ps.length > 2) html += '<div class="text-[8px]" style="color:#6B7280">+' + (ps.length-2) + '</div>';
      html += '</div>';
    }
    html += '</div>';
    grid.innerHTML = html;
  }

  // Lista de posts do mês
  var postList = document.getElementById('calPostList');
  var postCount = document.getElementById('calPostCount');
  if (postList) {
    var allPosts = posts.map(function(p){ return { source:'IG', type: p.type, caption: p.caption||'', timestamp: p.timestamp, likes: p.likes||0, comments: p.comments||0, url: p.url||'' }; })
      .concat(fbPosts.map(function(p){ return { source:'FB', type: 'POST', caption: p.message||'', timestamp: p.timestamp, likes: p.likes||0, comments: p.comments||0, url:'' }; }))
      .sort(function(a,b){ return new Date(b.timestamp) - new Date(a.timestamp); });

    if (postCount) postCount.textContent = allPosts.length + ' posts';

    var typeColor2 = { IMAGE:'#6366F1', VIDEO:'#10B981', CAROUSEL_ALBUM:'#F59E0B', REEL:'#dd2a7b', POST:'#1877F2' };
    var srcBadge = { IG:'#dd2a7b', FB:'#1877F2' };

    postList.innerHTML = allPosts.map(function(p) {
      var dt = new Date(p.timestamp);
      var dtStr = dt.getDate() + '/' + (dt.getMonth()+1) + ' ' + String(dt.getHours()).padStart(2,'0') + 'h';
      var c = typeColor2[p.type] || '#6B7280';
      var sc = srcBadge[p.source] || '#6B7280';
      var cap = p.caption.substring(0, 80) + (p.caption.length > 80 ? '\u2026' : '');
      return '<div class="flex items-center gap-3 py-2 border-b" style="border-color:#3A3D52">'
        + '<div class="w-10 text-center flex-shrink-0">'
        + '<div class="text-xs font-bold" style="color:#E5E7EB">' + dtStr + '</div>'
        + '<div class="text-[8px] font-bold mt-0.5 px-1 rounded" style="background:' + sc + '22;color:' + sc + '">' + p.source + '</div>'
        + '</div>'
        + '<div class="flex-1 min-w-0">'
        + '<div class="text-xs font-semibold text-white truncate">'
        + (p.url ? '<a href="' + p.url + '" target="_blank" rel="noopener" style="color:#E5E7EB;text-decoration:none">' + cap + '</a>' : cap)
        + '</div>'
        + '<div class="flex items-center gap-2 mt-0.5">'
        + '<span class="text-[8px] font-bold px-1.5 py-0.5 rounded" style="background:' + c + '22;color:' + c + '">' + (p.type === 'CAROUSEL_ALBUM' ? 'Carrossel' : p.type) + '</span>'
        + '<span class="text-[10px]" style="color:#9CA3AF">&#x2764; ' + p.likes + '</span>'
        + '<span class="text-[10px]" style="color:#9CA3AF">&#x1F4AC; ' + p.comments + '</span>'
        + '</div>'
        + '</div>'
        + '</div>';
    }).join('');
  }
}

// ═══════════════════════════════════════════════════════
// CRM — Nectar Leadboard
// ═══════════════════════════════════════════════════════
function renderCRM() {
  if (typeof NECTAR_LEADBOARD === 'undefined') return;
  var nl = NECTAR_LEADBOARD;
  var pl = nl.pipeline || {};
  var vendidas = nl.vendidas_mes || 0;
  var perdidas = nl.perdidas_mes || 0;
  var contatos = pl['Contatos'] || 0;
  var taxaConv = contatos > 0 ? (vendidas / contatos * 100).toFixed(1) + '%' : '—';
  var recAvulso = nl.receita_avulso_mes || 0;
  var mrr = nl.mrr_mes || 0;

  // KPIs
  var kpiRow = document.getElementById('crmKpiRow');
  if (kpiRow) {
    kpiRow.innerHTML = [
      { label:'Contatos (mês)', value: contatos, sub:'Leads recebidos', color:'#6366F1' },
      { label:'Vendas Fechadas', value: vendidas, sub: perdidas + ' perdidas', color:'#10B981' },
      { label:'Receita Avulso', value: 'R$\u00a0' + recAvulso.toLocaleString('pt-BR'), sub:'Maio 2026', color:'#F59E0B' },
      { label:'MRR', value: 'R$\u00a0' + mrr.toLocaleString('pt-BR'), sub:'Recorrente mensal', color:'#dd2a7b' }
    ].map(function(k) {
      return '<div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52">'
        + '<div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:' + k.color + '">' + k.label + '</div>'
        + '<div class="text-2xl md:text-3xl font-black text-white">' + k.value + '</div>'
        + '<div class="mt-2 text-[10px]" style="color:#9CA3AF">' + k.sub + '</div>'
        + '<div class="mt-3 h-0.5 rounded-full" style="background:linear-gradient(to right,' + k.color + ',transparent)"></div>'
        + '</div>';
    }).join('');
  }

  // Funil
  var funnel = document.getElementById('crmFunnelNew');
  if (funnel) {
    var stages = ['Contatos','Qualifica\u00e7\u00e3o','Agendamento','Qualificada','Vendida'];
    var colors = ['#6366F1','#8B5CF6','#F59E0B','#10B981','#10B981'];
    var maxVal = pl['Contatos'] || 1;
    funnel.innerHTML = stages.map(function(s, i) {
      var v = pl[s] || 0;
      var pct = maxVal > 0 ? Math.max(2, Math.round(v / maxVal * 100)) : 2;
      var isLast = i === stages.length - 1;
      return '<div class="mb-2">'
        + '<div class="flex items-center justify-between mb-1">'
        + '<span class="text-xs font-semibold" style="color:#E5E7EB">' + s + '</span>'
        + '<span class="text-xs font-black" style="color:' + colors[i] + '">' + v + (isLast ? ' &#x2714;' : '') + '</span>'
        + '</div>'
        + '<div class="w-full rounded-full" style="height:8px;background:rgba(255,255,255,0.07)">'
        + '<div class="rounded-full" style="height:8px;width:' + pct + '%;background:' + colors[i] + ';transition:width 0.6s"></div>'
        + '</div>'
        + '</div>';
    }).join('');
  }

  // Receita
  var recDiv = document.getElementById('crmReceita');
  if (recDiv) {
    var recTotal = recAvulso + mrr;
    recDiv.innerHTML = [
      { label:'Avulso', value: recAvulso, color:'#F59E0B' },
      { label:'MRR (recorrente)', value: mrr, color:'#10B981' },
      { label:'Total Maio', value: recTotal, color:'#6366F1' }
    ].map(function(r) {
      var pct = recTotal > 0 ? Math.round(r.value / recTotal * 100) : 0;
      return '<div>'
        + '<div class="flex justify-between mb-1">'
        + '<span class="text-xs font-semibold" style="color:#E5E7EB">' + r.label + '</span>'
        + '<span class="text-xs font-black" style="color:' + r.color + '">R$\u00a0' + r.value.toLocaleString('pt-BR') + '</span>'
        + '</div>'
        + '<div class="w-full rounded-full" style="height:6px;background:rgba(255,255,255,0.07)">'
        + '<div class="rounded-full" style="height:6px;width:' + (r.label === 'Total Maio' ? 100 : pct) + '%;background:' + r.color + '"></div>'
        + '</div>'
        + '</div>';
    }).join('');
  }

  // Histórico
  var hist = document.getElementById('crmHistorico');
  if (hist && nl.historico_mes) {
    var meses = Object.keys(nl.historico_mes).sort().reverse();
    hist.innerHTML = meses.map(function(m) {
      var h = nl.historico_mes[m];
      var parts = m.split('-');
      var label = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][parseInt(parts[1])-1] + '/' + parts[0].substring(2);
      return '<div class="flex items-center gap-4 py-2 border-b" style="border-color:#3A3D52">'
        + '<div class="w-12 text-xs font-bold" style="color:#9CA3AF">' + label + '</div>'
        + '<div class="flex-1 flex items-center gap-4">'
        + '<span class="text-xs font-bold" style="color:#10B981">&#x2714; ' + (h.vendidas||0) + ' vendas</span>'
        + '<span class="text-xs" style="color:#EF4444">&#x2715; ' + (h.perdidas||0) + ' perdidas</span>'
        + '</div>'
        + '</div>';
    }).join('');
  }
}
"""

# Add renderCalendario + renderCRM JS before the closing </script>
SCRIPT_END = "</script>\n</body>"
assert SCRIPT_END in html, "script end not found"
html = html.replace(SCRIPT_END, NEW_JS + "\n" + SCRIPT_END, 1)
print("✓ renderCalendario() + renderCRM() adicionados")

# ══════════════════════════════════════════════════════════════════════
# 5. Atualizar selectPlatform: chamar renderCalendario() e renderCRM()
# ══════════════════════════════════════════════════════════════════════
OLD_SOCIAL_SHOW = "  if (plat === 'social') {\n    if (socialMain) socialMain.style.display = '';\n  } else if (plat === 'organico') {"
NEW_SOCIAL_SHOW = "  if (plat === 'social') {\n    if (socialMain) socialMain.style.display = '';\n    renderCalendario();\n  } else if (plat === 'organico') {"
assert OLD_SOCIAL_SHOW in html, "social show block not found"
html = html.replace(OLD_SOCIAL_SHOW, NEW_SOCIAL_SHOW, 1)

OLD_CRM_SHOW = "  } else if (plat === 'crm') {\n    if (crmMain) crmMain.style.display = '';\n  }"
NEW_CRM_SHOW = "  } else if (plat === 'crm') {\n    if (crmMain) crmMain.style.display = '';\n    renderCRM();\n  }"
assert OLD_CRM_SHOW in html, "crm show block not found"
html = html.replace(OLD_CRM_SHOW, NEW_CRM_SHOW, 1)
print("✓ selectPlatform() atualizado com renderCalendario() e renderCRM()")

# ══════════════════════════════════════════════════════════════════════
# 6. Salvar
# ══════════════════════════════════════════════════════════════════════
# Remove surrogates if any
bad = [c for c in html if 0xD800 <= ord(c) <= 0xDFFF]
if bad:
    html = ''.join(c for c in html if not (0xD800 <= ord(c) <= 0xDFFF))
    print(f"✓ {len(bad)} surrogates removidos")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("\n✓ index.html salvo!")
print("  Calendário: grade maio 2026 com posts reais por data + lista completa")
print("  CRM: dados reais NECTAR_LEADBOARD (funil, receita, histórico)")
print("  Meta Ads: charts renderizam corretamente (renderAll antes de selectPlatform)")
