import difflib

# Test similarity calculation
pairs = [
    ("Durham", "Durham's Meatpacking  "),
    ("durham", "durham's meatpacking  "),  # lowercase
    ("Chicgo", "Chicago, Ill."),
    ("chicgo", "chicago, ill."),  # lowercase
    ("Chicago", "Chicago, Ill."),
]

print("Similarity ratios:")
for search, text in pairs:
    ratio = difflib.SequenceMatcher(None, search, text).ratio()
    print(f"  '{search}' vs '{text}' -> {ratio:.3f}")