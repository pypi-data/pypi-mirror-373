"""Convert RF-DETR checkpoint to HuggingFace format"""
import torch
import json
from pathlib import Path

# Load your checkpoint
checkpoint = torch.load("model-weights/checkbox-nano.pt", map_location='cpu', weights_only=False)

# Extract model info
model_state = checkpoint['model']
args = checkpoint['args']

print(f"Model has {len(model_state)} parameters")
print(f"Classes: {args.class_names}")
print(f"Number of classes: {args.num_classes}")

# Create HF-style config
config = {
    "architectures": ["RFDetrForObjectDetection"],
    "model_type": "rf-detr",
    "num_labels": args.num_classes,
    "id2label": {str(i): label for i, label in enumerate(args.class_names)},
    "label2id": {label: str(i) for i, label in enumerate(args.class_names)},
    
    # RF-DETR specific
    "encoder": args.encoder,  # dinov2_windowed_small
    "hidden_dim": args.hidden_dim,
    "num_queries": args.num_queries,
    "dec_layers": args.dec_layers,
    "dim_feedforward": args.dim_feedforward,
    "dropout": args.dropout,
    "sa_nheads": args.sa_nheads,
    "ca_nheads": args.ca_nheads,
    "two_stage": args.two_stage,
    
    # Detection specific
    "bbox_loss_coef": args.bbox_loss_coef,
    "giou_loss_coef": args.giou_loss_coef,
    "cls_loss_coef": args.cls_loss_coef,
    
    # Training config
    "resolution": args.resolution,
    "pretrained_encoder": args.encoder,
}

# Save config
output_dir = Path("temp/checkbox-rf-detr-hf")
output_dir.mkdir(exist_ok=True)

with open(output_dir / "config.json", "w") as f:
    json.dump(config, f, indent=2)

# Save model weights in HF format
torch.save(model_state, output_dir / "pytorch_model.bin")

print(f"\nSaved to {output_dir}")
print("Next steps:")
print("1. Copy the custom RF-DETR implementation files from Thastp/rf-detr-base")
print("2. Upload to HuggingFace Hub with these files")
print("3. Use with transformers library")