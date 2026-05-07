with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. Substitui a função trend() pela nova versão que usa o mês anterior
# ─────────────────────────────────────────────────────────────────────────────
old_trend = """\
function trend(metric) {
  var dates = getFilteredDates();
  var half  = Math.floor(dates.length / 2);
  var first = dates.slice(0, half);
  var last  = dates.slice(half);
  var camps = state.camp === 'all' ? Object.keys(CAMPAIGNS) : [state.camp];

  function sumDates(ds) {
    var s = { leads: 0, spend: 0, impr: 0, clicks: 0 };
    ds.forEach(function(d) {
      camps.forEach(function(c) {
        var v = ALL_DATA[d] && ALL_DATA[d][c]; if (!v) return;
        s.leads += v.leads; s.spend += v.spend; s.impr += v.impr; s.clicks += v.clicks;
      });
    });
    return s;
  }

  function calcM(s) {
    if (metric === 'leads')  return s.leads;
    if (metric === 'spend')  return s.spend;
    if (metric === 'ctr')    return s.impr   > 0 ? s.clicks / s.impr * 100 : 0;
    if (metric === 'cpc')    return s.clicks > 0 ? s.spend  / s.clicks : 0;
    if (metric === 'cpm')    return s.impr   > 0 ? s.spend  / s.impr * 1000 : 0;
    if (metric === 'cpl')    return s.leads  > 0 ? s.spend  / s.leads : 0;
    if (metric === 'clicks') return s.clicks;
    if (metric === 'impr')   return s.impr;
    return 0;
  }

  var s1 = sumDates(first), s2 = sumDates(last);
  var v1 = calcM(s1), v2 = calcM(s2);
  if (v1 === 0) return 0;
  return ((v2 - v1) / v1) * 100;
}"""

new_trend = """\
// Recua uma data exatamente 1 mes (ex: 2026-05-10 -> 2026-04-10)
function shiftMonthBack(isoDate) {
  var p = isoDate.split('-');
  var y = +p[0], m = +p[1], d = +p[2];
  if (--m === 0) { m = 12; y--; }
  var last = new Date(y, m, 0).getDate();
  return y + '-' + String(m).padStart(2,'0') + '-' + String(Math.min(d, last)).padStart(2,'0');
}

// Soma um conjunto de datas para uma metrica especifica
function aggregateDates(dates, camps, metric) {
  var s = { leads: 0, spend: 0, impr: 0, clicks: 0 };
  dates.forEach(function(d) {
    camps.forEach(function(c) {
      var v = ALL_DATA[d] && ALL_DATA[d][c]; if (!v) return;
      s.leads += v.leads; s.spend += v.spend; s.impr += v.impr; s.clicks += v.clicks;
    });
  });
  if (metric === 'leads')  return s.leads;
  if (metric === 'spend')  return s.spend;
  if (metric === 'ctr')    return s.impr   > 0 ? s.clicks / s.impr * 100 : 0;
  if (metric === 'cpc')    return s.clicks > 0 ? s.spend  / s.clicks : 0;
  if (metric === 'cpm')    return s.impr   > 0 ? s.spend  / s.impr * 1000 : 0;
  if (metric === 'cpl')    return s.leads  > 0 ? s.spend  / s.leads : 0;
  if (metric === 'clicks') return s.clicks;
  if (metric === 'impr')   return s.impr;
  return 0;
}

// Retorna a label do mes anterior ao primeiro dia do range atual
function prevMonthLabel(currDates) {
  var ref = currDates.length ? currDates[0] : state.since;
  var shifted = shiftMonthBack(ref);
  var m = parseInt(shifted.split('-')[1]);
  return MONTH_NAMES[m - 1];
}

// Compara metrica do periodo atual vs mesmo periodo do mes anterior
function trend(metric, trendDates) {
  var dates = trendDates || getFilteredDates();
  var camps = state.camp === 'all' ? Object.keys(CAMPAIGNS) : [state.camp];
  var prevDates = dates.map(shiftMonthBack).filter(function(d) {
    return ALL_DATA[d] !== undefined;
  });
  var vCurr = aggregateDates(dates,     camps, metric);
  var vPrev = aggregateDates(prevDates, camps, metric);
  if (vPrev === 0) return null; // sem dados do mes anterior
  return (vCurr - vPrev) / vPrev * 100;
}"""

if old_trend in content:
    content = content.replace(old_trend, new_trend, 1)
    print("OK: trend() rewritten")
else:
    print("FAIL: old trend() not found")
    # Debug
    idx = content.find('function trend(')
    print("trend found at:", idx)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Adiciona trendMetric e trendDates aos objetos KPI
# ─────────────────────────────────────────────────────────────────────────────

# Mapa das substituições: old linha → nova linha (com trendMetric)
kpi_replacements = [
    (
        "    { label: 'Adsets Ativos',   value: activeAdsets,   fmtFn: function(v) { return v; },          metric: null },",
        "    { label: 'Adsets Ativos',   value: activeAdsets,   fmtFn: function(v) { return v; },          metric: null, trendMetric: null },"
    ),
    (
        "    { label: 'An\\u00fancios At.', value: activeAds,     fmtFn: function(v) { return v; },          metric: null },",
        "    { label: 'An\\u00fancios At.', value: activeAds,     fmtFn: function(v) { return v; },          metric: null, trendMetric: null },"
    ),
    (
        "    { label: 'Verba Di\\u00e1ria', value: dailyBudget,   fmtFn: function(v) { return fmt.brl(v); }, metric: null },",
        "    { label: 'Verba Di\\u00e1ria', value: dailyBudget,   fmtFn: function(v) { return fmt.brl(v); }, metric: null, trendMetric: null },"
    ),
    (
        "    { label: 'Alcance',         value: agg.impr * 0.72, fmtFn: function(v) { return fmt.k(v); },   metric: null },",
        "    { label: 'Alcance',         value: agg.impr * 0.72, fmtFn: function(v) { return fmt.k(v); },   metric: null, trendMetric: 'impr' },"
    ),
    (
        "    { label: 'CTR',             value: agg.ctr,         fmtFn: function(v) { return fmt.pct(v); }, metric: 'ctr' },",
        "    { label: 'CTR',             value: agg.ctr,         fmtFn: function(v) { return fmt.pct(v); }, metric: 'ctr',  trendMetric: 'ctr' },"
    ),
    (
        "    { label: 'CPC',             value: agg.cpc,         fmtFn: function(v) { return fmt.brl(v); }, metric: 'cpc' },",
        "    { label: 'CPC',             value: agg.cpc,         fmtFn: function(v) { return fmt.brl(v); }, metric: 'cpc',  trendMetric: 'cpc' },"
    ),
    (
        "    { label: 'CPM',             value: agg.cpm,         fmtFn: function(v) { return fmt.brl(v); }, metric: 'cpm' },",
        "    { label: 'CPM',             value: agg.cpm,         fmtFn: function(v) { return fmt.brl(v); }, metric: 'cpm',  trendMetric: 'cpm' },"
    ),
    (
        "    { label: 'Cliques',         value: agg.clicks,      fmtFn: function(v) { return fmt.num(v); }, metric: null },",
        "    { label: 'Cliques',         value: agg.clicks,      fmtFn: function(v) { return fmt.num(v); }, metric: null, trendMetric: 'clicks' },"
    ),
    (
        "    { label: 'Leads',           value: agg.leads,       fmtFn: function(v) { return fmt.num(v); }, metric: null },",
        "    { label: 'Leads',           value: agg.leads,       fmtFn: function(v) { return fmt.num(v); }, metric: null, trendMetric: 'leads' },"
    ),
    (
        "    { label: 'CPL',             value: agg.cpl,         fmtFn: function(v) { return fmt.brl(v); }, metric: 'cpl' }",
        "    { label: 'CPL',             value: agg.cpl,         fmtFn: function(v) { return fmt.brl(v); }, metric: 'cpl',  trendMetric: 'cpl' }"
    ),
]

for old_line, new_line in kpi_replacements:
    if old_line in content:
        content = content.replace(old_line, new_line, 1)
        print(f"OK: trendMetric added to '{old_line[14:35].strip()}'")
    else:
        print(f"WARN: not found: '{old_line[14:50].strip()}'")

# Gasto Hoje — usa trendDates = [today] para comparar só o dia de hoje vs mesmo dia do mes anterior
old_gasto = (
    "{ label: 'Gasto Hoje',    value: spendHoje,     fmtFn: function(v) { return fmt.brl(v); }, metric: null,\n"
    "      colorFn: function(v) { return v <= dailyBudget * 1.0 ? '#10B981' : v <= dailyBudget * 1.2 ? '#F59E0B' : '#EF4444'; } },"
)
new_gasto = (
    "{ label: 'Gasto Hoje',    value: spendHoje,     fmtFn: function(v) { return fmt.brl(v); }, metric: null,\n"
    "      trendMetric: 'spend', trendDates: [today],\n"
    "      colorFn: function(v) { return v <= dailyBudget * 1.0 ? '#10B981' : v <= dailyBudget * 1.2 ? '#F59E0B' : '#EF4444'; } },"
)
if old_gasto in content:
    content = content.replace(old_gasto, new_gasto, 1)
    print("OK: trendMetric added to Gasto Hoje")
else:
    print("WARN: Gasto Hoje not found for trendMetric")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Atualiza o render do KPI card para usar trendMetric e mostrar "vs [mês]"
# ─────────────────────────────────────────────────────────────────────────────
old_render = """\
  var grid = document.getElementById('kpiGrid');
  grid.innerHTML = kpis.map(function(k, i) {
    var t      = trend(k.label.toLowerCase().replace(/ /g,''));
    var color  = k.colorFn ? k.colorFn(k.value) : (k.metric ? colorForMetric(k.metric, k.value) : '#E5E7EB');
    var tSign  = t >= 0 ? '+' : '';
    var tClass = k.metric === 'ctr' ? (t >= 0 ? 'trend-up' : 'trend-down') : (t <= 0 ? 'trend-up' : 'trend-down');
    var tIcon  = t >= 1 ? '\\u2191' : t <= -1 ? '\\u2193' : '\\u2192';
    return '<div class="card kpi-card p-3 md:p-4 fade-up" style="animation-delay:' + (0.05 * i) + 's;min-width:0">' +
      '<div class="flex items-start justify-between mb-1 gap-1">' +
      '<div class="text-[9px] md:text-[10px] font-semibold text-muted uppercase tracking-wider leading-tight">' + k.label + '</div>' +
      '<span class="text-[9px] md:text-[10px] ' + tClass + ' font-semibold flex-shrink-0">' + tIcon + tSign + t.toFixed(0) + '%</span>' +
      '</div>' +
      '<div class="text-sm md:text-xl font-bold truncate" style="color:' + color + '">' + k.fmtFn(k.value) + '</div>' +
      '</div>';
  }).join('');
}"""

new_render = """\
  var filteredDates = getFilteredDates();
  var _prevLabel = prevMonthLabel(filteredDates);
  var grid = document.getElementById('kpiGrid');
  grid.innerHTML = kpis.map(function(k, i) {
    var color  = k.colorFn ? k.colorFn(k.value) : (k.metric ? colorForMetric(k.metric, k.value) : '#E5E7EB');
    var trendHtml = '';
    if (k.trendMetric) {
      var tdates = k.trendDates || filteredDates;
      var t = trend(k.trendMetric, tdates);
      // label do mes de referencia para este KPI especifico
      var refLabel = prevMonthLabel(tdates);
      if (t !== null) {
        var tSign  = t >= 0 ? '+' : '';
        var tClass = (k.trendMetric === 'ctr' || k.trendMetric === 'leads' || k.trendMetric === 'clicks' || k.trendMetric === 'impr')
          ? (t >= 0 ? 'trend-up' : 'trend-down')
          : (t <= 0 ? 'trend-up' : 'trend-down');
        var tIcon  = t >= 1 ? '\\u2191' : t <= -1 ? '\\u2193' : '\\u2192';
        trendHtml = '<div class="flex flex-col items-end flex-shrink-0">' +
          '<span class="text-[9px] md:text-[10px] ' + tClass + ' font-semibold leading-none">' + tIcon + tSign + t.toFixed(0) + '%</span>' +
          '<span class="text-[8px] text-muted font-normal leading-none mt-0.5">vs ' + refLabel + '</span>' +
          '</div>';
      } else {
        trendHtml = '<span class="text-[8px] text-muted font-normal flex-shrink-0">sem hist.</span>';
      }
    }
    return '<div class="card kpi-card p-3 md:p-4 fade-up" style="animation-delay:' + (0.05 * i) + 's;min-width:0">' +
      '<div class="flex items-start justify-between mb-1 gap-1">' +
      '<div class="text-[9px] md:text-[10px] font-semibold text-muted uppercase tracking-wider leading-tight">' + k.label + '</div>' +
      trendHtml +
      '</div>' +
      '<div class="text-sm md:text-xl font-bold truncate" style="color:' + color + '">' + k.fmtFn(k.value) + '</div>' +
      '</div>';
  }).join('');
}"""

if old_render in content:
    content = content.replace(old_render, new_render, 1)
    print("OK: KPI card render updated with vs [mês] label")
else:
    print("FAIL: old KPI render block not found")
    # debug
    idx = content.find("var grid = document.getElementById('kpiGrid')")
    print("kpiGrid found at:", idx)
    if idx > 0:
        print(repr(content[idx:idx+300]))

# ─────────────────────────────────────────────────────────────────────────────
# Verify & write
# ─────────────────────────────────────────────────────────────────────────────
checks = ['shiftMonthBack', 'aggregateDates', 'prevMonthLabel', 'trendMetric',
          'trendDates', 'vs ' , 'refLabel', 'sem hist.']
for c in checks:
    print("CHECK:", c, "->", "OK" if c in content else "MISSING")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone.")
