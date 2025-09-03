from natural_pdf import PDF
from natural_pdf.selectors.parser import parse_selector, _build_filter_list
import difflib

# Test parsing
selector_str = 'text:closest("Durham@0.7")'
parsed = parse_selector(selector_str)
print("Parsed selector:", parsed)
print("Args:", repr(parsed['pseudo_classes'][0]['args']))

# Build filters
filters = _build_filter_list(parsed)
print("\nFilters built:", filters)

# Test similarity calculation manually
search_text = "Durham"
test_texts = ["Durham's Meatpacking  ", "Chicago, Ill.", "Violations"]

print(f"\nTesting similarity for '{search_text}':")
for text in test_texts:
    ratio = difflib.SequenceMatcher(None, search_text.lower(), text.lower()).ratio()
    print(f"  '{text}' -> ratio: {ratio:.3f}")