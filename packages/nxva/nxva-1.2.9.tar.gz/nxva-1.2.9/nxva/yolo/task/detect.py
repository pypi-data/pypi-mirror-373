import numpy as np
import torch

from .base_predictor import BasePredictor
from ..utils import ops


class DetectionPredictor(BasePredictor):
    def __init__(self, config: dict):
        super().__init__(config)
                
    def postprocess(self, pred, pre_imgs, imgs):
        """Post-processes predictions for an image and returns them.""" 
        if isinstance(pred, list):
            pred = torch.from_numpy(pred[0])

        pred = ops.non_max_suppression(
            pred,
            conf_threshold=self.conf,
            iou_threshold=self.iou,
            nc=self.nc,
            classes=self.classes,
            agnostic=self.agnostic,
            version=self.version,
            nms=self.nms,
        )
        results = []
        for i, det in enumerate(pred):
            if len(det):
                det = det.cpu().numpy()
                det[:, :4] = ops.scale_boxes(pre_imgs.shape[2:], det[:, :4], imgs[i].shape).round()
                det = det[np.argsort(det[:, 0])]
            else:
                det = np.zeros((0, 6), dtype=np.float32)
            results.append(det)
        return results