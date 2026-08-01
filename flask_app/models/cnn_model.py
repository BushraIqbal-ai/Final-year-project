# ==============================================================================
# Copyright (c) 2026 Dr ASU. All Rights Reserved.
# Project: Parkinson's Disease Dementia Detection System
# Developer: Dr ASU
# ==============================================================================

try:
    import torch
    import torch.nn as nn
    import torchvision.models as tv_models
    import torchvision.models.efficientnet as efficientnet
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

NUM_CLASSES = 5

class SEBlock(nn.Module):
    def __init__(self, channels, ratio=16):
        super().__init__()
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fc  = nn.Sequential(
            nn.Linear(channels, max(channels//ratio,1), bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(max(channels//ratio,1), channels, bias=False),
            nn.Sigmoid())
    def forward(self, x):
        b,c,_,_ = x.shape
        return x * self.fc(self.gap(x).view(b,c)).view(b,c,1,1)

class ChannelAttention(nn.Module):
    def __init__(self, channels, ratio=8):
        super().__init__()
        r = max(channels//ratio, 1)
        self.mlp = nn.Sequential(
            nn.Linear(channels, r, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(r, channels, bias=False))
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.gmp = nn.AdaptiveMaxPool2d(1)
    def forward(self, x):
        b,c,_,_ = x.shape
        w = torch.sigmoid(self.mlp(self.gap(x).view(b,c)) +
                          self.mlp(self.gmp(x).view(b,c)))
        return x * w.view(b,c,1,1)

class SpatialAttention(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, 7, padding=3, bias=False)
    def forward(self, x):
        cat = torch.cat([x.mean(1,keepdim=True),
                         x.max(1,keepdim=True).values], dim=1)
        return x * torch.sigmoid(self.conv(cat))

class CBAMBlock(nn.Module):
    def __init__(self, channels, ratio=8):
        super().__init__()
        self.ca = ChannelAttention(channels, ratio)
        self.sa = SpatialAttention()
    def forward(self, x):
        return self.sa(self.ca(x))

class CBAMSERefinement(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.cbam = CBAMBlock(channels)
        self.se   = SEBlock(channels)
    def forward(self, x):
        return self.se(self.cbam(x))

class C3BAMSEXAIv2(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        bb = tv_models.efficientnet_b3(weights=None)
        self.backbone = bb.features        # Bx1536x7x7
        self.cbam_se  = CBAMSERefinement(1536)
        self.gap      = nn.AdaptiveAvgPool2d(1)
        self.gmp      = nn.AdaptiveMaxPool2d(1)
        self.head     = nn.Sequential(
            nn.Linear(3072, 1024, bias=False), nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True), nn.Dropout(0.45),
            nn.Linear(1024,  512, bias=False), nn.BatchNorm1d(512),
            nn.ReLU(inplace=True), nn.Dropout(0.35),
            nn.Linear( 512,  256, bias=False), nn.BatchNorm1d(256),
            nn.ReLU(inplace=True), nn.Dropout(0.25),
            nn.Linear( 256, num_classes))
            
    def forward(self, x):
        x = self.backbone(x)
        x = self.cbam_se(x)
        x = torch.cat([self.gap(x).flatten(1),
                        self.gmp(x).flatten(1)], dim=1)
        return self.head(x)

def load_model(model_path, device='cpu'):
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is not installed.")

    model = C3BAMSEXAIv2(num_classes=NUM_CLASSES)
    state = torch.load(model_path, map_location=device, weights_only=False)
    
    if isinstance(state, dict):
        for key in ('model_state_dict', 'state_dict', 'model'):
            if key in state:
                state = state[key]
                break

    model.load_state_dict(state, strict=True)
    model.to(device)
    model.eval()
    return model
