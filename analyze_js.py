import os
import re

# Analyze all JS files for withdrawal/authorization endpoints
js_files = [f for f in os.listdir('js_files') if f.endswith('.js')]

for js_file in sorted(js_files):
    filepath = 'js_files/' + js_file
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print('=== ' + js_file + ' (len: ' + str(len(content)) + ') ===')
    
    # Look for API endpoint patterns
    api_patterns = re.findall(r'["\'](/[a-zA-Z0-9_/-]+)', content)
    for p in api_patterns:
        p_lower = p.lower()
        if any(kw in p_lower for kw in ['withdraw', 'withdrawal', 'account', 'auth', 'login', 'payout', 'balance', 'cashout', 'send', 'transfer']):
            if p not in ['/\",', '/\"', '/\\', '//', '/_next', '/_static']:
                print('  API: ' + p)
    
    # Look for endpoint patterns
    endpoint_patterns = re.findall(r'["\']([a-zA-Z0-9_/-]+(?:api|Api|API|withdraw|withdrawal|logout|login|auth|account|payout|balance|send|cashout)[a-zA-Z0-9_/-]*)[\'"]', content)
    for ep in set(endpoint_patterns):
        if len(ep) < 120:
            print('  Endpoint: ' + ep)
    
    # Look for fetch patterns
    fetch_patterns = re.findall(r'fetch\(\s*["\']([^"\']*)["\']', content)
    for fp in set(fetch_patterns):
        fp_lower = fp.lower()
        if any(kw in fp_lower for kw in ['api', 'http', 'withdraw', 'auth', 'login', 'logout']):
            print('  Fetch: ' + fp)
    
    # Look for headers mentioning authorization
    header_patterns = re.findall(r'["\']([^"\']*(?:authorization|Bearer|JWT|token|api[_-]?key)[^"\']*)["\']', content, re.IGNORECASE)
    for hp in set(header_patterns):
        if len(hp) < 150:
            print('  Header: ' + hp)
    
    # Look for post requests (ex: fetch(url, {method: 'POST'}))
    post_matches = re.findall(r'fetch\(\s*["\']([^"\']*)["\'][^)]*?method\s*:\s*["\'](?:POST|POST|post|post)["\'][^)]*?\)', content, re.IGNORECASE)
    for pm in set(post_matches):
        print('  Post: ' + pm)
    
    # Look for fx/post requests
    post_patterns2 = re.findall(r'post\(\s*["\']([^"\']*)["\']', content)
    for pp in set(post_patterns2):
        if len(pp) < 150:
            print('  Post: ' + pp)
    
    print()
