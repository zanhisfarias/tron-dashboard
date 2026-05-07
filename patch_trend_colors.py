with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    html = f.read()

# Substitui a lógica de cor do trend — simplifica para:
# positivo (aumento) = verde, negativo (queda) = vermelho
old_color_logic = (
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
    "      }"
)

new_color_logic = (
    "      if (t !== null) {\n"
    "        var tSign  = t >= 0 ? '+' : '';\n"
    "        var tClass = t > 0 ? 'trend-up' : t < 0 ? 'trend-down' : 'text-muted';\n"
    "        var tIcon  = t > 1 ? '\\u2191' : t < -1 ? '\\u2193' : '\\u2192';\n"
    "        trendHtml = '<div class=\"flex flex-col items-end flex-shrink-0\">' +\n"
    "          '<span class=\"text-[9px] md:text-[10px] ' + tClass + ' font-semibold leading-none\">' + tIcon + tSign + t.toFixed(0) + '%</span>' +\n"
    "          '<span class=\"text-[8px] text-muted font-normal leading-none mt-0.5\">vs ' + refLabel + '</span>' +\n"
    "          '</div>';\n"
    "      } else {\n"
    "        trendHtml = '<span class=\"text-[8px] text-muted font-normal flex-shrink-0\">sem hist.</span>';\n"
    "      }"
)

if old_color_logic in html:
    html = html.replace(old_color_logic, new_color_logic, 1)
    print("OK: trend color logic simplified")
else:
    print("FAIL: color logic block not found")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done.")
