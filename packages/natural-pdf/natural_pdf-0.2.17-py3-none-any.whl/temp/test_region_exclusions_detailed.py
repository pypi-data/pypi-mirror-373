"""Test region exclusions with detailed debugging"""
from natural_pdf import PDF

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Add exclusion
pdf.add_exclusion(lambda page: page.find(text="PREMISE").above(), label="header")

# Get page exclusions
print("Page exclusions:")
print(f"page._exclusions: {page._exclusions}")
print(f"pdf._exclusions: {pdf._exclusions}")

# Create a region in the excluded area
test_region = page.region(0, 0, 200, 50)
print(f"\nTest region: {test_region.bbox}")
print(f"Region's page: {test_region.page}")
print(f"Region's _page: {test_region._page}")
print(f"Region's _page._exclusions: {test_region._page._exclusions}")

# Try extraction with debug
print("\nExtracting with debug=True:")
text = test_region.extract_text(apply_exclusions=True, debug=True)
print(f"Result: '{text}'")