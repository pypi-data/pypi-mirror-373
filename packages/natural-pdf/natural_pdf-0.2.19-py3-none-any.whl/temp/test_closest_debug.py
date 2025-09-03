from natural_pdf import PDF
from natural_pdf.selectors.parser import parse_selector, selector_to_filter_func

# Test parsing
selector_str = 'text:closest("Durham@0.7")'
parsed = parse_selector(selector_str)
print("Parsed selector:", parsed)

# Test with actual PDF
pdf = PDF('pdfs/01-practice.pdf')
page = pdf.pages[0]

# Get all text elements
all_text = page.find_all('text')
print(f"\nTotal text elements: {len(all_text)}")

# Test the selector
results = page.find_all('text:closest("Durham@0.7")')
print(f"Results with :closest selector: {len(results)}")

# Let's manually test the filter function
filter_func = selector_to_filter_func(parsed)
print("\nTesting filter function manually:")
for i, el in enumerate(all_text[:5]):
    match = filter_func(el)
    print(f"  Element {i}: '{el.text}' -> {match}")