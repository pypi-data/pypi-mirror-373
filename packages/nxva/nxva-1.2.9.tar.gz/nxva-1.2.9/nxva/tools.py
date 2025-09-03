import cv2
import numpy as np

def generate_mask(h, w, roi_list):
    """
    Generate the mask of the roi.
    Args:
        h: int
            height of the mask
        w: int
            width of the mask
        roi_list: list or np.ndarray -> (N, 2)
            list of roi or single roi
    
    Returns:
        mask: np.ndarray (h, w) -> dtype=bool
            mask of the roi
    """
    if isinstance(roi_list, np.ndarray) and len(roi_list.shape) == 2:
        roi_list = [roi_list]

    mask = np.zeros((h, w), dtype=np.uint8)
    for roi in roi_list:
        cv2.fillPoly(mask, [roi.reshape((-1, 1, 2))], color=255)
    
    return mask.astype(bool)