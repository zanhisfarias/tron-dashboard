import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/Marketing/Desktop/Dashboard/index.html', encoding='utf-8') as f:
    html = f.read()

NEW_TIKTOK = '''<!-- ═══════════════════════════════════════════════════════
     TIKTOK ADS — Seção principal (oculta por padrão)
════════════════════════════════════════════════════════════ -->
<div id="tiktokMain" style="display:none" class="max-w-[1400px] mx-auto px-3 py-3 md:px-6 md:py-6 space-y-4 md:space-y-6">

  <!-- Banner -->
  <div class="card p-3 md:p-4 flex items-center gap-3 fade-up" style="border-color:rgba(238,29,82,0.3);box-shadow:0 0 32px rgba(238,29,82,0.08)">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background:rgba(238,29,82,0.12)">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.2 8.2 0 004.79 1.53V6.77a4.85 4.85 0 01-1.02-.08z" fill="#EE1D52"/></svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-semibold text-white">TikTok Ads — Estrutura pronta</div>
      <div class="text-[11px] text-muted mt-0.5">Visualização com dados de exemplo. Conecte a API para ativar dados reais.</div>
    </div>
    <div class="flex-shrink-0 text-[10px] font-bold px-3 py-1.5 rounded-full" style="background:rgba(238,29,82,0.12);color:#EE1D52">API pendente</div>
  </div>

  <!-- KPI Cards com glow -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 fade-up" style="animation-delay:0.05s">
    <div class="card tt-kpi-card p-4 md:p-5 tt-glow-red" style="border-color:rgba(238,29,82,0.35);background:linear-gradient(135deg,#1A1D27,rgba(238,29,82,0.05))">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#EE1D52">Gasto (mês)</div>
      <div class="text-2xl md:text-3xl font-black tt-num-red tt-count-anim">R$&nbsp;2.800</div>
      <div class="mt-2 text-[10px] font-semibold text-muted">CPV médio R$&nbsp;0,016</div>
      <div class="mt-3 h-0.5 rounded-full" style="background:linear-gradient(to right,#EE1D52,transparent)"></div>
    </div>
    <div class="card tt-kpi-card p-4 md:p-5 tt-glow-cyan" style="border-color:rgba(37,244,238,0.35);background:linear-gradient(135deg,#1A1D27,rgba(37,244,238,0.05))">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#25F4EE">Views (3s+)</div>
      <div class="text-2xl md:text-3xl font-black tt-num-cyan tt-count-anim">180 mil</div>
      <div class="mt-2 text-[10px] font-semibold" style="color:#25F4EE">Watch Rate 34,6%</div>
      <div class="mt-3 h-0.5 rounded-full" style="background:linear-gradient(to right,#25F4EE,transparent)"></div>
    </div>
    <div class="card tt-kpi-card p-4 md:p-5 tt-glow-purp" style="border-color:rgba(139,92,246,0.35);background:linear-gradient(135deg,#1A1D27,rgba(139,92,246,0.05))">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#A78BFA">Eng. Rate</div>
      <div class="text-2xl md:text-3xl font-black tt-count-anim" style="background:linear-gradient(135deg,#A78BFA,#c4b5fd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">4,2%</div>
      <div class="mt-2 text-[10px] font-semibold text-muted">Likes · Shares · Saves</div>
      <div class="mt-3 h-0.5 rounded-full" style="background:linear-gradient(to right,#A78BFA,transparent)"></div>
    </div>
    <div class="card tt-kpi-card p-4 md:p-5 tt-glow-gold" style="border-color:rgba(251,188,5,0.35);background:linear-gradient(135deg,#1A1D27,rgba(251,188,5,0.05))">
      <div class="text-[9px] font-bold uppercase tracking-widest mb-2" style="color:#FBBC05">Leads / CPL</div>
      <div class="text-2xl md:text-3xl font-black tt-num-gold tt-count-anim">22</div>
      <div class="mt-2 text-[10px] font-semibold" style="color:#F59E0B">CPL médio R$&nbsp;127</div>
      <div class="mt-3 h-0.5 rounded-full" style="background:linear-gradient(to right,#FBBC05,transparent)"></div>
    </div>
  </div>

  <!-- Funil de retenção moderno -->
  <div class="card p-4 md:p-6 fade-up" style="animation-delay:0.09s;border-color:rgba(37,244,238,0.15);background:linear-gradient(180deg,rgba(37,244,238,0.03) 0%,#1A1D27 100%)">
    <div class="flex flex-col md:flex-row md:items-center justify-between mb-5 gap-1">
      <div>
        <div class="text-sm font-bold text-white tracking-wide">Funil de Atenção do Vídeo</div>
        <div class="text-[10px] text-muted mt-0.5">Cada etapa revela onde o público perde interesse — do alcance ao lead</div>
      </div>
      <div class="text-[10px] font-semibold px-3 py-1 rounded-full" style="background:rgba(37,244,238,0.08);color:#25F4EE">Mai/2026 · exemplo</div>
    </div>
    <div id="tiktokFunnel" class="space-y-2"></div>
  </div>

  <!-- Radar + Polar Area -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
    <div class="card p-4 md:p-5 fade-up" style="animation-delay:0.13s;border-color:rgba(238,29,82,0.15);background:linear-gradient(135deg,#1A1D27,rgba(238,29,82,0.03))">
      <div class="mb-4">
        <div class="text-sm font-bold text-white">Perfil de Engajamento</div>
        <div class="text-[10px] text-muted mt-0.5">Radar por campanha · Likes · Shares · Saves · Comentários · Watch%</div>
      </div>
      <div class="flex items-center gap-4 mb-3 flex-wrap">
        <span class="flex items-center gap-1.5 text-[10px] font-semibold" style="color:#EE1D52"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#EE1D52"></span>In-Feed Brand</span>
        <span class="flex items-center gap-1.5 text-[10px] font-semibold" style="color:#25F4EE"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#25F4EE"></span>Spark Contábil</span>
        <span class="flex items-center gap-1.5 text-[10px] font-semibold" style="color:#FBBC05"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#FBBC05"></span>In-Feed DP</span>
      </div>
      <canvas id="tiktokRadarChart" height="210"></canvas>
    </div>
    <div class="card p-4 md:p-5 fade-up" style="animation-delay:0.17s;border-color:rgba(139,92,246,0.15);background:linear-gradient(135deg,#1A1D27,rgba(139,92,246,0.03))">
      <div class="mb-4">
        <div class="text-sm font-bold text-white">Alcance por Dia da Semana</div>
        <div class="text-[10px] text-muted mt-0.5">Sexta-feira lidera — melhor janela de veiculação</div>
      </div>
      <canvas id="tiktokPolarChart" height="210"></canvas>
    </div>
  </div>

  <!-- Tabela -->
  <div class="card fade-up" style="animation-delay:0.21s;border-color:rgba(238,29,82,0.12)">
    <div class="flex flex-col md:flex-row md:items-center justify-between px-4 md:px-5 py-3 gap-2" style="border-bottom:1px solid rgba(238,29,82,0.15)">
      <div>
        <div class="text-sm font-bold text-white">Performance por Criativo</div>
        <div class="text-[10px] text-muted mt-0.5 hidden md:block">Mai/2026 · Watch% · Conclusão · Eng. Rate · CPL</div>
      </div>
      <div class="text-[10px] font-bold px-2.5 py-1 rounded-full" style="background:rgba(238,29,82,0.1);color:#EE1D52">4 vídeos</div>
    </div>
    <div class="overflow-x-auto">
      <table class="tbl">
        <thead><tr>
          <th class="text-left">Criativo</th>
          <th class="text-left hidden md:table-cell">Formato</th>
          <th class="text-right">Gasto</th>
          <th class="text-right hidden md:table-cell">Impressões</th>
          <th class="text-right">Watch%</th>
          <th class="text-right hidden md:table-cell">Conclusão</th>
          <th class="text-right hidden md:table-cell">Eng. Rate</th>
          <th class="text-right">Leads</th>
          <th class="text-right">CPL</th>
          <th class="text-center">Status</th>
        </tr></thead>
        <tbody>
          <tr>
            <td class="font-semibold text-white" style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">In-Feed — Brand Awareness</td>
            <td class="hidden md:table-cell"><span class="text-[9px] font-bold px-2 py-0.5 rounded-full" style="background:rgba(238,29,82,0.12);color:#EE1D52">In-Feed</span></td>
            <td class="text-right font-semibold">R$&nbsp;1.200</td>
            <td class="text-right text-muted hidden md:table-cell">280.000</td>
            <td class="text-right font-bold" style="color:#25F4EE">34,6%</td>
            <td class="text-right text-muted hidden md:table-cell">12,3%</td>
            <td class="text-right hidden md:table-cell font-semibold" style="color:#10B981">4,8%</td>
            <td class="text-right font-bold" style="color:#10B981">10</td>
            <td class="text-right font-bold" style="color:#10B981">R$&nbsp;120</td>
            <td class="text-center"><span class="text-[9px] font-bold px-2 py-0.5 rounded-full" style="background:rgba(16,185,129,0.12);color:#10B981">Ativo</span></td>
          </tr>
          <tr>
            <td class="font-semibold text-white" style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Spark Ads — Contábil</td>
            <td class="hidden md:table-cell"><span class="text-[9px] font-bold px-2 py-0.5 rounded-full" style="background:rgba(37,244,238,0.12);color:#25F4EE">Spark</span></td>
            <td class="text-right font-semibold">R$&nbsp;800</td>
            <td class="text-right text-muted hidden md:table-cell">160.000</td>
            <td class="text-right font-bold" style="color:#25F4EE">36,0%</td>
            <td class="text-right text-muted hidden md:table-cell">15,1%</td>
            <td class="text-right hidden md:table-cell font-semibold" style="color:#10B981">5,2%</td>
            <td class="text-right font-bold" style="color:#10B981">8</td>
            <td class="text-right font-semibold">R$&nbsp;100</td>
            <td class="text-center"><span class="text-[9px] font-bold px-2 py-0.5 rounded-full" style="background:rgba(16,185,129,0.12);color:#10B981">Ativo</span></td>
          </tr>
          <tr>
            <td class="font-semibold text-white" style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">In-Feed — Dep. Pessoal</td>
            <td class="hidden md:table-cell"><span class="text-[9px] font-bold px-2 py-0.5 rounded-full" style="background:rgba(238,29,82,0.12);color:#EE1D52">In-Feed</span></td>
            <td class="text-right font-semibold">R$&nbsp;500</td>
            <td class="text-right text-muted hidden md:table-cell">60.000</td>
            <td class="text-right font-bold" style="color:#F59E0B">30,0%</td>
            <td class="text-right text-muted hidden md:table-cell">9,8%</td>
            <td class="text-right hidden md:table-cell text-muted">3,1%</td>
            <td class="text-right font-semibold">4</td>
            <td class="text-right font-semibold" style="color:#F59E0B">R$&nbsp;125</td>
            <td class="text-center"><span class="text-[9px] font-bold px-2 py-0.5 rounded-full" style="background:rgba(16,185,129,0.12);color:#10B981">Ativo</span></td>
          </tr>
          <tr>
            <td class="font-semibold text-white" style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">TopView</td>
            <td class="hidden md:table-cell"><span class="text-[9px] font-bold px-2 py-0.5 rounded-full" style="background:rgba(107,114,128,0.15);color:#9CA3AF">TopView</span></td>
            <td class="text-right font-semibold">R$&nbsp;300</td>
            <td class="text-right text-muted hidden md:table-cell">20.000</td>
            <td class="text-right font-bold" style="color:#25F4EE">38,0%</td>
            <td class="text-right text-muted hidden md:table-cell">18,5%</td>
            <td class="text-right hidden md:table-cell text-muted">2,4%</td>
            <td class="text-right text-muted font-semibold">0</td>
            <td class="text-right text-muted">—</td>
            <td class="text-center"><span class="text-[9px] font-bold px-2 py-0.5 rounded-full" style="background:rgba(16,185,129,0.12);color:#10B981">Ativo</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Footer TikTok -->
  <footer class="flex flex-col md:flex-row items-center justify-between gap-1 py-2 text-center md:text-left">
    <span class="text-[10px] text-muted">Tron — Dashboard de Performance — TikTok Ads</span>
    <span class="text-[10px] text-muted">Dados de exemplo · API não conectada</span>
  </footer>
</div>
'''

# Substituir o bloco inteiro entre os marcadores
pattern = r'<!-- ═+\s*TIKTOK ADS.*?</div>\s*\n(?=\n<script)'
html_new = re.sub(pattern, NEW_TIKTOK + '\n', html, flags=re.DOTALL)

if html_new == html:
    print("ERRO: padrão não encontrado")
else:
    with open('C:/Users/Marketing/Desktop/Dashboard/index.html', 'w', encoding='utf-8') as f:
        f.write(html_new)
    print("OK — arquivo salvo")
