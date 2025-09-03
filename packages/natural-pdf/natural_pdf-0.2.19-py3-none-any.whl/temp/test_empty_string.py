from natural_pdf import PDF
from natural_pdf.selectors.parser import parse_selector

# Test parsing empty string
selector_str = 'text:closest("")'
parsed = parse_selector(selector_str)
print("Parsed selector:", parsed)
print("Args:", repr(parsed['pseudo_classes'][0]['args']))

# Test with actual PDF
pdf = PDF('pdfs/01-practice.pdf')
page = pdf.pages[0]

# Try the selector
results = page.find_all('text:closest("")')
print(f"Results with empty string: {len(results)}")