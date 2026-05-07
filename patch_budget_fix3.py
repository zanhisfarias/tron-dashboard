with open(r'C:\Users\Marketing\Desktop\dashboard.html', encoding='utf-8') as f:
    html = f.read()

# applyLiveData: adiciona total_daily_budget
old_apply = (
    "  if (d.campaigns)        CAMPAIGNS        = d.campaigns;\n"
    "  if (d.all_dates)        ALL_DATES        = d.all_dates;\n"
    "  if (d.all_data)         ALL_DATA         = d.all_data;\n"
    "  if (d.adsets_raw)       ADSETS_RAW       = d.adsets_raw;\n"
    "  if (d.adset_metrics)    ADSET_METRICS    = d.adset_metrics;\n"
    "  if (d.creatives)        CREATIVES        = d.creatives;\n"
    "  if (d.nectar_leadboard) NECTAR_LEADBOARD = d.nectar_leadboard;\n"
)
new_apply = (
    "  if (d.campaigns)          CAMPAIGNS          = d.campaigns;\n"
    "  if (d.all_dates)          ALL_DATES          = d.all_dates;\n"
    "  if (d.all_data)           ALL_DATA           = d.all_data;\n"
    "  if (d.adsets_raw)         ADSETS_RAW         = d.adsets_raw;\n"
    "  if (d.adset_metrics)      ADSET_METRICS      = d.adset_metrics;\n"
    "  if (d.creatives)          CREATIVES          = d.creatives;\n"
    "  if (d.nectar_leadboard)   NECTAR_LEADBOARD   = d.nectar_leadboard;\n"
    "  if (d.total_daily_budget) TOTAL_DAILY_BUDGET = d.total_daily_budget;\n"
)

if old_apply in html:
    html = html.replace(old_apply, new_apply, 1)
    print("OK: applyLiveData updated")
else:
    print("FAIL: applyLiveData block not found")

with open(r'C:\Users\Marketing\Desktop\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done.")
