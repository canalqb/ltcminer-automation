import os
import re

# Analyze all JS files for withdrawal/payment transaction patterns
js_files = [f for f in os.listdir('js_files') if f.endswith('.js')]

for fname in sorted(js_files):
    filepath = 'js_files/' + fname
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Look for payment/withdrawal/cashout related patterns
    patterns = [
        ('payment', 'PAYMENT'),
        ('cashout', 'CASHOUT'),
        ('payout', 'PAYOUT'),
        ('withdraw', 'WITHDRAW'),
        ('transfer', 'TRANSFER'),
        ('send', 'SEND'),
        ('ledger', 'LEDGER'),
        ('transaction', 'TRANSACTION'),
        ('network', 'NETWORK'),
        ('api_url', 'API_URL'),
        ('base_url', 'BASE_URL'),
        ('task_api', 'TASK_API'),
    ]
    
    for keyword, label in patterns:
        matches = list(re.finditer(keyword, content, re.IGNORECASE))
        if matches:
            print('=== ' + fname + ' - [' + label + '] ===')
            for i, m in enumerate(matches[:5]):
                start = max(0, m.start() - 100)
                end = min(len(content), m.end() + 200)
                ctx = content[start:end].replace('\n', ' ')[:300]
                print('  ...' + ctx + '...')
            print()
