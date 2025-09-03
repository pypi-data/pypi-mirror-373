from PIL import Image

import numpy as np
import torch, cv2

from .base_predictor import BasePredictor
from ..utils import ops


class ClassificationPredictor(BasePredictor):
    def __init__(self, config: dict):
        super().__init__(config)
        self.transforms = ops.classify_transforms(size=self.size)

    def preprocess(self, imgs):
        if not isinstance(imgs, torch.Tensor):
            img_stack = np.stack(
                [self.transforms(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))) for im in imgs]
            )
        return img_stack, imgs

    def postprocess(self, preds, img=None, orig_imgs=None):
        preds = preds[0] if isinstance(preds, (list, tuple)) else preds
        preds = torch.from_numpy(preds) if isinstance(preds, np.ndarray) else preds
        
        top5 = torch.topk(preds, k=5, dim=1)
        return preds, top5