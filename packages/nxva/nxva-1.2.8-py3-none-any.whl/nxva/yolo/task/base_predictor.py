from typing import List, Dict, Union

import numpy as np
import torch

from ..utils import ops
from ..utils.torch_utils import build_nms
from ..nn.autobackend import AutoBackend


class BasePredictor:
    """
    This class provides the foundation for all YOLO task predictors including
    detection, segmentation, pose estimation, and classification. It handles
    common functionality such as model loading, preprocessing, inference, and
    postprocessing pipeline.
    """

    DEFAULT_CONFIG = {
        'device': 'cpu',
        'conf': 0.25,
        'iou': 0.45,
        'nms_type': 'torch', #torch/numpy
        'classes': None,
        'class_names': None,
        'agnostic': False,
        'fp16': False,
        'replace': {},
        'nc': 0,
        'kpt_shape': None,
    }

    def __init__(self, config: dict):
        """
        Initialize the BasePredictor class.

        Args:
            config (dict): Configuration dictionary containing:
                - weights (str): Path to the model file
                - version (str): Version of the model
                - task (str): Task type (detect, segment, pose, classify)
                - device (str): Device to run inference on ("cuda" or "cpu")
                - size (int): Input image size for preprocessing
                - conf (float): Confidence threshold for filtering predictions
                - iou (float): IoU threshold for NMS
                - classes (list): Classes to exclude from detection
                - class_names (dict): Dictionary mapping class indices to class names
                - fp16 (bool): Whether to use FP16 precision
        """
        # Step 1: merge default config
        for k, v in self.DEFAULT_CONFIG.items():
            config.setdefault(k, v)

        # Step 2: check required keys
        required_keys = ['version', 'weights', 'task', 'size']
        missing_required = [k for k in required_keys if not config.get(k)]
        if missing_required:
            raise ValueError(f"Missing required config keys or values: {missing_required}")

        # Step 3: check class_names and nc
        if (config['nc'] in [None, 0]) and not config['class_names']:
            raise ValueError("'nc' cannot be 0 or None when 'class_names' is also None")

        # Step 4: setting conig
        self.model_path = config['weights']
        self.task = config['task']
        self.device = config['device']
        self.version = config['version']
        self.size = config['size']

        # NMS
        self.conf = config['conf']
        self.iou = config['iou']
        self.classes = config['classes']
        self.class_names = config['class_names']
        self.agnostic = config['agnostic']

        # other settings
        self.nc = config['nc']
        self.kpt_shape = config['kpt_shape']

        # Step 5: initialize model
        self.nms = build_nms(config['nms_type'])
        self.model = AutoBackend(self.model_path, self.device, config)

        # Step 6: if class_names is not provided, get it from model or generate default
        if self.class_names is None:
            if hasattr(self.model, 'names'):
                self.class_names = self.model.names
                self.nc = len(self.class_names) if self.nc == 0 else self.nc
            elif self.nc != 0:
                self.class_names = {i: f'class_{i}' for i in range(self.nc)}
            else:
                raise ValueError("nc and class_names cannot be both None")
        if self.version not in ['yolov5', 'yolov5nu', 'yolov8', 'yolo11']:
            raise ValueError(f"Invalid version: {self.version}")

        # Step 7: special handling for pose task
        if self.task == 'pose':
            self.nc = config.get('nc', 1)  # force set nc to 1 (or user-defined)
            if self.kpt_shape is None:
                if hasattr(self.model, 'kpt_shape'):
                    self.kpt_shape = self.model.kpt_shape
                else:
                    self.kpt_shape = (17, 3)


        # Step 8: sync class_names / nc / kpt_shape back to config
        config['class_names'] = self.class_names
        config['nc'] = self.nc
        config['kpt_shape'] = self.kpt_shape
        self.config = config

        print('='*30)
        for k, v in self.config.items():
            print(f'{k}: {v}')
        print('='*30)

    def __call__(self, imgs):
        """
        Perform complete inference pipeline on input images.
        
        This method orchestrates the full inference process: preprocessing,
        model inference, and postprocessing.
        
        Args:
            imgs: Input images (a list of numpy array)
            
        Returns:
            Processed detection results
        """
        # Execute the complete inference pipeline
        pre_imgs, imgs = self.preprocess(imgs)
        pred = self.infer(pre_imgs)
        dets = self.postprocess(pred, pre_imgs, imgs)
        return dets

    def preprocess(self, im: Union[List[np.ndarray], torch.Tensor]) -> torch.Tensor:
        """
        Prepare input images for model inference.
        
        This method performs the necessary preprocessing steps including:
        - Resizing images to the target size using letterbox
        - Converting BGR to RGB color space
        - Transposing dimensions from BHWC to BCHW format
        - Normalizing pixel values to [0, 1] range
        
        Args:
            im (List[np.ndarray]): List of input images, each of shape (H, W, 3)

        Returns:
            tuple: (preprocessed_images, original_images)
                - preprocessed_images: numpy.ndarray of shape (N, 3, H, W)
                - original_images: List of original input images
        """        
        if self.size is None:
            raise ValueError("size is not set")
        if isinstance(im, torch.Tensor):
            im = im.cpu().numpy()
            
        # Apply letterbox transformation to resize images while maintaining aspect ratio
        pre_img = np.stack([ops.letterbox(img=x, new_shape=self.size) for x in im])
    
        # Convert BGR to RGB color space
        if pre_img.shape[-1] == 3:
            pre_img = pre_img[..., ::-1]  # BGR to RGB
            
        # Transpose from BHWC to BCHW format for PyTorch models
        pre_img = pre_img.transpose((0, 3, 1, 2))  # BHWC to BCHW, (n, 3, h, w)
        
        # Ensure memory layout is contiguous and convert to float32
        pre_img = np.ascontiguousarray(pre_img, dtype=np.float32)
    
        # Normalize pixel values from [0, 255] to [0, 1]
        pre_img /= 255
        return pre_img, im

    def infer(self, imgs):
        """
        Perform model inference on preprocessed images.
        
        This method runs the actual model forward pass to generate predictions.
        Subclasses may override this method to add task-specific preprocessing
        or postprocessing steps.
        
        Args:
            imgs: Preprocessed input images
            **kwargs: Additional keyword arguments to pass to the model
            
        Returns:
            Model predictions (format depends on task type)
        """
        return self.model(imgs)

    def postprocess(self, preds, img, orig_imgs):
        """
        Post-process model predictions to generate final results.
        
        This method should be implemented by subclasses to handle task-specific
        postprocessing such as NMS, coordinate transformations, and result formatting.
        
        Args:
            preds: Raw model predictions
            img: Preprocessed images
            orig_imgs: Original input images
            
        Returns:
            Processed results in task-specific format
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement this method")

