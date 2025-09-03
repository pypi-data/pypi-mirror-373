import torch, cv2, numpy as np
from .detect import DetectionPredictor
from ..utils import ops


class SegmentationPredictor(DetectionPredictor):
    """
    A class extending the DetectionPredictor class for prediction based on a segmentation model.
    """
    def __init__(self, config: dict):
        super().__init__(config)

    def postprocess(self, preds, img, orig_imgs):
        weight_type = self.config['weights'].split('.')[-1]
        if weight_type == 'pt':
            proto = preds[1][-1] if isinstance(preds[1], tuple) else preds[1]
        else:
            if weight_type == 'engine':
                preds[0], preds[1] = preds[1], preds[0]

            proto = torch.from_numpy(preds[1][None, ...] if preds[1].ndim == 3 else preds[1])

        """Applies non-max suppression and processes detections for each image in an input batch."""
        p = ops.non_max_suppression(
            preds,
            conf_threshold=self.conf,
            iou_threshold=self.iou,
            nc=self.nc,
            classes=self.classes,
            agnostic=self.agnostic,
            version=self.version,
            nms=self.nms,
        )
        results, bbox, mask = [], [], []        

        for i, (pred, orig_img) in enumerate(zip(p, orig_imgs)):
            if not len(pred): 
                masks = None
            masks = ops.process_mask(proto[i], pred[:, 6:], pred[:, :4], img.shape[2:], upsample=True)  # HWC
            pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], orig_img.shape)
            results.append({'boxes': pred[:, :6], 'mask': masks})
        return results