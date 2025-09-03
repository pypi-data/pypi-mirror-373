"""
Demo of the text:closest() selector for fuzzy text matching in Natural PDF.

This selector is designed to handle OCR errors and text variations by:
1. First finding exact substring matches
2. Then ranking other elements by similarity score
"""

from natural_pdf import PDF

# Load a PDF
pdf = PDF("pdfs/01-practice.pdf")
page = pdf.pages[0]

print("=== text:closest() Selector Demo ===\n")

# Example 1: Basic fuzzy matching (default threshold 0.0 - all elements)
print("1. Find elements closest to 'Durham' (no threshold):")
results = page.find_all('text:closest("Durham")')
print(f"   Found {len(results)} elements (all text elements)")
print(f"   First 3: {[r.text.strip() for r in results[:3]]}\n")

# Example 2: With similarity threshold
print("2. Find elements with at least 40% similarity to 'Durham':")
results = page.find_all('text:closest("Durham@0.4")')
print(f"   Found {len(results)} elements")
for r in results:
    print(f"   - '{r.text.strip()}'")
print()

# Example 3: OCR error simulation
print("3. Simulate OCR errors:")
print("   Searching for 'Durharn' (OCR error: 'rn' instead of 'm'):")
results = page.find_all('text:closest("Durharn@0.4")')
print(f"   Found: {[r.text.strip() for r in results if 'Durham' in r.text]}\n")

# Example 4: Case insensitive matching (default)
print("4. Case insensitive search for 'chicago':")
results = page.find_all('text:closest("chicago@0.6")')
print(f"   Found: {[r.text.strip() for r in results if 'Chicago' in r.text]}\n")

# Example 5: Combining with other selectors
print("5. Find fuzzy matches with size constraints:")
results = page.find_all('text:closest("Violation@0.6")[size>10]')
print(f"   Found {len(results)} elements with size > 10")
if results:
    print(f"   Example: '{results[0].text.strip()}' (size={results[0].size})\n")

# Example 6: Practical use case - finding labels
print("6. Practical OCR use case - finding form labels:")
print("   Looking for 'Date:' even if OCR missed the colon:")
results = page.find_all('text:closest("Date@0.8")')
date_labels = [r for r in results if "Date" in r.text]
if date_labels:
    print(f"   Found: '{date_labels[0].text.strip()}'")
    # Now find the value to the right
    value = date_labels[0].right(until='text')
    print(f"   Value: '{value.extract_text().strip()}'")

print("\n=== Key Features ===")
print("- Default threshold is 0.0 (matches all elements, sorted by similarity)")
print("- Exact substring matches always come first")
print("- Case insensitive by default (use case=True for case sensitive)")
print("- Threshold specified with @ separator: 'search@0.8'")
print("- Uses Python's difflib.SequenceMatcher for similarity calculation")
print("- Empty search string returns no results")