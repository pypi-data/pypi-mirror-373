import torch
import numpy as np

from .detect import DetectionPredictor
from ..utils import ops


class PosePredictor(DetectionPredictor):
    def __init__(self, config: dict):
        super().__init__(config)

    def postprocess(self, preds, img, orig_imgs):
        if isinstance(preds, list):
            preds = preds[0] if preds[0].ndim == 3 else preds[-1]
            preds = torch.from_numpy(preds)

        preds = ops.non_max_suppression(
            preds,
            conf_threshold=self.conf,
            iou_threshold=self.iou,
            nc=self.nc,
            classes=self.classes,
            agnostic=self.agnostic,
            version=self.version,
            nms=self.nms,
            task=self.task,
        )
        results = []
        for pred, orig_img in zip(preds, orig_imgs):
            pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], orig_img.shape).round()
            pred_kpts = pred[:, 6:].view(len(pred), *self.kpt_shape) if len(pred) else pred[:, 6:]
            pred_kpts = ops.scale_coords(img.shape[2:], pred_kpts, orig_img.shape)
            results.append({'boxes': pred[:, :6], 'keypoints': pred_kpts})
        return results