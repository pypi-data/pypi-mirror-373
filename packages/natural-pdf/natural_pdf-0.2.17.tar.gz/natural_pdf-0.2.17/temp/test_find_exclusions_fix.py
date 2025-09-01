"""Test that the find methods now work with PDF-level exclusions."""

from natural_pdf import PDF

# Load a test PDF
pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Add PDF-level exclusion for the header
pdf.add_exclusion(lambda page: page.find(text="PREMISE").above())

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