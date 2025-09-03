"""Test the interactive guide drawing functionality"""

from natural_pdf.core.pdf import PDF
from natural_pdf.analyzers.guides import Guides

# Load a sample PDF
pdf = PDF("tests/sample_pdfs/simple_table.pdf")
page = pdf.pages[0]

# Create guides
guides = Guides(page)

# Add some initial guides for testing
guides.vertical.from_content()
guides.horizontal.from_lines(n=5)

print("Initial vertical guides:", list(guides.vertical))
print("Initial horizontal guides:", list(guides.horizontal))

# This would open the interactive widget in Jupyter
# guides.vertical.draw()

# For non-Jupyter testing, we can check the method exists
assert hasattr(guides.vertical, 'draw')
assert callable(guides.vertical.draw)

print("\nSuccess! The draw() method is available on GuidesList objects.")
print("To use it interactively, run this in a Jupyter notebook:")
print("  guides.vertical.draw()")
print("  guides.horizontal.draw(width=600)")