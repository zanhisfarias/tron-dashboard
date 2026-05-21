import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── 1. update_dashboard.py — adiciona receita ao fetch_nectar_leadboard() ────
with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', encoding='utf-8') as f:
    ud = f.read()

old_return = '''    pipeline["Vendida"] = vendidas_mes  # Vendida = fechadas no mês

    total_pipeline = sum(v for k, v in pipeline.items() if k != "Vendida")
    print(f"      Pipeline: {pipeline}")
    print(f"      Vendidas no mês: {vendidas_mes} | Perdidas no mês: {perdidas_mes}")

    return {
        "pipeline":      pipeline,
        "vendidas_mes":  vendidas_mes,
        "perdidas_mes":  perdidas_mes,
        "historico_mes": historico_mes,
    }'''

new_return = '''    pipeline["Vendida"] = vendidas_mes  # Vendida = fechadas no mês

    total_pipeline = sum(v for k, v in pipeline.items() if k != "Vendida")
    print(f"      Pipeline: {pipeline}")
    print(f"      Vendidas no mês: {vendidas_mes} | Perdidas no mês: {perdidas_mes}")

    # ── Receita financeira via /oportunidades/ (valorAvulso + valorMensal) ──
    receita_avulso_mes  = 0.0
    mrr_mes             = 0.0
    receita_historico   = {}   # {mes_iso: {"avulso": x, "mrr": x}}

    try:
        print("  → Buscando receita financeira em /oportunidades/...")
        start_op = 0
        while True:
            resp_op = requests.get(
                f"{NECTAR_BASE}/oportunidades/",
                params={"api_token": NECTAR_TOKEN, "displayLength": 200,
                        "displayStart": start_op, "status": 2},
                timeout=30,
            )
            resp_op.raise_for_status()
            oports = resp_op.json()
            oports = oports if isinstance(oports, list) else oports.get("data", [])
            if not oports:
                break

            for op in oports:
                dc = (op.get("dataConclusao") or op.get("dataAtualizacao") or "")[:10]
                mes_iso = dc[:7] if dc else ""
                va = float(op.get("valorAvulso", 0) or 0)
                vm = float(op.get("valorMensal", 0) or 0)

                if mes_iso:
                    if mes_iso not in receita_historico:
                        receita_historico[mes_iso] = {"avulso": 0.0, "mrr": 0.0}
                    receita_historico[mes_iso]["avulso"] += va
                    receita_historico[mes_iso]["mrr"]    += vm

                if mes_ini <= dc <= mes_fim:
                    receita_avulso_mes += va
                    mrr_mes            += vm

            if len(oports) < 200:
                break
            start_op += 200
            if start_op > 10000:
                break

        print(f"      Receita mês: avulso=R${receita_avulso_mes:.2f} | MRR=R${mrr_mes:.2f}")
    except Exception as e:
        print(f"    AVISO: erro ao buscar receita: {e}")

    return {
        "pipeline":           pipeline,
        "vendidas_mes":       vendidas_mes,
        "perdidas_mes":       perdidas_mes,
        "historico_mes":      historico_mes,
        "receita_avulso_mes": receita_avulso_mes,
        "mrr_mes":            mrr_mes,
        "receita_historico":  receita_historico,
    }'''

if old_return in ud:
    ud = ud.replace(old_return, new_return, 1)
    print("OK: fetch_nectar_leadboard() updated with receita")
else:
    print("FAIL: return block not found in update_dashboard.py")

with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(ud)

# ── 2. dashboard.html — adiciona KPI Receita após ROAS ───────────────────────
with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    html = f.read()

# 2a. Adiciona cálculo de receita junto com CAC/ROAS
old_roas_calc = (
    "  var vendasMes = (NECTAR_LEADBOARD && NECTAR_LEADBOARD.vendidas_mes) || 0;\n"
    "  var cac  = vendasMes > 0 ? spendMes / vendasMes : null;\n"
    "  var roas = (vendasMes > 0 && spendMes > 0) ? (vendasMes * TICKET_MEDIO) / spendMes : null;\n"
)
new_roas_calc = (
    "  var vendasMes = (NECTAR_LEADBOARD && NECTAR_LEADBOARD.vendidas_mes) || 0;\n"
    "  // Receita financeira real do Nectar (valorAvulso + valorMensal das oportunidades vendidas)\n"
    "  var receitaAvulso = (NECTAR_LEADBOARD && NECTAR_LEADBOARD.receita_avulso_mes) || 0;\n"
    "  var mrrMes        = (NECTAR_LEADBOARD && NECTAR_LEADBOARD.mrr_mes) || 0;\n"
    "  // Receita total do mes: avulso + MRR. Se sem dados reais, usa vendas x ticket\n"
    "  var receitaMes = (receitaAvulso + mrrMes) > 0\n"
    "    ? (receitaAvulso + mrrMes)\n"
    "    : (vendasMes > 0 ? vendasMes * TICKET_MEDIO : null);\n"
    "  var cac  = vendasMes > 0 ? spendMes / vendasMes : null;\n"
    "  var roas = (receitaMes !== null && spendMes > 0) ? receitaMes / spendMes : null;\n"
)

if old_roas_calc in html:
    html = html.replace(old_roas_calc, new_roas_calc, 1)
    print("OK: receita calc added to renderKPIs")
else:
    print("FAIL: roas calc block not found")

# 2b. Histórico de receita para trend
old_hist_calc = (
    "  var vendasMesAnt = hist[String(mesAnt)] || hist[mesAntStr] || 0;\n"
    "  var cacAnt  = vendasMesAnt > 0 ? spendMesAnt / vendasMesAnt : null;\n"
    "  var roasAnt = (vendasMesAnt > 0 && spendMesAnt > 0) ? (vendasMesAnt * TICKET_MEDIO) / spendMesAnt : null;\n"
)
new_hist_calc = (
    "  var vendasMesAnt = hist[String(mesAnt)] || hist[mesAntStr] || 0;\n"
    "  var recHist = (NECTAR_LEADBOARD && NECTAR_LEADBOARD.receita_historico) || {};\n"
    "  var recAntObj = recHist[mesAntStr] || {};\n"
    "  var receitaMesAnt = ((recAntObj.avulso || 0) + (recAntObj.mrr || 0)) > 0\n"
    "    ? (recAntObj.avulso || 0) + (recAntObj.mrr || 0)\n"
    "    : (vendasMesAnt > 0 ? vendasMesAnt * TICKET_MEDIO : null);\n"
    "  var cacAnt     = vendasMesAnt > 0 ? spendMesAnt / vendasMesAnt : null;\n"
    "  var roasAnt    = (receitaMesAnt !== null && spendMesAnt > 0) ? receitaMesAnt / spendMesAnt : null;\n"
    "  var receitaTrend = (receitaMes !== null && receitaMesAnt !== null && receitaMesAnt > 0)\n"
    "    ? (receitaMes - receitaMesAnt) / receitaMesAnt * 100 : null;\n"
)

if old_hist_calc in html:
    html = html.replace(old_hist_calc, new_hist_calc, 1)
    print("OK: receita trend calc added")
else:
    print("FAIL: hist calc block not found")

# 2c. Adiciona KPI Receita antes de CAC no array
old_cac_kpi = (
    "    { label: 'CAC',             value: cac,\n"
    "      fmtFn: function(v) { return v !== null ? fmt.brl(v) : '--'; },"
)
new_receita_kpi = (
    "    { label: 'Receita',         value: receitaMes,\n"
    "      fmtFn: function(v) {\n"
    "        if (v === null) return '--';\n"
    "        return v >= 1000 ? 'R$' + (v/1000).toFixed(1) + 'k' : fmt.brl(v);\n"
    "      },\n"
    "      metric: null, trendMetric: null,\n"
    "      colorFn: function(v) { return v === null ? '#6B7280' : v > 0 ? '#10B981' : '#EF4444'; },\n"
    "      trendOverride: receitaTrend, trendLower: false },\n"
    "    { label: 'CAC',             value: cac,\n"
    "      fmtFn: function(v) { return v !== null ? fmt.brl(v) : '--'; },"
)

if old_cac_kpi in html:
    html = html.replace(old_cac_kpi, new_receita_kpi, 1)
    print("OK: Receita KPI added to array")
else:
    print("FAIL: CAC KPI not found")

# ── Checks ────────────────────────────────────────────────────────────────────
for c in ['receitaAvulso', 'mrrMes', 'receitaMes', 'Receita', 'receitaTrend',
          'receita_avulso_mes', 'mrr_mes', 'receita_historico']:
    print("CHECK:", c, "->", "OK" if c in html or c in ud else "MISSING")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\nDone.")
