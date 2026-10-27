import os
import re

# Analyze the main HTML for API routes and endpoints
with open('dashboard_brotli.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

print('=== Main HTML analysis ===')
print()

# Find all script references
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
print('--- Script files ---')
for s in scripts:
    print('  ' + s)
print()

# Find all href/script references that could be API endpoints
endpoints = re.findall(r'["\'](/[a-zA-Z0-9_./?=-]+)', html)
relevant = set()
for ep in endpoints:
    ep_clean = ep.strip('/')
    if ep_clean and not ep_clean.startswith('_next'):
        ep_lower = ep_clean.lower()
        if any(kw in ep_lower for kw in ['api', 'auth', 'login', 'withdraw', 'payout', 'balance', 'account', 'user', 'transaction', 'cashout', 'send', 'dashboard', 'profile', 'settings']):
            if len(ep_clean) < 150:
                relevant.add(ep_clean)

print('--- Relevant endpoints ---')
for ep in sorted(relevant):
    print('  ' + ep)
print()

# Find any mentions of endpoints in script tags
script_endpoints = re.findall(r'fetch\(\s*["\'](/[a-zA-Z0-9_/?=&-]+)["\']', html)
print('--- Fetch URLs in HTML ---')
for u in set(script_endpoints):
    print('  ' + u)
