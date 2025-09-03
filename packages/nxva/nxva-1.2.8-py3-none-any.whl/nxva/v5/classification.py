import os
import cv2
import sys
import yaml
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from nxva.utilities import timer
from typing import Union
from dataclasses import dataclass
import warnings

IMAGENET_MEAN = 0.485, 0.456, 0.406  # RGB mean
IMAGENET_STD = 0.229, 0.224, 0.225  # RGB standard deviation

class CenterCrop:
    # YOLOv5 CenterCrop class for image preprocessing, i.e. T.Compose([CenterCrop(size), ToTensor()])
    def __init__(self, size=640):
        super().__init__()
        self.h, self.w = (size, size) if isinstance(size, int) else size

    def __call__(self, im):  # im = np.array HWC
        imh, imw = im.shape[:2]
        m = min(imh, imw)  # min dimension
        top, left = (imh - m) // 2, (imw - m) // 2
        return cv2.resize(im[top:top + m, left:left + m], (self.w, self.h), interpolation=cv2.INTER_LINEAR)
    
    
class ToTensor:
    # YOLOv5 ToTensor class for image preprocessing, i.e. T.Compose([LetterBox(size), ToTensor()])
    def __init__(self, half=False):
        super().__init__()
        self.half = half

    def __call__(self, im):  # im = np.array HWC in BGR order
        im = np.ascontiguousarray(im.transpose((2, 0, 1))[::-1])  # HWC to CHW -> BGR to RGB -> contiguous
        im = torch.from_numpy(im)  # to torch
        im = im.half() if self.half else im.float()  # uint8 to fp16/32
        im /= 255.0  # 0-255 to 0.0-1.0
        return im
    

def classify_transforms(size=640):
    # Transforms to apply if albumentations not installed
    assert isinstance(size, int), f'ERROR: classify_transforms size {size} must be integer, not (list, tuple)'
    # T.Compose([T.ToTensor(), T.Resize(size), T.CenterCrop(size), T.Normalize(IMAGENET_MEAN, IMAGENET_STD)])
    return T.Compose([CenterCrop(size), ToTensor(), T.Normalize(IMAGENET_MEAN, IMAGENET_STD)])

class BaseClassifier:
    """
    BaseClassifier.

    A base class for creating classifier.

    Attributes:
        model_path (str): Path to the model file.
        device (str): "cuda" or "cpu".
        size (int): The size of the input image.
        fp16 (bool): Flag for using FP16 precision during inference.
        transforms (callable): Transformation function for preprocessing input images.
        class_names (list): List of class names for the model's outputs.
    """
    def __init__(self, model_path, device, size, class_names=None, fp16=False, verbose=False):
        """
        Initialize the BaseClassifier class.

        Args:
            model_path (str): Path to the model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            verbose (bool): Whether to output the timer.
        """
        assert model_path, 'ERROR: model_path required.'
        self.model_path = model_path
        self.device = device
        self.size = size
        self.fp16 = fp16
        self.class_names = class_names
        self.transforms = classify_transforms(self.size)
        self.model = self.load_model()

        if self.class_names is None:
            if hasattr(self.model, 'module') and self.model.class_names:
                self.class_names = self.model.module.names
            elif hasattr(self.model, 'names') and self.model.names:
                self.class_names = self.model.names
            else:
                warnings.warn("No 'class_names' found in the configuration.", UserWarning)
        
    def load_model(self):
        raise NotImplementedError("Subclasses should overwrite this method to load the model!")

    @timer()
    def preprocess(self, imgs):
        """Prepares input image before inference."""
        if isinstance(imgs, list):
            imgs = [self.transforms(img) for img in imgs]
            imgs = torch.stack(imgs)
        else:
            imgs = self.transforms(imgs)
            imgs = imgs.unsqueeze(0)
        
        imgs = imgs.to(self.device)

        if self.fp16:
            imgs = imgs.half()
        return imgs
    
    @timer()
    def post_process(self, results, top_k=1):
        """Post-processes predictions for an image and returns them."""
        ret = []  
        top_k = min(top_k, len(self.class_names))
        for result in results:
            if top_k < 0:
                rank = np.argsort(result)[::-1] # Displays all rankings
            else:
                rank = np.argsort(result)[::-1][:top_k] # Displays the top_k rankings.

            processed_result = {i: result[i] for i in rank}
                
            ret.append(processed_result)
            
        return ret

    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the specified model."""
        raise NotImplementedError("Subclasses should overwrite this method to run the classification!")
    
    def destroy(self):
        pass
    
    def __call__(self, imgs, top_k=1):
        """Performs inference on the given image source."""
        pre_imgs = self.preprocess(imgs) 
        if not self.needs_tensor():
            pre_imgs = pre_imgs.cpu().numpy()

        results = self.infer(pre_imgs)
        ret = self.post_process(results, top_k = top_k)
        return ret
        
    def needs_tensor(self):
        return True

class TorchClassifier(BaseClassifier):
    """
    TorchClassifier.

    A class for loading and running classification models in PyTorch format.
    """
    def __init__(self, model_path, device, size, class_names=None, fp16=False, verbose=False):
        """
        Initialize the TorchClassifier class.

        Args:
            model_path (str): Path to the PyTorch model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            verbose (bool): Whether to output the timer.
        """
        super().__init__(model_path, device, size, class_names, fp16, verbose)

    def load_model(self):
        """Load PyTorch model."""
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        sys.path.insert(0, os.path.join(current_dir, 'yolov5'))
        from models.experimental import attempt_load
        sys.path.remove(os.path.join(current_dir, 'yolov5'))

        model = attempt_load(self.model_path, device=self.device)
        model = model.half().eval() if self.fp16 else model.float().eval()
        return model
    
    @timer()
    def infer(self, imgs):  
        """Runs inference on a given image using the PyTorch model."""
        with torch.no_grad():
            results = self.model(imgs)
            results = F.softmax(results, dim=1)  # probabilities
            results = results.cpu().numpy()
        return results
    
class ONNXClassifier(BaseClassifier):
    """
    ONNXClassifier.

    A class for loading and running classification models in ONNX format.

    Attributes:
        size (tuple): The size of the model input, typically (width, height).
    """
    def __init__(self, model_path, device, size, class_names=None, fp16=False, verbose=False):
        """
        Initialize the ONNXClassifier class.

        Args:
            model_path (str): Path to the ONNX model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            verbose (bool): Whether to output the timer.
        """
        super().__init__(model_path, device, size, class_names, fp16, verbose)
        self.size = self.determine_input_size()
        assert self.size == (size, size) ,"The input size of the model is not the same as the size in the config file."

    def load_model(self):
        """Load ONNX model."""
        import onnxruntime as ort
        if self.device == 'cuda':
            print("Using CUDA")
            providers = [("CUDAExecutionProvider", {"device_id": 0})]
        else:
            print("Using CPU")
            providers = ["CPUExecutionProvider"]

        return ort.InferenceSession(self.model_path, providers=providers)
    
    def determine_input_size(self):
        """Determines the input size expected by the model."""
        input_shape = self.model.get_inputs()[0].shape
        assert len(input_shape) == 4, "Input shape is not 4D" 
        assert input_shape[2] is not None and input_shape[3] is not None, "Input height/width is None"
        return (input_shape[2], input_shape[3])
    
    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the ONNX model."""
        results = self.model.run(None, {self.model.get_inputs()[0].name: imgs})  # Perform inference
        results = F.softmax(torch.tensor(results[0]), dim=1)  # Convert result to tensor and apply softmax
        results = results.cpu().numpy()  # Move to CPU and convert to NumPy
        return results
    
    def needs_tensor(self):
        return False

class TensorRTClassifier(BaseClassifier):
    """
    TensorRTClassifier.

    A class for loading and running classification models in TensorRT format.

    Attributes:
        trt (module): TensorRT module.
        cuda (module): PyCUDA module.
        engine (TensorRT.ICudaEngine): TensorRT engine.
        context (TensorRT.IExecutionContext): TensorRT execution context.
        size (tuple): The size of the input image.
        fixed_batch (int): The fixed batch size of the model.
        bindings (list): List of buffer bindings. Pointer to the input and output buffers.
        inputs (list): List of input buffers.  
        outputs (list): List of output buffers.
        stream (pycuda.driver.Stream): CUDA stream. Used for asynchronous memory transfers.
    """
    def __init__(self, model_path, device, size, class_names=None, fp16=False, verbose=False):
        """
        Initialize the TensorRTClassifier class.

        Args:
            model_path (str): Path to the PyTorch model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            verbose (bool): Whether to output the timer.
        """
        assert device == "cuda", "TensorRT only supports CUDA."
        self.trt, self.cuda = self._import_dependencies()
        super().__init__(model_path, device, size, class_names, fp16, verbose)
        self.engine = self.model
        self.context = self.engine.create_execution_context()  # create a context
        self.size, self.fixed_batch = self.get_input_size()
        assert self.size == (size, size), "The input size of the model is not the same as the size in the config file."
        self.bindings, self.inputs, self.outputs, self.stream = self.prepare_buffers()

    def _import_dependencies(self):
        import tensorrt as trt
        import pycuda.driver as cuda
        import pycuda.autoinit  # Ensures initialization of CUDA

        return trt, cuda
    
    def load_model(self):
        """Load TensorRT model."""
        logger = self.trt.Logger(self.trt.Logger.INFO)
        with open(self.model_path, "rb") as f, self.trt.Runtime(logger) as runtime:
            return runtime.deserialize_cuda_engine(f.read())
    
    def get_input_size(self):
        """Determines the input size expected by the model."""
        for binding_index in range(self.engine.num_bindings):
            if self.engine.binding_is_input(binding_index):
                shape = self.engine.get_binding_shape(binding_index)
                return (shape[2], shape[3]), shape[0]
    
    def prepare_buffers(self):
        """Prepare input and output buffers for TensorRT inference."""
        bindings = [] 
        stream = self.cuda.Stream() 
        inputs, outputs = [], [] 

        for binding_index in range(self.engine.num_bindings): 
            binding_shape = self.engine.get_binding_shape(binding_index) #(B. C, H, W)
            if self.fp16 and self.engine.get_binding_dtype(binding_index) == self.trt.DataType.FLOAT: 
                binding_dtype = np.float16 
            else:
                binding_dtype = self.trt.nptype(self.engine.get_binding_dtype(binding_index)) 
            binding_size = self.trt.volume(binding_shape) * np.dtype(binding_dtype).itemsize 
            device_mem = self.cuda.mem_alloc(binding_size) 
            bindings.append(int(device_mem)) 
            
            if self.engine.binding_is_input(binding_index): 
                host_mem = np.zeros(binding_shape, dtype=binding_dtype)
                inputs.append({'host': host_mem, 'device': device_mem})
            else:
                host_mem = np.zeros(binding_shape, dtype=binding_dtype)
                outputs.append({'host': host_mem, 'device': device_mem})

        return bindings, inputs, outputs, stream
    
    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the TensorRT model."""
        try:
            batch_size = imgs.shape[0]
            if batch_size > self.fixed_batch:
                raise ValueError(f"Input batch size {batch_size} exceeds the fixed batch size {self.fixed_batch}.")
            if batch_size < self.fixed_batch:
                padding = np.zeros((self.fixed_batch - batch_size, *imgs.shape[1:]), dtype=imgs.dtype)
                imgs = np.concatenate([imgs, padding], axis=0) 

            # Transfer input data to the GPU
            self.cuda.memcpy_htod_async(self.inputs[0]['device'], imgs, self.stream)

            # Run inference
            self.context.execute_async_v2(bindings=self.bindings, stream_handle=self.stream.handle)

            # Transfer predictions back from the GPU
            for output in self.outputs:
                self.cuda.memcpy_dtoh_async(output['host'], output['device'], self.stream)

            self.stream.synchronize()
            results = self.outputs[0]['host'][0:batch_size]
            results = F.softmax(torch.tensor(results), dim=1) # Convert result to tensor and apply softmax
            results = results.cpu().numpy()  # Move to CPU and convert to NumPy
        except self.cuda.LogicError as e:
            print(f"CUDA logic error: {str(e)}")
        except self.cuda.MemoryError as e:
            print(f"CUDA memory error: {str(e)}")
        except Exception as e:
            print(f"General error during CUDA operations: {str(e)}")

        return results
    
    def needs_tensor(self):
        return False
    
class Torch2trtClassifier(BaseClassifier):
    """
    Torch2trtClassifier.

    A class for loading and running classification models in trt format.
    """
    def __init__(self, model_path, device, size, class_names=None, fp16=False, verbose=False):
        """
        Initialize the Torch2trtClassifier class.

        Args:
            model_path (str): Path to the trt model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            verbose (bool): Whether to output the timer.
        """
        super().__init__(model_path, device, size, class_names, fp16, verbose)
        
    def load_model(self):
        """Load Torch2trt model."""
        from torch2trt import TRTModule
        model_trt = TRTModule()
        model_trt.load_state_dict(torch.load(self.model_path))
        model_trt.eval()
        return model_trt
    
    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the Torch2trt model."""
        with torch.no_grad():
            results = self.model(imgs)
            results = F.softmax(results, dim=1)  # probabilities
            results = results.cpu().numpy()
        return results

class JITClassifier(BaseClassifier):
    """
    JITClassifier.

    A class for loading and running classification models in jit format.
    """
    def __init__(self, model_path, device, size, class_names=None, fp16=False, verbose=False):
        """
        Initialize the JITClassifier class.

        Args:
            model_path (str): Path to the jit model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            verbose (bool): Whether to output the timer.
        """
        super().__init__(model_path, device, size, class_names, fp16, verbose)

    def load_model(self):
        """Load Torch2trt model."""
        model = torch.jit.load(self.model_path, map_location = self.device)
        model = model.half().eval() if self.fp16 else model.float().eval()
        return model

    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the jit model."""
        with torch.no_grad():
            results = self.model(imgs)
            results = F.softmax(results, dim=1)  # probabilities
            results = results.cpu().numpy()
        return results

# =============================================================================
# ClassifierBuilder
# =============================================================================   

@dataclass(frozen=True)
class ClassifierOptions:
    weights: str = './weights/yolov5s-cls.pt'
    size: Union[int, tuple] = 640
    class_names: dict = None
    fp16: bool = False
    verbose: bool = False

def Classifier(config: Union[str, ClassifierOptions]):
    """
    Initialize the Classifier function.

    Args:
        config (Union[str, ClassifierOptions]): A YAML configuration file path or a ClassifierOptions object.

    Raises:
        ValueError: If the config isn't a YAML file or ClassifierOptions object.
        ValueError: If the model weight file format is unsupported.

    Example:
        1. YAML file
            >>> model = Classifier("config.yaml")
            >>> results = model(images)
            >>> print(results)
        2. object
            >>> options = ClassifierOptions(conf_threshold=0.6, verbose=True....)
            >>> model = Classifier(options)
            >>> results = model(images)
            >>> print(results)
    """
    # Load config from a YAML file or a ClassifierOptions object
    if isinstance(config, str) and config.endswith(('yaml', 'yml')):
        with open(config, 'r') as f:
            setting = yaml.safe_load(f)

    elif isinstance(config, ClassifierOptions):
        setting = {k: v for k, v in config.__dict__.items() if not k.startswith("__")}

    else:
        raise ValueError("Config must be a YAML file or an object.")

    weight_path = setting['weights']
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load the appropriate classifier model based on file type
    if weight_path.endswith('.onnx'):
        # print(f"Loading ONNX model: {weight_path}")
        model = ONNXClassifier(
            model_path=weight_path,
            device=device.type,  # 'cuda' or 'cpu'
            size=setting.get('size', 640),
            class_names=setting.get('class_names', None),
            fp16=setting.get('fp16', False),
            verbose=setting.get('verbose',False)
        )
    elif weight_path.endswith(('.pt', '.pth')):
        if '_trt' in weight_path:
            # print(f"Loading TensorRT model: {weight_path}")
            model = Torch2trtClassifier(
                model_path=weight_path,
                device=device.type,  # 'cuda' or 'cpu'
                size=setting.get('size', 640),
                class_names=setting.get('class_names', None),
                fp16=setting.get('fp16', False),
                verbose=setting.get('verbose',False)
            )
        else:
            # print(f"Loading Pytorch model: {weight_path}")
            model = TorchClassifier(
                model_path=weight_path,
                device=device.type,  # 'cuda' or 'cpu'
                size=setting.get('size', 640),
                class_names=setting.get('class_names', None),
                fp16=setting.get('fp16', False),
                verbose=setting.get('verbose',False)
            )
    elif weight_path.endswith('.jit'):
        # print(f"Loading JIT model: {weight_path}")
        model = JITClassifier(
            model_path=weight_path,
            device=device.type,  # 'cuda' or 'cpu'
            size=setting.get('size', 640),
            class_names=setting.get('class_names', None),
            fp16=setting.get('fp16', False),
            verbose=setting.get('verbose',False)
        )
    elif weight_path.endswith('.engine'):
        # print(f"Loading TensorRT model: {weight_path}")
        model = TensorRTClassifier(
            model_path=weight_path,
            device=device.type,  # 'cuda' or 'cpu'
            size=setting.get('size', 640),
            class_names=setting.get('class_names', None),
            fp16=setting.get('fp16', False),
            verbose=setting.get('verbose',False)
        )
    else:
        raise ValueError(f"Unsupported model format: {weight_path}")

    return model
