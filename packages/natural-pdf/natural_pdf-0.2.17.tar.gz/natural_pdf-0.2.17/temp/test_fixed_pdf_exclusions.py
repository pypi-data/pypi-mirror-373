"""Test PDF-level exclusions with proper Region returns."""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

# Load the PDF
pdf = PDF("pdfs/m27.pdf")

# Add PDF-level exclusions that properly return Regions
print("Adding fixed PDF-level exclusions...")
pdf.add_exclusion(
    lambda page: page.find("text:contains(PREMISE)").above() 
    if page.find("text:contains(PREMISE)") else None,
    label="header_exclusion"
)
pdf.add_exclusion(
    lambda page: page.find("text:regex(Page \d+ of)").expand(10) 
    if page.find("text:regex(Page \d+ of)") else None,
    label="footer_exclusion"
)

page = pdf.pages[0]

# Create guides and extract table
print("\nCreating guides and extracting table...")
headers = (
    page
    .find("text:contains(NUMBER)")
    .right(include_source=True)
    .expand(top=3, bottom=3)
    .find_all('text')
)

guides = Guides(page)
guides.vertical.from_content(headers, align='left')
guides.horizontal.from_stripes()

# Extract table with apply_exclusions=True (default)
table_result = guides.extract_table(include_outer_boundaries=True)
df = table_result.to_df()

print(f"\nTable shape: {df.shape}")
print("\nFirst few rows:")
print(df.head())

# Check if excluded content is present
print("\nChecking for excluded content...")
table_text = df.to_string()
has_alphabetic = "ALPHABETIC LISTING" in table_text
has_page_num = "Page 1 of" in table_text or "Page" in table_text and "of" in table_text

print(f"Contains 'ALPHABETIC LISTING': {has_alphabetic}")
print(f"Contains 'Page X of Y': {has_page_num}")

if has_alphabetic or has_page_num:
    print("\n❌ FAILED: Exclusions not properly applied")
    # Show what's in the first row/column that should be excluded
    print("\nFirst column values (should not have header text):")
    print(df.iloc[:5, 0])
else:
    print("\n✅ SUCCESS: Exclusions properly applied")

# Debug: Check exclusion regions
print("\n\nDebug: Checking exclusion regions...")
exclusions = page._get_exclusion_regions(debug=True)
print(f"\nTotal exclusion regions: {len(exclusions)}")
for i, exc in enumerate(exclusions):
    print(f"  Exclusion {i}: {exc.bbox} (label: {exc.label})")