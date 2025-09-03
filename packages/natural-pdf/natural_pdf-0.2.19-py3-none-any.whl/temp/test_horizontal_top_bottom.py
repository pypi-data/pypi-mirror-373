"""Test horizontal guides with top/bottom alignment on real PDF."""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

# Load the PDF
pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Find some row headers to use as markers
# First, let's find what text elements exist
all_text = page.find_all('text')[:20]
print("First 20 text elements:")
for t in all_text:
    print(f"  '{t.text}' at y={t.top:.2f}")

# Look for rows containing numbers in the first column
rows = page.find_all('text[x0<100]')[:5]  # Get elements in left column

print("Found rows:")
for i, row in enumerate(rows):
    print(f"  {i}: '{row.text}' at y={row.top:.2f}-{row.bottom:.2f}")

# Test with align='top' (should use top edge of each row)
guides_top = Guides(page)
guides_top.horizontal.from_content(rows, align='top', outer=False)

print(f"\nHorizontal guides with align='top': {sorted(guides_top.horizontal)}")
print("Expected: top edges of each row")

# Test with align='bottom' (should use bottom edge of each row)
guides_bottom = Guides(page)
guides_bottom.horizontal.from_content(rows, align='bottom', outer=False)

print(f"\nHorizontal guides with align='bottom': {sorted(guides_bottom.horizontal)}")
print("Expected: bottom edges of each row")

# Verify they're different
if guides_top.horizontal != guides_bottom.horizontal:
    print("\n✅ SUCCESS: top and bottom alignment produce different guides")
else:
    print("\n❌ FAILED: top and bottom alignment produced the same guides")

# Test the class method too
guides_class_top = Guides.from_content(page, axis='horizontal', markers=rows, align='top', outer=False)
guides_class_bottom = Guides.from_content(page, axis='horizontal', markers=rows, align='bottom', outer=False)

print(f"\nClass method with top: {sorted(guides_class_top.horizontal)}")
print(f"Class method with bottom: {sorted(guides_class_bottom.horizontal)}")

if guides_class_top.horizontal == guides_top.horizontal and guides_class_bottom.horizontal == guides_bottom.horizontal:
    print("\n✅ SUCCESS: Class method produces same results as instance method")
else:
    print("\n❌ FAILED: Class method produces different results")