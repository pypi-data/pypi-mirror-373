"""Checkbox detection using flood fill from center - X vs empty box."""

import numpy as np
from collections import deque




def flood_fill_size(image, start_x, start_y, threshold=200):
    """
    Flood fill from a point and return the size of filled region.
    Larger region = empty box. Smaller region = X or other mark.
    """
    if isinstance(image, np.ndarray) and len(image.shape) == 3:
        image = np.mean(image, axis=2).astype(np.uint8)
    
    height, width = image.shape
    if start_x >= width or start_y >= height:
        return 0
    
    # Track visited pixels
    visited = np.zeros_like(image, dtype=bool)
    
    # Queue for flood fill
    queue = deque([(start_x, start_y)])
    visited[start_y, start_x] = True
    
    # Count pixels in flood fill region
    count = 0
    
    # 8-directional flood fill
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                  (0, 1), (1, -1), (1, 0), (1, 1)]
    
    while queue:
        x, y = queue.popleft()
        count += 1
        
        # Check all 8 neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check bounds
            if 0 <= nx < width and 0 <= ny < height:
                # If not visited and light enough (not ink)
                if not visited[ny, nx] and image[ny, nx] >= threshold:
                    visited[ny, nx] = True
                    queue.append((nx, ny))
    
    return count


def detect_checkbox_flood(region, debug=False):
    """
    Detect if checkbox is checked using flood fill from center.
    Empty box = large flood region. X = small flood region.
    """
    # Convert to grayscale numpy array
    img = np.array(region.render(crop=True).convert('L'))
    height, width = img.shape
    
    # Start flood fill from center
    center_x, center_y = width // 2, height // 2
    
    # Try flood fill from center
    flood_size = flood_fill_size(img, center_x, center_y)
    total_pixels = width * height
    flood_ratio = flood_size / total_pixels
    
    # Also try a few points near center in case center pixel is dark
    alt_points = [
        (center_x - 2, center_y),
        (center_x + 2, center_y),
        (center_x, center_y - 2),
        (center_x, center_y + 2),
    ]
    
    max_flood_size = flood_size
    for x, y in alt_points:
        if 0 <= x < width and 0 <= y < height:
            size = flood_fill_size(img, x, y)
            max_flood_size = max(max_flood_size, size)
    
    max_flood_ratio = max_flood_size / total_pixels
    
    # Decision logic:
    # - If flood fills >50% of box, it's likely empty
    # - If flood fills <20% of box, it's likely marked with X
    is_empty = max_flood_ratio > 0.5
    is_marked = max_flood_ratio < 0.2
    
    if debug:
        print(f"Flood fill results:")
        print(f"  Center flood: {flood_size} pixels ({flood_ratio:.1%})")
        print(f"  Max flood: {max_flood_size} pixels ({max_flood_ratio:.1%})")
        print(f"  Decision: {'EMPTY' if is_empty else 'MARKED' if is_marked else 'UNCERTAIN'}")
    
    return {
        'is_checked': is_marked,
        'is_empty': is_empty,
        'flood_ratio': max_flood_ratio,
        'confidence': abs(max_flood_ratio - 0.35) / 0.35  # Confidence based on distance from uncertain middle
    }


def simple_center_darkness(region, sample_size=5):
    """
    Even simpler: just check if center region is dark.
    Good for quick X detection.
    """
    img = np.array(get_region_image(region).convert('L'))
    height, width = img.shape
    
    # Sample center region
    cy, cx = height // 2, width // 2
    half = sample_size // 2
    
    # Extract center patch
    y1 = max(0, cy - half)
    y2 = min(height, cy + half + 1)
    x1 = max(0, cx - half)
    x2 = min(width, cx + half + 1)
    
    center_patch = img[y1:y2, x1:x2]
    center_darkness = np.mean(center_patch)
    
    # X marks usually have dark center
    return center_darkness < 200


def ink_blob_analysis(region, threshold=200):
    """
    Analyze connected components of ink.
    X pattern typically has 1 large connected component.
    Empty box has small scattered components (noise).
    """
    img = np.array(get_region_image(region).convert('L'))
    binary = img < threshold
    
    # Simple connected component analysis without scipy
    # Count number of ink "blobs"
    visited = np.zeros_like(binary, dtype=bool)
    blob_sizes = []
    
    # Iterative flood fill to avoid recursion limit
    def get_blob_size(start_y, start_x):
        """Iterative flood fill to get connected component size."""
        if visited[start_y, start_x] or not binary[start_y, start_x]:
            return 0
        
        stack = [(start_y, start_x)]
        visited[start_y, start_x] = True
        size = 0
        
        while stack:
            y, x = stack.pop()
            size += 1
            
            # Check 8 neighbors
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    ny, nx = y + dy, x + dx
                    if (0 <= ny < binary.shape[0] and 
                        0 <= nx < binary.shape[1] and
                        not visited[ny, nx] and 
                        binary[ny, nx]):
                        visited[ny, nx] = True
                        stack.append((ny, nx))
        
        return size
    
    # Find all blobs
    for y in range(binary.shape[0]):
        for x in range(binary.shape[1]):
            if binary[y, x] and not visited[y, x]:
                blob_size = get_blob_size(y, x)
                if blob_size > 10:  # Ignore tiny noise
                    blob_sizes.append(blob_size)
    
    # Analysis
    total_ink = np.sum(binary)
    largest_blob = max(blob_sizes) if blob_sizes else 0
    num_blobs = len(blob_sizes)
    
    # X typically has 1-2 large blobs, empty box has many small ones
    is_x_pattern = (num_blobs <= 3 and largest_blob > total_ink * 0.6)
    
    return {
        'is_x_pattern': is_x_pattern,
        'num_blobs': num_blobs,
        'largest_blob_ratio': largest_blob / total_ink if total_ink > 0 else 0,
        'total_ink_ratio': total_ink / binary.size
    }


def analyze_checkbox(region, method='flood', debug=False):
    """
    Main function to analyze checkbox using specified method.
    
    Methods:
    - 'flood': Flood fill from center (default, most reliable)
    - 'center': Check center darkness (fastest)
    - 'blob': Connected component analysis (most thorough)
    - 'all': Run all methods and vote
    """
    if method == 'flood':
        result = detect_checkbox_flood(region, debug)
        return result['is_checked']
    
    elif method == 'center':
        return simple_center_darkness(region)
    
    elif method == 'blob':
        result = ink_blob_analysis(region)
        return result['is_x_pattern']
    
    elif method == 'all':
        # Run all methods and vote
        flood_result = detect_checkbox_flood(region, debug=False)
        center_result = simple_center_darkness(region)
        blob_result = ink_blob_analysis(region)
        
        votes = sum([
            flood_result['is_checked'],
            center_result,
            blob_result['is_x_pattern']
        ])
        
        if debug:
            print("All methods:")
            print(f"  Flood fill: {'MARKED' if flood_result['is_checked'] else 'EMPTY'}")
            print(f"  Center darkness: {'MARKED' if center_result else 'EMPTY'}")
            print(f"  Blob analysis: {'X PATTERN' if blob_result['is_x_pattern'] else 'EMPTY/OTHER'}")
            print(f"  Final vote: {votes}/3 say MARKED")
        
        return votes >= 2
    
    else:
        raise ValueError(f"Unknown method: {method}")




def compare_checkboxes(regions, labels=None):
    """
    Compare multiple checkbox regions across all metrics.
    
    Args:
        regions: List of checkbox regions to analyze
        labels: Optional list of labels for each region (e.g., ['Acceptable', 'Deficient', 'At-Risk'])
    
    Returns:
        pandas DataFrame with metrics as rows and regions as columns
    """
    import pandas as pd
    
    if labels is None:
        labels = [f'Region_{i+1}' for i in range(len(regions))]
    
    # Initialize results dictionary
    results = {label: {} for label in labels}
    
    for i, (region, label) in enumerate(zip(regions, labels)):
        # Get grayscale image
        img = np.array(region.render(crop=True).convert('L'))
        height, width = img.shape
        total_pixels = height * width
        
        # 1. Basic pixel metrics
        dark_pixels = np.sum(img < 200)
        results[label]['dark_pixel_count'] = dark_pixels
        results[label]['dark_pixel_ratio'] = dark_pixels / total_pixels
        results[label]['mean_intensity'] = np.mean(img)
        results[label]['std_intensity'] = np.std(img)
        results[label]['ink_score'] = (255 - np.mean(img)) / 2.55
        
        # 2. Flood fill metrics
        flood_result = detect_checkbox_flood(region, debug=False)
        results[label]['flood_ratio'] = flood_result['flood_ratio']
        results[label]['flood_confidence'] = flood_result['confidence']
        results[label]['is_empty_flood'] = flood_result['is_empty']
        results[label]['is_marked_flood'] = flood_result['is_checked']
        
        # 3. Center darkness
        cy, cx = height // 2, width // 2
        center_patch = img[max(0, cy-2):min(height, cy+3), max(0, cx-2):min(width, cx+3)]
        results[label]['center_darkness'] = np.mean(center_patch)
        results[label]['is_marked_center'] = np.mean(center_patch) < 200
        
        # 4. Blob analysis
        blob_result = ink_blob_analysis(region)
        results[label]['num_blobs'] = blob_result['num_blobs']
        results[label]['largest_blob_ratio'] = blob_result['largest_blob_ratio']
        results[label]['total_ink_ratio'] = blob_result['total_ink_ratio']
        results[label]['is_x_pattern'] = blob_result['is_x_pattern']
        
        # 5. Spatial distribution
        # Check if ink is concentrated in diagonal patterns (X shape)
        binary = img < 200
        # Main diagonal
        diag1_sum = sum(binary[i, i] for i in range(min(height, width)))
        # Anti-diagonal
        diag2_sum = sum(binary[i, width-1-i] for i in range(min(height, width)))
        diagonal_ratio = (diag1_sum + diag2_sum) / (2 * min(height, width))
        results[label]['diagonal_ink_ratio'] = diagonal_ratio
        
        # 6. Edge vs center distribution
        edge_mask = np.zeros_like(binary)
        edge_mask[0:3, :] = True
        edge_mask[-3:, :] = True
        edge_mask[:, 0:3] = True
        edge_mask[:, -3:] = True
        edge_ink = np.sum(binary & edge_mask)
        center_ink = np.sum(binary & ~edge_mask)
        results[label]['edge_ink_ratio'] = edge_ink / np.sum(edge_mask) if np.sum(edge_mask) > 0 else 0
        results[label]['center_ink_ratio'] = center_ink / np.sum(~edge_mask) if np.sum(~edge_mask) > 0 else 0
        
        # 7. Final voting
        votes = sum([
            results[label]['is_marked_flood'],
            results[label]['is_marked_center'],
            results[label]['is_x_pattern']
        ])
        results[label]['vote_score'] = votes
        results[label]['is_checked'] = votes >= 2
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Add row for identifying which is most likely checked
    most_checked_scores = {
        'dark_pixel_ratio': df.loc['dark_pixel_ratio'].idxmax(),
        'ink_score': df.loc['ink_score'].idxmax(),
        'flood_ratio': df.loc['flood_ratio'].idxmin(),  # Lower is more marked
        'center_darkness': df.loc['center_darkness'].idxmin(),  # Lower is darker
        'diagonal_ink_ratio': df.loc['diagonal_ink_ratio'].idxmax(),
        'vote_score': df.loc['vote_score'].idxmax(),
    }
    
    # Add summary row
    df.loc['most_likely_checked'] = [most_checked_scores.get(col, '') for col in df.columns]
    
    return df


# Example usage scaffold
def analyze_three_checkboxes():
    """
    Example scaffold for analyzing three checkbox regions.
    """
    import natural_pdf as npdf
    import pandas as pd
    
    # Set pandas display options for better viewing
    pd.set_option('display.max_rows', None)
    pd.set_option('display.float_format', '{:.3f}'.format)
    
    # Load your PDF
    pdf = npdf.PDF("your_form.pdf")
    page = pdf[0]
    
    # Method 1: If you have the regions already
    # regions = [region1, region2, region3]
    # labels = ['Acceptable', 'Deficient', 'At-Risk']
    
    # Method 2: Find them relative to text labels
    checkbox_area = page.find('text:contains("Housing")')  # Or however you identify the area
    
    regions = []
    labels = ['Acceptable', 'Deficient', 'At-Risk']
    
    for label in labels:
        cb = checkbox_area.find(f'text={label}').left(width=15)
        if cb:
            regions.append(cb)
        else:
            print(f"Warning: Could not find checkbox for {label}")
    
    # Run comparison
    df = compare_checkboxes(regions, labels)
    
    # Display results
    print("\nCheckbox Analysis Results:")
    print("=" * 80)
    print(df)
    
    print("\n\nKey Metrics Interpretation:")
    print("-" * 80)
    print("dark_pixel_ratio: Higher = more ink")
    print("ink_score: 0-100, higher = more marking")
    print("flood_ratio: Lower = more marked (ink blocks flood fill)")
    print("center_darkness: Lower = darker center (X pattern)")
    print("diagonal_ink_ratio: Higher = more X-like pattern")
    print("vote_score: 0-3, number of methods that think it's checked")
    
    print("\n\nConclusion:")
    print("-" * 80)
    checked_col = df.loc['is_checked']
    checked_labels = [col for col in checked_col.index if checked_col[col]]
    if checked_labels:
        print(f"Checked boxes: {', '.join(checked_labels)}")
    else:
        print("No boxes appear to be checked")
    
    # Find most likely based on vote
    vote_scores = df.loc['vote_score']
    max_vote = vote_scores.max()
    if max_vote > 0:
        most_likely = vote_scores.idxmax()
        print(f"Most likely checked (by vote): {most_likely}")
    
    return df


# Quick test function for three regions
def quick_compare(region1, region2, region3, labels=['Region 1', 'Region 2', 'Region 3']):
    """
    Quick comparison of three regions.
    
    Example:
        df = quick_compare(acceptable_cb, deficient_cb, at_risk_cb, 
                          ['Acceptable', 'Deficient', 'At-Risk'])
    """
    return compare_checkboxes([region1, region2, region3], labels)


def which_is_checked(*regions, labels=None):
    """
    Simple function that tells you which checkbox is checked.
    
    Usage:
        checked = which_is_checked(region1, region2, region3)
        print(checked)  # "Region 2"
        
        # With labels:
        checked = which_is_checked(accept_cb, deficient_cb, risk_cb,
                                 labels=['Acceptable', 'Deficient', 'At-Risk'])
        print(checked)  # "Deficient"
    """
    if labels is None:
        labels = [f'Checkbox {i+1}' for i in range(len(regions))]
    
    # Quick analysis of each
    scores = []
    for region, label in zip(regions, labels):
        img = np.array(region.render(crop=True).convert('L'))
        
        # Just check center darkness - simplest reliable method
        h, w = img.shape
        cy, cx = h // 2, w // 2
        center = img[max(0, cy-3):min(h, cy+4), max(0, cx-3):min(w, cx+4)]
        darkness = 255 - np.mean(center)  # Higher = darker
        
        scores.append((label, darkness))
    
    # Sort by darkness
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Simple decision
    if scores[0][1] > scores[1][1] * 1.5:  # Clear winner
        return scores[0][0]
    else:
        # Not clear - return with uncertainty
        return f"{scores[0][0]} (uncertain - also check {scores[1][0]})"


def show_checkbox_comparison(*regions, labels=None):
    """
    Visual comparison of checkboxes - shows which is darkest.
    
    Usage:
        show_checkbox_comparison(cb1, cb2, cb3, labels=['A', 'B', 'C'])
    """
    if labels is None:
        labels = [f'Option {i+1}' for i in range(len(regions))]
    
    print("\nCheckbox Analysis:")
    print("-" * 40)
    
    results = []
    for region, label in zip(regions, labels):
        img = np.array(region.render(crop=True).convert('L'))
        
        # Simple metrics
        darkness = 255 - np.mean(img)
        dark_pixels = np.sum(img < 200)
        
        results.append({
            'label': label,
            'darkness': darkness,
            'dark_pixels': dark_pixels
        })
    
    # Sort by darkness
    results.sort(key=lambda x: x['darkness'], reverse=True)
    
    # Show results
    print(f"Most likely checked: {results[0]['label']}")
    print()
    
    # Simple bar chart
    max_darkness = max(r['darkness'] for r in results)
    for r in results:
        bar_length = int(30 * r['darkness'] / max_darkness) if max_darkness > 0 else 0
        bar = '█' * bar_length
        print(f"{r['label']:15} {bar} {r['darkness']:.0f}")
    
    # Confidence check
    if len(results) >= 2:
        ratio = results[0]['darkness'] / results[1]['darkness'] if results[1]['darkness'] > 0 else 10
        if ratio < 1.3:
            print(f"\n⚠️  Low confidence - {results[1]['label']} is almost as dark")
        elif ratio > 2:
            print(f"\n✓ High confidence - clearly {results[0]['label']}")


def is_this_checked(region, reference_checked=None, reference_unchecked=None):
    """
    Check if a single checkbox is marked, optionally using reference examples.
    
    Usage:
        # Simple check
        if is_this_checked(my_checkbox):
            print("It's checked!")
        
        # With references for better accuracy
        if is_this_checked(my_checkbox, 
                          reference_checked=known_checked_cb,
                          reference_unchecked=known_empty_cb):
            print("It's checked!")
    """
    img = np.array(region.render(crop=True).convert('L'))
    darkness = 255 - np.mean(img)
    
    if reference_checked is None and reference_unchecked is None:
        # Simple threshold
        return darkness > 40  # Adjust based on your forms
    
    # Compare to references
    if reference_checked:
        checked_img = np.array(reference_checked.render(crop=True).convert('L'))
        checked_darkness = 255 - np.mean(checked_img)
    else:
        checked_darkness = 60  # Default
    
    if reference_unchecked:
        unchecked_img = np.array(reference_unchecked.render(crop=True).convert('L'))
        unchecked_darkness = 255 - np.mean(unchecked_img)
    else:
        unchecked_darkness = 20  # Default
    
    # Which is it closer to?
    threshold = (checked_darkness + unchecked_darkness) / 2
    return darkness > threshold


def debug_regions(regions, labels=None):
    """Debug function to check what's in each region."""
    if labels is None:
        labels = [f'Region_{i+1}' for i in range(len(regions))]
    
    print("Debugging regions:")
    print("=" * 60)
    
    for i, (region, label) in enumerate(zip(regions, labels)):
        print(f"\n{label}:")
        print(f"  Region object: {region}")
        print(f"  Bbox: {region.bbox if hasattr(region, 'bbox') else 'N/A'}")
        
        # Get the image
        img = np.array(region.render(crop=True).convert('L'))
        print(f"  Image shape: {img.shape}")
        print(f"  Image dtype: {img.dtype}")
        print(f"  Unique values: {len(np.unique(img))}")
        print(f"  Min/Max values: {img.min()}/{img.max()}")
        
        # Show a small sample of the center
        h, w = img.shape
        cy, cx = h//2, w//2
        sample = img[max(0,cy-2):cy+3, max(0,cx-2):cx+3]
        print(f"  Center sample:\n{sample}")
        
        # Save images for inspection
        from PIL import Image
        pil_img = Image.fromarray(img, mode='L')
        filename = f"/tmp/checkbox_{label.lower().replace(' ', '_').replace('-', '_')}.png"
        pil_img.save(filename)
        print(f"  Saved to: {filename}")