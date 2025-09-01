"""Test that PDF-level exclusions work with guides.extract_table()."""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

# Load the PDF
pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Add PDF-level exclusions
print("Adding PDF-level exclusions...")
pdf.add_exclusion(lambda page: page.find("text:contains(PREMISE)").above())
pdf.add_exclusion(lambda page: page.find("text:regex(Page \d+ of)"))

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
table_result = guides.extract_table(include_outer_boundaries=True, apply_exclusions=True)
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
else:
    print("\n✅ SUCCESS: Exclusions properly applied")

# Now test with page-level exclusions for comparison
print("\n\nTesting with page-level exclusions...")
page2 = pdf.pages[0]
header = page2.find("text:contains(PREMISE)").above()
footer = page2.find("text:regex(Page \d+ of)")

if header:
    page2.add_exclusion(header)
if footer:
    page2.add_exclusion(footer)

guides2 = Guides(page2)
guides2.vertical.from_content(headers, align='left')
guides2.horizontal.from_stripes()

table_result2 = guides2.extract_table(include_outer_boundaries=True)
df2 = table_result2.to_df()

print(f"\nTable shape with page exclusions: {df2.shape}")
table_text2 = df2.to_string()
has_alphabetic2 = "ALPHABETIC LISTING" in table_text2
has_page_num2 = "Page 1 of" in table_text2 or "Page" in table_text2 and "of" in table_text2

print(f"Contains 'ALPHABETIC LISTING': {has_alphabetic2}")
print(f"Contains 'Page X of Y': {has_page_num2}")

if has_alphabetic2 or has_page_num2:
    print("\n❌ FAILED: Page exclusions not properly applied")
else:
    print("\n✅ SUCCESS: Page exclusions properly applied")

# Debug: Check exclusion regions
print("\n\nDebug: Checking exclusion regions...")
exclusions = page._get_exclusion_regions(debug=True)
print(f"\nTotal exclusion regions: {len(exclusions)}")