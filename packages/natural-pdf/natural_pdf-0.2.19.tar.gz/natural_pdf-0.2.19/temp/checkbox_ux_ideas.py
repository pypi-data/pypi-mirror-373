"""
Practical UX patterns for checkbox detection in form processing.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class CheckboxCalibrator:
    """
    Learn optimal thresholds from user-provided examples.
    """
    def __init__(self):
        self.checked_examples = []
        self.unchecked_examples = []
        self.thresholds = {}
        
    def add_example(self, region, is_checked: bool):
        """Add a labeled example."""
        metrics = self._extract_metrics(region)
        if is_checked:
            self.checked_examples.append(metrics)
        else:
            self.unchecked_examples.append(metrics)
    
    def calibrate(self):
        """Find optimal thresholds based on examples."""
        if not self.checked_examples or not self.unchecked_examples:
            raise ValueError("Need both checked and unchecked examples")
        
        # For each metric, find threshold that best separates checked/unchecked
        checked_df = pd.DataFrame(self.checked_examples)
        unchecked_df = pd.DataFrame(self.unchecked_examples)
        
        for metric in checked_df.columns:
            checked_vals = checked_df[metric].values
            unchecked_vals = unchecked_df[metric].values
            
            # Find threshold that maximizes separation
            all_vals = np.concatenate([checked_vals, unchecked_vals])
            best_threshold = None
            best_score = 0
            
            for threshold in np.percentile(all_vals, [10, 20, 30, 40, 50, 60, 70, 80, 90]):
                # Score based on correct classification
                correct = np.sum(checked_vals < threshold) + np.sum(unchecked_vals >= threshold)
                score = correct / len(all_vals)
                if score > best_score:
                    best_score = score
                    best_threshold = threshold
            
            self.thresholds[metric] = {
                'value': best_threshold,
                'accuracy': best_score,
                'checked_mean': np.mean(checked_vals),
                'unchecked_mean': np.mean(unchecked_vals)
            }
    
    def predict(self, region, confidence_threshold=0.7):
        """Predict if checkbox is checked based on calibrated thresholds."""
        metrics = self._extract_metrics(region)
        votes = 0
        total_weight = 0
        
        for metric, value in metrics.items():
            if metric in self.thresholds:
                threshold_info = self.thresholds[metric]
                weight = threshold_info['accuracy']
                if weight > confidence_threshold:
                    if value < threshold_info['value']:
                        votes += weight
                    total_weight += weight
        
        confidence = votes / total_weight if total_weight > 0 else 0
        return confidence > 0.5, confidence
    
    def save(self, path: str):
        """Save calibration to file."""
        with open(path, 'w') as f:
            json.dump({
                'thresholds': self.thresholds,
                'n_checked': len(self.checked_examples),
                'n_unchecked': len(self.unchecked_examples)
            }, f, indent=2)
    
    def load(self, path: str):
        """Load calibration from file."""
        with open(path, 'r') as f:
            data = json.load(f)
            self.thresholds = data['thresholds']
    
    def _extract_metrics(self, region):
        """Extract key metrics from region."""
        img = np.array(region.render(crop=True).convert('L'))
        h, w = img.shape
        cy, cx = h // 2, w // 2
        
        # Center sample
        center = img[max(0, cy-2):min(h, cy+3), max(0, cx-2):min(w, cx+3)]
        
        return {
            'center_darkness': np.mean(center),
            'dark_pixel_ratio': np.sum(img < 200) / img.size,
            'std_intensity': np.std(img),
            'edge_center_ratio': np.mean(img[0:2, :]) / np.mean(center) if np.mean(center) > 0 else 1
        }


class FormCheckboxProcessor:
    """
    Process multiple instances of the same form with checkboxes.
    """
    def __init__(self, template_config: Dict):
        """
        template_config = {
            'checkboxes': {
                'option1': {'find': 'text=Acceptable', 'direction': 'left', 'width': 15},
                'option2': {'find': 'text=Deficient', 'direction': 'left', 'width': 15},
                'option3': {'find': 'text=At-Risk', 'direction': 'left', 'width': 15},
            },
            'constraints': {
                'exactly_one': True,  # Exactly one must be checked
                'min_checked': 1,     # At least this many
                'max_checked': 1,     # At most this many
            }
        }
        """
        self.config = template_config
        self.calibrator = CheckboxCalibrator()
        self.results = []
    
    def process_form(self, page, form_id: str) -> Dict:
        """Process a single form instance."""
        results = {'form_id': form_id, 'checkboxes': {}, 'valid': True, 'confidence': 1.0}
        
        # Find all checkboxes
        for name, config in self.config['checkboxes'].items():
            try:
                # Find the checkbox region
                ref = page.find(config['find'])
                if not ref:
                    results['checkboxes'][name] = {'found': False}
                    results['valid'] = False
                    continue
                
                # Navigate to checkbox
                direction = config.get('direction', 'left')
                width = config.get('width', 15)
                if direction == 'left':
                    cb = ref.left(width=width)
                elif direction == 'right':
                    cb = ref.right(width=width)
                elif direction == 'above':
                    cb = ref.above(height=width)
                elif direction == 'below':
                    cb = ref.below(height=width)
                
                # Analyze checkbox
                if self.calibrator.thresholds:
                    # Use calibrated prediction
                    is_checked, confidence = self.calibrator.predict(cb)
                else:
                    # Use default analysis
                    from temp.checkbox_checks import analyze_checkbox
                    is_checked = analyze_checkbox(cb, method='all')
                    confidence = 0.8  # Default confidence
                
                results['checkboxes'][name] = {
                    'found': True,
                    'checked': is_checked,
                    'confidence': confidence,
                    'bbox': cb.bbox
                }
                results['confidence'] = min(results['confidence'], confidence)
                
            except Exception as e:
                results['checkboxes'][name] = {'found': False, 'error': str(e)}
                results['valid'] = False
        
        # Check constraints
        if results['valid'] and 'constraints' in self.config:
            checked_count = sum(1 for cb in results['checkboxes'].values() 
                              if cb.get('found') and cb.get('checked'))
            
            constraints = self.config['constraints']
            if 'exactly_one' in constraints and constraints['exactly_one']:
                results['constraint_met'] = checked_count == 1
            elif 'min_checked' in constraints:
                results['constraint_met'] = checked_count >= constraints['min_checked']
                if 'max_checked' in constraints:
                    results['constraint_met'] &= checked_count <= constraints['max_checked']
            else:
                results['constraint_met'] = True
            
            results['checked_count'] = checked_count
        
        self.results.append(results)
        return results
    
    def process_batch(self, pdf_paths: List[str], page_num: int = 0):
        """Process multiple PDFs."""
        import natural_pdf as npdf
        
        for pdf_path in pdf_paths:
            pdf = npdf.PDF(pdf_path)
            page = pdf[page_num]
            form_id = Path(pdf_path).stem
            yield self.process_form(page, form_id)
    
    def get_summary(self) -> pd.DataFrame:
        """Get summary of all processed forms."""
        data = []
        for result in self.results:
            row = {'form_id': result['form_id'], 'valid': result['valid']}
            for name, info in result['checkboxes'].items():
                row[f'{name}_checked'] = info.get('checked', False)
                row[f'{name}_confidence'] = info.get('confidence', 0)
            row['constraint_met'] = result.get('constraint_met', False)
            row['overall_confidence'] = result.get('confidence', 0)
            data.append(row)
        
        return pd.DataFrame(data)
    
    def flag_for_review(self, confidence_threshold: float = 0.8) -> List[str]:
        """Get forms that need human review."""
        return [r['form_id'] for r in self.results 
                if r['confidence'] < confidence_threshold or not r['valid']]


class InteractiveCheckboxReviewer:
    """
    Interactive tool for reviewing uncertain cases.
    """
    def __init__(self, processor: FormCheckboxProcessor):
        self.processor = processor
        self.corrections = {}
    
    def review_uncertain(self, confidence_threshold: float = 0.8):
        """Show uncertain cases for review."""
        uncertain = [r for r in self.processor.results 
                    if r['confidence'] < confidence_threshold]
        
        print(f"Found {len(uncertain)} uncertain cases to review")
        
        for i, result in enumerate(uncertain):
            print(f"\n--- Form {i+1}/{len(uncertain)}: {result['form_id']} ---")
            print(f"Overall confidence: {result['confidence']:.2f}")
            
            for name, info in result['checkboxes'].items():
                if info.get('found'):
                    status = "✓" if info['checked'] else "✗"
                    conf = info['confidence']
                    print(f"{name}: {status} (confidence: {conf:.2f})")
            
            # In a real implementation, show the actual checkbox images
            correction = input("Correct? (y/n/skip): ").lower()
            if correction == 'n':
                # Get corrections
                for name in result['checkboxes']:
                    if result['checkboxes'][name].get('found'):
                        checked = input(f"Is {name} checked? (y/n): ").lower() == 'y'
                        self.corrections[f"{result['form_id']}_{name}"] = checked
    
    def export_training_data(self, output_dir: str):
        """Export examples for future training."""
        # Implementation would save checkbox images with labels


class CheckboxExampleManager:
    """
    Manage a library of checkbox examples.
    """
    def __init__(self, examples_dir: str):
        self.examples_dir = Path(examples_dir)
        self.examples_dir.mkdir(exist_ok=True)
        
    def save_example(self, region, label: str, is_checked: bool):
        """Save a checkbox example."""
        subdir = self.examples_dir / ('checked' if is_checked else 'unchecked')
        subdir.mkdir(exist_ok=True)
        
        # Save image
        img = region.render(crop=True)
        filename = f"{label}_{len(list(subdir.glob('*.png')))}.png"
        img.save(subdir / filename)
        
        # Save metadata
        meta = {
            'label': label,
            'is_checked': is_checked,
            'bbox': region.bbox,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        with open(subdir / f"{filename}.json", 'w') as f:
            json.dump(meta, f)
    
    def load_examples(self) -> Tuple[List, List]:
        """Load all examples."""
        checked = list((self.examples_dir / 'checked').glob('*.png'))
        unchecked = list((self.examples_dir / 'unchecked').glob('*.png'))
        return checked, unchecked
    
    def create_calibrator(self) -> CheckboxCalibrator:
        """Create calibrator from saved examples."""
        calibrator = CheckboxCalibrator()
        
        # Mock implementation - would load actual images
        checked, unchecked = self.load_examples()
        print(f"Loading {len(checked)} checked and {len(unchecked)} unchecked examples")
        
        return calibrator


# Example usage patterns
if __name__ == "__main__":
    print("UX Pattern Examples")
    print("=" * 60)
    
    # Pattern 1: Simple pairwise comparison
    print("\n1. PAIRWISE COMPARISON")
    print("Pros: Simple, no setup needed")
    print("Cons: No learning, must process each time")
    print("""
    from temp.checkbox_checks import compare_checkboxes
    
    df = compare_checkboxes([cb1, cb2, cb3], ['A', 'B', 'C'])
    winner = df.loc['vote_score'].idxmax()
    print(f"Checked: {winner}")
    """)
    
    # Pattern 2: Calibration-based
    print("\n2. CALIBRATION-BASED")
    print("Pros: Learns from examples, improves over time")
    print("Cons: Requires initial setup")
    print("""
    calibrator = CheckboxCalibrator()
    
    # Add examples
    calibrator.add_example(checked_cb, is_checked=True)
    calibrator.add_example(unchecked_cb, is_checked=False)
    calibrator.calibrate()
    
    # Use on new checkboxes
    is_checked, confidence = calibrator.predict(new_cb)
    """)
    
    # Pattern 3: Template-based batch processing
    print("\n3. TEMPLATE-BASED BATCH")
    print("Pros: Handles many forms, constraint checking")
    print("Cons: Requires template definition")
    print("""
    config = {
        'checkboxes': {
            'acceptable': {'find': 'text=Acceptable', 'direction': 'left'},
            'deficient': {'find': 'text=Deficient', 'direction': 'left'},
        },
        'constraints': {'exactly_one': True}
    }
    
    processor = FormCheckboxProcessor(config)
    for result in processor.process_batch(pdf_files):
        if not result['constraint_met']:
            print(f"Invalid: {result['form_id']}")
    """)
    
    # Pattern 4: Confidence-based triage
    print("\n4. CONFIDENCE-BASED TRIAGE")
    print("Pros: Focuses human review on uncertain cases")
    print("Cons: Still requires some manual review")
    print("""
    # Process all forms
    results = processor.process_batch(pdfs)
    
    # Auto-accept high confidence
    high_conf = [r for r in results if r['confidence'] > 0.9]
    
    # Flag for review
    needs_review = processor.flag_for_review(confidence_threshold=0.8)
    print(f"Review needed: {len(needs_review)} forms")
    """)
    
    # Pattern 5: Active learning
    print("\n5. ACTIVE LEARNING")
    print("Pros: Improves accuracy with minimal human input")
    print("Cons: More complex implementation")
    print("""
    reviewer = InteractiveCheckboxReviewer(processor)
    
    # Review uncertain cases
    reviewer.review_uncertain(confidence_threshold=0.7)
    
    # Update calibrator with corrections
    for correction in reviewer.corrections:
        calibrator.add_example(region, is_checked=correction)
    calibrator.calibrate()
    """)