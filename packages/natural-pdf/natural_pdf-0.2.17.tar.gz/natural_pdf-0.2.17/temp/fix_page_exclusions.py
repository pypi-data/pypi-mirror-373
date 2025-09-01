"""Script to fix the remaining exclusion bugs in page.py"""

import re

# Read the file
with open('/Users/soma/Development/natural-pdf/natural_pdf/core/page.py', 'r') as f:
    content = f.read()

# Fix 1: Line 1132 in find() method
# Change: if apply_exclusions and self._exclusions and results_collection:
# To: if apply_exclusions and results_collection:
content = re.sub(
    r'(\s+)if apply_exclusions and self\._exclusions and results_collection:',
    r'\1if apply_exclusions and results_collection:',
    content
)

# Fix 2: Line 1227 in find_all() method
# Same change pattern
content = re.sub(
    r'(\s+)if apply_exclusions and self\._exclusions and results_collection:',
    r'\1if apply_exclusions and results_collection:',
    content
)

# Fix 3: Line 1599 in get_elements() method
# Change: if apply_exclusions and self._exclusions:
# To: if apply_exclusions:
content = re.sub(
    r'(\s+)if apply_exclusions and self\._exclusions:',
    r'\1if apply_exclusions:',
    content
)

# Write the fixed content back
with open('/Users/soma/Development/natural-pdf/natural_pdf/core/page.py', 'w') as f:
    f.write(content)

print("Fixed exclusion checks in page.py")
print("- find() method: removed self._exclusions check")
print("- find_all() method: removed self._exclusions check")
print("- get_elements() method: removed self._exclusions check")