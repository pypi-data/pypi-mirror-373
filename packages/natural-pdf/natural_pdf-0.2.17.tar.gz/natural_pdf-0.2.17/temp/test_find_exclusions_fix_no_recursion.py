"""Test that the find methods now work with PDF-level exclusions (without recursion)."""

from natural_pdf import PDF

# Load a test PDF
pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Add PDF-level exclusion using a Region directly to avoid recursion
# First, get the header region without exclusions
header_element = page.find(text="PREMISE", apply_exclusions=False)
if header_element:
    header_region = header_element.above()
    pdf.add_exclusion(header_region)
else:
    print("WARNING: Could not find PREMISE text for exclusion")

# Test 1: find() should now exclude the header text
print("Test 1: find() with PDF-level exclusions")
result = page.find("text:contains(FEBRUARY)", apply_exclusions=True)
if result is None:
    print("✅ SUCCESS: find() correctly excluded header text")
else:
    print(f"❌ FAILED: find() returned {result.text}")

# Test 2: find_all() should exclude header elements
print("\nTest 2: find_all() with PDF-level exclusions")
all_text = page.find_all("text", apply_exclusions=False)
filtered_text = page.find_all("text", apply_exclusions=True)
print(f"Without exclusions: {len(all_text)} elements")
print(f"With exclusions: {len(filtered_text)} elements")
if len(filtered_text) < len(all_text):
    print("✅ SUCCESS: find_all() excluded some elements")
else:
    print("❌ FAILED: find_all() didn't exclude any elements")

# Test 3: get_elements() should exclude header elements
print("\nTest 3: get_elements() with PDF-level exclusions")
all_elements = page.get_elements(apply_exclusions=False)
filtered_elements = page.get_elements(apply_exclusions=True)
print(f"Without exclusions: {len(all_elements)} elements")
print(f"With exclusions: {len(filtered_elements)} elements")
if len(filtered_elements) < len(all_elements):
    print("✅ SUCCESS: get_elements() excluded some elements")
else:
    print("❌ FAILED: get_elements() didn't exclude any elements")

# Test that excluded text is not in the filtered results
print("\nChecking excluded text...")
excluded_texts = ["FEBRUARY", "ALPHABETIC LISTING", "M27"]
for text in excluded_texts:
    found_in_filtered = any(
        text in str(el.text) if hasattr(el, 'text') else False 
        for el in filtered_text
    )
    if not found_in_filtered:
        print(f"✅ '{text}' correctly excluded")
    else:
        print(f"❌ '{text}' still present in filtered results")

# Also test that the original table extraction issue is fixed
print("\n\nTesting original table extraction issue...")
from natural_pdf.analyzers.guides import Guides

# Add exclusion for footer too
footer_element = page.find("text:regex(Page \\d+ of)", apply_exclusions=False)
if footer_element:
    pdf.add_exclusion(footer_element.expand())

headers = (
    page
    .find(text="NUMBER", apply_exclusions=False)
    .right(include_source=True)
    .expand(top=3, bottom=3)
    .find_all('text')
)

guides = Guides(page)
guides.vertical.from_content(headers, align='left')
guides.horizontal.from_stripes()

result = guides.extract_table(include_outer_boundaries=True, apply_exclusions=True, header=False)
df = result.to_df()

# Check if excluded content is in the table
table_str = df.to_string()
has_feb = "FEBRUARY" in table_str
has_alphabetic = "ALPHABETIC LISTING" in table_str

print(f"\nTable extraction with exclusions:")
print(f"Contains 'FEBRUARY': {has_feb}")
print(f"Contains 'ALPHABETIC LISTING': {has_alphabetic}")

if not has_feb and not has_alphabetic:
    print("✅ SUCCESS: Table extraction correctly excludes header/footer!")
else:
    print("❌ FAILED: Exclusions not working in table extraction")