import importlib
import numpy as np
from typing import Dict

import torch

from .utils.loader import load_config


class YOLO:
    """    
    This class provides a unified interface for different YOLO tasks including
    detection, segmentation, pose estimation, and classification. It dynamically
    loads the appropriate predictor based on the task specified in the configuration.
    """
    
    _REGISTER = {
        "detect":   ("nxva.yolo.task.detect",   "DetectionPredictor"),
        "segment":  ("nxva.yolo.task.segment",  "SegmentationPredictor"),
        "pose":     ("nxva.yolo.task.pose",     "PosePredictor"),
        "classify": ("nxva.yolo.task.classify", "ClassificationPredictor"),
    }

    def __init__(self, config: dict):
        """
        Initialize the YOLO model with the given configuration.
        
        Args:
            config (dict): Configuration dictionary containing model parameters,
                         task type, and other settings
        """

        # Load and validate configuration
        self.config = load_config(config)
        # Get task type from config, default to 'detect' if not specified
        self.task = self.config.get('task', 'detect')

        # Extract module and class names for the specified task
        module_name, class_name = self._REGISTER[self.task]

        # Dynamically import the module and get the predictor class
        module = importlib.import_module(module_name)
        predictor_class = getattr(module, class_name)
        
        # Initialize the predictor with the configuration
        self._predictor = predictor_class(self.config)

    def __call__(self, imgs):
        """
        Perform inference on the input images.
        
        This method allows the YOLO object to be called directly like a function,
        delegating the inference to the appropriate predictor.
        
        Args:
            imgs: Input images (can be single image or batch of images)
            
        Returns:
            Prediction results from the model
        """
        return self._predictor(imgs)


class YOLOToolBox(YOLO):
    """    
    This class extends the base YOLO class with additional utility methods
    for model evaluation, export, and performance testing.
    """
    def __init__(self, config: dict):
        """
        Initialize the YOLO toolbox with the given configuration.
        
        Args:
            config (dict): Configuration dictionary containing model parameters
        """
        super().__init__(config)

    def __call__(self, imgs, img_paths):
        """
        Perform inference and construct results using the Results object.
        
        This method overrides the parent's __call__ method to provide
        additional result processing and formatting.
        
        Args:
            imgs: Input images for inference
            
        Returns:
            Processed results using the Results object for visualization
        """
        return self.construct_results(self._predictor(imgs), imgs, img_paths)
    
    def export(self, model:object = None, shape: tuple = (1, 3, 224, 224), dynamic: bool = False, type: str = 'fp16', output_path: str = 'model.engine', task: str = 'torch2engine'):
        """
        Export the model to different formats (ONNX, TensorRT engine, etc.).
        
        Args:
            model: Model to export (defaults to the predictor's model)
            shape: Input shape for the model (batch_size, channels, height, width)
            dynamic: Whether to use dynamic batch size
            type: Precision type for export (fp16, fp32, etc.)
            output_path: Path where the exported model will be saved
            task: Export task type (torch2engine, torch2onnx, onnx2engine)
            model_wrapper: Optional wrapper function to modify the model before export
        """
        yolo_task = self.config['task']
        if model is None:
            model = self._predictor.model.model
            model.to(torch.device(self.config['device']))

        if yolo_task == 'segment':
            def custom_forward(self, x):
                outputs = self.model(x)
                return outputs[0], outputs[1][-1]
        else:
            def custom_forward(self, x):
                outputs = self.model(x)
                return outputs[0]

        from nxva.yolo.utils.torch_utils import ExportWrapper        
        ExportWrapper.forward = custom_forward

        model = ExportWrapper(model)       

        if self.config['weights'].split('.')[-1] != 'pt':
            raise ValueError("Only pt weights are supported for export")

        from nxva.nxtrt.convert import Convert        
        # Validate input shape format
        assert len(shape) == 4, "The input shape must be (1, C, H, W)"
        
        # Perform the specified export task
        if task == 'torch2engine':
            Convert.torch_to_engine(model, shape, onnx_output_path=output_path, dynamic=dynamic, type=type)
        elif task == 'torch2onnx':
            Convert.convert_torch2onnx(model, shape, onnx_output_path=output_path, dynamic=dynamic, type=type)
        elif task == 'onnx2engine':
            Convert.convert_onnx2engine(model, shape, output_path=output_path, dynamic=dynamic, type=type)
        # elif task == 'onnx2jit':
        #     Convert.torch_to_jit(self.model, (1, 3, 224, 224), onnx_output_path=output_path, dynamic=False, type='fp16')
        else:
            raise ValueError(f"Unsupported task: {self.task}. Supported tasks: {self.supported_tasks}")

    def speed(self, val_txt_path, batch_size=1):
        """
        Perform speed testing on the model using validation data.
        
        This method measures the inference time for preprocessing, inference,
        and postprocessing stages separately.
        
        Args:
            val_txt_path: Path to validation data text file
            batch_size: Batch size for testing
        """
        from nxva.toolbox.val import SpeedCalculator, Profile, DatasetLoader
        
        # Initialize speed calculator
        self.speed = SpeedCalculator()            
        
        # Create data loader for validation
        val_loader = DatasetLoader(val_txt_path, task=self.predictor.task, num_kpts=self.predictor.kpt_shape, batch_size=batch_size)

        #warmup
        for val_img, gt_label in val_loader:
            n = len(val_img)
            pre_imgs, imgs = self._predictor.preprocess(val_img)
            pred = self._predictor.infer(pre_imgs)
            dets = self._predictor.postprocess(pred, pre_imgs, imgs)

        # Iterate through validation data and measure performance
        for val_img, gt_label in val_loader:
            n = len(val_img)
            
            # Create profilers for different stages
            profilers = (
                Profile(device=self.predictor.model.device),  # Preprocessing
                Profile(device=self.predictor.model.device),  # Inference
                Profile(device=self.predictor.model.device),  # Postprocessing
            )
            
            # Measure preprocessing time
            with profilers[0]:
                pre_imgs, imgs = self.predictor.preprocess(val_img)
                
            # Measure inference time
            with profilers[1]:
                pred = self.predictor.infer(pre_imgs)
                
            # Measure postprocessing time
            with profilers[2]:
                dets = self.predictor.postprocess(pred, pre_imgs, imgs)
                
            # Update speed calculator with measurements
            self.speed.update(n ,profilers)
            
        # Print speed test results
        print(self.speed.compute())

    def construct_results(self, preds, orig_imgs, img_paths):
        """
        Construct Results objects to encapsulate prediction results.
        
        This method uses the ultralytics Results object to standardize prediction
        results, enabling consistent visualization and processing across different
        YOLO tasks.
        
        Args:
            preds: List of prediction results from the model
            orig_imgs: List of original images in numpy array format
            
        Returns:
            List of Results objects containing processed predictions
        """
        from nxva.toolbox.result import Results
        
        results = []
        
        # Determine weight type from configuration
        weight_type = self.config['weights'].split('.')[-1]
        class_names = self.config['class_names']

        # Process predictions for each image based on task type
        for pred, orig_img, img_path in zip(preds, orig_imgs, img_paths):
            if self.task == 'detect':
                # Handle detection task - concatenate predictions if multiple detections
                if pred.shape[0] != 0:
                    pass
                else:
                    pred = np.zeros((1, 6))
                pred = torch.from_numpy(pred)
                results.append(Results(orig_img=orig_img, path=img_path, names=class_names, boxes=pred[:, :6]))            
                
            elif self.task == 'pose':
                # Handle pose estimation task - separate boxes and keypoints
                boxes, kpts = pred['boxes'], pred['keypoints']
                r = Results(orig_img=orig_img, path=img_path, names=class_names, boxes=boxes)            
                r.update(keypoints=kpts)
                results.append(r)

            elif self.task == 'segment':
                # Handle segmentation task - filter predictions with valid masks
                box, masks = pred['boxes'], pred['mask']
                keep = masks.sum((-2, -1)) > 0  # only keep predictions with masks
                box, masks = box[keep], masks[keep]
                results.append(Results(orig_img=orig_img, path=img_path, names=class_names, boxes=box, masks=masks))

            elif self.task == 'classify':
                # Handle classification task - use probabilities
                results.append(Results(orig_img=orig_img, path=img_path, names=class_names, probs=pred[0]))  
                
        return results