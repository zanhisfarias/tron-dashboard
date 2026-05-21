"""fix_calendar.py — Reconstrói socialMain com calendário mensal no modelo da imagem."""
import sys
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML = r"C:\Users\Marketing\Desktop\Dashboard\index.html"
with open(HTML, encoding="utf-8") as f:
    html = f.read()

# ── Substitui o conteúdo interno do socialMain ──────────────────────
OLD = '''  <!-- Banner Calendário -->
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

NEW = '''  <!-- Cabeçalho calendário -->
  <div class="flex items-center justify-between mb-1">
    <div>
      <div class="text-lg font-black text-white">Maio 2026</div>
      <div class="text-[11px] mt-0.5" style="color:#9CA3AF">Calendário Editorial — Instagram &amp; Facebook</div>
    </div>
    <div class="flex items-center gap-3">
      <span class="flex items-center gap-1.5 text-[11px] font-semibold" style="color:#dd2a7b">
        <span class="inline-block w-2.5 h-2.5 rounded-full" style="background:#dd2a7b"></span>Instagram
      </span>
      <span class="flex items-center gap-1.5 text-[11px] font-semibold" style="color:#38BDF8">
        <span class="inline-block w-2.5 h-2.5 rounded-full" style="background:#38BDF8"></span>Facebook
      </span>
    </div>
  </div>

  <!-- Grade calendário principal -->
  <div class="card overflow-hidden" style="background:#1E2130;border-color:#2A2D3E">
    <!-- Header dias da semana -->
    <div class="grid grid-cols-7 border-b" style="border-color:#2A2D3E">
      <div class="py-2 text-center text-[11px] font-bold" style="color:#F87171">DOM</div>
      <div class="py-2 text-center text-[11px] font-bold" style="color:#9CA3AF">SEG</div>
      <div class="py-2 text-center text-[11px] font-bold" style="color:#9CA3AF">TER</div>
      <div class="py-2 text-center text-[11px] font-bold" style="color:#9CA3AF">QUA</div>
      <div class="py-2 text-center text-[11px] font-bold" style="color:#9CA3AF">QUI</div>
      <div class="py-2 text-center text-[11px] font-bold" style="color:#9CA3AF">SEX</div>
      <div class="py-2 text-center text-[11px] font-bold" style="color:#F87171">SÁB</div>
    </div>
    <!-- Células -->
    <div id="calGrid" class="grid grid-cols-7" style="min-height:480px"></div>
  </div>'''

assert OLD in html, "socialMain inner not found"
html = html.replace(OLD, NEW, 1)
print("✓ socialMain HTML substituído")

# ── Substituir renderCalendario() ────────────────────────────────────
OLD_JS = """// ═══════════════════════════════════════════════════════
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
      var cap = p.caption.substring(0, 80) + (p.caption.length > 80 ? '\\u2026' : '');
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
}"""

NEW_JS = r"""// ═══════════════════════════════════════════════════════
// CALENDÁRIO EDITORIAL — modelo grade mensal
// ═══════════════════════════════════════════════════════
function renderCalendario() {
  var igPosts  = (typeof ORGANIC_DATA !== 'undefined' && ORGANIC_DATA.ig) ? ORGANIC_DATA.ig.posts || [] : [];
  var fbPosts  = (typeof ORGANIC_DATA !== 'undefined' && ORGANIC_DATA.fb) ? ORGANIC_DATA.fb.posts || [] : [];

  // Mapear posts reais por dia do mês (maio = month 4)
  var byDay = {};
  igPosts.forEach(function(p) {
    var d = new Date(p.timestamp);
    if (d.getMonth() !== 4) return;
    var day = d.getDate();
    if (!byDay[day]) byDay[day] = [];
    var title = (p.caption || '').replace(/\n/g,' ').trim().substring(0, 38) || ('Post ' + (p.type||'IG'));
    byDay[day].push({ title: title, src: 'ig', url: p.url||'', type: p.type||'IMAGE', likes: p.likes||0, comments: p.comments||0 });
  });
  fbPosts.forEach(function(p) {
    var d = new Date(p.timestamp);
    if (d.getMonth() !== 4) return;
    var day = d.getDate();
    if (!byDay[day]) byDay[day] = [];
    var title = (p.message || '').replace(/\n/g,' ').trim().substring(0, 38) || 'Post Facebook';
    byDay[day].push({ title: title, src: 'fb', url: '', type: 'POST', likes: p.likes||0, comments: p.comments||0 });
  });

  // Construir grade
  var grid = document.getElementById('calGrid');
  if (!grid) return;

  // maio 2026: dia 1 = quinta-feira (col 4, 0-indexed; DOM=0)
  var firstDay = 4;
  var totalDays = 31;
  var today = 21; // 21/05/2026

  // Dias de abril para completar 1ª semana
  var aprilDays = [26,27,28,29,30];
  var cells = '';

  // Células de abril (semana anterior)
  aprilDays.forEach(function(d) {
    cells += '<div class="border-r border-b p-1.5" style="border-color:#2A2D3E;min-height:90px">'
      + '<div class="text-[11px] font-semibold mb-1" style="color:#374151">' + d + '</div>'
      + '</div>';
  });

  // Dias de maio
  for (var d = 1; d <= totalDays; d++) {
    var ps = byDay[d] || [];
    var isToday = (d === today);
    var isSun = ((firstDay + d - 1) % 7 === 0);
    var isSat = ((firstDay + d - 1) % 7 === 6);
    var isWeekend = isSun || isSat;
    var numColor = isToday ? '#dd2a7b' : (isWeekend ? '#F87171' : '#E5E7EB');
    var bgStyle = isToday
      ? 'background:rgba(221,42,123,0.06);border:1.5px solid #dd2a7b'
      : 'border-right:1px solid #2A2D3E;border-bottom:1px solid #2A2D3E';

    cells += '<div class="p-1.5 relative" style="' + bgStyle + ';min-height:90px">'
      + '<div class="text-[12px] font-bold mb-1.5" style="color:' + numColor + '">' + d + '</div>';

    ps.forEach(function(p) {
      var isIG = p.src === 'ig';
      var bg   = isIG ? 'rgba(221,42,123,0.12)'  : 'rgba(56,189,248,0.12)';
      var fg   = isIG ? '#F9A8D4'                 : '#7DD3FC';
      var dot  = isIG ? '#dd2a7b'                 : '#38BDF8';
      var link = p.url ? '<a href="' + p.url + '" target="_blank" rel="noopener" style="color:' + fg + ';text-decoration:none">' + p.title + '</a>'
                       : p.title;
      cells += '<div class="flex items-start gap-1 mb-1 px-1.5 py-0.5 rounded" style="background:' + bg + '">'
        + '<span class="mt-0.5 flex-shrink-0 w-1.5 h-1.5 rounded-full" style="background:' + dot + '"></span>'
        + '<span class="text-[10px] font-semibold leading-tight" style="color:' + fg + ';word-break:break-word">' + link + '</span>'
        + '</div>';
    });

    cells += '</div>';
  }

  // Completar última semana com dias de junho
  var lastCol = (firstDay + totalDays - 1) % 7; // coluna do dia 31 (0=dom)
  var remaining = lastCol === 6 ? 0 : (6 - lastCol);
  for (var j = 1; j <= remaining; j++) {
    cells += '<div class="border-r border-b p-1.5" style="border-color:#2A2D3E;min-height:90px">'
      + '<div class="text-[11px] font-semibold mb-1" style="color:#374151">' + j + '</div>'
      + '</div>';
  }

  grid.innerHTML = cells;
}"""

assert OLD_JS in html, "renderCalendario JS not found"
html = html.replace(OLD_JS, NEW_JS, 1)
print("✓ renderCalendario() reescrito no modelo grade mensal")

# Garantir que renderCalendario é chamado ao abrir
OLD_CAL_CALL = "    if (socialMain) socialMain.style.display = '';\n    renderCalendario();"
assert OLD_CAL_CALL in html, "renderCalendario call not found"
print("✓ chamada renderCalendario() já existe no selectPlatform")

# Salvar
bad = [c for c in html if 0xD800 <= ord(c) <= 0xDFFF]
if bad:
    html = ''.join(c for c in html if not (0xD800 <= ord(c) <= 0xDFFF))
    print(f"✓ {len(bad)} surrogates removidos")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("\n✓ index.html salvo!")
print("  Calendário: grade 7 colunas, pílulas rosa (IG) e azul (FB), hoje destacado")
