"""Test using RT-DETR with DINOv2 backbone in transformers"""
from transformers import RTDetrConfig, RTDetrForObjectDetection
import torch

# Create config with DINOv2 backbone
config = RTDetrConfig(
    # Model architecture
    backbone="facebook/dinov2-small",  # DINOv2 small variant
    use_pretrained_backbone=False,  # We'll load our weights
    backbone_kwargs={
        "out_indices": [3, 6, 9, 12],  # Match the indices from your model
    },
    
    # Detection head config (from your checkpoint)
    num_labels=3,  # checked, unchecked, (background?)
    hidden_dim=256,
    num_queries=300,
    decoder_layers=2,
    d_model=256,
    dim_feedforward=2048,
    dropout=0.0,
    nheads=8,  # sa_nheads from your model
    
    # Loss coefficients
    bbox_loss_coefficient=5.0,
    giou_loss_coefficient=2.0,
    cls_loss_coefficient=1.0,
)

# Initialize model
model = RTDetrForObjectDetection(config)

print(f"Model initialized with {sum(p.numel() for p in model.parameters())} parameters")

# Your checkpoint has these keys in the state dict
# We'd need to map them to the RT-DETR expected keys
checkpoint = torch.load("model-weights/checkbox-nano.pt", map_location='cpu', weights_only=False)
state_dict = checkpoint['model']

# Show some key mappings needed
print("\nYour model keys (first 5):")
for key in list(state_dict.keys())[:5]:
    print(f"  {key}")
    
print("\nRT-DETR expects keys like:")
for key in list(model.state_dict().keys())[:5]:
    print(f"  {key}")
    
print("\nWould need to create a mapping between these formats")