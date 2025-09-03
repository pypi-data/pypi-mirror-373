"""Test marker ordering with a real PDF."""
from natural_pdf import PDF

# Load a test PDF
pdf = PDF("pdfs/01-practice.pdf")
page = pdf.pages[0]

# Find some text elements to use as markers
all_text = page.find_all("text")
print("Sample text elements:")
for i, elem in enumerate(all_text[:10]):
    print(f"{i}: '{elem.text}' at x={elem.x0:.1f}")

# Create guides with markers in specific order
print("\n--- Testing vertical guides with markers ---")

# Let's find specific text elements at different positions
violations_elem = page.find('text:contains("Violations")')
date_elem = page.find('text:contains("Date")')
total_elem = page.find('text:contains("Total")')

if violations_elem and date_elem and total_elem:
    print(f"\nElement positions:")
    print(f"'Violations' at x={violations_elem.x0:.1f}")
    print(f"'Date' at x={date_elem.x0:.1f}")
    print(f"'Total' at x={total_elem.x0:.1f}")
    
    # Create guides with markers in a specific order
    guides = page.guides.from_content(
        axis="vertical",
        markers=["Violations", "Date", "Total"],
        align="left",
        outer=True
    )
    
    print(f"\nResulting vertical guides: {sorted(guides.vertical)}")
    print(f"Page bounds: {page.bbox}")
    
    # Show visually
    page.guides.vertical.from_content(
        markers=["Violations", "Date", "Total"],
        align="left",
        outer=True
    )
    page.show(guides=True)