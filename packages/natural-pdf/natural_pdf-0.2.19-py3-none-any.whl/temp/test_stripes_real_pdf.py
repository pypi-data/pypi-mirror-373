"""Test from_stripes with a real PDF that has striped rows."""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

# Load the PDF (assuming m27.pdf has the striped table)
pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Test 1: Manual selection with specific color
print("Test 1: Manual selection with color='#00ffff'")
guides = Guides(page)
guides.horizontal.from_stripes(color='#00ffff')

print(f"Found {len(guides.horizontal)} horizontal guides")
if guides.horizontal:
    print(f"Guide range: {min(guides.horizontal):.2f} to {max(guides.horizontal):.2f}")
    print(f"First 5 guides: {sorted(guides.horizontal)[:5]}")

# Test 2: Auto-detect most common stripe color
print("\nTest 2: Auto-detect stripes")
guides2 = Guides(page)
guides2.horizontal.from_stripes()

print(f"Found {len(guides2.horizontal)} horizontal guides")
if guides2.horizontal:
    print(f"Guide range: {min(guides2.horizontal):.2f} to {max(guides2.horizontal):.2f}")

# Test 3: Manual selection of stripes
print("\nTest 3: Manual selection of stripe elements")
cyan_stripes = page.find_all('rect[fill=#00ffff]')
print(f"Found {len(cyan_stripes)} cyan rectangles")

if cyan_stripes:
    guides3 = Guides(page)
    guides3.horizontal.from_stripes(cyan_stripes)
    print(f"Created {len(guides3.horizontal)} guides from stripes")
    
    # Show how this captures both edges of each stripe
    print("\nFirst stripe edges:")
    first_stripe = cyan_stripes[0]
    print(f"  Stripe at y={first_stripe.top:.2f} to {first_stripe.bottom:.2f}")
    print(f"  Guides include: {first_stripe.top:.2f} in guides? {first_stripe.top in guides3.horizontal}")
    print(f"  Guides include: {first_stripe.bottom:.2f} in guides? {first_stripe.bottom in guides3.horizontal}")

# Test 4: Compare with traditional approach
print("\nComparison with traditional from_content approach:")
# Traditional way would only get one edge per stripe
guides4 = Guides(page)
guides4.horizontal.from_content(cyan_stripes, align='top', outer=False)
print(f"from_content (top only): {len(guides4.horizontal)} guides")

guides5 = Guides(page)
guides5.horizontal.from_content(cyan_stripes, align='bottom', outer=False)
print(f"from_content (bottom only): {len(guides5.horizontal)} guides")

print(f"from_stripes (both edges): {len(guides3.horizontal)} guides")

# Verify we get approximately 2x guides with from_stripes
if len(cyan_stripes) > 0:
    expected_guides = len(set([s.top for s in cyan_stripes] + [s.bottom for s in cyan_stripes]))
    print(f"\nExpected unique edges: {expected_guides}")
    print(f"Actual from_stripes: {len(guides3.horizontal)}")