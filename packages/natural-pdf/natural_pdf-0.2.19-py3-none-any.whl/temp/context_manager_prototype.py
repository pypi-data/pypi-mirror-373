#!/usr/bin/env python3
"""
Prototype implementation of context manager for Natural PDF directional options.

This demonstrates how Option 1 (Global Context Manager) would work in practice.
"""

import natural_pdf as npdf
from contextlib import contextmanager
from typing import Any, Dict, Optional

@contextmanager
def with_directional_options(
    directional_offset: Optional[float] = None,
    auto_multipage: Optional[bool] = None,
    **kwargs
):
    """
    Context manager to temporarily override directional method options.
    
    Parameters
    ----------
    directional_offset : float, optional
        Temporary offset in points for directional methods (default: keep current)
    auto_multipage : bool, optional  
        Temporary setting for automatic multipage navigation (default: keep current)
    **kwargs : dict
        Additional layout options to override
    
    Examples
    --------
    >>> # Temporarily use larger offset
    >>> with with_directional_options(directional_offset=5.0):
    ...     region = element.below()  # Uses 5.0 offset
    
    >>> # Multiple options
    >>> with with_directional_options(directional_offset=10.0, auto_multipage=True):
    ...     region = element.below(until="Section 2")  # Can span pages
    
    >>> # Nested contexts
    >>> with with_directional_options(directional_offset=5.0):
    ...     with with_directional_options(auto_multipage=True):
    ...         # Both options are active here
    ...         region = element.below()
    
    Warning
    -------
    This context manager modifies global state and is NOT thread-safe.
    Do not use in multi-threaded applications.
    """
    # Build options dict
    options = {}
    if directional_offset is not None:
        options['directional_offset'] = directional_offset
    if auto_multipage is not None:
        options['auto_multipage'] = auto_multipage
    options.update(kwargs)
    
    # Store original values
    original_values = {}
    layout_options = npdf.options.layout
    
    for key, value in options.items():
        if hasattr(layout_options, key):
            original_values[key] = getattr(layout_options, key)
            setattr(layout_options, key, value)
        else:
            raise ValueError(f"Unknown layout option: {key}")
    
    try:
        yield
    finally:
        # Restore original values
        for key, original_value in original_values.items():
            setattr(layout_options, key, original_value)


# Convenience functions for common use cases
@contextmanager
def with_offset(offset: float):
    """Temporarily set directional offset."""
    with with_directional_options(directional_offset=offset):
        yield


@contextmanager  
def with_multipage():
    """Temporarily enable multipage navigation."""
    with with_directional_options(auto_multipage=True):
        yield


@contextmanager
def no_offset():
    """Temporarily disable directional offset (set to 0)."""
    with with_directional_options(directional_offset=0.0):
        yield


# Demo usage
if __name__ == "__main__":
    import tempfile
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    # Create a test PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        c = canvas.Canvas(tmp.name, pagesize=letter)
        
        # Page 1
        c.drawString(100, 700, "Header 1")
        c.drawString(100, 600, "Content 1")
        c.drawString(100, 500, "Footer 1")
        
        # Page 2  
        c.showPage()
        c.drawString(100, 700, "Header 2")
        c.drawString(100, 600, "Content 2")
        
        c.save()
        
        # Test the context managers
        print("=== Testing Context Managers ===")
        pdf = npdf.PDF(tmp.name)
        page = pdf.pages[0]
        
        # Find header
        header = page.find('text:contains("Header 1")')
        
        # Test 1: Default behavior
        print(f"\n1. Default offset: {npdf.options.layout.directional_offset}")
        region1 = header.below(height=50)
        print(f"   Region bbox: {region1.bbox}")
        
        # Test 2: With custom offset
        print(f"\n2. Using with_offset(10.0):")
        with with_offset(10.0):
            print(f"   Inside context: offset={npdf.options.layout.directional_offset}")
            region2 = header.below(height=50)
            print(f"   Region bbox: {region2.bbox}")
            print(f"   Y difference: {region2.top - region1.top}")
        print(f"   After context: offset={npdf.options.layout.directional_offset}")
        
        # Test 3: No offset
        print(f"\n3. Using no_offset():")
        with no_offset():
            region3 = header.below(height=50)
            print(f"   Region bbox: {region3.bbox}")
            print(f"   Includes header: {region3.top <= header.bottom}")
        
        # Test 4: Multipage navigation
        print(f"\n4. Testing multipage:")
        print(f"   Default auto_multipage: {npdf.options.layout.auto_multipage}")
        
        # This would normally stop at page boundary
        region4 = header.below(until='text:contains("Header 2")')
        print(f"   Without multipage: stops at page boundary")
        
        # This can cross pages
        with with_multipage():
            print(f"   Inside context: auto_multipage={npdf.options.layout.auto_multipage}")
            # Note: This would work if multipage was fully implemented
            # region5 = header.below(until="Header 2") 
            # print(f"   Region type: {type(region5).__name__}")  # Would be FlowRegion
        
        # Test 5: Nested contexts
        print(f"\n5. Nested contexts:")
        with with_offset(5.0):
            print(f"   Outer: offset={npdf.options.layout.directional_offset}")
            with with_offset(10.0):
                print(f"   Inner: offset={npdf.options.layout.directional_offset}")
            print(f"   Back to outer: offset={npdf.options.layout.directional_offset}")
        print(f"   Back to default: offset={npdf.options.layout.directional_offset}")
        
        # Cleanup
        import os
        os.unlink(tmp.name)