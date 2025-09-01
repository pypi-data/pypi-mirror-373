"""Test exclusion with detailed debugging"""
from natural_pdf import PDF

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Add exclusion
pdf.add_exclusion(lambda page: page.find(text="PREMISE").above(), label="header")

# First, verify the exclusion works on the page itself
print("Page-level text extraction:")
print("Without exclusions:", page.extract_text(apply_exclusions=False)[:100])
print("With exclusions:", page.extract_text(apply_exclusions=True)[:100])

# Now test on a specific region that should be excluded
print("\n\nRegion in excluded area (0, 0, 200, 50):")
excluded_region = page.region(0, 0, 200, 50)
print("Without exclusions:", repr(excluded_region.extract_text(apply_exclusions=False)))
print("With exclusions:", repr(excluded_region.extract_text(apply_exclusions=True)))

# Test the actual problematic cell region
print("\n\nProblematic cell region (32.06, 0.5, 73.18, 79.54):")
cell_region = page.region(32.06, 0.5, 73.18288, 79.54)
print("Without exclusions:", repr(cell_region.extract_text(apply_exclusions=False)))
print("With exclusions:", repr(cell_region.extract_text(apply_exclusions=True)))

# Check if the region inherits the page
print(f"\nCell region's page: {cell_region.page}")
print(f"Cell region's _page: {getattr(cell_region, '_page', 'Not found')}")
print(f"Same as original page: {cell_region.page is page if hasattr(cell_region, 'page') else 'N/A'}")