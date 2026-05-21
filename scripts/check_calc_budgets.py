import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', encoding='utf-8') as f:
    content = f.read()

# calc_budgets
s = content.find('def calc_budgets(')
e = content.find('\ndef ', s + 1)
print("=== calc_budgets ===")
print(content[s:e])

# CAMPAIGN_META
s2 = content.find('CAMPAIGN_META')
print("\n=== CAMPAIGN_META ===")
print(content[s2:s2+600])
