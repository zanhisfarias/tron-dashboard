# fix_cal_colors.py — Calendário com cores por produto/quadro
import re, sys

FILE = r'C:\Users\Marketing\Desktop\Dashboard\index.html'

with open(FILE, 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# ─── 1. ATUALIZAR LEGENDA do cabeçalho do calendário ───────────────────────
OLD_LEGEND = '''    <!-- Legenda -->
    <div class="flex gap-3 items-center">
      <span class="flex items-center gap-1 text-[11px] font-semibold" style="color:#F9A8D4">
        <span class="inline-block w-2 h-2 rounded-full" style="background:#dd2a7b"></span>Instagram
      </span>
      <span class="flex items-center gap-1 text-[11px] font-semibold" style="color:#7DD3FC">
        <span class="inline-block w-2 h-2 rounded-full" style="background:#38BDF8"></span>Facebook
      </span>
    </div>'''

NEW_LEGEND = '''    <!-- Legenda por produto -->
    <div class="flex flex-wrap gap-2 items-center">
      <span class="flex items-center gap-1 text-[10px] font-semibold" style="color:#67E8F9"><span class="inline-block w-2 h-2 rounded-full" style="background:#06B6D4"></span>TGC</span>
      <span class="flex items-center gap-1 text-[10px] font-semibold" style="color:#F9A8D4"><span class="inline-block w-2 h-2 rounded-full" style="background:#EC4899"></span>DP</span>
      <span class="flex items-center gap-1 text-[10px] font-semibold" style="color:#C4B5FD"><span class="inline-block w-2 h-2 rounded-full" style="background:#A855F7"></span>Box</span>
      <span class="flex items-center gap-1 text-[10px] font-semibold" style="color:#FCA5A5"><span class="inline-block w-2 h-2 rounded-full" style="background:#EF4444"></span>Ordix</span>
      <span class="flex items-center gap-1 text-[10px] font-semibold" style="color:#86EFAC"><span class="inline-block w-2 h-2 rounded-full" style="background:#22C55E"></span>Laris</span>
      <span class="flex items-center gap-1 text-[10px] font-semibold" style="color:#FDE68A"><span class="inline-block w-2 h-2 rounded-full" style="background:#F59E0B"></span>QIAE</span>
      <span class="flex items-center gap-1 text-[10px] font-semibold" style="color:#FDA4AF"><span class="inline-block w-2 h-2 rounded-full" style="background:#F43F5E"></span>Editorial</span>
    </div>'''

if OLD_LEGEND in html:
    html = html.replace(OLD_LEGEND, NEW_LEGEND)
    print('✓ Legenda atualizada com 7 produtos')
else:
    print('⚠ Legenda não encontrada — verificar âncora')

# ─── 2. SUBSTITUIR renderCalendario() ──────────────────────────────────────
OLD_CAL_START = '// ═══════════════════════════════════════════════════════\n// CALENDÁRIO EDITORIAL — modelo grade mensal\n// ═══════════════════════════════════════════════════════\nfunction renderCalendario() {'
OLD_CAL_END   = '\n}\n\n// ═══════════════════════════════════════════════════════\n// CRM — Nectar Leadboard'

idx_start = html.find(OLD_CAL_START)
idx_end   = html.find(OLD_CAL_END, idx_start)

if idx_start == -1 or idx_end == -1:
    print('✗ Âncoras de renderCalendario não encontradas')
    sys.exit(1)

NEW_CAL = r'''// ═══════════════════════════════════════════════════════
// CALENDÁRIO EDITORIAL — cores por produto/quadro
// ═══════════════════════════════════════════════════════
function renderCalendario() {
  var igPosts = (typeof ORGANIC_DATA !== 'undefined' && ORGANIC_DATA.ig) ? ORGANIC_DATA.ig.posts || [] : [];
  var fbPosts = (typeof ORGANIC_DATA !== 'undefined' && ORGANIC_DATA.fb) ? ORGANIC_DATA.fb.posts || [] : [];

  // ── Paleta por produto ──────────────────────────────
  // [bg, fg, dot]
  var PRODUTO_COLORS = {
    TGC:      ['rgba(6,182,212,0.13)',   '#67E8F9', '#06B6D4'],
    DP:       ['rgba(236,72,153,0.13)',  '#F9A8D4', '#EC4899'],
    Box:      ['rgba(168,85,247,0.13)',  '#C4B5FD', '#A855F7'],
    Ordix:    ['rgba(239,68,68,0.13)',   '#FCA5A5', '#EF4444'],
    Laris:    ['rgba(34,197,94,0.13)',   '#86EFAC', '#22C55E'],
    QIAE:     ['rgba(245,158,11,0.13)',  '#FDE68A', '#F59E0B'],
    Editorial:['rgba(244,63,94,0.13)',   '#FDA4AF', '#F43F5E']
  };

  // ── Detectar produto pela caption ──────────────────
  function detectProduto(caption) {
    var c = (caption || '').toLowerCase();
    if (/\btgc\b|gestão\s+cont|contab|mei|abertura.*empresa|empresa.*abertura|fiscal|imposto|tribut|nota fiscal/.test(c)) return 'TGC';
    if (/\bdp\b|departamento\s+pessoal|folha|férias|rescis|holerite|fgts|pró-labore|pro-labore|admissão|demissão|clt|esocial|inss|salário.*dif|dif.*salário/.test(c)) return 'DP';
    if (/\bbox\b/.test(c)) return 'Box';
    if (/\bordix\b/.test(c)) return 'Ordix';
    if (/\blaris\b/.test(c)) return 'Laris';
    if (/\bqiae\b|\bia\b|inteligência\s+artif|automação|chatgpt|machine\s+learning/.test(c)) return 'QIAE';
    return 'Editorial';
  }

  // ── Mapear posts por dia (maio = month 4) ──────────
  var byDay = {};
  igPosts.forEach(function(p) {
    var d = new Date(p.timestamp);
    if (d.getMonth() !== 4) return;
    var day = d.getDate();
    if (!byDay[day]) byDay[day] = [];
    var caption = (p.caption || '').replace(/\n/g,' ').trim();
    var title   = caption.substring(0, 36) || ('Post IG');
    var produto = detectProduto(caption);
    byDay[day].push({ title: title, url: p.url||'', produto: produto });
  });
  fbPosts.forEach(function(p) {
    var d = new Date(p.timestamp);
    if (d.getMonth() !== 4) return;
    var day = d.getDate();
    if (!byDay[day]) byDay[day] = [];
    var caption = (p.message || '').replace(/\n/g,' ').trim();
    var title   = caption.substring(0, 36) || 'Post Facebook';
    var produto = detectProduto(caption);
    byDay[day].push({ title: title, url: '', produto: produto });
  });

  // ── Construir grade ─────────────────────────────────
  var grid = document.getElementById('calGrid');
  if (!grid) return;

  // maio 2026: dia 1 = quinta-feira (col 4, 0=DOM)
  var firstDay  = 4;
  var totalDays = 31;
  var today     = (new Date().getMonth() === 4) ? new Date().getDate() : 21;

  var cells = '';

  // Dias de abril (overflow)
  [26,27,28,29,30].forEach(function(d) {
    cells += '<div class="p-1.5" style="min-height:90px;border-bottom:1px solid #2A2D3E">'
      + '<div class="text-[11px] font-semibold" style="color:#374151">' + d + '</div>'
      + '</div>';
  });

  // Dias de maio
  for (var d = 1; d <= totalDays; d++) {
    var ps       = byDay[d] || [];
    var isSun    = ((firstDay + d - 1) % 7 === 0);
    var isSat    = ((firstDay + d - 1) % 7 === 6);
    var isToday  = (d === today);
    var numColor = isToday ? '#EC4899' : (isSun||isSat ? '#F87171' : '#D1D5DB');
    var cellStyle = 'min-height:90px;border-bottom:1px solid #2A2D3E;'
      + (isToday ? 'background:rgba(236,72,153,0.06);outline:1.5px solid #EC4899;outline-offset:-1px' : '');

    cells += '<div class="p-1.5" style="' + cellStyle + '">'
      + '<div class="text-[12px] font-bold mb-1.5" style="color:' + numColor + '">' + d + '</div>';

    ps.forEach(function(p) {
      var pal  = PRODUTO_COLORS[p.produto] || PRODUTO_COLORS.Editorial;
      var bg   = pal[0], fg = pal[1], dot = pal[2];
      var inner = p.url
        ? '<a href="' + p.url + '" target="_blank" rel="noopener" style="color:' + fg + ';text-decoration:none">' + p.title + '</a>'
        : p.title;
      cells += '<div class="flex items-start gap-1 mb-1 px-1.5 py-[3px] rounded" style="background:' + bg + '">'
        + '<span class="mt-[3px] flex-shrink-0 w-[6px] h-[6px] rounded-full" style="background:' + dot + '"></span>'
        + '<span class="text-[10px] font-semibold leading-tight" style="color:' + fg + ';word-break:break-word">' + inner + '</span>'
        + '</div>';
    });

    cells += '</div>';
  }

  // Dias de junho (overflow)
  var lastCol   = (firstDay + totalDays - 1) % 7;
  var remaining = lastCol === 6 ? 0 : (6 - lastCol);
  for (var j = 1; j <= remaining; j++) {
    cells += '<div class="p-1.5" style="min-height:90px;border-bottom:1px solid #2A2D3E">'
      + '<div class="text-[11px] font-semibold" style="color:#374151">' + j + '</div>'
      + '</div>';
  }

  grid.innerHTML = cells;
}'''

html = html[:idx_start] + NEW_CAL + html[idx_end:]
print('✓ renderCalendario() substituído com paleta por produto')

# ─── 3. SALVAR ─────────────────────────────────────────────────────────────
with open(FILE, 'w', encoding='utf-8', errors='replace') as f:
    f.write(html)

print('✓ index.html salvo!')
print('  Calendário: 7 cores por produto (TGC/DP/Box/Ordix/Laris/QIAE/Editorial)')
