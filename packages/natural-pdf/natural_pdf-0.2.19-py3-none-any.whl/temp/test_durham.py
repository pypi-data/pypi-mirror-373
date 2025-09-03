from natural_pdf import PDF
import difflib

pdf = PDF('pdfs/01-practice.pdf')
page = pdf.pages[0]

# Find all text elements
all_text = page.find_all('text')
print(f"Total text elements: {len(all_text)}")

# Look for Durham-related text
print("\nLooking for Durham-related text:")
for el in all_text:
    if "Durham" in el.text:
        print(f"  Found: '{el.text}'")

# Test similarity
search_text = "Durharn"  # OCR error: rn instead of m
print(f"\nTesting similarity for '{search_text}':")
for el in all_text[:20]:  # Just check first 20
    if el.text:
        ratio = difflib.SequenceMatcher(None, search_text.lower(), el.text.lower()).ratio()
        if ratio > 0.3:
            print(f"  '{el.text}' -> ratio: {ratio:.3f}")

# Test the actual selector
results = page.find_all('text:closest("Durharn@0.4")')
print(f"\nResults with threshold 0.4: {len(results)}")
for r in results[:5]:
    print(f"  - {r.text}")