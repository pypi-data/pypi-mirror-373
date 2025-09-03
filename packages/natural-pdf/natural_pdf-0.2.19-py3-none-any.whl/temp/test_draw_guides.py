"""Example usage of the interactive guide drawing feature"""

# In a Jupyter notebook:
from natural_pdf import NaturalPDF

# Load a PDF
pdf = NaturalPDF.from_file("your_pdf.pdf")
page = pdf[0]

# Create guides
guides = page.guides()

# Detect some initial guides (optional)
guides.vertical.from_lines(n=5)
guides.horizontal.from_lines(n=5)

# Open interactive editor for vertical guides
guides.vertical.draw()

# Open interactive editor for horizontal guides
guides.horizontal.draw(width=600)  # Smaller widget

# After editing, the guides are automatically updated
# You can now use them to extract tables:
table = page.extract_table(guides)