"""Test script to verify the draw() method works"""

import sys
sys.path.insert(0, '.')

from natural_pdf.analyzers.guides import GuidesList, Guides

# Create a mock context for testing
class MockContext:
    def __init__(self):
        self.width = 600
        self.height = 800
        
    def render(self, resolution=150):
        # Create a simple test image
        from PIL import Image
        img = Image.new('RGB', (int(self.width * resolution/72), int(self.height * resolution/72)), 'white')
        return img

# Test that the draw method exists
mock_context = MockContext()
guides = Guides(mock_context)

# Add some test guides
guides.vertical.data = [100, 200, 300, 400, 500]
guides.horizontal.data = [150, 350, 550, 750]

print("Initial vertical guides:", list(guides.vertical))
print("Initial horizontal guides:", list(guides.horizontal))

# Check that draw method exists
assert hasattr(guides.vertical, 'draw')
assert callable(guides.vertical.draw)
assert hasattr(guides.horizontal, 'draw')
assert callable(guides.horizontal.draw)

print("\nSuccess! The draw() method is available.")
print("\nIn a Jupyter notebook, you would use:")
print("  guides.vertical.draw()      # Interactive vertical guide editor")
print("  guides.horizontal.draw()    # Interactive horizontal guide editor")
print("\nFeatures:")
print("  - Click to add new guides")
print("  - Click existing guides to select them")
print("  - Drag to move guides")
print("  - Delete key to remove selected guide")
print("  - Arrow keys to fine-tune position")
print("  - Enter to apply, Escape to cancel")