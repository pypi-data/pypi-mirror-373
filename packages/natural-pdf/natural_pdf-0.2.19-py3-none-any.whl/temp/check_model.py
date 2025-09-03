from ultralytics import RTDETR
import os

model_path = "/Users/soma/Development/natural-pdf/model-weights/checkbox-nano.pt"
print(f"Model exists: {os.path.exists(model_path)}")

try:
    model = RTDETR(model_path)
    print(f"Model loaded successfully")
    print(f"Model names: {model.names}")
    print(f"Model task: {model.task}")
    
    # Try to get architecture info
    if hasattr(model.model, 'yaml'):
        print(f"Model yaml: {model.model.yaml}")
    
    # Check the model structure
    if hasattr(model.model, 'model'):
        for i, module in enumerate(model.model.model):
            print(f"Layer {i}: {module}")
            if i > 5:  # Just show first few layers
                break
                
except Exception as e:
    print(f"Error: {e}")
    
    # Try loading as generic model to inspect
    import torch
    try:
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        print(f"\nCheckpoint keys: {list(checkpoint.keys())}")
        
        # Check for model configuration
        if 'model' in checkpoint and hasattr(checkpoint['model'], 'yaml'):
            print(f"Model yaml: {checkpoint['model'].yaml}")
        
        # Check train args for model info
        if 'train_args' in checkpoint:
            args = checkpoint['train_args']
            print(f"\nTraining args:")
            print(f"  Model: {getattr(args, 'model', 'Unknown')}")
            print(f"  Task: {getattr(args, 'task', 'Unknown')}")
            
        # Check epoch info
        if 'epoch' in checkpoint:
            print(f"  Epochs trained: {checkpoint['epoch']}")
            
    except Exception as e2:
        print(f"Error loading checkpoint: {e2}")