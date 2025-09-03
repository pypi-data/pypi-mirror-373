"""Simplified checkbox detection - just the most effective methods."""

import numpy as np


def is_checkbox_marked_simple(region, method='center'):
    """
    Simplified checkbox detection using only the most effective methods.
    
    Methods:
    - 'center': Check if center is dark (fastest, most reliable)
    - 'flood': Check flood fill ratio (slightly more robust)
    - 'both': Use both and require agreement
    """
    img = np.array(region.render(crop=True).convert('L'))
    
    if method == 'center':
        # Just check center darkness
        h, w = img.shape
        cy, cx = h // 2, w // 2
        # Sample 5x5 center region
        center_region = img[max(0, cy-2):min(h, cy+3), 
                           max(0, cx-2):min(w, cx+3)]
        center_mean = np.mean(center_region)
        return center_mean < 190  # Threshold can be tuned
    
    elif method == 'flood':
        # Simple flood fill from center
        h, w = img.shape
        cy, cx = h // 2, w // 2
        
        # Count pixels reachable from center
        visited = np.zeros_like(img, dtype=bool)
        stack = [(cy, cx)]
        visited[cy, cx] = True
        count = 0
        
        while stack and count < h * w:  # Safety limit
            y, x = stack.pop()
            count += 1
            
            # Check 4 neighbors (simpler than 8)
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ny, nx = y + dy, x + dx
                if (0 <= ny < h and 0 <= nx < w and 
                    not visited[ny, nx] and img[ny, nx] > 200):
                    visited[ny, nx] = True
                    stack.append((ny, nx))
        
        flood_ratio = count / (h * w)
        return flood_ratio < 0.3  # Less than 30% fillable = marked
    
    elif method == 'both':
        # Require both methods to agree
        center_dark = is_checkbox_marked_simple(region, 'center')
        flood_blocked = is_checkbox_marked_simple(region, 'flood')
        return center_dark and flood_blocked
    
    else:
        # Ultra simple: just count dark pixels
        dark_ratio = np.sum(img < 200) / img.size
        return dark_ratio > 0.15  # More than 15% dark pixels


def analyze_checkboxes_simple(regions, labels=None):
    """
    Quick analysis of multiple checkboxes.
    Returns dict with results and which one is most likely checked.
    """
    if labels is None:
        labels = [f'CB{i+1}' for i in range(len(regions))]
    
    results = {}
    
    for region, label in zip(regions, labels):
        img = np.array(region.render(crop=True).convert('L'))
        h, w = img.shape
        
        # Get key metrics
        cy, cx = h // 2, w // 2
        center_sample = img[max(0, cy-2):min(h, cy+3), 
                           max(0, cx-2):min(w, cx+3)]
        
        results[label] = {
            'center_darkness': np.mean(center_sample),
            'dark_pixel_ratio': np.sum(img < 200) / img.size,
            'is_marked': is_checkbox_marked_simple(region, 'center')
        }
    
    # Find which one is most likely marked (darkest center)
    darkest = min(results.items(), key=lambda x: x[1]['center_darkness'])
    
    return {
        'results': results,
        'most_likely_marked': darkest[0],
        'marked_checkboxes': [label for label, data in results.items() if data['is_marked']]
    }


# Usage example:
if __name__ == "__main__":
    print("Simple Checkbox Detection")
    print("=" * 50)
    print("""
    # Single checkbox
    is_marked = is_checkbox_marked_simple(checkbox_region)
    
    # Multiple checkboxes
    result = analyze_checkboxes_simple([cb1, cb2, cb3], 
                                     ['Acceptable', 'Deficient', 'At-Risk'])
    print(result['most_likely_marked'])  # 'Acceptable'
    print(result['marked_checkboxes'])   # ['Acceptable']
    
    # Just check center (fastest)
    if is_checkbox_marked_simple(region, method='center'):
        print("Checkbox is marked!")
    """)