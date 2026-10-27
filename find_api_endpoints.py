import os
import re

# Read all JS files
js_files = os.listdir('js_files')
for fname in sorted(js_files):
    filepath = 'js_files/' + fname
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Look for specific patterns related to API calls
    # Search for patterns like: fetch('...', {method: 'POST'}), or axios.post
    patterns = [
        # Post requests
        r'fetch\(\s*["\']([^"\']+)["\']\s*,\s*\{[^}]*?method\s*:\s*["\'](?:POST|POST|post)["\'][^}]*?\}\)',
        # Post with {method: 'POST'}
        r'["\']([^"\']+)["\'][^)]*?,\{[^}]*?method\s*:\s*["\'](?:POST|POST|post)["\']',
        # axios calls
        r'axios\.(get|post|put|delete)\(\s*["\']([^"\']+)["\']',
        # fetch with method
        r'fetch\(\s*["\']([^"\']+)["\']',
        # URL patterns
        r'[\"\'](/[a-zA-Z0-9_/-]+)["\']',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for m in set(matches):
            if len(m) < 150:
                print(f'{fname}: {m}')
