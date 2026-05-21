"""Fix renderOrgPosts, add Insights/Editorial sections and JS."""
import sys, json, re

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML = r"C:\Users\Marketing\Desktop\Dashboard\index.html"

with open(HTML, encoding="utf-8", errors="surrogateescape") as f:
    lines = f.readlines()

# ── 1. renderOrgPosts tbody block (lines 3336-3352, 1-indexed → 3335-3351 0-indexed) ──
new_tbody = """\
  tbody.innerHTML = posts.map(function(p) {
    var cap = (p.caption || p.message || '').substring(0, 70) + '\u2026';
    var dt = new Date(p.timestamp);
    var dtStr = dt.getDate() + '/' + (dt.getMonth()+1);
    var eng = (p.likes||0) + (p.comments||0) + (p.shares||0);
    var rawType = p.type || 'POST';
    var typeLabel = rawType === 'CAROUSEL_ALBUM' ? 'CARROSSEL' : rawType === 'IMAGE' ? 'FOTO' : rawType === 'VIDEO' ? 'V\u00cdDEO' : rawType;
    var typeColor = typeLabel === 'FOTO' ? '#6366F1' : typeLabel === 'V\u00cdDEO' ? '#10B981' : typeLabel === 'CARROSSEL' ? '#F59E0B' : typeLabel === 'REEL' ? '#dd2a7b' : '#6B7280';
    var thumbCell = '';
    if (p.thumb) {
      var href = p.url ? ' href="' + p.url + '" target="_blank"' : '';
      thumbCell = '<td style="padding:6px 5px"><a' + href + ' style="display:block;width:44px;height:44px;border-radius:6px;overflow:hidden;border:1px solid #3A3D52"><img src="' + p.thumb + '" style="width:100%;height:100%;object-fit:cover" loading="lazy"></a></td>';
    } else {
      var icon = (typeLabel === 'V\u00cdDEO' || typeLabel === 'REEL') ? '\ud83c\udfa4' : typeLabel === 'CARROSSEL' ? '\ud83d\uddc2\ufe0f' : '\ud83d\udcf7';
      thumbCell = '<td style="padding:6px 5px"><div style="width:44px;height:44px;border-radius:6px;background:#2A2D3E;display:flex;align-items:center;justify-content:center;font-size:18px;border:1px solid #3A3D52">' + icon + '</div></td>';
    }
    return '<tr>'
      + thumbCell
      + '<td style="max-width:200px"><div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#E5E7EB;font-size:11px">' + cap + '</div>'
      + '<span class="text-[8px] font-bold px-1.5 py-0.5 rounded mt-1 inline-block" style="background:' + typeColor + '22;color:' + typeColor + '">' + typeLabel + '</span></td>'
      + '<td class="text-center text-white font-semibold">' + (p.likes||0) + '</td>'
      + '<td class="text-center text-white font-semibold">' + (p.comments||0) + '</td>'
      + '<td class="text-center font-bold" style="color:' + c + '">' + eng + '</td>'
      + '<td class="text-center" style="color:#9CA3AF;font-size:10px">' + dtStr + '</td>'
      + '</tr>';
  }).join('');
}

"""

# Find the start line (tbody.innerHTML = posts.map)
start_idx = None
end_idx   = None
for i, l in enumerate(lines):
    if "tbody.innerHTML = posts.map" in l and start_idx is None:
        start_idx = i
    if start_idx and "}).join('');" in l:
        # next line should be closing brace of renderOrgPosts
        if i > start_idx + 5:
            end_idx = i + 2  # include closing }
            break

print(f"Replacing lines {start_idx}–{end_idx}")
lines[start_idx:end_idx] = [new_tbody]

# ── 2. Add Insights + Editorial HTML before <!-- Placeholder para plataformas pendentes --> ──
html = "".join(lines)

OLD_PENDING = "  <!-- Placeholder para plataformas pendentes -->\n  <div class=\"grid grid-cols-1 md:grid-cols-3 gap-3\" id=\"orgPendingRow\">"

NEW_SECTIONS = """\
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

  <!-- Placeholder para plataformas pendentes -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3" id="orgPendingRow">"""

assert OLD_PENDING in html, "Pending anchor not found"
html = html.replace(OLD_PENDING, NEW_SECTIONS, 1)
print("✓ Seções Insights + Editorial inseridas no HTML")

# ── 3. JS: renderOrgInsights + renderOrgEditorial ──
JS_ANCHOR = "// Gráfico de evolução Google Ads (dados de exemplo)"

INSIGHTS_JS = r"""
// ══════════════════════════════════════════════════════════
// ORGÂNICO — Insights automáticos + Linha Editorial
// ══════════════════════════════════════════════════════════

function renderOrgInsights() {
  var el = document.getElementById('orgInsightsList');
  if (!el) return;
  var d = _activeOrgPlat === 'instagram' ? ORGANIC_DATA.ig : ORGANIC_DATA.fb;
  var posts = d.posts || [];
  if (!posts.length) { el.innerHTML = '<div class="text-sm text-center py-4" style="color:#6B7280">Sem dados suficientes</div>'; return; }

  function insightCard(icon, title, body, type) {
    var colors = { good:'#10B981', warn:'#F59E0B', tip:'#6366F1', info:'#dd2a7b' };
    var bgs    = { good:'rgba(16,185,129,0.08)', warn:'rgba(245,158,11,0.08)', tip:'rgba(99,102,241,0.08)', info:'rgba(221,42,123,0.08)' };
    var col = colors[type] || colors.info;
    var bg  = bgs[type]   || bgs.info;
    return '<div class="p-3 rounded-xl" style="background:' + bg + ';border:1px solid ' + col + '22">'
      + '<div class="flex items-center gap-2 mb-1.5"><span style="font-size:16px">' + icon + '</span>'
      + '<div class="text-[10px] font-bold" style="color:' + col + '">' + title + '</div></div>'
      + '<div class="text-[11px] leading-relaxed" style="color:#E5E7EB">' + body + '</div></div>';
  }

  // Análise por formato
  var byType = {};
  posts.forEach(function(p) {
    var t = (p.type||'POST').replace('CAROUSEL_ALBUM','CARROSSEL').replace('IMAGE','FOTO').replace('VIDEO','VÍDEO');
    if (!byType[t]) byType[t] = { count:0, eng:0 };
    byType[t].count++;
    byType[t].eng += (p.likes||0) + (p.comments||0)*2;
  });
  var bestType = null, bestEng = 0;
  Object.keys(byType).forEach(function(t) {
    var avg = byType[t].eng / byType[t].count;
    if (avg > bestEng) { bestEng = avg; bestType = t; }
  });

  // Melhor horário
  var byHour = {};
  posts.forEach(function(p) {
    var h = new Date(p.timestamp).getHours();
    if (!byHour[h]) byHour[h] = { count:0, eng:0 };
    byHour[h].count++;
    byHour[h].eng += (p.likes||0) + (p.comments||0)*2;
  });
  var bestHour = null, bestHourEng = 0;
  Object.keys(byHour).forEach(function(h) {
    var avg = byHour[h].eng / byHour[h].count;
    if (avg > bestHourEng) { bestHourEng = avg; bestHour = parseInt(h); }
  });

  // Taxa engajamento
  var totalLikes    = posts.reduce(function(s,p){ return s + (p.likes||0); },0);
  var totalComments = posts.reduce(function(s,p){ return s + (p.comments||0); },0);
  var engRate = d.followers ? ((totalLikes+totalComments)/posts.length/d.followers*100) : 0;

  // Posts sem comentário
  var zeroComments = posts.filter(function(p){ return (p.comments||0) === 0; }).length;
  var zeroPct = Math.round(zeroComments/posts.length*100);

  // Melhor post
  var topPost = posts.slice().sort(function(a,b){ return ((b.likes||0)+(b.comments||0)*2)-((a.likes||0)+(a.comments||0)*2); })[0];

  // Frequência
  var daysSpan = posts.length > 1
    ? Math.round(Math.abs(new Date(posts[0].timestamp)-new Date(posts[posts.length-1].timestamp))/(1000*60*60*24)) : 0;
  var postsPerWeek = daysSpan > 0 ? (posts.length/daysSpan*7).toFixed(1) : posts.length;

  var insights = [];

  if (bestType) {
    var tIcons = { REEL:'🎬', VÍDEO:'🎬', CARROSSEL:'🗂️', FOTO:'📷', POST:'📄' };
    insights.push(insightCard(tIcons[bestType]||'📊', 'Formato campeão: ' + bestType,
      'Posts do tipo <strong>' + bestType + '</strong> geram em média <strong>' + Math.round(bestEng) + '</strong> interações. Priorize esse formato na próxima semana.', 'good'));
  }
  if (bestHour !== null) {
    var period = bestHour < 12 ? 'manhã' : bestHour < 18 ? 'tarde' : 'noite';
    insights.push(insightCard('🕐', 'Melhor horário: ' + bestHour + 'h (' + period + ')',
      'Seus posts com maior engajamento foram publicados às <strong>' + bestHour + 'h</strong>. Teste consistentemente nesse horário.', 'tip'));
  }
  var engMsg = engRate >= 3
    ? 'Taxa de <strong>' + engRate.toFixed(2) + '%</strong> — acima da média do setor (1–3%). Conteúdo gerando conexão genuína.'
    : 'Taxa de <strong>' + engRate.toFixed(2) + '%</strong> — abaixo de 3%. Use CTAs claros: "Comente qual desafio você enfrenta 👇"';
  insights.push(insightCard('❤️', 'Taxa de Engajamento', engMsg, engRate >= 3 ? 'good' : 'warn'));

  if (zeroPct > 50)
    insights.push(insightCard('💬', zeroPct + '% dos posts sem comentários',
      'Adicione <strong>perguntas abertas</strong> no caption: "Você já automatizou sua conciliação bancária? Conta pra gente 👇"', 'warn'));

  if (topPost) {
    var topCap = (topPost.caption||topPost.message||'').substring(0,55) + '…';
    insights.push(insightCard('🏆', 'Post mais engajado',
      '"' + topCap + '" com <strong>' + (topPost.likes||0) + ' curtidas</strong> e <strong>' + (topPost.comments||0) + ' comentários</strong>. Replique o formato.', 'info'));
  }

  insights.push(insightCard('📅', 'Frequência: ' + postsPerWeek + ' posts/semana',
    postsPerWeek >= 4
      ? 'Ótima consistência. O algoritmo favorece perfis com publicações regulares — mantenha o ritmo.'
      : 'O ideal é <strong>4–7 posts/semana</strong>. Crie um banco de conteúdo com 2 semanas de antecedência.', postsPerWeek >= 4 ? 'good' : 'warn'));

  el.innerHTML = insights.join('');
}

function renderOrgEditorial() {
  var el = document.getElementById('orgEditorialContent');
  if (!el) return;

  var roteiros = [
    { formato:'REEL / Vídeo Curto', icon:'🎬', color:'#10B981', tempo:'15–30s', objetivo:'Alcance e novos seguidores',
      estrutura:[
        '🎯 <b>Hook (0–3s):</b> Afirmação impactante. Ex: "Você está perdendo dinheiro todo mês sem saber."',
        '📌 <b>Problema (3–8s):</b> A dor do público. Ex: "Fechar o mês sem saber se lucrou é mais comum do que parece."',
        '💡 <b>Solução (8–22s):</b> Produto em ação. Ex: "Com o TGC você vê o resultado em tempo real."',
        '📣 <b>CTA (22–30s):</b> "Arrasta pra cima e conheça. Link na bio."'
      ],
      dicas:['Texto na tela nos primeiros 3s','Música tendência aumenta alcance em até 3x','Grave em vertical 9:16']
    },
    { formato:'Carrossel Educativo', icon:'🗂️', color:'#F59E0B', tempo:'5–10 slides', objetivo:'Salvamentos e compartilhamentos',
      estrutura:[
        '📌 <b>Slide 1 (Capa):</b> Título impactante. Ex: "5 erros que todo contador comete no fechamento."',
        '📋 <b>Slides 2–8:</b> Um erro/dica por slide. Texto curto, visual limpo.',
        '✅ <b>Slide penúltimo:</b> Resumo ou checklist.',
        '📣 <b>Slide final:</b> "Salva esse post 💾 | Comenta qual erro você já cometeu 👇"'
      ],
      dicas:['Caption curto — conteúdo está no carrossel','Tema: reforma tributária, eSocial, IR','Capa com curiosidade para incentivar o arraste']
    },
    { formato:'Post de Autoridade', icon:'📷', color:'#6366F1', tempo:'1 imagem + caption longo', objetivo:'Conexão e novos seguidores',
      estrutura:[
        '🔎 <b>Primeira linha:</b> Gancho. Ex: "O contador que me disse isso mudou meu negócio."',
        '📖 <b>Desenvolvimento:</b> História, dado ou insight real. 150–300 palavras.',
        '💬 <b>Encerramento:</b> "Você concorda? Comenta sua experiência 👇"',
        '🏷️ <b>Hashtags:</b> 5–10 específicas do nicho contábil/agro'
      ],
      dicas:['Foto real da equipe performa melhor que arte','Inclua dado ou estatística','Repost nos Stories com enquete']
    },
    { formato:'Stories Interativo', icon:'⭕', color:'#dd2a7b', tempo:'3–5 frames', objetivo:'Engajamento e retenção',
      estrutura:[
        '❓ <b>Frame 1:</b> Enquete. Ex: "Você usa integração bancária? Sim / Não"',
        '💡 <b>Frame 2:</b> Dado revelador. Ex: "85% ainda fazem isso manualmente..."',
        '🎯 <b>Frame 3:</b> Solução + CTA. Ex: "O TGC automatiza em 1 clique. Arrasta 👉"',
        '🔗 <b>Frame 4:</b> Link direto ou "Chama no Direct"'
      ],
      dicas:['Stories todos os dias','Enquete e caixinha aumentam alcance orgânico','Reposte posts do feed sempre']
    }
  ];

  el.innerHTML = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">'
    + roteiros.map(function(r) {
      return '<div class="rounded-xl p-4" style="background:#1A1D27;border:1px solid #3A3D52">'
        + '<div class="flex items-center gap-2 mb-3">'
          + '<span style="font-size:20px">' + r.icon + '</span>'
          + '<div><div class="text-[11px] font-bold text-white">' + r.formato + '</div>'
          + '<div class="text-[9px] font-semibold mt-0.5" style="color:' + r.color + '">' + r.tempo + ' · ' + r.objetivo + '</div></div>'
        + '</div>'
        + '<div class="space-y-1.5 mb-3">'
          + r.estrutura.map(function(s){ return '<div class="text-[10px] leading-relaxed" style="color:#D1D5DB">' + s + '</div>'; }).join('')
        + '</div>'
        + '<div class="border-t pt-2" style="border-color:#2A2D3E">'
          + '<div class="text-[8px] font-bold uppercase tracking-widest mb-1.5" style="color:' + r.color + '">Dicas rápidas</div>'
          + '<div class="flex flex-wrap gap-1">'
            + r.dicas.map(function(d){ return '<span class="text-[9px] px-2 py-0.5 rounded-full" style="background:' + r.color + '18;color:' + r.color + '">' + d + '</span>'; }).join('')
          + '</div></div></div>';
    }).join('') + '</div>';
}

"""

assert JS_ANCHOR in html, "JS anchor not found"
html = html.replace(JS_ANCHOR, INSIGHTS_JS + "\n" + JS_ANCHOR, 1)
print("✓ JS renderOrgInsights() + renderOrgEditorial() adicionado")

# ── 4. Chamar em renderOrganicoDashboard + selectOrgPlat ──
OLD_RENDER = "function renderOrganicoDashboard() {\n  renderOrgKpis();\n  renderOrgPosts();\n  renderOrgChart();\n}"
NEW_RENDER = "function renderOrganicoDashboard() {\n  renderOrgKpis();\n  renderOrgPosts();\n  renderOrgChart();\n  renderOrgInsights();\n  renderOrgEditorial();\n}"
assert OLD_RENDER in html
html = html.replace(OLD_RENDER, NEW_RENDER, 1)

OLD_SEL = "  renderOrgKpis();\n  renderOrgPosts();\n  renderOrgChart();\n}"
NEW_SEL = "  renderOrgKpis();\n  renderOrgPosts();\n  renderOrgChart();\n  renderOrgInsights();\n  renderOrgEditorial();\n}"
idx = html.find(NEW_RENDER)
second = html.find(OLD_SEL, idx + len(NEW_RENDER))
if second != -1:
    html = html[:second] + NEW_SEL + html[second+len(OLD_SEL):]
    print("✓ selectOrgPlat() atualizado")

with open(HTML, "w", encoding="utf-8", errors="surrogateescape") as f:
    f.write(html)
print("\n✓ index.html salvo!")
print("  → Thumbnails reais nas linhas da tabela")
print("  → 6 Insights automáticos de performance")
print("  → 4 roteiros de Linha Editorial")
