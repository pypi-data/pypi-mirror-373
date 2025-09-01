"""Test that the fix for region exclusions works"""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Check initial text
print("Initial text:")
print(page.extract_text()[:200])

# Add exclusions
pdf.add_exclusion(lambda page: page.find(text="PREMISE").above())
pdf.add_exclusion(lambda page: page.find("text:regex(Page \d+ of)").expand())

# Test region extraction with exclusions
print("\n\nRegion in excluded area (0, 0, 200, 50):")
excluded_region = page.region(0, 0, 200, 50)
print("Without exclusions:", repr(excluded_region.extract_text(apply_exclusions=False)))
print("With exclusions:", repr(excluded_region.extract_text(apply_exclusions=True)))

# Now test the full table extraction
print("\n\nFull table extraction:")
headers = (
    page
    .find(text="NUMBER")
    .right(include_source=True)
    .expand(top=3, bottom=3)
    .find_all('text')
)

guides = Guides(page)
guides.vertical.from_content(headers, align='left')
guides.horizontal.from_stripes()

result = guides.extract_table(include_outer_boundaries=True, apply_exclusions=True, header=False)
df = result.to_df()

print(f"Shape: {df.shape}")
print("\nFirst row:")
for col, val in df.iloc[0].items():
    print(f"  {repr(col)}: {repr(val)}")

# Check if excluded content is in the table
table_str = df.to_string()
has_feb = "FEBRUARY" in table_str or "FEBR" in table_str and "RUARY" in table_str
has_alphabetic = "ALPHABETIC LISTING" in table_str

print(f"\nContains 'FEBRUARY': {has_feb}")
print(f"Contains 'ALPHABETIC LISTING': {has_alphabetic}")

if has_feb or has_alphabetic:
    print("\n❌ FAILED: Exclusions not working properly")
else:
    print("\n✅ SUCCESS: Exclusions working correctly!")