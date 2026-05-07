with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    content = f.read()

# ── 1. Adiciona TICKET_MEDIO após DATA:END ────────────────────────────────────
old_live_comment = "// ---------------------------------------------------------\n// Modo ao vivo -- detecta se esta rodando no servidor Flask"
new_live_comment = (
    "var TICKET_MEDIO = 400; // Ticket medio por venda (R$)\n"
    "\n"
    "// ---------------------------------------------------------\n"
    "// Modo ao vivo -- detecta se esta rodando no servidor Flask"
)
if old_live_comment in content:
    content = content.replace(old_live_comment, new_live_comment, 1)
    print("OK: TICKET_MEDIO added")
else:
    print("WARN: insertion point not found")

# ── 2. Adiciona CAC e ROAS no array kpis dentro de renderKPIs() ──────────────
# Precisamos inserir após o cálculo de spendHoje e antes do var kpis = [
# Vamos adicionar o cálculo de CAC/ROAS antes do array

old_kpis_open = (
    "  // Gasto do dia mais recente com dados\n"
    "  var today = ALL_DATES[ALL_DATES.length - 1] || '';\n"
    "  var spendHoje = camps.reduce(function(s, c) {\n"
    "    var d = ALL_DATA[today] && ALL_DATA[today][c];\n"
    "    return s + (d ? d.spend : 0);\n"
    "  }, 0);\n"
    "\n"
    "  var kpis = ["
)

new_kpis_open = (
    "  // Gasto do dia mais recente com dados\n"
    "  var today = ALL_DATES[ALL_DATES.length - 1] || '';\n"
    "  var spendHoje = camps.reduce(function(s, c) {\n"
    "    var d = ALL_DATA[today] && ALL_DATA[today][c];\n"
    "    return s + (d ? d.spend : 0);\n"
    "  }, 0);\n"
    "\n"
    "  // CAC e ROAS — baseados no mes atual (dados Nectar + gasto acumulado mes)\n"
    "  var mesAtual = (new Date().getMonth() + 1);\n"
    "  var mesStr   = '2026-' + String(mesAtual).padStart(2, '0');\n"
    "  var allCamps = Object.keys(CAMPAIGNS);\n"
    "  var spendMes = ALL_DATES.filter(function(d){ return d.startsWith(mesStr); })\n"
    "    .reduce(function(s, d) {\n"
    "      return s + allCamps.reduce(function(ss, c) {\n"
    "        var v = ALL_DATA[d] && ALL_DATA[d][c]; return ss + (v ? v.spend : 0);\n"
    "      }, 0);\n"
    "    }, 0);\n"
    "  var vendasMes = (NECTAR_LEADBOARD && NECTAR_LEADBOARD.vendidas_mes) || 0;\n"
    "  var cac  = vendasMes > 0 ? spendMes / vendasMes : null;\n"
    "  var roas = (vendasMes > 0 && spendMes > 0) ? (vendasMes * TICKET_MEDIO) / spendMes : null;\n"
    "\n"
    "  // Mes anterior para trend de CAC/ROAS\n"
    "  var mesAnt = mesAtual === 1 ? 12 : mesAtual - 1;\n"
    "  var mesAntStr = '2026-' + String(mesAnt).padStart(2, '0');\n"
    "  var spendMesAnt = ALL_DATES.filter(function(d){ return d.startsWith(mesAntStr); })\n"
    "    .reduce(function(s, d) {\n"
    "      return s + allCamps.reduce(function(ss, c) {\n"
    "        var v = ALL_DATA[d] && ALL_DATA[d][c]; return ss + (v ? v.spend : 0);\n"
    "      }, 0);\n"
    "    }, 0);\n"
    "  var hist = (NECTAR_LEADBOARD && NECTAR_LEADBOARD.historico_mes) || {};\n"
    "  var vendasMesAnt = hist[String(mesAnt)] || hist[mesAntStr] || 0;\n"
    "  var cacAnt  = vendasMesAnt > 0 ? spendMesAnt / vendasMesAnt : null;\n"
    "  var roasAnt = (vendasMesAnt > 0 && spendMesAnt > 0) ? (vendasMesAnt * TICKET_MEDIO) / spendMesAnt : null;\n"
    "\n"
    "  var kpis = ["
)

if old_kpis_open in content:
    content = content.replace(old_kpis_open, new_kpis_open, 1)
    print("OK: CAC/ROAS calc inserted")
else:
    print("FAIL: kpis open not found")

# ── 3. Adiciona CAC e ROAS antes do fechamento do array kpis ─────────────────
# O último item do array é CPL — vamos inserir CAC e ROAS logo depois de CPL
old_cpl_line = "    { label: 'CPL',             value: agg.cpl,         fmtFn: function(v) { return fmt.brl(v); }, metric: 'cpl',  trendMetric: 'cpl' }"
new_cpl_line = (
    "    { label: 'CPL',             value: agg.cpl,         fmtFn: function(v) { return fmt.brl(v); }, metric: 'cpl',  trendMetric: 'cpl' },\n"
    "    { label: 'CAC',             value: cac,\n"
    "      fmtFn: function(v) { return v !== null ? fmt.brl(v) : '--'; },\n"
    "      metric: null, trendMetric: null,\n"
    "      colorFn: function(v) {\n"
    "        if (v === null) return '#6B7280';\n"
    "        return v <= TICKET_MEDIO * 0.5 ? '#10B981' : v <= TICKET_MEDIO ? '#F59E0B' : '#EF4444';\n"
    "      },\n"
    "      trendOverride: cacAnt !== null && cac !== null ? ((cac - cacAnt) / cacAnt * 100) : null,\n"
    "      trendLower: true },\n"
    "    { label: 'ROAS',            value: roas,\n"
    "      fmtFn: function(v) { return v !== null ? v.toFixed(2) + 'x' : '--'; },\n"
    "      metric: null, trendMetric: null,\n"
    "      colorFn: function(v) {\n"
    "        if (v === null) return '#6B7280';\n"
    "        return v >= 3 ? '#10B981' : v >= 1 ? '#F59E0B' : '#EF4444';\n"
    "      },\n"
    "      trendOverride: roasAnt !== null && roas !== null ? ((roas - roasAnt) / roasAnt * 100) : null,\n"
    "      trendLower: false }"
)

if old_cpl_line in content:
    content = content.replace(old_cpl_line, new_cpl_line, 1)
    print("OK: CAC and ROAS KPIs added to array")
else:
    print("FAIL: CPL line not found")

# ── 4. Atualiza o render do card para suportar trendOverride e trendLower ─────
old_trend_block = (
    "    if (k.trendMetric) {\n"
    "      var tdates = k.trendDates || filteredDates;\n"
    "      var t = trend(k.trendMetric, tdates);\n"
    "      // label do mes de referencia para este KPI especifico\n"
    "      var refLabel = prevMonthLabel(tdates);\n"
    "      if (t !== null) {\n"
    "        var tSign  = t >= 0 ? '+' : '';\n"
    "        var tClass = (k.trendMetric === 'ctr' || k.trendMetric === 'leads' || k.trendMetric === 'clicks' || k.trendMetric === 'impr')\n"
    "          ? (t >= 0 ? 'trend-up' : 'trend-down')\n"
    "          : (t <= 0 ? 'trend-up' : 'trend-down');\n"
    "        var tIcon  = t >= 1 ? '\\u2191' : t <= -1 ? '\\u2193' : '\\u2192';\n"
    "        trendHtml = '<div class=\"flex flex-col items-end flex-shrink-0\">' +\n"
    "          '<span class=\"text-[9px] md:text-[10px] ' + tClass + ' font-semibold leading-none\">' + tIcon + tSign + t.toFixed(0) + '%</span>' +\n"
    "          '<span class=\"text-[8px] text-muted font-normal leading-none mt-0.5\">vs ' + refLabel + '</span>' +\n"
    "          '</div>';\n"
    "      } else {\n"
    "        trendHtml = '<span class=\"text-[8px] text-muted font-normal flex-shrink-0\">sem hist.</span>';\n"
    "      }\n"
    "    }"
)

new_trend_block = (
    "    if (k.trendOverride !== undefined || k.trendMetric) {\n"
    "      var t, refLabel;\n"
    "      if (k.trendOverride !== undefined) {\n"
    "        t = k.trendOverride;\n"
    "        refLabel = MONTH_NAMES[(mesAnt - 1)];\n"
    "      } else {\n"
    "        var tdates = k.trendDates || filteredDates;\n"
    "        t = trend(k.trendMetric, tdates);\n"
    "        refLabel = prevMonthLabel(tdates);\n"
    "      }\n"
    "      if (t !== null) {\n"
    "        var tSign  = t >= 0 ? '+' : '';\n"
    "        // trendLower: true = menor e melhor (CAC, CPC, CPM, CPL); false = maior e melhor (ROAS, leads, CTR)\n"
    "        var goodWhenUp = k.trendLower === false ||\n"
    "          (k.trendMetric && (k.trendMetric === 'ctr' || k.trendMetric === 'leads' || k.trendMetric === 'clicks' || k.trendMetric === 'impr'));\n"
    "        var tClass = goodWhenUp ? (t >= 0 ? 'trend-up' : 'trend-down') : (t <= 0 ? 'trend-up' : 'trend-down');\n"
    "        var tIcon  = t >= 1 ? '\\u2191' : t <= -1 ? '\\u2193' : '\\u2192';\n"
    "        trendHtml = '<div class=\"flex flex-col items-end flex-shrink-0\">' +\n"
    "          '<span class=\"text-[9px] md:text-[10px] ' + tClass + ' font-semibold leading-none\">' + tIcon + tSign + t.toFixed(0) + '%</span>' +\n"
    "          '<span class=\"text-[8px] text-muted font-normal leading-none mt-0.5\">vs ' + refLabel + '</span>' +\n"
    "          '</div>';\n"
    "      } else {\n"
    "        trendHtml = '<span class=\"text-[8px] text-muted font-normal flex-shrink-0\">sem hist.</span>';\n"
    "      }\n"
    "    }"
)

if old_trend_block in content:
    content = content.replace(old_trend_block, new_trend_block, 1)
    print("OK: trendOverride support added to card render")
else:
    print("FAIL: trend block not found")

# ── Checks ────────────────────────────────────────────────────────────────────
for c in ['TICKET_MEDIO', 'cac', 'roas', 'CAC', 'ROAS', 'vendasMes', 'spendMes',
          'trendOverride', 'trendLower', 'cacAnt', 'roasAnt']:
    print("CHECK:", c, "->", "OK" if c in content else "MISSING")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone.")
