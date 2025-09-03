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
class ClassifierOptions:
    weights: str = './weights/yolo11s-cls.pt'
    size: Union[int, tuple] = 640
    device: str = None
    class_names: dict = None
    fp16: bool = False
    verbose: bool = False
    batch: int = 1
    visualze: bool = False
    augment: bool = False
    embed: Optional[List[int]] = None
    project: str = None
    name: str = None

class Classifier():
    """
    A class to customize YOLOv11 classification output format based on a YAML configuration or an object.

    Attributes:
        weights (str): Path to the model weights file.
        size (int or tuple): Defines the image size for inference. Can be a single integer for square resizing
            or a (height, width) tuple.
        device (str): Specifies the device for inference.
        class_names (dict): Dictionary mapping class indices to class names.
        fp16 (bool): Whether to use half precision (FP16) for inference.
        verbose (bool): If True, enables verbose output during the model's initialization and subsequent operations.
        batch (int): Specifies the batch size for inference.
        visualize (bool): Activates visualization of model features during inference.
        augment (bool): Enables test-time augmentation (TTA) for predictions, potentially improving detection
            robustness at the cost of inference speed.
        embed (list): Specifies the layers from which to extract feature vectors or embeddings.
        project (str): Name of the project directory where prediction outputs are saved if save is enabled.
        name (str): Name of the prediction run. Used for creating a subdirectory within the project folder.
    """
    def __init__(self, config: Union[str, ClassifierOptions]):
        """
        Initialize the Classifier class.
        
        Args:
            config (Union[str, ClassifierOptions]): A YAML configuration file path or a 'ClassifierOptions' object.
        Raises:
            ValueError: If the config isn't a YAML file or 'ClassifierOptions' object.

        Example:
            1. YAML file
                >>> model = Classifier("config.yaml")
                >>> results = model(images)
                >>> print(results)
            2. object
                >>> options = ClassifierOptions(verbose=True....)
                >>> model = Classifier(options)
                >>> results = model(images)
                >>> print(results)
        """
        # Load config from a YAML file or a ClassifierOptions object
        if isinstance(config, str) and config.endswith(('yaml', 'yml')):
            with open(config, 'r') as f:
                self.config = yaml.safe_load(f)

        elif isinstance(config, ClassifierOptions):
            self.config = {k: v for k, v in config.__dict__.items() if not k.startswith("__")}

        else:
            raise ValueError("Config must be a YAML file or object.")

        # Initialize attributes with values from the configuration
        self.weights = self.config['weights']
        self.size = self.config.get('size', 640)
        self.device = self.config.get('device', None)
        self.class_names = self.config.get('class_names', None)
        self.batch = self.config.get('batch', 1)
        self.visualize = self.config.get('visualize', False)
        self.augment = self.config.get('augment', False)
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
        """Load the classification model based on YOLO."""
        model = YOLO(model = self.weights, task='classify')
        return model
    
    def _initialize_class_names(self):
        """Initialize the class names."""
        # Initialize class_names if not already set
        if not self.class_names:
            if hasattr(self.model, 'names') and self.model.names:
                self.class_names = self.model.names
            else:
                warnings.warn("No 'class_names' found in the configuration.", UserWarning)
    
    def __call__(self, images, top_k=1, *args, **kwargs):
        """
        Performs inference on the given image source and customizes the output format.

        Args:
            images (str | Path | int | PIL.Image | np.ndarray | torch.Tensor | List | Tuple): The input image(s)
                to performs inference on. Accepts various types including file paths, URLs, PIL images, numpy arrays,
                and torch tensors.
            **kwargs: Additional keyword arguments passed to the model inference.

        Return:
            (List): A list of customized output results, where each result contains the top-k predictions for the
                corresponding input.
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
            batch = self.batch,
            visualize = self.visualize,
            augment = self.augment,
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
            all_class_ids = result.probs.data
            sorted_class_ids = (-all_class_ids).argsort(0).tolist()
            confidences = all_class_ids[sorted_class_ids].cpu().numpy()
            
            if top_k < 0:
                selected_indices = range(len(sorted_class_ids)) # Displays all rankings
            else:
                selected_indices = range(min(top_k, len(sorted_class_ids))) # Displays the top_k rankings.

            formatted_result = {sorted_class_ids[i] : confidences[i] for i in selected_indices}
            customed_results.append(formatted_result)
        return customed_results
            
    def destroy(self):
        """
        Clean up resources.

        Deletes the model instance to release memory and ensure proper resource cleanup.
        """
        if self.model:
            del self.model