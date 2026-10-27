import os
import re

# Analyze the largest JS files more deeply
large_files = ['_next_static_chunks_13gbu0ktm8n5k.js.js', '_next_static_chunks_0ni-8dyxk08xj.js.js']

for fname in large_files:
    filepath = 'js_files/' + fname
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print('=' * 60)
    print('FILE: ' + fname)
    print('=' * 60)
    print('Total length:', len(content))
    print()
    
    # Search for withdrawal related keywords (case insensitive)
    patterns_to_search = [
        'withdraw',
        'Payment',
        'payout',
        'balance',
        'cashout',
        'transfer',
        'send',
        'transaction',
        'Transaction',
        'return',
    ]
    
    for pattern in patterns_to_search:
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL))
        if matches:
            # Show first 3 matches with context
            for i, m in enumerate(matches[:3]):
                start = max(0, m.start() - 80)
                end = min(len(content), m.end() + 150)
                context = content[start:end].replace('\n', ' ')[:230]
                print('  [' + pattern.upper() + '] ...' + context + '...')
            print()
