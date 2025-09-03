#!/usr/bin/env python3
"""
Test to explore how context managers might work with Natural PDF
"""

import natural_pdf as npdf
from contextlib import contextmanager
import threading

# Test 1: Check current global option system
print("=== Current Global Options ===")
print(f"Default directional_offset: {npdf.options.layout.directional_offset}")
print(f"Default auto_multipage: {npdf.options.layout.auto_multipage}")

# Test 2: See how options are used in directional methods
print("\n=== How Options Are Used ===")
# Let's trace through the code to see how offset is used

# Test 3: Prototype a context manager approach
@contextmanager
def temporary_options(**kwargs):
    """Context manager to temporarily change options."""
    # Store original values
    original_values = {}
    
    for key, value in kwargs.items():
        parts = key.split('.')
        obj = npdf.options
        
        # Navigate to the right section
        for part in parts[:-1]:
            obj = getattr(obj, part)
        
        # Store original and set new value
        final_key = parts[-1]
        original_values[key] = getattr(obj, final_key)
        setattr(obj, final_key, value)
    
    try:
        yield
    finally:
        # Restore original values
        for key, original_value in original_values.items():
            parts = key.split('.')
            obj = npdf.options
            
            for part in parts[:-1]:
                obj = getattr(obj, part)
            
            final_key = parts[-1]
            setattr(obj, final_key, original_value)

# Test the context manager
print("\n=== Testing Context Manager ===")
print(f"Before: offset={npdf.options.layout.directional_offset}")

with temporary_options(**{'layout.directional_offset': 5.0}):
    print(f"Inside context: offset={npdf.options.layout.directional_offset}")

print(f"After: offset={npdf.options.layout.directional_offset}")

# Test 4: Check thread safety
print("\n=== Thread Safety Test ===")
results = []

def thread_func(thread_id, offset_value):
    with temporary_options(**{'layout.directional_offset': offset_value}):
        import time
        time.sleep(0.1)  # Simulate some work
        results.append((thread_id, npdf.options.layout.directional_offset))

threads = []
for i in range(3):
    t = threading.Thread(target=thread_func, args=(i, float(i * 10)))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Thread results (thread_id, offset):")
for result in sorted(results):
    print(f"  Thread {result[0]}: offset={result[1]}")

print("\nConclusion: Global options are NOT thread-safe!")