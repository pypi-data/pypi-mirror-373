import os
import sys
import cv2
import time
import yaml
import torch
import warnings
import torchvision
import numpy as np
from threading import Lock
from nxva.utilities import timer
from typing import Union, List, Optional
from dataclasses import dataclass


def DIoU(bboxes1, bboxes2):
    """
    Parameters
    ----------
    bboxes1 : numpy.ndarray (n, 4)
    bboxes2 : numpy.ndarray (m, 4)

    Returns
    -------
    dious : numpy.ndarray (n, m)
    """
    if bboxes1.ndim == 1:
        bboxes1 = np.expand_dims(bboxes1, 0)
    if bboxes2.ndim == 1:
        bboxes2 = np.expand_dims(bboxes2, 0)
    rows = bboxes1.shape[0]
    cols = bboxes2.shape[0]
    dious = np.zeros((rows, cols))
    if rows * cols == 0:
        return dious
    
    # xmin,ymin,xmax,ymax->[:,0],[:,1],[:,2],[:,3]
    w1 = bboxes1[:, 2:2+1] - bboxes1[:, 0:0+1]  # r
    h1 = bboxes1[:, 3:3+1] - bboxes1[:, 1:1+1]  # r
    w2 = bboxes2[:, 2:2+1] - bboxes2[:, 0:0+1]  # c
    h2 = bboxes2[:, 3:3+1] - bboxes2[:, 1:1+1]  # c
    
    area1 = w1 * h1  # r
    area2 = w2 * h2  # c

    center_x1 = (bboxes1[:, 2:2+1] + bboxes1[:, 0:0+1]) / 2  # r
    center_y1 = (bboxes1[:, 3:3+1] + bboxes1[:, 1:1+1]) / 2  # r
    center_x2 = (bboxes2[:, 2:2+1] + bboxes2[:, 0:0+1]) / 2  # c
    center_y2 = (bboxes2[:, 3:3+1] + bboxes2[:, 1:1+1]) / 2  # c
    # (r, c)
    center_dx = center_x1 - center_x2.T
    center_dy = center_y1 - center_y2.T
    
    # (r, c)
    inter_min_x = np.maximum(bboxes1[:, 0:0+1], bboxes2[:, 0:0+1].T)  
    inter_min_y = np.maximum(bboxes1[:, 1:1+1], bboxes2[:, 1:1+1].T) 
    inter_max_x = np.minimum(bboxes1[:, 2:2+1], bboxes2[:, 2:2+1].T)
    inter_max_y = np.minimum(bboxes1[:, 3:3+1], bboxes2[:, 3:3+1].T)
    outer_min_x = np.minimum(bboxes1[:, 0:0+1], bboxes2[:, 0:0+1].T)
    outer_min_y = np.minimum(bboxes1[:, 1:1+1], bboxes2[:, 1:1+1].T)
    outer_max_x = np.maximum(bboxes1[:, 2:2+1], bboxes2[:, 2:2+1].T)
    outer_max_y = np.maximum(bboxes1[:, 3:3+1], bboxes2[:, 3:3+1].T)
    
    # (r, c)
    inter_x = np.clip((inter_max_x - inter_min_x), a_min=0, a_max=None)
    inter_y = np.clip((inter_max_y - inter_min_y), a_min=0, a_max=None)
    inter_area = inter_x * inter_y
    outer_x = np.clip((outer_max_x - outer_min_x), a_min=0, a_max=None)
    outer_y = np.clip((outer_max_y - outer_min_y), a_min=0, a_max=None)
    inter_diag = center_dx ** 2 + center_dy ** 2
    outer_diag = outer_x ** 2 + outer_y ** 2
    union_area = area1 + area2.T - inter_area
    dious = inter_area / union_area - inter_diag / outer_diag
    dious = np.clip(dious, a_min=-1.0, a_max=1.0)
    
    return dious


# =============================================================================
# Non-maximum-suppression
# =============================================================================
def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def box_area(box):
    # box = xyxy(4,n)
    return (box[2] - box[0]) * (box[3] - box[1])


def box_iou(box1, box2, eps=1e-7):
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    (a1, a2), (b1, b2) = box1[:, None].chunk(2, 2), box2.chunk(2, 1)
    inter = (torch.min(a2, b2) - torch.max(a1, b1)).clamp(0).prod(2)

    # IoU = inter / (area1 + area2 - inter)
    return inter / (box_area(box1.T)[:, None] + box_area(box2.T) - inter + eps)


# =============================================================================
# Yolo detection tools
# =============================================================================
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


def clip_coords(boxes, img_shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    boxes[:, 0].clamp_(0, img_shape[1] - 1)  # x1
    boxes[:, 1].clamp_(0, img_shape[0] - 1)  # y1
    boxes[:, 2].clamp_(0, img_shape[1] - 1)  # x2
    boxes[:, 3].clamp_(0, img_shape[0] - 1)  # y2
    
    
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

class BaseDetector:
    """
    BaseDetector.

    A base class for creating detector.

    Attributes:
        model_path (str): Path to the PyTorch model file.
        device (str): "cuda" or "cpu".
        size (int): The size of the input image.
        conf_thres (float): Confidence threshold.
        iou_thres (float): IoU threshold.
        classes (list): List of class names.
        class_names (dict): Dictionary mapping class indices to class names.
        fp16 (bool): Whether to use FP16 precision.
        agnostic (bool): Merges overlapping boxes of different classes.
        verbose (bool): Whether to output the timer.
    """
    def __init__(self, model_path, device, size, conf_thres=0.25, iou_thres=0.7, classes=None, class_names=None, fp16=False, agnostic=False, verbose=False):
        """
        Initialize the BaseDetector class.

        Args:
            model_path (str): Path to the PyTorch model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            conf_thres (float): Confidence threshold.
            iou_thres (float): IoU threshold.
            classes (list): List of class names.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            agnostic (bool): Merges overlapping boxes of different classes.
            verbose (bool): Whether to output the timer.
        """
        self.model_path = model_path
        self.device = device
        self.size = size
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.classes = classes
        self.class_names = class_names
        self.fp16 = fp16
        self.agnostic = agnostic
        self.verbose = verbose
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
    def preprocess(self, imgs, to_tensor=False):
        """
        Prepares input image before inference.
        Args:
            imgs (list or np.ndarray): Input images.
            roi_list (list): A list of regions of ROI.
            to_tensor (bool): Converts the processed images into tensor format.
        """
        if not len(imgs):
            return [], [], [], []
        
        if isinstance(imgs, np.ndarray):
            imgs = [imgs]
        
        pre_imgs = []
        for img in imgs:
            pre_img = letterbox(img, self.size, auto=False)[0]
            pre_img = pre_img.transpose((2, 0, 1))[::-1]  # HWC -> CHW, BGR -> RGB
            pre_img = np.ascontiguousarray(pre_img)
            if to_tensor:
                pre_img = torch.from_numpy(pre_img).float().to(self.device)
                pre_img /= 255
                if self.fp16:
                    pre_img = pre_img.half()

            else:
                pre_img = pre_img.astype(np.float32) / 255.0
                if self.fp16:
                    pre_img = pre_img.astype(np.float16)

            pre_imgs.append(pre_img)

        if to_tensor:
            pre_imgs = torch.stack(pre_imgs)
        else:
            pre_imgs = np.stack(pre_imgs)

        return pre_imgs, imgs

    @timer()
    def post_process(self, pred, pre_imgs, imgs):
        """Post-processes predictions for an image and returns them."""
        dets = []
        for i, det in enumerate(pred):
            if len(det):
                det[:, :4] = scale_coords(pre_imgs.shape[2:], det[:, :4], imgs[i].shape).round()
                det = det.cpu().numpy()
                det = det[np.argsort(det[:, 0])]  # sort by horizontal axis
            else:
                det = det.cpu().numpy()

            dets.append(det)

        return dets
    
    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the specified model."""
        raise NotImplementedError("Subclasses should overwrite this method to run the detection!")
    
    def __call__(self, imgs):
        """Performs inference on the given image source."""
        pre_imgs, imgs = self.preprocess(imgs, to_tensor=self.needs_tensor())
        pred = self.infer(pre_imgs)
        if not self.needs_tensor():
            pred = torch.from_numpy(pred)

        pred = self.non_max_suppression(
            pred,
            conf_thres=self.conf_thres,
            iou_thres=self.iou_thres,
            classes=self.classes,
            agnostic=self.agnostic,
            max_det=300
        )

        dets = self.post_process(pred, pre_imgs, imgs)
        return dets
        
    def needs_tensor(self):
        return True
    
    def destroy(self):
        pass

    @timer()
    def non_max_suppression(
        self,
        prediction,
        conf_thres=0.25,
        iou_thres=0.7,
        classes=None,
        agnostic=False,
        multi_label=False,
        labels=(),
        max_det=300,
        nm=0,  # number of masks
    ):
        """Non-Maximum Suppression (NMS) on inference results to reject overlapping detections

        Returns:
            list of detections, on (n,6) tensor per image [xyxy, conf, cls]
        """

        if isinstance(prediction, (list, tuple)):  # YOLOv5 model in validation model, output = (inference_out, loss_out)
            prediction = prediction[0]  # select only inference output

        device = prediction.device
        mps = 'mps' in device.type  # Apple MPS
        if mps:  # MPS not fully supported yet, convert tensors to CPU before NMS
            prediction = prediction.cpu()
        bs = prediction.shape[0]  # batch size
        nc = prediction.shape[2] - nm - 5  # number of classes
        xc = prediction[..., 4] > conf_thres  # candidates

        # Checks
        assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
        assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'

        # Settings
        # min_wh = 2  # (pixels) minimum box width and height
        max_wh = 7680  # (pixels) maximum box width and height
        max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
        time_limit = 0.5 + 0.05 * bs  # seconds to quit after
        redundant = True  # require redundant detections
        multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
        merge = False  # use merge-NMS

        t = time.time()
        mi = 5 + nc  # mask start index
        output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
        for xi, x in enumerate(prediction):  # image index, image inference
            # Apply constraints
            # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
            x = x[xc[xi]]  # confidence

            # Cat apriori labels if autolabelling
            if labels and len(labels[xi]):
                lb = labels[xi]
                v = torch.zeros((len(lb), nc + nm + 5), device=x.device)
                v[:, :4] = lb[:, 1:5]  # box
                v[:, 4] = 1.0  # conf
                v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
                x = torch.cat((x, v), 0)

            # If none remain process next image
            if not x.shape[0]:
                continue

            # Compute conf
            x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

            # Box/Mask
            box = xywh2xyxy(x[:, :4])  # center_x, center_y, width, height) to (x1, y1, x2, y2)
            mask = x[:, mi:]  # zero columns if no masks

            # Detections matrix nx6 (xyxy, conf, cls)
            if multi_label:
                i, j = (x[:, 5:mi] > conf_thres).nonzero(as_tuple=False).T
                x = torch.cat((box[i], x[i, 5 + j, None], j[:, None].float(), mask[i]), 1)
            else:  # best class only
                conf, j = x[:, 5:mi].max(1, keepdim=True)
                x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_thres]

            # Filter by class
            if classes is not None:
                x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

            # Apply finite constraint
            # if not torch.isfinite(x).all():
            #     x = x[torch.isfinite(x).all(1)]

            # Check shape
            n = x.shape[0]  # number of boxes
            if not n:  # no boxes
                continue
            elif n > max_nms:  # excess boxes
                x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence
            else:
                x = x[x[:, 4].argsort(descending=True)]  # sort by confidence

            # Batched NMS
            c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
            boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
            i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
            if i.shape[0] > max_det:  # limit detections
                i = i[:max_det]
            if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
                # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
                iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
                weights = iou * scores[None]  # box weights
                x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
                if redundant:
                    i = i[iou.sum(1) > 1]  # require redundancy

            output[xi] = x[i]
            if mps:
                output[xi] = output[xi].to(device)
            if (time.time() - t) > time_limit:
                # LOGGER.warning(f'WARNING ⚠️ NMS time limit {time_limit:.3f}s exceeded')
                break  # time limit exceeded

        return output

class TorchDetector(BaseDetector):
    """
    TorchDetector.

    A class for loading and running detection models in PyTorch format.

    Attributes:
        nc (int): The number of classes in the model.
    """
    def __init__(self, model_path, device, size, conf_thres=0.25, iou_thres=0.7, classes=None, class_names=None, fp16=False, agnostic=False, verbose=False):
        """
        Initialize the TorchDetector class.

        Args:
            model_path (str): Path to the PyTorch model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            conf_thres (float): Confidence threshold.
            iou_thres (float): IoU threshold.
            classes (list): List of class names.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            agnostic (bool): Merges overlapping boxes of different classes.
            verbose (bool): Whether to output the timer.
        """
        super().__init__(model_path, device, size, conf_thres, iou_thres, classes, class_names, fp16, agnostic, verbose)
        self.nc = self.model.nc
        
    def load_model(self):
        """Load PyTorch model"""
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
            pred = self.model(imgs)[0]
        return pred
    

class ONNXDetector(BaseDetector):
    """
    ONNXDetector.

    A class for loading and running detection models in ONNX format.

    Attributes:
        size (int): The size of the model.
        nc (int): The number of classes in the model.
    """
    def __init__(self, model_path, device, size, conf_thres=0.25, iou_thres=0.7, classes=None, class_names=None, fp16=False, agnostic=False, verbose=False):
        """
        Initialize the ONNXDetector class.

        Args:
            model_path (str): Path to the ONNX model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            conf_thres (float): Confidence threshold.
            iou_thres (float): IoU threshold.
            classes (list): List of class names.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            agnostic (bool): Merges overlapping boxes of different classes.
            verbose (bool): Whether to output the timer.
        """
        super().__init__(model_path, device, size, conf_thres, iou_thres, classes, class_names, fp16, agnostic, verbose)
        self.size = self.determine_input_size()
        assert self.size == (size, size), "The input size of the model is not the same as the size in the config file."
        self.nc = self._get_num_classes()
        
    def load_model(self):
        """Load ONNX model"""
        import onnxruntime as ort
        
        if self.device == "cuda":
            print("Using CUDA")
            providers = [("CUDAExecutionProvider", {"device_id": 0})]  
        else:
            print("Using CPU")
            providers = ["CPUExecutionProvider"]
            
        return ort.InferenceSession(self.model_path, providers=providers)
    
    def determine_input_size(self):
        """Determines the input size expected by the model."""
        input_shape = self.model.get_inputs()[0].shape
        return (input_shape[2], input_shape[3])
    
    def _get_num_classes(self):
        """Determines the number of classes by the model."""
        outputs = self.model.get_outputs()
        for output in outputs:
            return output.shape[2] - 5
    
    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the ONNX model."""
        pred = self.model.run(None, {self.model.get_inputs()[0].name: imgs})[0]
        return pred
    
    def needs_tensor(self):
        return False

class TensorRTDetector_Threading(BaseDetector):
    """
    This class is used for TensorRT inference in sub-threading. It uses a dedicated CUDA context for each thread.
    context = engine.create_execution_context() default creates a context in main threading.
    We need to actively create a context manager in each sub-thread by using cuda.Device(0).make_context().
    Seems like to register a context in each thread, we need to use a lock to avoid conflicts.
    """
    def __init__(self, model_path, device, size, conf_thres=0.25, iou_thres=0.7, classes=None, class_names=None, fp16=False, agnostic=False, verbose=False):
        assert device == "cuda", "TensorRT only supports CUDA."
        self.trt, self.cuda = self._import_dependencies()
        super().__init__(model_path, device, size, conf_thres, iou_thres, classes, class_names, fp16, agnostic, verbose)

        # create a dedicated cuda context
        self.cfx = self.cuda.Device(0).make_context()
        
        self.engine = self.model
        self.context = self.engine.create_execution_context()
        self.size, self.fixed_batch = self.get_input_size()
        assert self.size == (size, size), "The input size of the model is not the same as the size in the config file."
        self.bindings, self.inputs, self.outputs, self.stream = self.prepare_buffers()
        self.lock = Lock()
        self.nc = self._get_num_classes()
        
    def _import_dependencies(self):
        import tensorrt as trt
        import pycuda.driver as cuda
        import pycuda.autoinit  # Ensures initialization of CUDA
        return trt, cuda
    
    def get_input_size(self):
        """Determines the input size expected by the model."""
        for binding_index in range(self.engine.num_bindings):
            if self.engine.binding_is_input(binding_index):
                shape = self.engine.get_binding_shape(binding_index)
                return (shape[2], shape[3]), shape[0]
    
    def load_model(self):
        logger = self.trt.Logger(self.trt.Logger.INFO)
        with open(self.model_path, "rb") as f, self.trt.Runtime(logger) as runtime:
            return runtime.deserialize_cuda_engine(f.read())
        
    def prepare_buffers(self):
        """Prepare input and output buffers for TensorRT inference."""
        bindings = [] 
        stream = self.cuda.Stream() 
        inputs, outputs = [], [] 

        for binding_index in range(self.engine.num_bindings): 
            binding_shape = self.engine.get_binding_shape(binding_index) 
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
    
    def _get_num_classes(self):
        """Determines the number of classes by the model."""
        for binding_index in range(self.engine.num_bindings):
            if not self.engine.binding_is_input(binding_index):
                binding_shape = self.engine.get_binding_shape(binding_index)
                return binding_shape[2] - 5
    
    @timer()
    def infer(self, imgs):
        with self.lock:
            try:
                self.cfx.push()  # attach the context before running the engine
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
                pred = self.outputs[0]['host'][0:batch_size]
            except self.cuda.LogicError as e:
                print(f"CUDA logic error: {str(e)}")
            except self.cuda.MemoryError as e:
                print(f"CUDA memory error: {str(e)}")
            except Exception as e:
                print(f"General error during CUDA operations: {str(e)}")
            finally:  # detach the context after running the engine
                self.cfx.pop()
                
        return pred
    
    def destroy(self):
        self.cfx.pop() # detach the context before destroying the engine
    
    def needs_tensor(self):
        return False

class TensorRTDetector(BaseDetector):
    """
    TensorRTDetector.

    A class for loading and running detection models in TensorRT format.

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
        nc (int): The number of classes in the model
    """
    def __init__(self, model_path, device, size, conf_thres=0.25, iou_thres=0.7, classes=None, class_names=None, fp16=False, agnostic=False, verbose=False):
        """
        Args:
            model_path (str): Path to the TensorRT model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            conf_thres (float): Confidence threshold.
            iou_thres (float): IoU threshold.
            classes (list): List of class names.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            agnostic (bool): Merges overlapping boxes of different classes.
            verbose (bool): Whether to output the timer.
        """
        assert device == "cuda", "TensorRT only supports CUDA."
        self.trt, self.cuda = self._import_dependencies()
        super().__init__(model_path, device, size, conf_thres, iou_thres, classes, class_names, fp16, agnostic, verbose)
        self.engine = self.model
        self.context = self.engine.create_execution_context()  # create a context
        self.size, self.fixed_batch = self.get_input_size()
        assert self.size == (size, size), "The input size of the model is not the same as the size in the config file."
        self.bindings, self.inputs, self.outputs, self.stream = self.prepare_buffers()
        self.nc = self._get_num_classes()

    def _import_dependencies(self):
        import tensorrt as trt
        import pycuda.driver as cuda
        import pycuda.autoinit  # Ensures initialization of CUDA
        return trt, cuda
    
    def get_input_size(self):
        """Determines the input size expected by the model."""
        for binding_index in range(self.engine.num_bindings):
            if self.engine.binding_is_input(binding_index):
                shape = self.engine.get_binding_shape(binding_index)
                return (shape[2], shape[3]), shape[0]
    
    def load_model(self):
        """Load TensorRT model"""
        logger = self.trt.Logger(self.trt.Logger.INFO)
        with open(self.model_path, "rb") as f, self.trt.Runtime(logger) as runtime:
            return runtime.deserialize_cuda_engine(f.read())
        
    def prepare_buffers(self):
        """Prepare input and output buffers for TensorRT inference."""
        bindings = [] 
        stream = self.cuda.Stream() 
        inputs, outputs = [], [] 

        for binding_index in range(self.engine.num_bindings): 
            binding_shape = self.engine.get_binding_shape(binding_index) 
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
    
    def _get_num_classes(self):
        """Determines the number of classes by the model."""
        for binding_index in range(self.engine.num_bindings):
            if not self.engine.binding_is_input(binding_index):
                binding_shape = self.engine.get_binding_shape(binding_index)
                nc = binding_shape[2] - 5
                return nc
    
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
            pred = self.outputs[0]['host'][0:batch_size]
        except self.cuda.LogicError as e:
            print(f"CUDA logic error: {str(e)}")
        except self.cuda.MemoryError as e:
            print(f"CUDA memory error: {str(e)}")
        except Exception as e:
            print(f"General error during CUDA operations: {str(e)}")

        return pred
    
    def needs_tensor(self):
        return False

class Torch2trtDetector(BaseDetector):
    """
    Torch2trtDetector.

    A class for loading and running detection models in trt format.

    Attributes:
        nc (int): The number of classes in the model.
    """
    def __init__(self, model_path, device, size, conf_thres=0.25, iou_thres=0.7, classes=None, class_names=None, fp16=False, agnostic=False, verbose=False):
        """
        Initialize the Torch2trtDetector class.

        Args:
            model_path (str): Path to the Torch2trt model file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            conf_thres (float): Confidence threshold.
            iou_thres (float): IoU threshold.
            classes (list): List of class names.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            agnostic (bool): Merges overlapping boxes of different classes.
            verbose (bool): Whether to output the timer.
        """
        super().__init__(model_path, device, size, conf_thres, iou_thres, classes, class_names, fp16, agnostic, verbose)
        self.nc = self._get_num_classes()
        
    def load_model(self):
        """Load Torch2trt model"""
        from torch2trt import TRTModule
        model_trt = TRTModule()
        model_trt.load_state_dict(torch.load(self.model_path))
        model_trt.eval()
        return model_trt
    
    def _get_num_classes(self):
        """Determines the number of classes by the model."""
        engine = self.model.engine
        for binding_index in range(engine.num_bindings):
            if not engine.binding_is_input(binding_index):
                binding_shape = engine.get_binding_shape(binding_index)
                nc = binding_shape[2] - 5
                
        return nc
    
    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the Torch2trt model."""
        with torch.no_grad():
            pred = self.model(imgs)[0]
        return pred
    
class JITDetector(BaseDetector):
    """
    JITDetector.

    A class for loading and running detection models in jit format.

    Attributes:
        nc (int): The number of classes in the model.
    """
    def __init__(self, model_path, device, size, conf_thres=0.25, iou_thres=0.7, classes=None, class_names=None, fp16=False, agnostic=False, verbose=False):
        """
        Initialize the JITDetector class.

        Args:
            model_path (str): Path to the JIT file.
            device (str): "cuda" or "cpu".
            size (int): The size of the input image.
            conf_thres (float): Confidence threshold.
            iou_thres (float): IoU threshold.
            classes (list): List of class names.
            class_names (dict): Dictionary mapping class indices to class names.
            fp16 (bool): Whether to use FP16 precision.
            agnostic (bool): Merges overlapping boxes of different classes.
            verbose (bool): Whether to output the timer.
        """
        super().__init__(model_path, device, size, conf_thres, iou_thres, classes, class_names, fp16, agnostic, verbose)
        self.nc = self._get_num_classes()

    def load_model(self):
        """Load JIT model"""
        model = torch.jit.load(self.model_path, map_location = self.device)
        model = model.half().eval() if self.fp16 else model.float().eval()
        return model
    
    def _get_num_classes(self):
        """
        Determines the number of classes by the model.

        state_dict (OrderedDict):
            'model.0.conv.weight': torch.Size([32, 3, 6, 6])
            'model.0.conv.bias': torch.Size([32])
             .....
            'model.24.m.1.weight': torch.Size([255, 256, 1, 1])
            'model.24.m.1.bias': torch.Size([255])
            'model.24.m.2.weight': torch.Size([255, 512, 1, 1])
            'model.24.m.2.bias': torch.Size([255])
        """
        num_anchors = 3
        state_dict = self.model.state_dict()
        for name, param in state_dict.items():
            if 'm.0.weight' in name:
                output_channels  = param.shape[0]
                nc = (output_channels // num_anchors) - 5
                return nc
        
    @timer()
    def infer(self, imgs):
        """Runs inference on a given image using the JIT model."""
        with torch.no_grad():
            pred = self.model(imgs)[0]
            return pred
        
# =============================================================================
# DetectorBuilder
# =============================================================================

@dataclass(frozen=True)
class DetectorOptions:
    weights: str = './weights/yolov5s.pt'
    size: int = 640
    conf_threshold: float = 0.25
    iou_threshold: float = 0.7
    classes: Optional[List[int]] = None
    class_names: dict = None
    fp16: bool = False
    agnostic_nms: bool = False
    verbose: bool = False

def Detector(config: Union[str, DetectorOptions]):
    """
    Initialize the Detector function.

    Args:
        config (Union[str, DetectorOptions]): A YAML configuration file path or a DetectorOptions object.
    Raises:
        ValueError: If the config isn't a YAML file or 'DetectorOptions' object.
        ValueError: If the model weight file format is unsupported.

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
            setting = yaml.safe_load(f)

    elif isinstance(config, DetectorOptions):
        setting = {k: v for k, v in config.__dict__.items() if not k.startswith("__")}

    else:
        raise ValueError("Config must be a YAML file or an object.")

    weight_path = setting['weights']
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load the appropriate detector model based on file type
    if weight_path.endswith('.onnx'):
        # print(f"Loading ONNX model: {weight_path}")
        model = ONNXDetector(
            model_path=weight_path,
            device=device.type,  # 'cuda' or 'cpu'
            size=setting.get('size', 640),
            conf_thres=setting.get('conf_threshold', 0.25),
            iou_thres=setting.get('iou_threshold', 0.7),
            classes=setting.get('classes', None),
            class_names = setting.get('class_names', None),
            fp16=setting.get('fp16', False),
            agnostic = setting.get('agnostic_nms', False),
            verbose=setting.get('verbose', False)
        )
    elif weight_path.endswith(('.pt', '.pth')):
        if '_trt' in weight_path:
            # print(f"Loading TensorRT model: {weight_path}")
            model = Torch2trtDetector(
                model_path=weight_path,
                device=device.type,  # 'cuda' or 'cpu'
                size=setting.get('size', 640),
                conf_thres=setting.get('conf_threshold', 0.25),
                iou_thres=setting.get('iou_threshold', 0.7),
                classes=setting.get('classes', None),
                class_names = setting.get('class_names', None),
                fp16=setting.get('fp16', False),
                agnostic = setting.get('agnostic_nms', False),
                verbose=setting.get('verbose', False)
            )
        else:
            # print(f"Loading Pytorch model: {weight_path}")
            model = TorchDetector(
                model_path=weight_path,
                device=device,
                size=setting.get('size', 640),
                conf_thres=setting.get('conf_threshold', 0.25),
                iou_thres=setting.get('iou_threshold', 0.7),
                classes=setting.get('classes', None),
                class_names = setting.get('class_names', None),
                fp16=setting.get('fp16', False),
                agnostic = setting.get('agnostic_nms', False),
                verbose=setting.get('verbose', False)
            )
    elif weight_path.endswith('.engine'):
        # print(f"Loading TensorRT model: {weight_path}")
        model = TensorRTDetector(
            model_path=weight_path,
            device=device.type,  # 'cuda' or 'cpu'
            size=setting.get('size', 640),
            conf_thres=setting.get('conf_threshold', 0.25),
            iou_thres=setting.get('iou_threshold', 0.7),
            classes=setting.get('classes', None),
            class_names = setting.get('class_names', None),
            fp16=setting.get('fp16', False),
            agnostic = setting.get('agnostic_nms', False),
            verbose=setting.get('verbose', False)
        )
    elif weight_path.endswith('.jit'):
        # print(f"Loading JIT model: {weight_path}")
        model = JITDetector(
            model_path=weight_path,
            device=device.type,  # 'cuda' or 'cpu'
            size=setting.get('size', 640),
            conf_thres=setting.get('conf_threshold', 0.25),
            iou_thres=setting.get('iou_threshold', 0.7),
            classes=setting.get('classes', None),
            class_names = setting.get('class_names', None),
            fp16=setting.get('fp16', False),
            agnostic = setting.get('agnostic_nms', False),
            verbose=setting.get('verbose', False)
        )
    
    else:
        raise ValueError(f"Unsupported model format: {weight_path}")
    
    return model

# =============================================================================
# Load model
# =============================================================================
    
def load_model(weight, device):
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    sys.path.insert(0, os.path.join(current_dir, 'yolov5'))
    from models.experimental import attempt_load
    sys.path.remove(os.path.join(current_dir, 'yolov5'))

    model = attempt_load(weight, device=device)
    return model
