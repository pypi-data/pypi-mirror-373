import cv2, time, math, contextlib

import numpy as np
import torch, torchvision
import torch.nn.functional as F

#==========================================
# Detection and Pose
#==========================================


def empty_like(x):
    """
    Create empty torch.Tensor or np.ndarray with same shape as input and float32 dtype.
    
    Function:
        Create empty container with same shape as input for improved memory allocation efficiency.
    
    Input:
        x (torch.Tensor | np.ndarray): Input tensor or array
    
    Output:
        torch.Tensor | np.ndarray: Empty tensor or array with same shape as input, dtype float32
    
    Example:
        >>> tensor = torch.rand(2, 3, 4)
        >>> empty_tensor = empty_like(tensor)
        >>> print(empty_tensor.shape)  # torch.Size([2, 3, 4])
    """
    return (
        torch.empty_like(x, dtype=torch.float32) if isinstance(x, torch.Tensor) else np.empty_like(x, dtype=np.float32)
    )


def xywh2xyxy(x):
    """
    Convert bounding box coordinates from (x, y, width, height) format to (x1, y1, x2, y2) format.
    
    Function:
        Convert center point coordinates and width/height format to top-left and bottom-right format
        where (x1, y1) is the top-left corner and (x2, y2) is the bottom-right corner.
    
    Input:
        x (np.ndarray | torch.Tensor): Input bounding box coordinates in (x, y, width, height) format
                                      with shape (..., 4)
    
    Output:
        np.ndarray | torch.Tensor: Converted bounding box coordinates in (x1, y1, x2, y2) format
                                  with same shape as input
    
    Example:
        >>> boxes = torch.tensor([[100, 100, 50, 30]])  # center(100,100), width=50, height=30
        >>> xyxy_boxes = xywh2xyxy(boxes)
        >>> print(xyxy_boxes)  # [[75, 85, 125, 115]]
    """
    assert x.shape[-1] == 4, f"input shape last dimension expected 4 but input shape is {x.shape}"
    y = empty_like(x)  # faster than clone/copy
    xy = x[..., :2]  # centers
    wh = x[..., 2:] / 2  # half width-height
    y[..., :2] = xy - wh  # top left xy
    y[..., 2:] = xy + wh  # bottom right xy
    return y


def xywh2xyxy(x):
    """
    Convert bounding box coordinates from (x, y, width, height) format to (x1, y1, x2, y2) format.
    
    Function:
        Convert center point coordinates and width/height format to top-left and bottom-right format
        where (x1, y1) is the top-left corner and (x2, y2) is the bottom-right corner.
    
    Input:
        x (np.ndarray | torch.Tensor): Input bounding box coordinates in (x, y, width, height) format
                                      with shape (..., 4)
    
    Output:
        np.ndarray | torch.Tensor: Converted bounding box coordinates in (x1, y1, x2, y2) format
                                  with same shape as input
    
    Example:
        >>> boxes = torch.tensor([[100, 100, 50, 30]])  # center(100,100), width=50, height=30
        >>> xyxy_boxes = xywh2xyxy(boxes)
        >>> print(xyxy_boxes)  # [[75, 85, 125, 115]]
    """
    assert x.shape[-1] == 4, f"input shape last dimension expected 4 but input shape is {x.shape}"
    y = empty_like(x)  # faster than clone/copy
    xy = x[..., :2]  # centers
    wh = x[..., 2:] / 2  # half width-height
    y[..., :2] = xy - wh  # top left xy
    y[..., 2:] = xy + wh  # bottom right xy
    return y


def xyxy2xywh(x):
    """
    Convert bounding box coordinates from (x1, y1, x2, y2) format to (x, y, width, height) format where (x1, y1) is the
    top-left corner and (x2, y2) is the bottom-right corner.

    Args:
        x (np.ndarray | torch.Tensor): Input bounding box coordinates in (x1, y1, x2, y2) format.

    Returns:
        (np.ndarray | torch.Tensor): Bounding box coordinates in (x, y, width, height) format.
    """
    assert x.shape[-1] == 4, f"input shape last dimension expected 4 but input shape is {x.shape}"
    y = empty_like(x)  # faster than clone/copy
    y[..., 0] = (x[..., 0] + x[..., 2]) / 2  # x center
    y[..., 1] = (x[..., 1] + x[..., 3]) / 2  # y center
    y[..., 2] = x[..., 2] - x[..., 0]  # width
    y[..., 3] = x[..., 3] - x[..., 1]  # height
    return y
    

def xywhr2xyxyxyxy(x):
    """
    Convert batched Oriented Bounding Boxes (OBB) from [xywh, rotation] to [xy1, xy2, xy3, xy4] format.

    Args:
        x (np.ndarray | torch.Tensor): Boxes in [cx, cy, w, h, rotation] format with shape (N, 5) or (B, N, 5).
            Rotation values should be in radians from 0 to pi/2.

    Returns:
        (np.ndarray | torch.Tensor): Converted corner points with shape (N, 4, 2) or (B, N, 4, 2).
    """
    cos, sin, cat, stack = (
        (torch.cos, torch.sin, torch.cat, torch.stack)
        if isinstance(x, torch.Tensor)
        else (np.cos, np.sin, np.concatenate, np.stack)
    )

    ctr = x[..., :2]
    w, h, angle = (x[..., i : i + 1] for i in range(2, 5))
    cos_value, sin_value = cos(angle), sin(angle)
    vec1 = [w / 2 * cos_value, w / 2 * sin_value]
    vec2 = [-h / 2 * sin_value, h / 2 * cos_value]
    vec1 = cat(vec1, -1)
    vec2 = cat(vec2, -1)
    pt1 = ctr + vec1 + vec2
    pt2 = ctr + vec1 - vec2
    pt3 = ctr - vec1 - vec2
    pt4 = ctr - vec1 + vec2
    return stack([pt1, pt2, pt3, pt4], -2)


def clip_boxes(boxes, shape):
    """
    Clip bounding boxes to image boundaries to prevent exceeding image bounds.
    
    Function:
        Restrict bounding box coordinates within image bounds [0, width] and [0, height]
        to ensure boxes don't exceed image boundaries.
    
    Input:
        boxes (torch.Tensor | numpy.ndarray): Bounding boxes to clip in (x1, y1, x2, y2) format
                                              with shape (..., 4)
        shape (tuple): Image shape (height, width)
    
    Output:
        numpy.ndarray: Clipped bounding boxes with coordinates restricted to image bounds
                      with same shape as input
    
    Example:
        >>> boxes = torch.tensor([[-10, -5, 650, 480]])  # boxes exceeding boundaries
        >>> shape = (480, 640)  # image dimensions
        >>> clipped = clip_boxes(boxes, shape)
        >>> print(clipped)  # [[0, 0, 640, 480]]
    """
    boxes[..., [0, 2]] = boxes[..., [0, 2]].clip(0, shape[1])  # x1, x2
    boxes[..., [1, 3]] = boxes[..., [1, 3]].clip(0, shape[0])  # y1, y2

    return boxes


def scale_boxes(img1_shape, boxes, img0_shape, ratio_pad=None, padding=True, xywh=False):
    """
    Scale bounding boxes from one image size to another image size.
    
    Function:
        Scale bounding box coordinates from processed image size back to original image size.
        Supports YOLO-style padding and different bounding box formats.
    
    Input:
        img1_shape (tuple): Image shape corresponding to bounding boxes (height, width)
        boxes (torch.Tensor): Bounding box coordinates in (x1, y1, x2, y2) format
        img0_shape (tuple): Target image shape (height, width)
        ratio_pad (tuple, optional): Scale ratio and padding (ratio, pad), auto-calculated if not provided
        padding (bool): Whether to consider YOLO-style padding, default True
        xywh (bool): Whether bounding box format is xywh, default False
    
    Output:
        numpy.ndarray: Scaled bounding boxes in (x1, y1, x2, y2) format
    
    Example:
        >>> img1_shape = (640, 640)  # processed image size
        >>> boxes = torch.tensor([[100, 100, 200, 200]])
        >>> img0_shape = (480, 640)  # original image size
        >>> scaled_boxes = scale_boxes(img1_shape, boxes, img0_shape)
    """
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (
            round((img1_shape[1] - img0_shape[1] * gain) / 2 - 0.1),
            round((img1_shape[0] - img0_shape[0] * gain) / 2 - 0.1),
        )  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    if padding:
        boxes[..., 0] -= pad[0]  # x padding
        boxes[..., 1] -= pad[1]  # y padding
        if not xywh:
            boxes[..., 2] -= pad[0]  # x padding
            boxes[..., 3] -= pad[1]  # y padding
    boxes[..., :4] /= gain
    return clip_boxes(boxes, img0_shape)


def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None, normalize: bool = False, padding: bool = True):
    """
    Scale segmentation coordinates from one image size to another image size.
    
    Function:
        Scale segmentation coordinates from processed image size back to original image size.
        Supports coordinate normalization and YOLO-style padding handling.
    
    Input:
        img1_shape (tuple): Source image shape (height, width)
        coords (torch.Tensor): Coordinates to scale with shape (N, 2)
        img0_shape (tuple): Target image shape (height, width)
        ratio_pad (tuple, optional): Scale ratio and padding values ((ratio_h, ratio_w), (pad_h, pad_w))
        normalize (bool): Whether to normalize coordinates to range [0, 1], default False
        padding (bool): Whether coordinates are based on YOLO-style padded images, default True
    
    Output:
        torch.Tensor: Scaled coordinates
    
    Example:
        >>> img1_shape = (640, 640)  # processed image size
        >>> coords = torch.tensor([[100, 100], [200, 200]])
        >>> img0_shape = (480, 640)  # original image size
        >>> scaled_coords = scale_coords(img1_shape, coords, img0_shape)
    """
    if coords.shape[0] == 0:
        return torch.zeros((17, 3), device=coords.device)
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0]
        pad = ratio_pad[1]

    if padding:
        coords[..., 0] -= pad[0]  # x padding
        coords[..., 1] -= pad[1]  # y padding
    coords[..., 0] /= gain
    coords[..., 1] /= gain
    coords = clip_coords(coords, img0_shape)
    if normalize:
        coords[..., 0] /= img0_shape[1]  # width
        coords[..., 1] /= img0_shape[0]  # height
    return coords


def clip_coords(coords, shape):
    """
    Clip line coordinates to the image boundaries.
    
    Function:
        Restrict coordinates within image bounds [0, width] and [0, height]
        to prevent coordinates from exceeding image boundaries.
    
    Input:
        coords (torch.Tensor | numpy.ndarray): Line coordinates list with shape (..., 2)
        shape (tuple): Image dimensions (height, width)
    
    Output:
        torch.Tensor | numpy.ndarray: Clipped coordinates with same type as input
    
    Example:
        >>> coords = torch.tensor([[-10, -5], [650, 480]])  # coordinates exceeding boundaries
        >>> shape = (480, 640)  # image dimensions
        >>> clipped = clip_coords(coords, shape)
        >>> print(clipped)  # [[0, 0], [640, 480]]
    """
    if isinstance(coords, torch.Tensor):  # faster individually (WARNING: inplace .clamp_() Apple MPS bug)
        coords[..., 0] = coords[..., 0].clamp(0, shape[1])  # x
        coords[..., 1] = coords[..., 1].clamp(0, shape[0])  # y
    else:  # np.array (faster grouped)
        coords[..., 0] = coords[..., 0].clip(0, shape[1])  # x
        coords[..., 1] = coords[..., 1].clip(0, shape[0])  # y
    return coords


def scale_coordsV5(img1_shape, coords, img0_shape, ratio_pad=None):
    """
    YOLOv5 version coordinate scaling function.
    
    Function:
        Specialized coordinate scaling implementation for YOLOv5.
        Scale coordinates from processed image size back to original image size.
    
    Input:
        img1_shape (tuple): Source image shape (height, width)
        coords (torch.Tensor): Coordinates to scale with shape (N, 2)
        img0_shape (tuple): Target image shape (height, width)
        ratio_pad (tuple, optional): Scale ratio and padding values, auto-calculated if not provided
    
    Output:
        torch.Tensor: Scaled coordinates, rounded to nearest integer
    
    Example:
        >>> img1_shape = (640, 640)  # processed image size
        >>> coords = torch.tensor([[100, 100], [200, 200]])
        >>> img0_shape = (480, 640)  # original image size
        >>> scaled_coords = scale_coordsV5(img1_shape, coords, img0_shape)
    """
    def clip_coords(boxes, img_shape, step=2):
        # Clip bounding xyxy bounding boxes to image shape (height, width)
        boxes[:, 0::step].clamp_(0, img_shape[1])  # x1
        boxes[:, 1::step].clamp_(0, img_shape[0])  # y1
        
    step=1
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0]
        pad = ratio_pad[1]
    if isinstance(gain, (list, tuple)):
        gain = gain[0]
    coords[:, 0::step] -= pad[0]  # x padding
    coords[:, 1::step] -= pad[1]  # y padding
    coords[:, 0::step] /= gain
    coords[:, 1::step] /= gain
    clip_coords(coords, img0_shape, step=step)
    coords = coords.round()
    return coords


def box_area(box):
    """
    Calculate the area of bounding boxes.
    
    Function:
        Calculate area based on top-left and bottom-right coordinates of bounding boxes.
        Uses formula: area = width × height
    
    Input:
        box (torch.Tensor): Bounding box coordinates in (x1, y1, x2, y2) format
                           with shape (4,) or (4, n)
    
    Output:
        torch.Tensor: Bounding box area
    
    Example:
        >>> box = torch.tensor([10, 10, 50, 30])  # (x1, y1, x2, y2)
        >>> area = box_area(box)
        >>> print(area)  # 800 (width=40 × height=20)
    """
    # box = xyxy(4,n)
    return (box[2] - box[0]) * (box[3] - box[1])



def box_iou(box1, box2, eps=1e-7):
    """
    Calculate Intersection over Union (IoU) values between bounding boxes.
    
    Function:
        Calculate IoU (Intersection over Union) values between two sets of bounding boxes.
        Also known as Jaccard index, used to measure the overlap between two bounding boxes.
    
    Input:
        box1 (torch.Tensor): First set of bounding boxes with shape (N, 4) in (x1, y1, x2, y2) format
        box2 (torch.Tensor): Second set of bounding boxes with shape (M, 4) in (x1, y1, x2, y2) format
        eps (float): Small value to prevent division by zero, default 1e-7
    
    Output:
        torch.Tensor: IoU matrix with shape (N, M)
                     containing IoU values for each pair of bounding boxes from box1 and box2
    
    Example:
        >>> box1 = torch.tensor([[0, 0, 10, 10]])  # one bounding box
        >>> box2 = torch.tensor([[5, 5, 15, 15]])  # another bounding box
        >>> iou = box_iou(box1, box2)
        >>> print(iou)  # [[0.1429]] (intersection area 25 / union area 175)
    """
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    (a1, a2), (b1, b2) = box1[:, None].chunk(2, 2), box2.chunk(2, 1)
    inter = (torch.min(a2, b2) - torch.max(a1, b1)).clamp(0).prod(2)

    # IoU = inter / (area1 + area2 - inter)
    return inter / (box_area(box1.T)[:, None] + box_area(box2.T) - inter + eps)
    

def non_max_suppression(
    prediction,
    conf_threshold=0.25,
    iou_threshold=0.7,
    classes=None,
    agnostic=False,
    max_det=300,
    nc=0,
    version='yolo11',
    nms=None,
    task=None
):
    """
    Non-Maximum Suppression (NMS) processing on inference results to remove overlapping detections.
    
    Function:
        Apply Non-Maximum Suppression to YOLO model inference results.
        Remove low-confidence and high-overlap detection boxes, retaining the best detections.
        Supports multiple YOLO versions (yolov5, yolov8, yolo11, etc.).
    
    Input:
        prediction (torch.Tensor | numpy.ndarray): Model inference results
        conf_thres (float): Confidence threshold, default 0.25
        iou_thres (float): IoU threshold, default 0.7
        classes (list, optional): Specific class indices to keep
        agnostic (bool): Whether to perform class-agnostic NMS, default False
        max_det (int): Maximum number of detections per image, default 300
        nc (int): Number of classes, default 0 (auto-calculate)
        version (str): YOLO version, default 'yolov11'
    
    Output:
        list: List of detection results for each image
             Each element is a tensor with shape (n, 6) in format [x1, y1, x2, y2, conf, cls]
    
    Example:
        >>> prediction = model(images)
        >>> detections = non_max_suppression(prediction, conf_thres=0.5, iou_thres=0.45)
        >>> for det in detections:
        ...     print(det.shape)  # torch.Size([n, 6])
    """    
    if isinstance(prediction, (list, tuple)):  # YOLOv5 model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0]  # select only inference output
    if isinstance(prediction, np.ndarray):
        prediction = torch.from_numpy(prediction)
    # Settings
    max_wh = 7680  # (pixels) maximum box width and height
    max_nms = 3000  # maximum number of boxes into torchvision.ops.nms()
    num_bbox_conf = 5 if version == 'yolov5' else 4
    multiplier = 0 if agnostic else max_wh
    v5_task_not_pose = task != 'pose'

    bs, _, num_feat = prediction.shape
    nc = nc or (num_feat - num_bbox_conf)  # e.g. 36
    mi = num_bbox_conf + nc 
    classes_tensor = torch.tensor(classes, device=prediction.device) if classes is not None else None

    time_limit = 0.5 + 0.05 * bs  # seconds to quit after
    output = [torch.zeros((0, 6), device=prediction.device)] * bs

    t = time.time()
    for xi, x in enumerate(prediction):  # image index, image inference
        if version == 'yolov5':
            xc = x[..., 4] > conf_threshold
            if v5_task_not_pose:
                x[..., 5:] *= x[..., 4, None]
        elif version in ['yolov5u', 'yolov8', 'yolo11']:
            x = x.transpose(-1, -2)
            xc = x[..., 4:mi].amax(-1) > conf_threshold
        x = x[xc]  # confidence

        if not x.shape[0]:
            continue
        box  = xywh2xyxy(x[..., :4])
        cls  = x[:, num_bbox_conf:num_bbox_conf+nc]
        mask = x[:, num_bbox_conf+nc:]

        conf, j = cls.max(1, keepdim=True)
        x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_threshold]
        # Filter by class
        if classes is not None:
            x = x[(x[..., 5:6] == classes_tensor).any(1)]
        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue

        # Batched NMS
        # boxes, scores = x[..., :4] + c, x[..., 4]  # boxes (offset by class), scores
        # c = x[..., 5:6] * multiplier # c is the class offset if agnostic is True all boxes view as same class, else c is the class offset for each box depending on the class
        # i = nms(boxes + c, scores, iou_threshold=iou_threshold)[:max_det] # NMS 

        i = nms(x[..., :4] + x[..., 5:6] * multiplier, x[..., 4], iou_threshold=iou_threshold)[:max_det] # NMS 
        output[xi] = x[i]
        if (time.time() - t) > time_limit:
            break  # time limit exceeded
    return output


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114)):
    """
    Resize image to specified dimensions while maintaining aspect ratio and padding borders.
    
    Function:
        Resize input image to specified new dimensions while maintaining original aspect ratio.
        Fill empty areas with specified color, ensuring image is a multiple of 32 pixels.
    
    Input:
        img (numpy.ndarray): Input image with shape (height, width, channels)
        new_shape (tuple | int): Target dimensions, default (640, 640)
        color (tuple): Padding color (R, G, B), default (114, 114, 114)
    
    Output:
        numpy.ndarray: Resized image with dimensions new_shape
    
    Example:
        >>> img = cv2.imread('image.jpg')  # shape (480, 640, 3)
        >>> resized = letterbox(img, new_shape=(416, 416))
        >>> print(resized.shape)  # (416, 416, 3)
    """
    # Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    elif isinstance(new_shape, tuple):
        new_shape = new_shape
    else:
        raise TypeError(f"Unsupported type for new_shape: {type(new_shape)}")
    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    dw /= 2  # divide padding into 2 sides
    dh /= 2
    
    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img

#==========================================
# Classification
#==========================================
DEFAULT_MEAN = (0.0, 0.0, 0.0)
DEFAULT_STD = (1.0, 1.0, 1.0)
DEFAULT_CROP_FRACTION = 1.0
def classify_transforms(
    size=224,
    mean=DEFAULT_MEAN,
    std=DEFAULT_STD,
    interpolation="BILINEAR",
    crop_fraction: float = DEFAULT_CROP_FRACTION,
):
    """
    Create a composition of image transforms for classification tasks.
    
    Function:
        Generate image preprocessing transform sequence suitable for classification models.
        Includes resizing, center cropping, tensor conversion, and normalization.
    
    Input:
        size (int | tuple): Target image size
                          If integer, represents shortest edge length
                          If tuple, represents (height, width)
        mean (tuple): RGB channel mean values for normalization
        std (tuple): RGB channel standard deviation values for normalization
        interpolation (str): Interpolation method, options: 'NEAREST', 'BILINEAR', or 'BICUBIC'
        crop_fraction (float): Crop fraction, default DEFAULT_CROP_FRACTION
    
    Output:
        torchvision.transforms.Compose: Composition of image transforms
    
    Example:
        >>> transforms = classify_transforms(size=224)
        >>> img = Image.open("path/to/image.jpg")
        >>> transformed_img = transforms(img)
        >>> print(transformed_img.shape)  # torch.Size([3, 224, 224])
    """
    import torchvision.transforms as T  # scope for faster 'import ultralytics'

    if isinstance(size, (tuple, list)):
        assert len(size) == 2, f"'size' tuples must be length 2, not length {len(size)}"
        scale_size = tuple(math.floor(x / crop_fraction) for x in size)
    else:
        scale_size = math.floor(size / crop_fraction)
        scale_size = (scale_size, scale_size)

    # Aspect ratio is preserved, crops center within image, no borders are added, image is lost
    if scale_size[0] == scale_size[1]:
        # Simple case, use torchvision built-in Resize with the shortest edge mode (scalar size arg)
        tfl = [T.Resize(scale_size[0], interpolation=getattr(T.InterpolationMode, interpolation))]
    else:
        # Resize the shortest edge to matching target dim for non-square target
        tfl = [T.Resize(scale_size)]
    tfl.extend(
        [
            T.CenterCrop(size),
            T.ToTensor(),
            T.Normalize(mean=torch.tensor(mean), std=torch.tensor(std)),
        ]
    )
    return T.Compose(tfl)

#==========================================
# Mask
#==========================================
def process_mask(protos, masks_in, bboxes, shape, upsample=False, version='yolo11'):
    """
    Apply masks to bounding boxes using the output of the mask head.
    
    Function:
        Combine prototype masks and mask coefficients to generate final segmentation masks.
        Supports different YOLO model versions and optional upsampling.
    
    Input:
        protos (torch.Tensor): Prototype mask tensor with shape [mask_dim, mask_h, mask_w]
        masks_in (torch.Tensor): Mask coefficients tensor with shape [n, mask_dim]
                                where n is the number of masks after NMS
        bboxes (torch.Tensor): Bounding box tensor with shape [n, 4]
        shape (tuple): Input image dimensions (h, w)
        upsample (bool): Whether to upsample masks to original image size, default False
        version (str): YOLO version, default 'yolo11'
    
    Output:
        torch.Tensor: Binary mask tensor with shape [n, h, w]
                     where n is the number of masks after NMS
    
    Example:
        >>> protos = torch.rand(32, 160, 160)  # prototype masks
        >>> masks_in = torch.rand(5, 32)  # mask coefficients for 5 objects
        >>> bboxes = torch.rand(5, 4)  # 5 bounding boxes
        >>> shape = (640, 640)  # image dimensions
        >>> masks = process_mask(protos, masks_in, bboxes, shape)
        >>> print(masks.shape)  # torch.Size([5, 640, 640])
    """
    c, mh, mw = protos.shape  # CHW
    ih, iw = shape
    if masks_in.shape[0] == 0:
        return torch.zeros((0, mh, mw), device=protos.device)
    masks = (masks_in @ protos.float().view(c, -1)).view(-1, mh, mw)  # CHW
    width_ratio = mw / iw
    height_ratio = mh / ih

    downsampled_bboxes = bboxes.clone()
    downsampled_bboxes[:, 0] *= width_ratio
    downsampled_bboxes[:, 2] *= width_ratio
    downsampled_bboxes[:, 3] *= height_ratio
    downsampled_bboxes[:, 1] *= height_ratio

    masks = crop_mask(masks, downsampled_bboxes)  # CHW
    if upsample:
        masks = F.interpolate(masks[None], shape, mode="bilinear", align_corners=False)[0]  # CHW
    if version in ['yolov8', 'yolo11']:
        threshold = 0.0
    elif version == 'yolov5':
        threshold = 0.5
    else:
        raise ValueError(f"Invalid version: {version}")
    return masks.gt_(threshold)


def crop_mask(masks, boxes):
    """
    Crop predicted masks to bounding box regions.
    
    Function:
        Set mask pixels outside bounding boxes to zero, retaining masks within bounding boxes.
        Uses vectorized operations for improved efficiency.
    
    Input:
        masks (torch.Tensor): Mask tensor with shape [n, h, w]
        boxes (torch.Tensor): Bounding box coordinate tensor with shape [n, 4]
                             in relative coordinate format (x1, y1, x2, y2)
    
    Output:
        torch.Tensor: Cropped masks with shape [n, h, w]
    
    Example:
        >>> masks = torch.rand(2, 100, 100)  # 2 masks
        >>> boxes = torch.tensor([[10, 10, 50, 50], [20, 20, 80, 80]])  # 2 bounding boxes
        >>> cropped = crop_mask(masks, boxes)
        >>> print(cropped.shape)  # torch.Size([2, 100, 100])
    """
    _, h, w = masks.shape
    x1, y1, x2, y2 = torch.chunk(boxes[:, :, None], 4, 1)  # x1 shape(1,1,n)
    r = torch.arange(w, device=masks.device, dtype=x1.dtype)[None, None, :]  # rows shape(1,w,1)
    c = torch.arange(h, device=masks.device, dtype=x1.dtype)[None, :, None]  # cols shape(h,1,1)

    return masks * ((r >= x1) * (r < x2) * (c >= y1) * (c < y2))


def scale_masks(masks, shape, padding: bool = True):
    """
    Rescale segmentation masks to target shape.
    
    Function:
        Scale masks from one size to another size.
        Supports YOLO-style padding handling.
    
    Input:
        masks (torch.Tensor): Mask tensor with shape (N, C, H, W)
        shape (tuple): Target height and width (height, width)
        padding (bool): Whether masks are based on YOLO-style padded images, default True
    
    Output:
        torch.Tensor: Rescaled masks
    
    Example:
        >>> masks = torch.rand(1, 1, 160, 160)  # 1 mask
        >>> shape = (640, 640)  # target size
        >>> scaled = scale_masks(masks, shape)
        >>> print(scaled.shape)  # torch.Size([1, 1, 640, 640])
    """
    mh, mw = masks.shape[2:]
    gain = min(mh / shape[0], mw / shape[1])  # gain  = old / new
    pad = [mw - shape[1] * gain, mh - shape[0] * gain]  # wh padding
    if padding:
        pad[0] /= 2
        pad[1] /= 2
    top, left = (int(round(pad[1] - 0.1)), int(round(pad[0] - 0.1))) if padding else (0, 0)  # y, x
    bottom, right = (
        mh - int(round(pad[1] + 0.1)),
        mw - int(round(pad[0] + 0.1)),
    )
    masks = masks[..., top:bottom, left:right]

    masks = F.interpolate(masks, shape, mode="bilinear", align_corners=False)  # NCHW
    return masks
    

def scale_image(masks, im0_shape, ratio_pad=None):
    """
    Scale masks or images to original image dimensions.
    
    Function:
        Scale resized and padded masks or images back to original image dimensions.
        Remove padding and adjust to correct dimensions.
    
    Input:
        masks (np.ndarray): Resized and padded masks/images
                           with shape [h, w, num] or [h, w, 3]
        im0_shape (tuple): Original image shape (height, width)
        ratio_pad (tuple, optional): Padding ratio and padding values
                                   in format (ratio, pad)
    
    Output:
        np.ndarray: Scaled masks with shape [h, w, num]
    
    Example:
        >>> masks = np.random.rand(640, 640, 3)  # padded image
        >>> im0_shape = (480, 640)  # original image size
        >>> scaled = scale_image(masks, im0_shape)
        >>> print(scaled.shape)  # (480, 640, 3)
    """
    # Rescale coordinates (xyxy) from im1_shape to im0_shape
    im1_shape = masks.shape
    if im1_shape[:2] == im0_shape[:2]:
        return masks
    if ratio_pad is None:  # calculate from im0_shape
        gain = min(im1_shape[0] / im0_shape[0], im1_shape[1] / im0_shape[1])  # gain  = old / new
        pad = (im1_shape[1] - im0_shape[1] * gain) / 2, (im1_shape[0] - im0_shape[0] * gain) / 2  # wh padding
    else:
        # gain = ratio_pad[0][0]
        pad = ratio_pad[1]
    top, left = int(pad[1]), int(pad[0])  # y, x
    bottom, right = int(im1_shape[0] - pad[1]), int(im1_shape[1] - pad[0])

    if len(masks.shape) < 2:
        raise ValueError(f'"len of masks shape" should be 2 or 3, but got {len(masks.shape)}')
    masks = masks[top:bottom, left:right]
    masks = cv2.resize(masks, (im0_shape[1], im0_shape[0]))
    if len(masks.shape) == 2:
        masks = masks[:, :, None]
    return masks

def min_index(arr1, arr2):
    """
    Find a pair of indexes with the shortest distance between two arrays of 2D points.

    Args:
        arr1 (np.ndarray): A NumPy array of shape (N, 2) representing N 2D points.
        arr2 (np.ndarray): A NumPy array of shape (M, 2) representing M 2D points.

    Returns:
        (tuple): A tuple containing the indexes of the points with the shortest distance in arr1 and arr2 respectively.
    """
    dis = ((arr1[:, None, :] - arr2[None, :, :]) ** 2).sum(-1)
    return np.unravel_index(np.argmin(dis, axis=None), dis.shape)

def merge_multi_segment(segments):
    """
    Merge multiple segments into one list by connecting the coordinates with the minimum distance between each segment.
    This function connects these coordinates with a thin line to merge all segments into one.

    Args:
        segments (List[List]): Original segmentations in COCO's JSON file.
                               Each element is a list of coordinates, like [segmentation1, segmentation2,...].

    Returns:
        s (List[np.ndarray]): A list of connected segments represented as NumPy arrays.
    """
    s = []
    segments = [np.array(i).reshape(-1, 2) for i in segments]
    idx_list = [[] for _ in range(len(segments))]

    # Record the indexes with min distance between each segment
    for i in range(1, len(segments)):
        idx1, idx2 = min_index(segments[i - 1], segments[i])
        idx_list[i - 1].append(idx1)
        idx_list[i].append(idx2)

    # Use two round to connect all the segments
    for k in range(2):
        # Forward connection
        if k == 0:
            for i, idx in enumerate(idx_list):
                # Middle segments have two indexes, reverse the index of middle segments
                if len(idx) == 2 and idx[0] > idx[1]:
                    idx = idx[::-1]
                    segments[i] = segments[i][::-1, :]

                segments[i] = np.roll(segments[i], -idx[0], axis=0)
                segments[i] = np.concatenate([segments[i], segments[i][:1]])
                # Deal with the first segment and the last one
                if i in {0, len(idx_list) - 1}:
                    s.append(segments[i])
                else:
                    idx = [0, idx[1] - idx[0]]
                    s.append(segments[i][idx[0] : idx[1] + 1])

        else:
            for i in range(len(idx_list) - 1, -1, -1):
                if i not in {0, len(idx_list) - 1}:
                    idx = idx_list[i]
                    nidx = abs(idx[1] - idx[0])
                    s.append(segments[i][nidx:])
    return s

def masks2segments(masks, strategy: str = "all"):
    """
    Convert masks to segments using contour detection.

    Args:
        masks (torch.Tensor): Binary masks with shape (batch_size, 160, 160).
        strategy (str): Segmentation strategy, either 'all' or 'largest'.

    Returns:
        (list): List of segment masks as float32 arrays.
    """
    segments = []
    for x in masks.int().cpu().numpy().astype("uint8"):
        c = cv2.findContours(x, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        if c:
            if strategy == "all":  # merge and concatenate all segments
                c = (
                    np.concatenate(merge_multi_segment([x.reshape(-1, 2) for x in c]))
                    if len(c) > 1
                    else c[0].reshape(-1, 2)
                )
            elif strategy == "largest":  # select largest segment
                c = np.array(c[np.array([len(x) for x in c]).argmax()]).reshape(-1, 2)
        else:
            c = np.zeros((0, 2))  # no segments found
        segments.append(c.astype("float32"))
    return segments