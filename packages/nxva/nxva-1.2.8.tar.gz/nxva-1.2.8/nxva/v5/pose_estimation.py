
from ultralytics.utils import ops
from ultralytics.nn.autobackend import AutoBackend
import cv2
import time
import yaml
import torch
import torchvision
import numpy as np
from typing import Union
from dataclasses import dataclass

def clip_coords_pose(coords, shape):
    """
    Clip line coordinates to the image boundaries.

    Args:
        coords (torch.Tensor | numpy.ndarray): A list of line coordinates.
        shape (tuple): A tuple of integers representing the size of the image in the format (height, width).

    Returns:
        (torch.Tensor | numpy.ndarray): Clipped coordinates
    """
    if isinstance(coords, torch.Tensor):  # faster individually (WARNING: inplace .clamp_() Apple MPS bug)
        coords[..., 0] = coords[..., 0].clamp(0, shape[1] - 1)  # x
        coords[..., 1] = coords[..., 1].clamp(0, shape[0] - 1)  # y
    else:  # np.array (faster grouped)
        coords[..., 0] = coords[..., 0].clip(0, shape[1] - 1)  # x
        coords[..., 1] = coords[..., 1].clip(0, shape[0] - 1)  # y
        
    return coords


def clip_coords(boxes, img_shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    boxes[:, 0].clamp_(0, img_shape[1] - 1)  # x1
    boxes[:, 1].clamp_(0, img_shape[0] - 1)  # y1
    boxes[:, 2].clamp_(0, img_shape[1] - 1)  # x2
    boxes[:, 3].clamp_(0, img_shape[0] - 1)  # y2

def scale_coords_pose(img1_shape, coords, img0_shape, ratio_pad=None, normalize=False, padding=True):
    """
    Rescale segment coordinates (xy) from img1_shape to img0_shape.

    Args:
        img1_shape (tuple): The shape of the image that the coords are from.
        coords (torch.Tensor): the coords to be scaled of shape n,2.
        img0_shape (tuple): the shape of the image that the segmentation is being applied to.
        ratio_pad (tuple): the ratio of the image size to the padded image size.
        normalize (bool): If True, the coordinates will be normalized to the range [0, 1]. Defaults to False.
        padding (bool): If True, assuming the boxes is based on image augmented by yolo style. If False then do regular
            rescaling.

    Returns:
        coords (torch.Tensor): The scaled coordinates.
    """
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    if padding:
        coords[..., 0] -= pad[0]  # x padding
        coords[..., 1] -= pad[1]  # y padding
    coords[..., 0] /= gain
    coords[..., 1] /= gain
    coords = clip_coords_pose(coords, img0_shape)
    if normalize:
        coords[..., 0] /= img0_shape[1]  # width
        coords[..., 1] /= img0_shape[0]  # height
        
    return coords


def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True):
    # Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, 64), np.mod(dh, 64)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2
    
    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    
    return img, ratio, (dw, dh)

class TorchPoseEstimator:
    def __init__(
        self, 
        model, 
        device, 
        size,
        draw_settings,
        conf_thres=0.25,
        iou_thres=0.7,
        fp16=False 
    ):
        """
        初始化姿勢估計器。

        :param model: 用於姿勢估計的模型。
        :param device: 執行模型的設備（例如 'cpu' 或 'cuda'）。
        :param size: 輸入圖像的尺寸。
        :param conf_thres: 檢測的置信度閾值。
        :param iou_thres: 非最大抑制的交叉聯合比閾值。
        :param fp16: 是否使用半精度浮點數（對於某些GPU加速有用）。
        """
        self.model = model.half().eval() if fp16 else model.float().eval()
        self.device = device
        self.size = size
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.fps16 = fp16
        self.draw_settings = draw_settings
        self._initialize_draw_settings()
        
    def _initialize_draw_settings(self):
        with open(self.draw_settings, 'r') as f:
            draw_settings = yaml.safe_load(f)
        self.bbox_color = tuple(draw_settings['bbox_color'])
        self.bbox_thickness = draw_settings['bbox_thickness']
        self.bbox_labelstr = draw_settings['bbox_labelstr']
        self.kpt_color_map = draw_settings['kpt_color_map']
        self.kpt_labelstr = draw_settings['kpt_labelstr']
        self.skeleton_map = draw_settings['skeleton_map']
        self.kpt_labelstr = draw_settings['kpt_labelstr']

    def __call__(self, imgs):
        """
        對一個或多個圖像進行姿勢估計。

        :param imgs: 圖像數據，可以是單一圖像或圖像列表。
        :return: 每個圖像的姿勢估計結果。
        """
        if not len(imgs):
            return [] 
        
        # preprocess
        if isinstance(imgs, np.ndarray):
            imgs = [imgs] 
            
        pre_imgs = []
        for img in imgs:
            pre_img = letterbox(img, self.size, auto=False)[0]
            pre_img = pre_img.transpose((2, 0, 1))[::-1]  # HWC -> CHW, BGR -> RGB
            pre_img = np.ascontiguousarray(pre_img)
            pre_img = torch.from_numpy(pre_img).float().to(self.device)
            pre_img /= 255
            if self.fps16:
                pre_img = pre_img.half()
            pre_imgs.append(pre_img)
        pre_imgs = torch.stack(pre_imgs) # 將列表轉為tensor
        
        with torch.no_grad():
            
            preds = self.model(pre_imgs)
            preds = ops.non_max_suppression(
                preds,
                conf_thres=self.conf_thres,
                iou_thres=self.iou_thres,
                nc=1, # 代表只有一個類別，也就是人
            )
        results = []
        for i, det in enumerate(preds):
            if len(det):
                det[:, :4] = scale_coords(pre_imgs.shape[2:], det[:, :4], imgs[i].shape).round()
                pred_det = det[:, :6].cpu().numpy() # [x1, y1, x2, y2, conf, cls]
                bbox_xyxy = pred_det[:, :4].astype(int)
                
                pred_kpts = det[:, 6:].view(len(det), self.model.kpt_shape[0], self.model.kpt_shape[1]) # [n, 17, 2]
                pred_kpts = scale_coords_pose(pre_imgs.shape[2:], pred_kpts, imgs[i].shape)
                pred_kpts = pred_kpts.cpu().numpy()
                pred_kpts[..., :2] = pred_kpts[..., :2].astype(int)
                bbox_keypoints = pred_kpts
            else:
                bbox_xyxy = np.zeros((0, 4), dtype=int) # 因為沒有偵測到人，所以bbox為空
                bbox_keypoints = np.zeros((0, self.model.kpt_shape[0], self.model.kpt_shape[1]), dtype=int) # 因為沒有偵測到人，所以keypoints為空
            images_result = {
                'bbox': bbox_xyxy,
                'keypoints': bbox_keypoints
            }
            results.append(images_result)
            
        return results
    
    def draw_skeleton_on_image(self, img, bbox_keypoints, conf_thres=0.25):
        for skeleton in self.skeleton_map:
            srt_kpt_id = skeleton['srt_kpt_id']
            srt_kpt_x = bbox_keypoints[srt_kpt_id][0]
            srt_kpt_y = bbox_keypoints[srt_kpt_id][1]
            srt_kpt_score = bbox_keypoints[srt_kpt_id][2]
            if srt_kpt_score < conf_thres:
                continue

            if srt_kpt_x == 0 and srt_kpt_y == 0:
                continue

            dst_kpt_id = skeleton['dst_kpt_id']
            dst_kpt_x = bbox_keypoints[dst_kpt_id][0]
            dst_kpt_y = bbox_keypoints[dst_kpt_id][1]
            dst_kpt_score = bbox_keypoints[dst_kpt_id][2]
            if dst_kpt_score < conf_thres:
                continue

            if dst_kpt_x == 0 and dst_kpt_y == 0:
                continue

            skeleton_color = skeleton['color']
            skeleton_thickness = skeleton['thickness']

            img = cv2.line(
                img,
                (int(srt_kpt_x), int(srt_kpt_y)),
                (int(dst_kpt_x), int(dst_kpt_y)),
                color=skeleton_color,
                thickness=skeleton_thickness
            )

        return img
    
    def draw_keypoints_on_image(self, img, bbox_keypoints, show_id=False, conf_thres=0.25):
        for kpt_id in self.kpt_color_map:
            kpt_color_info = self.kpt_color_map[kpt_id]
            kpt_color = kpt_color_info['color']
            kpt_radius = kpt_color_info['radius']
            kpt_x = bbox_keypoints[kpt_id][0]
            kpt_y = bbox_keypoints[kpt_id][1]
            kpt_score = bbox_keypoints[kpt_id][2]

            if kpt_score < conf_thres:
                continue

            img = cv2.circle(
                img,
                (int(kpt_x), int(kpt_y)),
                radius=kpt_radius,
                color=kpt_color,
                thickness=-1
            )

            if show_id:
                kpt_label = str(kpt_id)
                offset_x = self.kpt_labelstr.get('offset_x', 0)
                offset_y = self.kpt_labelstr.get('offset_y', 0)
                font_size = self.kpt_labelstr.get('font_size', 0.5)
                font_thickness = self.kpt_labelstr.get('font_thickness', 1)

                img = cv2.putText(
                    img,
                    kpt_label,
                    (int(kpt_x + offset_x), int(kpt_y + offset_y)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_size,
                    kpt_color,
                    font_thickness
                )

        return img 

    def draw_pose_results_on_images(self, image, bboxes, keypoints, show_id=False, conf_thres=0.25): 
        min_length = min(len(bboxes), len(keypoints))
        bboxes = bboxes[:min_length]
        keypoints = keypoints[:min_length]
        for bbox, kpts in zip(bboxes, keypoints):
     
            if bbox.size != 0: 
                cv2.rectangle(
                    image,
                    (int(bbox[0]), int(bbox[1])),
                    (int(bbox[2]), int(bbox[3])),
                    color=self.bbox_color,
                    thickness=self.bbox_thickness
                )

      
            if len(kpts) != 0:  
                image = self.draw_keypoints_on_image(image, kpts, show_id, conf_thres)
                image = self.draw_skeleton_on_image(image, kpts, conf_thres)
        
        return image
    
    def destroy(self):
        if self.model:
            del self.model
    
# =============================================================================
# PoseEstimatorBuilder
# ============================================================================= 

@dataclass(frozen=True)
class PoseEstimatorOptions:
    weights: str = './weights/yolov8x-pose.pt'
    draw_settings: str = './configuration/body_pose_settings.yaml'
    size: Union[int, tuple] = 640
    conf_threshold: float = 0.25
    iou_threshold: float = 0.7
    fp16: bool = False
    verbose: bool = False

def PoseEstimator(config: Union[str, PoseEstimatorOptions]):
    """
    A class to initializes and load the PoseEstimator model based on a YAML configuration or an object.

    Args:
            config (Union[str, PoseEstimatorOptions]): A YAML configuration file path or a PoseEstimatorOptions object.
        Raises:
            ValueError: If the config isn't a YAML file or 'PoseEstimatorOptions' object.

        Example:
            1. YAML file
                >>> model = PoseEstimator("config.yaml")
                >>> results = model(images)
                >>> print(results)
            2. object
                >>> options = PoseEstimatorOptions(conf_threshold=0.6, verbose=True....)
                >>> model = PoseEstimator(options)
                >>> results = model(images)
                >>> print(results)
        """
    
    # Load config from a YAML file or a PoseEstimatorOptions object
    if isinstance(config, str) and config.endswith(('yaml', 'yml')):
        with open(config, 'r') as f:
            setting = yaml.safe_load(f)

    elif isinstance(config, PoseEstimatorOptions):
        setting = {k: v for k, v in config.__dict__.items() if not k.startswith("__")}

    else:
        raise ValueError("Config must be a YAML file or an object.")
    
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    # Load model
    model = AutoBackend(
        weights=setting['weights'],
        device=device,
        fp16=setting.get('fp16', False),
        verbose=setting.get('verbose', False)
    )

    # Load the pose estimator model based on file type
    pose_estimator = TorchPoseEstimator(
        model=model,
        device=device.type,  # 'cuda' or 'cpu'
        size=setting.get('size', 640), 
        draw_settings=setting['draw_settings'],
        conf_thres=setting.get('conf_threshold', 0.25), 
        iou_thres=setting.get('iou_threshold', 0.7),
        fp16=setting.get('fp16', False)
    )

    return pose_estimator
