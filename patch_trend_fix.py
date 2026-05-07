with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    html = f.read()

# Substitui toda a função trend() por uma versão que compara média diária
# mês atual vs mês anterior completo — sempre tem dados, nunca retorna null por falta de hist.
old_trend_fn = """\
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

new_trend_fn = """\
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

// Determina o mes anterior a partir de uma data de referencia
function prevMonthOf(refDateStr) {
  var y = parseInt(refDateStr.substring(0, 4));
  var m = parseInt(refDateStr.substring(5, 7));
  if (--m === 0) { m = 12; y--; }
  return { year: y, mon: m, str: y + '-' + String(m).padStart(2, '0') };
}

// Retorna label curta do mes anterior (ex: "Abr")
function prevMonthLabel(currDates) {
  var ref = (currDates && currDates.length) ? currDates[0] : state.since;
  var pm = prevMonthOf(ref);
  return MONTH_NAMES[pm.mon - 1];
}

// Compara media diaria do mes atual vs media diaria do mes anterior completo.
// Usa medias diarias para ser justo independente de quantos dias correram no mes atual.
function trend(metric, trendDates) {
  var camps = state.camp === 'all' ? Object.keys(CAMPAIGNS) : [state.camp];

  // Mes de referencia: primeiro dia do range filtrado (ou state.since)
  var refDate    = (trendDates && trendDates.length) ? trendDates[0] : state.since;
  var currMonStr = refDate.substring(0, 7);          // ex: "2026-05"
  var pm         = prevMonthOf(refDate);
  var prevMonStr = pm.str;                           // ex: "2026-04"

  // Todas as datas de cada mes presentes em ALL_DATES
  var currDates = ALL_DATES.filter(function(d) { return d.startsWith(currMonStr); });
  var prevDates = ALL_DATES.filter(function(d) { return d.startsWith(prevMonStr); });

  if (!currDates.length || !prevDates.length) return null;

  // Para metricas derivadas (ctr, cpc, cpm, cpl) calcula direto sobre o total do periodo
  // Para metricas acumulativas (leads, spend, clicks, impr) usa media diaria
  var IS_RATE = (metric === 'ctr' || metric === 'cpc' || metric === 'cpm' || metric === 'cpl');

  var vCurr, vPrev;
  if (IS_RATE) {
    vCurr = aggregateDates(currDates, camps, metric);
    vPrev = aggregateDates(prevDates, camps, metric);
  } else {
    // Media diaria: total / dias — compara o ritmo, nao o volume absoluto
    vCurr = aggregateDates(currDates, camps, metric) / currDates.length;
    vPrev = aggregateDates(prevDates, camps, metric) / prevDates.length;
  }

  if (vPrev === 0) return null;
  return (vCurr - vPrev) / vPrev * 100;
}"""

if old_trend_fn in html:
    html = html.replace(old_trend_fn, new_trend_fn, 1)
    print("OK: trend() rewritten with daily-average comparison")
else:
    print("FAIL: old trend block not found")
    idx = html.find('function shiftMonthBack(')
    print(f"  shiftMonthBack at: {idx}")

# Atualiza também a referência ao mesAnt no render do trend (usava variável mesAnt do renderKPIs)
# Garante que refLabel usa a nova função prevMonthLabel
old_mesant_ref = "        refLabel = MONTH_NAMES[(mesAnt - 1)];"
new_mesant_ref = "        refLabel = prevMonthLabel(null);"

if old_mesant_ref in html:
    html = html.replace(old_mesant_ref, new_mesant_ref, 1)
    print("OK: trendOverride refLabel updated")
else:
    print("WARN: mesAnt refLabel not found")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done.")
