import torch

model_path = "/Users/soma/Development/natural-pdf/model-weights/checkbox-nano.pt"

# Load checkpoint
checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

print("Checkpoint keys:", checkpoint.keys())
print("\nArgs:", checkpoint['args'])

# Look at model structure
model = checkpoint['model']
print(f"\nModel type: {type(model)}")

# If it's an OrderedDict, it's just the state dict
if isinstance(model, dict):
    print(f"Model has {len(model)} weight tensors")
    # Look at first few keys to understand architecture
    for i, key in enumerate(list(model.keys())[:10]):
        print(f"  {key}")
        
# Check the args to understand what model this is
args = checkpoint['args']
print(f"\nModel configuration from args:")
for attr in ['model', 'task', 'mode', 'imgsz', 'batch', 'device']:
    if hasattr(args, attr):
        print(f"  {attr}: {getattr(args, attr)}")
        
# Try to determine RT-DETR variant
if hasattr(args, 'model'):
    model_name = getattr(args, 'model')
    print(f"\nModel name: {model_name}")
    
    # RT-DETR variants mapping
    if 'rtdetr' in str(model_name).lower():
        if '18' in str(model_name) or 'r18' in str(model_name):
            print("This appears to be RT-DETR with ResNet-18 backbone")
        elif '34' in str(model_name) or 'r34' in str(model_name):
            print("This appears to be RT-DETR with ResNet-34 backbone")
        elif '50' in str(model_name) or 'r50' in str(model_name):
            print("This appears to be RT-DETR with ResNet-50 backbone")
        elif '101' in str(model_name) or 'r101' in str(model_name):
            print("This appears to be RT-DETR with ResNet-101 backbone")