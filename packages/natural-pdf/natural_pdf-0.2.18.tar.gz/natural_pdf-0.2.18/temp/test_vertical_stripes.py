"""Test from_stripes with vertical stripes (column backgrounds)."""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

# Create a mock page with vertical stripes (simulating column backgrounds)
class MockRect:
    def __init__(self, fill, x0, x1, top, bottom):
        self.fill = fill
        self.x0 = x0
        self.x1 = x1
        self.top = top
        self.bottom = bottom

class MockPage:
    def __init__(self):
        self.bbox = (0, 0, 800, 600)
        # Create vertical stripes for alternating columns
        self.stripes = [
            MockRect('#f0f0f0', 100, 200, 0, 600),  # Column 1 background
            MockRect('#f0f0f0', 300, 400, 0, 600),  # Column 3 background
            MockRect('#f0f0f0', 500, 600, 0, 600),  # Column 5 background
        ]
        
    def find_all(self, selector):
        if selector == 'rect[fill=#f0f0f0]':
            return self.stripes
        elif selector == 'rect[fill]':
            # Include some other rects too
            return self.stripes + [
                MockRect('#ffffff', 0, 100, 0, 600),
                MockRect('#ffffff', 200, 300, 0, 600),
            ]
        return []

# Test vertical stripes
page = MockPage()
guides = Guides(page)

print("Testing vertical stripes (column backgrounds)")
guides.vertical.from_stripes(color='#f0f0f0')

print(f"\nFound {len(guides.vertical)} vertical guides")
print(f"Guides at: {sorted(guides.vertical)}")

# Verify we got both edges of each stripe
expected = [100, 200, 300, 400, 500, 600]
print(f"\nExpected: {expected}")
print(f"Match: {sorted(guides.vertical) == expected}")

# Test auto-detection
guides2 = Guides(page)
guides2.vertical.from_stripes()  # Should auto-detect the gray stripes

print(f"\nAuto-detect found {len(guides2.vertical)} guides")
print(f"Same result: {sorted(guides2.vertical) == sorted(guides.vertical)}")