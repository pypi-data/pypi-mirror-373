"""Test the fix with the actual PDF from the user's example."""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Get headers using the user's exact code
headers = (
    page
    .find("text:contains(NUMBER)")
    .right(include_source=True)
    .expand(top=3, bottom=3)
    .find_all('text')
)

print("Headers found:")
for i, h in enumerate(headers):
    print(f"  {i}: '{h.text}' at x={h.x0:.2f}")

# Create guides using ElementCollection
guides = Guides(page)
guides.vertical.from_content(headers, align='left', outer=False)

print(f"\nResulting vertical guides: {sorted(guides.vertical)}")

# Check specific headers that were problematic
print("\nChecking headers 3-5:")
for i, h in enumerate(headers[3:5]):
    print(f"  Header {i+3}: '{h.text}' at x={h.x0:.5f}")

# Test with just headers 3-5
guides2 = Guides(page)
guides2.vertical.from_content(headers[3:5], align='left', outer=False) 

print(f"\nGuides from headers[3:5]: {guides2.vertical}")
print(f"Expected: [328.32012, 539.63316]")

# Verify the fix
if 332.88095999999996 in guides2.vertical:
    print("\n❌ FAILED: Extra guide at 332.88 is still present")
else:
    print("\n✅ SUCCESS: Extra guide at 332.88 is not present")

# Test that outer guides work correctly too
guides3 = Guides(page)
guides3.vertical.from_content(headers[3:5], align='left', outer=True)
print(f"\nWith outer=True: {guides3.vertical}")