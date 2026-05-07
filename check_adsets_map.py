import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', encoding='utf-8') as f:
    content = f.read()

# fetch_adsets
s = content.find('def fetch_adsets(')
e = content.find('\ndef ', s + 1)
print("=== fetch_adsets ===")
print(content[s:e])

# CAMPAIGN_IDS
s2 = content.find('CAMPAIGN_IDS')
print("\n=== CAMPAIGN_IDS ===")
print(content[s2:s2+400])
