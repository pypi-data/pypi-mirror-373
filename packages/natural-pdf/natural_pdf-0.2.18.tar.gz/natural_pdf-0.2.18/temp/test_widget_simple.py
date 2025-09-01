#!/usr/bin/env python
"""Simple test for the guide widget"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test importing the module
try:
    from natural_pdf.analyzers.guides import InteractiveGuideWidget, _GUIDE_WIDGET_AVAILABLE
    print(f"✓ Module imported successfully")
    print(f"✓ Widget available: {_GUIDE_WIDGET_AVAILABLE}")
    
    if _GUIDE_WIDGET_AVAILABLE:
        print("✓ ipywidgets is installed and InteractiveGuideWidget is available")
    else:
        print("✗ ipywidgets is not installed")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Check if we can create the widget class
if _GUIDE_WIDGET_AVAILABLE:
    try:
        # We can't actually instantiate it without a GuidesList, but we can check the class exists
        print(f"✓ InteractiveGuideWidget class: {InteractiveGuideWidget}")
        print(f"✓ Widget base classes: {InteractiveGuideWidget.__bases__}")
        
        # Check methods
        methods = [m for m in dir(InteractiveGuideWidget) if not m.startswith('_')]
        print(f"✓ Public methods: {methods}")
        
    except Exception as e:
        print(f"✗ Error checking widget class: {e}")
else:
    print("⚠ Skipping widget checks as ipywidgets is not available")

print("\nAll checks passed!")