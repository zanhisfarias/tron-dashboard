import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open(r'C:\Users\Marketing\Desktop\update_dashboard.py', encoding='utf-8') as f:
    ud = f.read()

s = ud.find('def build_js_block(')
e = ud.find('\ndef ', s + 1)
print(ud[s:e])
