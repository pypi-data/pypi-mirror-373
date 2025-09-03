#!/usr/bin/env python
"""Test the guide widget functionality"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test importing and basic functionality
try:
    from natural_pdf.analyzers.guides import InteractiveGuideWidget, GuidesList, _GUIDE_WIDGET_AVAILABLE
    print("✓ Successfully imported InteractiveGuideWidget")
    
    if _GUIDE_WIDGET_AVAILABLE:
        print("✓ ipywidgets is available")
        
        # Create a mock GuidesList for testing
        class MockPage:
            def __init__(self):
                self.bbox = (0, 0, 595, 842)  # A4 page size in points
                
            def render(self, resolution=150):
                # Mock render method
                from PIL import Image
                width = int(595 * resolution / 72)
                height = int(842 * resolution / 72)
                return Image.new('RGB', (width, height), color='white')
                
        class MockGuides:
            def __init__(self):
                self.context = MockPage()
                
        class MockGuidesList:
            def __init__(self):
                self.data = [100, 200, 300]
                self._axis = 'vertical'
                self._parent = MockGuides()
        
        # Test creating the widget
        mock_guides = MockGuidesList()
        try:
            widget = InteractiveGuideWidget(mock_guides)
            print("✓ Successfully created InteractiveGuideWidget instance")
            print(f"  - Widget ID: {widget.widget_id}")
            print(f"  - Widget base classes: {InteractiveGuideWidget.__bases__}")
            
            # Check if the widget has the expected methods
            expected_methods = ['_generate_content', 'update_guides']
            for method in expected_methods:
                if hasattr(widget, method):
                    print(f"  - Has method: {method}")
                else:
                    print(f"  - Missing method: {method}")
                    
        except Exception as e:
            print(f"✗ Error creating widget: {e}")
            
    else:
        print("⚠ ipywidgets not available - widget functionality disabled")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    
print("\nWidget implementation test complete!")