# YOLO Neural Network Modules - Unified Interface Management
"""
This module provides all core components for YOLO models, including:
- Detection heads: DetectV5, DetectV11, SegmentV5, SegmentV11, Pose
- Convolutional layers: Conv, DWConv, Concat
- Network blocks: C2f, C3, C3k, C3k2, SPPF, C2PSA, Bottleneck
- Functional modules: DFL, PSABlock, Attention, Proto
"""

# Import all required classes
from .block import (
    Bottleneck,
    C2f,
    C2PSA,
    C3,
    C3k,
    C3k2,
    SPPF,
    DFL,
    PSABlock,
    Attention,
    Proto,
    SPP,
    Contract,
    Focus,
)

from .conv import (
    Conv,
    DWConv,
    Concat,
    torch1_10_Upsample,
    # torch1_10_Conv2d,
)

from .head import (
    DetectV5,
    DetectV11,
    SegmentV5,
    SegmentV11,
    PoseV5,
    PoseV11,
    Classify
)

# Unified public interface definition
__all__ = (
    # === Detection Head Classes ===
    "DetectV5",      # YOLOv5 detection head
    "DetectV11",     # YOLOv11 detection head
    "SegmentV5",     # YOLOv5 segmentation head
    "SegmentV11",    # YOLOv11 segmentation head
    "PoseV5",        # Pose estimation head
    "PoseV11",       # Pose estimation head
    "Classify",      # Classification head
    
    # === Convolutional Layer Classes ===
    "Conv",          # Standard convolutional layer
    "DWConv",        # Depth-wise separable convolution
    "Concat",        # Tensor concatenation layer
    "torch1_10_Upsample", # Upsampling layer
    # "torch1_10_Conv2d", # Convolutional layer
    
    # === Network Block Classes ===
    "C2f",           # C2f module
    "C3",            # C3 module
    "C3k",           # C3k module
    "C3k2",          # C3k2 module
    "SPPF",          # Spatial Pyramid Pooling (Fast)
    "C2PSA",         # C2PSA module
    "SPP",           # SPP module
    "Bottleneck",    # Bottleneck module
    "Contract",      # Contract module
    "Focus",         # Focus module
    
    # === Functional Module Classes ===
    "DFL",           # Distribution Focal Loss
    "PSABlock",      # Position Sensitive Attention block
    "Attention",     # Attention mechanism
    "Proto",         # Prototype network
)
