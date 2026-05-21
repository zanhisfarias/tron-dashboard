with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    content = f.read()

# A linha no arquivo tem o escape literal \u00e1 (não o char real)
old_verba = "{ label: 'Verba Di\\u00e1ria', value: dailyBudget,   fmtFn: function(v) { return fmt.brl(v); }, metric: null },"
new_verba = (
    "{ label: 'Gasto Hoje',    value: spendHoje,     fmtFn: function(v) { return fmt.brl(v); }, metric: 'spend_hoje' },\n"
    "    { label: 'Verba Di\\u00e1ria', value: dailyBudget,   fmtFn: function(v) { return fmt.brl(v); }, metric: null },"
)

if old_verba in content:
    content = content.replace(old_verba, new_verba, 1)
    print("OK: Gasto Hoje KPI inserted")
else:
    print("FAIL: target not found")

# ── Adiciona colorForMetric para spend_hoje ───────────────────────────────────
# THRESHOLDS já existe; spend_hoje não tem threshold — vamos colorir
# comparando com dailyBudget. Melhor: adicionar lógica diretamente no KPI render.
# A abordagem mais simples: adicionar cor customizada via fmtFn não ajuda,
# mas podemos adicionar um campo extra "color" ao objeto kpi.
# Vamos refatorar para que o objeto kpi aceite "colorFn" opcional.

# Localizar onde o kpi color é computado na renderização
old_color_line = "    var color  = k.metric ? colorForMetric(k.metric, k.value) : '#E5E7EB';"
new_color_line = (
    "    var color  = k.colorFn ? k.colorFn(k.value) : (k.metric ? colorForMetric(k.metric, k.value) : '#E5E7EB');"
)

if old_color_line in content:
    content = content.replace(old_color_line, new_color_line, 1)
    print("OK: colorFn support added to KPI render")
else:
    print("WARN: color line not found")

# ── Adiciona colorFn ao KPI Gasto Hoje ───────────────────────────────────────
old_gasto_kpi = "{ label: 'Gasto Hoje',    value: spendHoje,     fmtFn: function(v) { return fmt.brl(v); }, metric: 'spend_hoje' },"
new_gasto_kpi = (
    "{ label: 'Gasto Hoje',    value: spendHoje,     fmtFn: function(v) { return fmt.brl(v); }, metric: null,\n"
    "      colorFn: function(v) { return v <= dailyBudget * 1.0 ? '#10B981' : v <= dailyBudget * 1.2 ? '#F59E0B' : '#EF4444'; } },"
)

if old_gasto_kpi in content:
    content = content.replace(old_gasto_kpi, new_gasto_kpi, 1)
    print("OK: colorFn added to Gasto Hoje")
else:
    print("WARN: Gasto Hoje KPI not found for colorFn")

# ── Verificação final ─────────────────────────────────────────────────────────
checks = ['spendHoje', 'Gasto Hoje', 'colorFn']
for c in checks:
    print("CHECK:", c, "->", "OK" if c in content else "MISSING")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done.")
