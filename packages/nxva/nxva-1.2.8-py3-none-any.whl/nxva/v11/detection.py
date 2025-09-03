from dataclasses import dataclass
from typing import Union, List, Optional
from ultralytics import YOLO
import yaml
import torch
import numpy as np
from pathlib import Path
from PIL import Image

@dataclass(frozen=True)
class DetectorOptions:
    weights: str = './weights/yolo11s.pt'
    size: Union[int, tuple] = 640
    device: str = None
    conf_threshold: float = 0.25
    iou_threshold: float = 0.7
    classes: Optional[List[int]] = None
    class_names: dict = None
    fp16: bool = False
    verbose: bool = False
    batch: int = 1
    max_det: int = 300
    vid_stride: int = 1
    stream_buffer: bool = False
    visualze: bool = False
    augment: bool = False
    agnostic_nms: bool = False
    embed: Optional[List[int]] = None
    project: str = None
    name: str = None

class Detector():
    """
    A class to customize YOLOv11 detection output format based on a YAML configuration or an object.

    Attributes:
        weights (str): Path to the model weights file.
        size (int or tuple): Defines the image size for inference. Can be a single integer for square resizing
            or a (height, width) tuple.
        device (str): Specifies the device for inference.
        conf_threshold (float): The minimum confidence threshold for detections.
        iou_threshold (float): IoU threshold for Non-Maximum Suppression (NMS).
        classes (list): Only detections belonging to the specified classes will be returned.
        class_names (dict): Dictionary mapping class indices to class names.
        fp16 (bool): Whether to use half precision (FP16) for inference.
        verbose (bool): If True, enables verbose output during the model's initialization and subsequent operations.
        batch (int): Specifies the batch size for inference.
        max_det (int): Maximun number of detections allowed per image.
        vid_stride (int): Frame stride for video inputs.
        stream_buffer (bool): Determines whether to queue incoming frames for video streams.
        visualize (bool): Activates visualization of model features during inference.
        augment (bool): Enables test-time augmentation (TTA) for predictions, potentially improving detection
            robustness at the cost of inference speed.
        agnostic_nms (bool): Enables class-agnostic Non-Maximum Suppression (NMS), which merges overlapping boxes
            of different classes.
        embed (list): Specifies the layers from which to extract feature vectors or embeddings.
        project (str): Name of the project directory where prediction outputs are saved if save is enabled.
        name (str): Name of the prediction run. Used for creating a subdirectory within the project folder.
    """
    def __init__(self, config: Union[str, DetectorOptions]):
        """
        Initialize the Detector class.
        
        Args:
            config (Union[str, DetectorOptions]): A YAML configuration file path or a 'DetectorOptions' object.
        Raises:
            ValueError: If the config isn't a YAML file or 'DetectorOptions' object.

        Example:
            1. YAML file
                >>> model = Detector("config.yaml")
                >>> results = model(images)
                >>> print(results)
            2. object
                >>> options = DetectorOptions(conf_threshold=0.6, verbose=True....)
                >>> model = Detector(options)
                >>> results = model(images)
                >>> print(results)
        """
        # Load config from a YAML file or a DetectorOptions object
        if isinstance(config, str) and config.endswith(('yaml', 'yml')):
            with open(config, 'r') as f:
                self.config = yaml.safe_load(f)

        elif isinstance(config, DetectorOptions):
            self.config = {k: v for k, v in config.__dict__.items() if not k.startswith("__")}

        else:
            raise ValueError("Config must be a YAML file or object.")
            
        # Initialize attributes with values from the configuration
        self.weights = self.config["weights"]
        self.size = self.config.get('size', 640)
        self.device = self.config.get('device', None)
        self.conf_thres = self.config.get('conf_threshold', 0.25)
        self.iou_thres = self.config.get('iou_threshold', 0.7)
        self.classes = self.config.get('classes', None)
        self.class_names = self.config.get('class_names', None)
        self.batch = self.config.get('batch', 1)
        self.max_det = self.config.get('max_det', 300)
        self.vid_stride = self.config.get('vid_stride', 1)
        self.stream_buffer = self.config.get('stream_buffer', False)
        self.visualize = self.config.get('visualize', False)
        self.augment = self.config.get('augment', False)
        self.agnostic_nms = self.config.get('agnostic_nms', False)
        self.embed = self.config.get('embed', None)
        self.fp16 = self.config.get('fp16', False)
        self.verbose = self.config.get('verbose', False)
        self.project = self.config.get('project', None)
        self.name = self.config.get('name', None)
        
        # Load model
        self.model = self._load_model()

        # Initialize class names
        self._initialize_class_names()

    def _load_model(self):
        """Load the detection model based on YOLO."""
        model = YOLO(model=self.weights, task='detect')
        return model
    
    def _initialize_class_names(self):
        """Initialize the class names."""
        # Initialize class_names if not already set
        if not self.class_names:
            if hasattr(self.model, 'names') and self.model.names:
                self.class_names = self.model.names
            else:
                self.class_names = {}

        try:
            # Fill in missing class IDs
            for i in range(len(self.model.names)):
                if i not in self.class_names:
                    self.class_names[i] = str(i)
        except:
            print("Exception when filling in missing class.", flush=True)
        
        self.class_names = dict(sorted(self.class_names.items())) # Sort

        # Filter class names based on specified class IDs in self.classes
        cls = {}
        if self.classes:
            for cls_id in self.classes:
                if cls_id in self.class_names:
                    cls[cls_id] = self.class_names[cls_id]
            self.class_names = cls

    def __call__(self, images, *args, **kwargs):
        """
        Performs inference on the given image source and customizes the output format.

        Args:
            images (str | Path | int | PIL.Image | np.ndarray | torch.Tensor | List | Tuple): The input image(s) 
                to performs inference on. Accepts various types including file paths, URLs, PIL images, numpy arrays, 
                and torch tensors.
            **kwargs: Additional keyword arguments passed to the model inference.

        Return:
            (List): A list of customized output results, where each result contains [x1, y1, x2, y2, conf, label]
        """
        # Check images
        if isinstance(images, (np.ndarray, torch.Tensor)):
            if images.shape[0] == 0:
                print("The input image is empty", flush=True)
                return []
        elif isinstance(images, (list, tuple)):
            if not len(images):
                print("The input images list or tuple is empty", flush=True)
                return []
        # elif isinstance(images, (str, int, Path)):
        #     if not images:
        #         print("The source path, URL, or camera ID is empty", flush=True)
        #         return []
        elif isinstance(images, Image.Image):
            if images.size == (0, 0):
                print("The input PIL image is empty", flush=True)
                return []

        # Performs inference
        results = self.model(
            source = images,
            imgsz = self.size,
            device = self.device,
            conf = self.conf_thres,
            iou = self.iou_thres,
            classes = self.classes,
            batch = self.batch,
            max_det = self.max_det,
            vid_stride = self.vid_stride,
            stream_buffer = self.stream_buffer,
            visualize = self.visualize,
            augment = self.augment,
            agnostic_nms = self.agnostic_nms,
            embed = self.embed,
            half = self.fp16,
            verbose = self.verbose,
            project = self.project,
            name = self.name,
            **kwargs
        )

        # Customizes the output format
        customed_results = []
        for result in results:
            formatted_result = result.boxes.data.cpu().numpy()
            formatted_result[:, :4] = np.round(formatted_result[:, :4]).astype(int)
            formatted_result = formatted_result[np.argsort(formatted_result[:, 0])] # sort by horizontal axis
            customed_results.append(formatted_result)

        return customed_results
    
    def destroy(self):
        """
        Clean up resources.

        Deletes the model instance to release memory and ensure proper resource cleanup.
        """
        if self.model:
            del self.model