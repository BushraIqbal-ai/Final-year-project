# ==============================================================================
# Copyright (c) 2026 Dr ASU. All Rights Reserved.
# Project: Parkinson's Disease Dementia Detection System
# Developer: Dr ASU
# ==============================================================================

import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
import torchvision.transforms as transforms

class GradCAM:
    """Gradient-weighted Class Activation Mapping for EfficientNet-B3."""
    
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        # Target: last conv block of C3BAMSEXAIv2 backbone
        target_layer = list(self.model.backbone.children())[-1]

        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor, class_idx=None):
        self.model.zero_grad()
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        score = output[0, class_idx]
        score.backward()

        # Pool gradients over spatial dimensions
        weights = self.gradients.mean(dim=[2, 3], keepdim=True)  # [1, C, 1, 1]
        cam = (weights * self.activations).sum(dim=1, keepdim=True)  # [1, 1, H, W]
        cam = F.relu(cam)

        # Normalize to [0, 1]
        cam = cam.squeeze().cpu().numpy()
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()
        return cam

def overlay_gradcam(original_pil, cam, alpha=0.5):
    """Overlay the GradCAM heatmap on the original PIL image."""
    # Resize CAM to match original image
    img_array = np.array(original_pil.convert('RGB'))
    h, w = img_array.shape[:2]
    cam_resized = cv2.resize(cam, (w, h))
    
    # Apply colormap (INFERNO for medical aesthetic)
    heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_INFERNO)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    # Blend
    overlay = (alpha * heatmap + (1 - alpha) * img_array).astype(np.uint8)
    return Image.fromarray(overlay)
