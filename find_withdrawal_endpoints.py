import os
import re

# Read all JS files
js_files = os.listdir('js_files')
for fname in sorted(js_files):
    filepath = 'js_files/' + fname
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Search for withdrawal-related API patterns
    withdrawal_patterns = [
        r'["\'](/[a-zA-Z0-9_-]+/withdraw[a-zA-Z0-9_?-]*)["\']',
        r'["\'](/[a-zA-Z0-9_-]+/cashout[a-zA-Z0-9_?-]*)["\']',
        r'["\'](/[a-zA-Z0-9_-]+/payout[a-zA-Z0-9_?-]*)["\']',
        r'["\'](/[a-zA-Z0-9_-]+/payment[a-zA-Z0-9_?-]*)["\']',
        r'["\'](/[a-zA-Z0-9_-]+/transfer[a-zA-Z0-9_?-]*)["\']',
        r'["\'](/[a-zA-Z0-9_-]+/send[a-zA-Z0-9_?-]*)["\']',
        r'["\'](/[a-zA-Z0-9_-]+/deposit[a-zA-Z0-9_?-]*)["\']',
        r'["\'](/[a-zA-Z0-9_-]+/withdrawal[a-zA-Z0-9_?-]*)["\']',
    ]
    
    for pattern in withdrawal_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for m in set(matches):
            print(fname + ': ' + m)
