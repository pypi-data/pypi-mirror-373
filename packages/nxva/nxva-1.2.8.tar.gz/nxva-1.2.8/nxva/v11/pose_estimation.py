from dataclasses import dataclass
from typing import Union, List, Optional
from ultralytics import YOLO
import yaml
import torch
import numpy as np
from pathlib import Path
from PIL import Image
import warnings

@dataclass(frozen=True)
class PoseEstimatorOptions:
    weights: str = './weights/yolo11s-pose.pt'
    size: Union[int, tuple] = 640
    device: str = None
    conf_threshold: float = 0.25
    iou_threshold: float = 0.7
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

class PoseEstimator():
    """
    A class to customize YOLOv11 pose estimation output format based on a YAML configuration or an object.

    Attributes:
        weights (str): Path to the model weights file.
        size (int or tuple): Defines the image size for inference. Can be a single integer for square resizing
            or a (height, width) tuple.
        device (str): Specifies the device for inference.
        conf_threshold (float): The minimum confidence threshold for detections.
        iou_threshold (float): IoU threshold for Non-Maximum Suppression (NMS).
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
    def __init__(self, config: Union[str, PoseEstimatorOptions]):
        """
        Initialize the PoseEstimator class.
        
        Args:
            config (Union[str, PoseEstimatorOptions]): A YAML configuration file path or a 'PoseEstimatorOptions' object.
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
        # Load config from a YAML file or a pose estimation object
        if isinstance(config, str) and config.endswith(('yaml', 'yml')):
            with open(config, 'r') as f:
                self.config = yaml.safe_load(f)

        elif isinstance(config, PoseEstimatorOptions):
            self.config = {k: v for k, v in config.__dict__.items() if not k.startswith("__")}

        else:
            raise ValueError("Config must be a YAML file or object.")
        
        # Initialize attributes with values from the configuration
        setting = self.config
        self.weights = setting['weights']
        self.size = self.config.get('size', 640)
        self.device = setting.get('device', None)
        self.class_names = self.config.get('class_names', None)
        self.conf_thres = setting.get('conf_threshold', 0.25)
        self.iou_thres = setting.get('iou_threshold', 0.7)
        self.batch = setting.get('batch', 1)
        self.max_det = self.config.get('max_det', 300)
        self.vid_stride = setting.get('vid_stride', 1)
        self.stream_buffer = setting.get('stream_buffer', False)
        self.visualize = setting.get('visualize', False)
        self.augment = setting.get('augment', False)
        self.agnostic_nms = self.config.get('agnostic_nms', False)
        self.embed = self.config.get('embed', None)
        self.fp16 = setting.get('fp16', False)
        self.verbose = setting.get('verbose', False)
        self.project = setting.get('project', None)
        self.name = setting.get('name', None)

        # Load model
        self.model = self._load_model()

        # Initialize class names
        self._initialize_class_names()

    def _load_model(self):
        """Load the pose estimation model based on YOLO."""
        model = YOLO(model=self.weights, task='pose')
        return model
    
    def _initialize_class_names(self):
        """Initialize the class names."""
        # Initialize class_names if not already set
        if not self.class_names:
            if hasattr(self.model, 'names') and self.model.names:
                self.class_names = self.model.names
            else:
                warnings.warn("No 'class_names' found in the configuration.", UserWarning)

    def __call__(self, images, *args, **kwargs):
        """
        Performs inference on the given image source and customizes the output format.

        Args:
            images (str | Path | int | PIL.Image | np.ndarray | torch.Tensor | List | Tuple): The input image(s)
                to performs inference on. Accepts various types including file paths, URLs, PIL images, numpy arrays,
                and torch tensors.
            **kwargs: Additional keyword arguments passed to the model inference.

        Return:
            (List): A list of customized output results, where each result contains two keys: bbox, keypoints
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
        self.results = self.model(
            source = images,
            imgsz = self.size,
            device = self.device,
            conf = self.conf_thres,
            iou = self.iou_thres,
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
        for result in self.results:
            boxes = result.boxes.data.cpu().numpy()
            boxes[:, :4] = np.round(boxes[:, :4]).astype(int)
            keypoints_conf = result.keypoints.data.cpu().numpy()
            keypoints_conf[:, :, :2] = np.round(keypoints_conf[:, :, :2]).astype(int)
            keypoints_conf[:, :, 2] = np.round(keypoints_conf[:, :, 2], 5)

            customed_results.append({'bbox': boxes,'keypoints': keypoints_conf})

        return customed_results
    
    def show_results(
        self,
        conf=True,
        line_width=None,
        font_size=None,
        font="Arial.ttf",
        pil=False,
        img=None,
        im_gpu=None,
        kpt_radius=5,
        kpt_line=True,
        labels=True,
        boxes=True,
        masks=True,
        probs=True,
        show=False,
        save=False,
        filename=None,
        color_mode="class",
    ):
        """
        Plots prediction results on an input image.

        Args:
            conf (bool): Whether to plot detection confidence scores.
            line_width (float | None): Line width of bounding boxes. If None, scaled to image size.
            font_size (float | None): Font size for text. If None, scaled to image size.
            font (str): Font to use for text.
            pil (bool): Whether to return the image as a PIL Image.
            img (np.ndarray | None): Image to plot on. If None, uses original image.
            im_gpu (torch.Tensor | None): Normalized image on GPU for faster mask plotting.
            kpt_radius (int): Radius of drawn keypoints.
            kpt_line (bool): Whether to draw lines connecting keypoints.
            labels (bool): Whether to plot labels of bounding boxes.
            boxes (bool): Whether to plot bounding boxes.
            masks (bool): Whether to plot masks.
            probs (bool): Whether to plot classification probabilities.
            show (bool): Whether to display the annotated image.
            save (bool): Whether to save the annotated image.
            filename (str | None): Filename to save image if save is True.
            color_mode (bool): Specify the color mode, e.g., 'instance' or 'class'. Default to 'class'.

        Returns:
            (np.ndarray): Annotated image as a numpy array.

        Example:
            >>> annotated image = model.show_results()
            >>> cv2.imshow("result", annotated image)
        """
        annotated_images = []
        for result in self.results:
            annotated_images.append(result.plot(
                conf=conf,
                line_width=line_width,
                font_size=font_size,
                font=font,
                pil=pil,
                img=img,
                im_gpu=im_gpu,
                kpt_radius=kpt_radius,
                kpt_line=kpt_line,
                labels=labels,
                boxes=boxes,
                masks=masks,
                probs=probs,
                show=show,
                save=save,
                filename=filename,
                color_mode=color_mode,
            ))

        return annotated_images
    
    def destroy(self):
        """
        Clean up resources.

        Deletes the model instance to release memory and ensure proper resource cleanup.
        """
        if self.model:
            del self.model