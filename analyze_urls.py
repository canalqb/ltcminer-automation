import os
import re

# Search for all URL patterns in JS files that look like API calls
js_files = [f for f in os.listdir('js_files') if f.endswith('.js')]

for fname in sorted(js_files):
    filepath = 'js_files/' + fname
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find all URL patterns
    urls = re.findall(r'["\']((?:https?://)?[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9_./?-]*)?)[\'"]', content)
    for u in urls:
        u_clean = u.strip('"\'')
        if len(u_clean) < 200:
            # Check if it looks like an API endpoint
            u_lower = u_clean.lower()
            if any(kw in u_lower for kw in ['api', 'auth', 'login', 'withdraw', 'task', 'cashout', 'balance', 'payout', 'transfer', 'payment', 'send', 'user', 'account']):
                print('  ' + fname + ': ' + u_clean)
