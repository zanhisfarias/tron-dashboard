"""
patch_organico2.py
  1. Atualiza ORGANIC_DATA.ig.posts com thumbs reais
  2. Atualiza tabela de posts para mostrar thumbnail
  3. Adiciona seção Insights (análise automática dos dados)
  4. Adiciona seção Linha Editorial (roteiros e dicas)
"""
import sys, json, re

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML = r"C:\Users\Marketing\Desktop\Dashboard\index.html"

with open(HTML, encoding="utf-8") as f:
    html = f.read()

# ─────────────────────────────────────────────────────────
# 1. Atualizar ORGANIC_DATA com posts frescos (com thumbs)
# ─────────────────────────────────────────────────────────
with open(r"C:\Users\Marketing\Desktop\Dashboard\ig_posts_fresh.json", encoding="utf-8") as f:
    ig_posts = json.load(f)

# Pega o ORGANIC_DATA atual do bloco DATA e atualiza os posts IG
pattern = r'var ORGANIC_DATA = (\{.*?\});'
match = re.search(pattern, html, re.DOTALL)
if match:
    current_data = json.loads(match.group(1))
    current_data["ig"]["posts"] = ig_posts
    new_organic_js = "var ORGANIC_DATA = " + json.dumps(current_data, ensure_ascii=False, separators=(',', ':')) + ";"
    html = html[:match.start()] + new_organic_js + html[match.end():]
    print(f"✓ ORGANIC_DATA atualizado com {len(ig_posts)} posts com thumbnails")
else:
    print("! ORGANIC_DATA não encontrado via regex")

# ─────────────────────────────────────────────────────────
# 2. Tabela de posts — coluna Tipo vira Thumbnail + badge
# ─────────────────────────────────────────────────────────
OLD_TABLE_HEADER = """        <table class="tbl" id="orgPostsTable">
        <thead>
          <tr>
            <th class="text-left" style="min-width:180px">Conteúdo</th>
            <th>Tipo</th>
            <th>Curtidas</th>
            <th>Comentários</th>
            <th>Engaj.</th>
            <th>Data</th>
          </tr>
        </thead>"""
NEW_TABLE_HEADER = """        <table class="tbl" id="orgPostsTable">
        <thead>
          <tr>
            <th style="width:52px">Preview</th>
            <th class="text-left" style="min-width:160px">Conteúdo</th>
            <th>Curtidas</th>
            <th>Comentários</th>
            <th>Engaj.</th>
            <th>Data</th>
          </tr>
        </thead>"""
assert OLD_TABLE_HEADER in html
html = html.replace(OLD_TABLE_HEADER, NEW_TABLE_HEADER, 1)
print("✓ Cabeçalho da tabela atualizado")

# ─────────────────────────────────────────────────────────
# 3. renderOrgPosts() — adicionar thumbnail na linha
# ─────────────────────────────────────────────────────────
OLD_RENDER_POSTS = """  tbody.innerHTML = posts.map(function(p) {
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
  }).join('');"""

NEW_RENDER_POSTS = """  tbody.innerHTML = posts.map(function(p) {
    var cap = (p.caption || p.message || '').substring(0, 70) + '…';
    var dt = new Date(p.timestamp);
    var dtStr = dt.getDate() + '/' + (dt.getMonth()+1);
    var eng = (p.likes||0) + (p.comments||0) + (p.shares||0);
    var typeLabel = (p.type || 'POST').replace('CAROUSEL_ALBUM','CARROSSEL').replace('IMAGE','FOTO').replace('VIDEO','VÍDEO');
    var typeColor = { FOTO:'#6366F1', VÍDEO:'#10B981', CARROSSEL:'#F59E0B', REEL:'#dd2a7b', POST:'#6B7280' }[typeLabel] || '#6B7280';
    var thumbHtml = '';
    if (p.thumb) {
      var postUrl = p.url ? 'href="' + p.url + '" target="_blank"' : '';
      thumbHtml = '<a ' + postUrl + ' style="display:block;width:44px;height:44px;border-radius:6px;overflow:hidden;flex-shrink:0;border:1px solid #3A3D52">'
        + '<img src="' + p.thumb + '" style="width:100%;height:100%;object-fit:cover" loading="lazy" onerror="this.parentNode.innerHTML=\'<div style=\\\"width:44px;height:44px;border-radius:6px;background:#2A2D3E;display:flex;align-items:center;justify-content:center;font-size:18px\\\">📷</div>\'">'
        + '</a>';
    } else {
      thumbHtml = '<div style="width:44px;height:44px;border-radius:6px;background:#2A2D3E;display:flex;align-items:center;justify-content:center;font-size:18px;border:1px solid #3A3D52">'
        + (typeLabel === 'VÍDEO' || typeLabel === 'REEL' ? '🎬' : typeLabel === 'CARROSSEL' ? '🗂️' : '📷') + '</div>';
    }
    return '<tr>'
      + '<td style="padding:6px 5px"><div style="display:flex;justify-content:center">' + thumbHtml + '</div></td>'
      + '<td style="max-width:200px">'
        + '<div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#E5E7EB;font-size:11px">' + cap + '</div>'
        + '<span class="text-[8px] font-bold px-1.5 py-0.5 rounded mt-1 inline-block" style="background:' + typeColor + '22;color:' + typeColor + '">' + typeLabel + '</span>'
      + '</td>'
      + '<td class="text-center text-white font-semibold">' + (p.likes||0) + '</td>'
      + '<td class="text-center text-white font-semibold">' + (p.comments||0) + '</td>'
      + '<td class="text-center font-bold" style="color:' + c + '">' + eng + '</td>'
      + '<td class="text-center" style="color:#9CA3AF;font-size:10px">' + dtStr + '</td>'
      + '</tr>';
  }).join('');"""

assert OLD_RENDER_POSTS in html
html = html.replace(OLD_RENDER_POSTS, NEW_RENDER_POSTS, 1)
print("✓ renderOrgPosts() com thumbnails")

# ─────────────────────────────────────────────────────────
# 4. HTML — adicionar seções Insights + Editorial após tabela de posts
# ─────────────────────────────────────────────────────────
OLD_PENDING = """  <!-- Placeholder para plataformas pendentes -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3" id="orgPendingRow">"""

NEW_SECTIONS = """  <!-- Insights de Performance -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52" id="orgInsightsCard">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style="background:rgba(221,42,123,0.15)">
        <span style="font-size:14px">💡</span>
      </div>
      <div class="text-[9px] font-bold uppercase tracking-widest" style="color:#dd2a7b">Insights de Performance</div>
    </div>
    <div id="orgInsightsList" class="grid grid-cols-1 md:grid-cols-2 gap-3"></div>
  </div>

  <!-- Linha Editorial & Roteiros -->
  <div class="card p-4 md:p-5" style="background:#2A2D3E;border-color:#3A3D52" id="orgEditorialCard">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style="background:rgba(99,102,241,0.15)">
        <span style="font-size:14px">✍️</span>
      </div>
      <div class="text-[9px] font-bold uppercase tracking-widest" style="color:#6366F1">Linha Editorial & Roteiros</div>
    </div>
    <div id="orgEditorialContent"></div>
  </div>

  <!-- Placeholder para plataformas pendentes -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3" id="orgPendingRow">"""

assert OLD_PENDING in html
html = html.replace(OLD_PENDING, NEW_SECTIONS, 1)
print("✓ Seções Insights + Editorial adicionadas ao HTML")

# ─────────────────────────────────────────────────────────
# 5. JS — renderOrgInsights() + renderOrgEditorial()
#    Inserir antes do // Gráfico de evolução Google Ads
# ─────────────────────────────────────────────────────────
JS_ANCHOR = "// Gráfico de evolução Google Ads (dados de exemplo)"

INSIGHTS_JS = r"""
// ══════════════════════════════════════════════════════
// ORGÂNICO — Insights e Linha Editorial
// ══════════════════════════════════════════════════════

function renderOrgInsights() {
  var el = document.getElementById('orgInsightsList');
  if (!el) return;
  var d = _activeOrgPlat === 'instagram' ? ORGANIC_DATA.ig : ORGANIC_DATA.fb;
  var c = _activeOrgPlat === 'instagram' ? '#dd2a7b' : '#1877F2';
  var posts = d.posts || [];
  if (!posts.length) { el.innerHTML = '<div class="text-sm text-center py-4" style="color:#6B7280">Sem dados suficientes</div>'; return; }

  // --- Análise por formato ---
  var byType = {};
  posts.forEach(function(p) {
    var t = (p.type||'POST').replace('CAROUSEL_ALBUM','CARROSSEL').replace('IMAGE','FOTO').replace('VIDEO','VÍDEO');
    if (!byType[t]) byType[t] = { count:0, likes:0, comments:0, shares:0 };
    byType[t].count++;
    byType[t].likes    += p.likes    || 0;
    byType[t].comments += p.comments || 0;
    byType[t].shares   += p.shares   || 0;
  });
  var bestType = null, bestEng = 0;
  Object.keys(byType).forEach(function(t) {
    var avg = (byType[t].likes + byType[t].comments * 2) / byType[t].count;
    if (avg > bestEng) { bestEng = avg; bestType = t; }
  });

  // --- Análise de horário ---
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

  // --- Taxa de engajamento ---
  var totalLikes    = posts.reduce(function(s,p){ return s + (p.likes||0); }, 0);
  var totalComments = posts.reduce(function(s,p){ return s + (p.comments||0); }, 0);
  var avgEng = posts.length ? Math.round((totalLikes + totalComments) / posts.length) : 0;
  var engRate = d.followers ? ((totalLikes + totalComments) / posts.length / d.followers * 100) : 0;

  // --- Posts com comentários zero ---
  var zeroComments = posts.filter(function(p){ return (p.comments||0) === 0; }).length;
  var zeroPct = Math.round(zeroComments / posts.length * 100);

  // --- Melhor post ---
  var topPost = posts.slice().sort(function(a,b){ return ((b.likes||0)+(b.comments||0)*2)-((a.likes||0)+(a.comments||0)*2); })[0];

  // --- Build insights ---
  function insightCard(icon, title, body, type) {
    var colors = { good:'#10B981', warn:'#F59E0B', tip:'#6366F1', info:'#dd2a7b' };
    var bgs    = { good:'rgba(16,185,129,0.08)', warn:'rgba(245,158,11,0.08)', tip:'rgba(99,102,241,0.08)', info:'rgba(221,42,123,0.08)' };
    var col = colors[type] || colors.info;
    var bg  = bgs[type]   || bgs.info;
    return '<div class="p-3 rounded-xl" style="background:' + bg + ';border:1px solid ' + col + '22">'
      + '<div class="flex items-center gap-2 mb-1.5">'
        + '<span style="font-size:16px">' + icon + '</span>'
        + '<div class="text-[10px] font-bold" style="color:' + col + '">' + title + '</div>'
      + '</div>'
      + '<div class="text-[11px] leading-relaxed" style="color:#E5E7EB">' + body + '</div>'
    + '</div>';
  }

  var insights = [];

  // Formato campeão
  if (bestType) {
    var typeIcons = { REEL:'🎬', VÍDEO:'🎬', CARROSSEL:'🗂️', FOTO:'📷', POST:'📄' };
    insights.push(insightCard(
      typeIcons[bestType] || '📊',
      'Formato com maior engajamento: ' + bestType,
      'Posts do tipo <strong>' + bestType + '</strong> geram em média <strong>' + Math.round(bestEng) + '</strong> interações — priorize esse formato na próxima semana.',
      'good'
    ));
  }

  // Horário ideal
  if (bestHour !== null) {
    var period = bestHour < 12 ? 'manhã' : bestHour < 18 ? 'tarde' : 'noite';
    insights.push(insightCard(
      '🕐',
      'Melhor horário para postar: ' + bestHour + 'h',
      'A maioria dos seus posts com maior engajamento foram publicados às <strong>' + bestHour + 'h</strong> (' + period + '). Teste consistentemente nesse horário.',
      'tip'
    ));
  }

  // Taxa de engajamento
  var engStatus = engRate >= 3 ? 'good' : engRate >= 1 ? 'warn' : 'warn';
  var engMsg = engRate >= 3
    ? 'Taxa de <strong>' + engRate.toFixed(2) + '%</strong> — acima da média do setor (1–3%). Seu conteúdo está gerando conexão genuína.'
    : 'Taxa de <strong>' + engRate.toFixed(2) + '%</strong> — abaixo de 3%. Tente fazer perguntas diretas no caption e usar CTAs claros como "Comente abaixo qual desafio você enfrenta".';
  insights.push(insightCard('❤️', 'Taxa de Engajamento', engMsg, engStatus));

  // Posts sem comentários
  if (zeroPct > 50) {
    insights.push(insightCard(
      '💬',
      zeroPct + '% dos posts sem comentários',
      'A maioria dos posts não gerou conversa. Adicione <strong>perguntas abertas</strong> ao final de cada caption: "Você já usou integração bancária automática? Conta pra gente 👇"',
      'warn'
    ));
  }

  // Top post
  if (topPost) {
    var topCap = (topPost.caption || topPost.message || '').substring(0, 60) + '…';
    insights.push(insightCard(
      '🏆',
      'Post mais engajado do período',
      '"' + topCap + '" — <strong>' + (topPost.likes||0) + ' curtidas</strong> e <strong>' + (topPost.comments||0) + ' comentários</strong>. Analise o que funcionou e replique o formato.',
      'info'
    ));
  }

  // Frequência
  var daysSpan = posts.length > 1
    ? Math.round(Math.abs(new Date(posts[0].timestamp) - new Date(posts[posts.length-1].timestamp)) / (1000*60*60*24))
    : 0;
  var postsPerWeek = daysSpan > 0 ? (posts.length / daysSpan * 7).toFixed(1) : posts.length;
  var freqStatus = postsPerWeek >= 4 ? 'good' : 'warn';
  insights.push(insightCard(
    '📅',
    'Frequência de publicação: ' + postsPerWeek + ' posts/semana',
    postsPerWeek >= 4
      ? 'Frequência ótima. Mantenha a consistência — o algoritmo favorece perfis com publicações regulares.'
      : 'O ideal para crescimento orgânico é <strong>4–7 posts por semana</strong>. Considere criar um banco de conteúdo com 2 semanas de antecedência.',
    freqStatus
  ));

  el.innerHTML = insights.join('');
}

function renderOrgEditorial() {
  var el = document.getElementById('orgEditorialContent');
  if (!el) return;
  var c = _activeOrgPlat === 'instagram' ? '#dd2a7b' : '#1877F2';

  var roteiros = [
    {
      formato: 'REEL / Vídeo Curto',
      icon: '🎬',
      color: '#10B981',
      tempo: '15–30s',
      objetivo: 'Alcance e novos seguidores',
      estrutura: [
        '🎯 <b>Hook (0–3s):</b> Comece com uma afirmação impactante. Ex: "Você está perdendo dinheiro todo mês sem saber."',
        '📌 <b>Problema (3–8s):</b> Apresente a dor do público. Ex: "Fechar o mês sem saber se lucrou é mais comum do que parece."',
        '💡 <b>Solução (8–22s):</b> Mostre o produto/benefício em ação. Ex: "Com o TGC você vê o resultado em tempo real."',
        '📣 <b>CTA (22–30s):</b> "Arrasta pra cima e conheça. Link na bio."'
      ],
      dicas: ['Use texto na tela nos primeiros 3s', 'Música tendência aumenta alcance em até 3x', 'Grave em vertical (9:16)']
    },
    {
      formato: 'Carrossel Educativo',
      icon: '🗂️',
      color: '#F59E0B',
      tempo: '5–10 slides',
      objetivo: 'Salvamentos e compartilhamentos',
      estrutura: [
        '📌 <b>Slide 1 (Capa):</b> Título impactante. Ex: "5 erros que todo contador comete no fechamento."',
        '📋 <b>Slides 2–8:</b> Um erro/dica por slide. Texto curto, visual limpo.',
        '✅ <b>Slide penúltimo:</b> Resumo ou checklist rápida.',
        '📣 <b>Slide final:</b> CTA. Ex: "Salva esse post pra não esquecer 💾 | Comenta qual erro você já cometeu 👇"'
      ],
      dicas: ['Caption curto — o conteúdo está no carrossel', 'Cubra a primeira imagem com curiosidade para incentivar o arraste', 'Tema: reforma tributária, SPED, eSocial, IR']
    },
    {
      formato: 'Post de Autoridade (Imagem)',
      icon: '📷',
      color: '#6366F1',
      tempo: '1 imagem + caption longo',
      objetivo: 'Conexão e follow',
      estrutura: [
        '🔎 <b>Primeira linha do caption:</b> Gancho sem revelar tudo. Ex: "O contador que me disse isso mudou meu negócio."',
        '📖 <b>Desenvolvimento:</b> Conte uma história, dado ou insight real. 150–300 palavras.',
        '💬 <b>Pergunta de encerramento:</b> "Você concorda? Comenta sua experiência 👇"',
        '🏷️ <b>Hashtags:</b> 5–10 específicas do nicho contábil/agro'
      ],
      dicas: ['Use foto real da equipe ou produto — performa melhor que arte gráfica', 'Inclua dado ou estatística no caption', 'Repost nos Stories com enquete']
    },
    {
      formato: 'Stories Interativo',
      icon: '⭕',
      color: '#dd2a7b',
      tempo: '3–5 frames',
      objetivo: 'Engajamento e retenção de seguidores',
      estrutura: [
        '❓ <b>Frame 1:</b> Pergunta ou enquete. Ex: "Você usa integração bancária no seu escritório? Sim / Não"',
        '💡 <b>Frame 2:</b> Revelação + dado. Ex: "85% dos contadores ainda fazem isso manualmente..."',
        '🎯 <b>Frame 3:</b> Solução ou CTA. Ex: "O TGC automatiza em 1 clique. Arrasta pra ver 👉"',
        '🔗 <b>Frame 4 (opcional):</b> Link direto ou "Chama no Direct"'
      ],
      dicas: ['Stories todos os dias, mesmo que breve', 'Use enquete, quiz e caixinha de perguntas — aumentam o alcance orgânico', 'Reposte posts do feed nos Stories sempre']
    }
  ];

  el.innerHTML = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">'
    + roteiros.map(function(r) {
      return '<div class="rounded-xl p-4" style="background:#1A1D27;border:1px solid #3A3D52">'
        + '<div class="flex items-center gap-2 mb-3">'
          + '<span style="font-size:20px">' + r.icon + '</span>'
          + '<div>'
            + '<div class="text-[11px] font-bold text-white">' + r.formato + '</div>'
            + '<div class="text-[9px] font-semibold mt-0.5" style="color:' + r.color + '">' + r.tempo + ' · ' + r.objetivo + '</div>'
          + '</div>'
        + '</div>'
        + '<div class="space-y-1.5 mb-3">'
          + r.estrutura.map(function(s) {
            return '<div class="text-[10px] leading-relaxed" style="color:#D1D5DB">' + s + '</div>';
          }).join('')
        + '</div>'
        + '<div class="border-t pt-2" style="border-color:#2A2D3E">'
          + '<div class="text-[8px] font-bold uppercase tracking-widest mb-1.5" style="color:' + r.color + '">Dicas rápidas</div>'
          + '<div class="flex flex-wrap gap-1">'
            + r.dicas.map(function(d) {
              return '<span class="text-[9px] px-2 py-0.5 rounded-full" style="background:' + r.color + '18;color:' + r.color + '">' + d + '</span>';
            }).join('')
          + '</div>'
        + '</div>'
      + '</div>';
    }).join('')
    + '</div>';
}

"""

assert JS_ANCHOR in html
html = html.replace(JS_ANCHOR, INSIGHTS_JS + "\n" + JS_ANCHOR, 1)
print("✓ JS renderOrgInsights() + renderOrgEditorial() adicionado")

# ─────────────────────────────────────────────────────────
# 6. Chamar insights + editorial em renderOrganicoDashboard
# ─────────────────────────────────────────────────────────
OLD_RENDER_ORGANICO = """function renderOrganicoDashboard() {
  renderOrgKpis();
  renderOrgPosts();
  renderOrgChart();
}"""
NEW_RENDER_ORGANICO = """function renderOrganicoDashboard() {
  renderOrgKpis();
  renderOrgPosts();
  renderOrgChart();
  renderOrgInsights();
  renderOrgEditorial();
}"""
assert OLD_RENDER_ORGANICO in html
html = html.replace(OLD_RENDER_ORGANICO, NEW_RENDER_ORGANICO, 1)

# Também ao trocar plataforma dentro do orgânico
OLD_SELECT_ORG = """  renderOrgKpis();
  renderOrgPosts();
  renderOrgChart();
}"""
NEW_SELECT_ORG = """  renderOrgKpis();
  renderOrgPosts();
  renderOrgChart();
  renderOrgInsights();
  renderOrgEditorial();
}"""
# Cuidado: pode aparecer 2x (renderOrganicoDashboard já foi trocado)
# Encontra a segunda ocorrência (no selectOrgPlat)
idx = html.find(NEW_RENDER_ORGANICO)
second = html.find(OLD_SELECT_ORG, idx + len(NEW_RENDER_ORGANICO))
if second != -1:
    html = html[:second] + NEW_SELECT_ORG + html[second + len(OLD_SELECT_ORG):]
    print("✓ selectOrgPlat() atualizado")

# ─────────────────────────────────────────────────────────
# 7. Salva
# ─────────────────────────────────────────────────────────
with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("\n✓ index.html salvo com sucesso!")
print("  → Thumbnails reais dos posts IG")
print("  → Seção Insights com 6 análises automáticas")
print("  → Seção Linha Editorial com 4 roteiros")
