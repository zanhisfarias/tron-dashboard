import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', encoding='utf-8') as f:
    content = f.read()
start = content.find('def fetch_nectar_leadboard(')
end   = content.find('\ndef ', start + 1)
print(content[start:end])
