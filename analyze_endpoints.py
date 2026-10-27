import os
import re

# Analyze all JS files for withdrawal/transaction related patterns
js_files = [f for f in os.listdir('js_files') if f.endswith('.js')]

for fname in sorted(js_files):
    filepath = 'js_files/' + fname
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print('=' * 60)
    print('FILE: ' + fname)
    print('=' * 60)
    print('Total length:', len(content))
    print()
    
    # Find all variable assignments with __ prefixes (window globals)
    window_globals = re.findall(r'window\.(__[a-zA-Z0-9_]+)\s*=', content)
    for g in sorted(set(window_globals)):
        print('  Window Global: window.' + g)
    
    # Find all endpoint patterns
    print()
    print('--- Endpoints ---')
    endpoints = re.findall(r'[\"\'](/[a-zA-Z0-9_/-]+)', content)
    for ep in sorted(set(endpoints)):
        ep_lower = ep.lower()
        if any(kw in ep_lower for kw in ['api', 'auth', 'login', 'withdraw', 'balance', 'payout', 'account', 'user', 'send', 'cashout', 'transaction']):
            if not ep.startswith('//') and '/_next' not in ep:
                print('  ' + ep)
    
    # Find fetch URLs
    print()
    print('--- Fetch URLs ---')
    fetch_urls = re.findall(r'fetch\(\s*[\"\']([^\"\']*)[\"\']', content)
    for fu in sorted(set(fetch_urls)):
        fu_lower = fu.lower()
        if any(kw in fu_lower for kw in ['api', 'http', 'withdraw', 'auth', 'login', 'logout', 'account', 'user', 'balance', 'payout']):
            print('  ' + fu)
    
    # Find all /auth.php references (the site may use a mix of routes)
    print()
    print('--- Auth/PHP references ---')
    auth_refs = re.findall(r'[\"\'](/[a-zA-Z0-9_/.-]*auth[a-zA-Z0-9_/.-]*)', content, re.IGNORECASE)
    for ar in sorted(set(auth_refs)):
        print('  ' + ar)
    
    # Find all /api references
    print()
    print('--- API references ---')
    api_refs = re.findall(r'[\"\'](/api/[a-zA-Z0-9_/-]*)', content)
    for ar in sorted(set(api_refs)):
        print('  ' + ar)
    
    print()
