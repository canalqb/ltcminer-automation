import os
import re

# Analyze all JS files for withdrawal/payment API endpoints
js_files = [f for f in os.listdir('js_files') if f.endswith('.js')]

for fname in sorted(js_files):
    filepath = 'js_files/' + fname
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print('=' * 60)
    print('FILE: ' + fname)
    print('=' * 60)
    print('Length:', len(content))
    print()
    
    # Find all fetch URLs
    fetch_urls = re.findall(r'fetch\(\s*["\']([^"\']*)["\']', content)
    for fu in sorted(set(fetch_urls)):
        fu_lower = fu.lower()
        if any(kw in fu_lower for kw in ['api', 'http', 'withdraw', 'auth', 'login', 'logout', 'account', 'user', 'balance', 'payout', 'task']):
            print('Fetch URL: ' + fu)
    
    # Find all /api/ or /auth/ or /task/ endpoints
    endpoints = re.findall(r'["\'](/[a-zA-Z0-9_/-]+)', content)
    for ep in sorted(set(endpoints)):
        ep_lower = ep.lower()
        if any(kw in ep_lower for kw in ['api', 'auth', 'login', 'withdraw', 'payout', 'balance', 'account', 'user', 'task', 'ltcminer']):
            if len(ep) < 150 and not ep.startswith('//'):
                print('Endpoint: ' + ep)
    
    # Look for window variables related to balance/payout
    window_vars = re.findall(r'window\.(__[a-zA-Z0-9_]+)\s*=', content)
    for vw in sorted(set(window_vars)):
        print('Window Variable: window.' + vw)
    
    print()
