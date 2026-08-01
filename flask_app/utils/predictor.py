# ==============================================================================
# Copyright (c) 2026 Dr ASU. All Rights Reserved.
# Project: Parkinson's Disease Dementia Detection System
# Developer: Dr ASU
# ==============================================================================

import os
import uuid
import json

try:
    import torch
    import torch.nn.functional as F
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from config import Config

# ── Image transform pipeline ────────────────────────────────
if TORCH_AVAILABLE:
    TRANSFORM = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])

# ── Global model cache ───────────────────────────────────────
_model       = None
_gradcam_obj = None
_device      = 'cpu'
_model_error  = None   # stores error string if load failed


def get_model():
    global _model, _gradcam_obj, _device, _model_error
    if _model is not None:
        return _model, _gradcam_obj, _device

    if _model_error:
        raise RuntimeError(_model_error)

    if not TORCH_AVAILABLE:
        _model_error = "PyTorch not installed. Run: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu"
        raise RuntimeError(_model_error)

    if not os.path.exists(Config.MODEL_PATH):
        _model_error = f"Model file not found at: {Config.MODEL_PATH}"
        raise RuntimeError(_model_error)

    try:
        from models.cnn_model import load_model
        from utils.gradcam_utils import GradCAM

        _device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[NeuroScan] Loading model from {Config.MODEL_PATH} on {_device}...")
        _model = load_model(Config.MODEL_PATH, device=_device)
        _gradcam_obj = GradCAM(_model)
        print(f"[NeuroScan] Model loaded successfully!")
    except Exception as e:
        _model_error = str(e)
        raise RuntimeError(f"Model loading failed: {e}")

    return _model, _gradcam_obj, _device


def predict_image(image_path, generate_gradcam=True):
    """
    Run inference on an uploaded MRI image.
    Returns dict with class, confidence, all probabilities, and optional GradCAM path.
    """
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow not installed. Run: pip install Pillow")

    model, gradcam_obj, device = get_model()

    # Load and preprocess image
    original = Image.open(image_path).convert('RGB')
    input_tensor = TRANSFORM(original).unsqueeze(0).to(device)

    # Forward pass (no grad for speed)
    with torch.no_grad():
        logits = model(input_tensor)
        probs  = F.softmax(logits, dim=1)[0].cpu().numpy()

    predicted_idx   = int(probs.argmax())
    predicted_class = Config.CLASSES[predicted_idx]
    confidence      = float(probs[predicted_idx])

    all_probs = {
        Config.CLASSES[i]: round(float(probs[i]) * 100, 2)
        for i in range(len(probs))
    }

    # ── GradCAM ──────────────────────────────────────────────
    gradcam_filename = None
    if generate_gradcam and gradcam_obj is not None:
        try:
            from utils.gradcam_utils import overlay_gradcam

            input_grad = TRANSFORM(original).unsqueeze(0).to(device)
            input_grad.requires_grad_(True)
            cam     = gradcam_obj.generate(input_grad, class_idx=predicted_idx)
            overlay = overlay_gradcam(original, cam)

            gradcam_filename = f"gradcam_{uuid.uuid4().hex[:8]}.png"
            os.makedirs(Config.RESULTS_FOLDER, exist_ok=True)
            overlay.save(os.path.join(Config.RESULTS_FOLDER, gradcam_filename))
        except Exception as e:
            print(f"[NeuroScan] GradCAM skipped: {e}")
            gradcam_filename = None

    return {
        'predicted_class':  predicted_class,
        'confidence':       confidence,
        'confidence_pct':   round(confidence * 100, 2),
        'all_probs':        all_probs,
        'gradcam_filename': gradcam_filename,
        'class_color':      Config.CLASS_COLORS.get(predicted_class, '#64748b'),
        'class_info':       Config.CLASS_INFO.get(predicted_class, {}),
    }


def model_status():
    """Returns a dict describing current model load state."""
    global _model, _model_error
    if _model is not None:
        return {'loaded': True,  'message': 'Model ready', 'torch': True}
    if _model_error:
        return {'loaded': False, 'message': _model_error, 'torch': TORCH_AVAILABLE}
    if not TORCH_AVAILABLE:
        return {'loaded': False, 'message': 'PyTorch not installed', 'torch': False}
    if not os.path.exists(Config.MODEL_PATH):
        return {'loaded': False, 'message': f'Model file missing: {Config.MODEL_PATH}', 'torch': True}
    return {'loaded': False, 'message': 'Model not yet loaded (will load on first prediction)', 'torch': True}
