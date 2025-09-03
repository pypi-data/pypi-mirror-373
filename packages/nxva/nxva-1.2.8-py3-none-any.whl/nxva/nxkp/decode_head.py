import numpy as np
from functools import lru_cache

def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def _softmax(x, axis):
    x = x - np.max(x, axis=axis, keepdims=True)
    ex = np.exp(x)
    return ex / np.sum(ex, axis=axis, keepdims=True)

@lru_cache(maxsize=4) # 只記住最近四個不同的輸入
def grid_xy_cached(fh:int, fw:int):
    gy, gx = np.meshgrid(np.arange(fh), np.arange(fw), indexing="ij")
    return gx, gy


# =============================================================================
# Decode YOLO heads
# =============================================================================
def decode_yolo_head(
    outputs,
    img_size,
    version="yolov5",   # "yolov5", "yolov8", "yolo11"
    with_sigmoid=True,
    task="detect" # "detect", "pose"
):
    """
    統一 YOLO head decode 入口。
    根據 version 自動選用對應 decode function。
    回傳 shape: (B, N, 5+nc) 或 (B, N, 5+nc+17*3) (pose)
    """
    supported_types = ["yolov5", "yolov8", "yolo11"]
    if version == "yolov5":
        return decode_yolov5_head(outputs, img_size, with_sigmoid, task=task)
    elif version == "yolov8" or version == "yolo11":
        return decode_yolov8_11_head(outputs, img_size, task=task)
    else:
        raise ValueError(f"version must be one of {supported_types}, got {version}")

def decode_yolov5_head(
    outputs,
    img_size,
    with_sigmoid=True,
    task="detect"  # "detect", "pose"
):
    if task == "detect":
        return decode_yolov5_detect_heads(outputs, img_size, with_sigmoid)

    elif task == "pose":
        pass

    else:
        raise ValueError(f"task must be 'detect' or 'pose', got {task}")

def decode_yolov5_detect_heads(
    outputs,
    img_size,
    with_sigmoid=True
):
    """
    YOLOv5 後處理（內建 anchors；輸出 (N, 5+nc) 矩陣）。
    不進行原圖縮放／去 letterbox；bbox 座標位於模型輸入尺度。

    參數
    ----
    outputs
        各層輸出，shape=(B, C, H, W)。
    img_size
        (in_h, in_w)，用於計算 stride。
    with_sigmoid
        是否先做 sigmoid。

    回傳
    ----
    np.ndarray, shape=(N, 5+nc)：
        [x, y, w, h, obj_conf, cls1_conf, …]
    """
    # 內建 YOLOv5 anchors (stride 8 / 16 / 32)
    YOLOV5_ANCHORS = np.array([
        [[10, 13],  [16, 30],  [33, 23]],
        [[30, 61],  [62, 45],  [59, 119]],
        [[116, 90], [156, 198], [373, 326]]
    ], dtype=np.float32)
    # YOLOV5_ANCHORS[0] /= 8.0 
    # YOLOV5_ANCHORS[1] /= 16.0 
    # YOLOV5_ANCHORS[2] /= 32.0 

    if isinstance(img_size, int):
        img_size = (img_size, img_size)
    in_h, in_w = img_size
    num_anchors = 3
    matrices = []         # 先收集每層候選，再 concat 起來
    for i, feat in enumerate(outputs):
        # feat: (B, C, H, W)
        bsz, fc, fh, fw = feat.shape
        anchor_offset   = fc // num_anchors      # = 5 + nc
        nc              = anchor_offset - 5

        # stride: 每格對應的像素寬 / 高
        stride_w = in_w / fw
        stride_h = in_h / fh

        # reshape
        feat = feat.transpose(0, 2, 3, 1)                # (B, H, W, C)
        if with_sigmoid:
            feat = _sigmoid(feat)
        feat = feat.reshape(bsz, fh, fw, num_anchors, anchor_offset)  # (B, H, W, A, 5+nc)
        # grid
        grid_x, grid_y = grid_xy_cached(fh, fw)  # (H, W)
        grid = np.stack((grid_x, grid_y), axis=-1)       # (H, W, 2)
        grid = grid[None, ..., None, :]                  # (1, H, W, 1, 2)

        # 解碼 bbox
        anchor_wh = YOLOV5_ANCHORS[i][None, None, None, :, :]   # (1, 1, 1, A, 2)
        pred_xy = (feat[..., 0:2] * 2.0 - 0.5 + grid) * np.array([stride_w, stride_h])
        pred_wh = (feat[..., 2:4] * 2.0) ** 2 * anchor_wh
        boxes   = np.concatenate((pred_xy, pred_wh), axis=-1)   # (B, H, W, A, 4)
        # objectness & class scores
        obj_conf   = feat[..., 4:5]                             # (B, H, W, A, 1)
        cls_scores = feat[..., 5:]                              # (B, H, W, A, nc)

        # flatten (H, W, A) → N
        N_layer         = fh * fw * num_anchors
        boxes_flat      = boxes.reshape(bsz, N_layer, 4)        # (B, N, 4)
        obj_flat        = obj_conf.reshape(bsz, N_layer, 1)     # (B, N, 1)
        cls_scores_flat = cls_scores.reshape(bsz, N_layer, nc)  # (B, N, nc)

        layer_mat = np.concatenate(                             # (B, N, 5+nc)
            [boxes_flat, obj_flat, cls_scores_flat], 
            axis=-1
        )
        matrices.append(layer_mat)

    if not matrices:
        nc = outputs[0].shape[1] - 5 if len(outputs) > 0 else 0
        return np.empty((0, 5 + nc), dtype=np.float32)
            
    # 把三層沿 axis=1 拼起來 → (B, N_total, 5+nc)
    return np.concatenate(matrices, axis=1).astype(np.float32)

def decode_yolov8_11_head(
    outputs,
    img_size,
    task="detect"  # "detect", "pose"
):
    """
    YOLOv11 head後處理，輸入各層head，輸出bbox。

    Parameters
    ----
        task: str
            任務類型，"detect" 或 "pose"。

        outputs: list of np.ndarray or torch.Tensor, 各層輸出，shape=(B, C, H, W)。
            detect:
                包含以下三個 head: head_s8, head_s16, head_s32
                shape =(1,64+nc, H, W) (80^2, 40^2, 20^2)
            pose:
                包含以下四個 head: head_s8, head_s16, head_s32, head_kpt
                head_kpt shape=(1,51,8400)

        img_size: tuple
            模型輸入尺寸 (h, w)，用於計算 stride。

    
    Returns
    -------
        detect:
            v5:
                np.ndarray, shape=(B, N_total, 5+nc):
                    [x, y, w, h, obj_conf, cls1_conf, cls2_conf, …] 
            v8/v11:
                v8開始 channel first -> B, C, N
                np.ndarray, shape=(B, 4+nc, N_total):
                    [x, y, w, h, cls1_conf, cls2_conf, …] 
        pose:
            np.ndarray, shape=(B, 4+1+17*3, N_total): #(B, C, N) -> channel first
                [x, y, w, h, obj_conf, cls1_conf, cls2_conf, …, kpt1_x, kpt1_y, kpt1_v, kpt2_x, kpt2_y, kpt2_v, …]
                (pose: 4+1 為 bbox 部分(nc=1)，17*3 為 keypoint 部分)
    """
    bbox_matrices, feature_shapes = decode_yolov8_11_detect_heads(outputs[:3], img_size)  # 前三層是 bbox head
    if task == "detect":
        return bbox_matrices  # (B, 4+nc, N_total)

    elif task == "pose":
        kpt_matrices = decode_yolov8_11_pose_heads(outputs[3], img_size, feature_shapes)  # 第四層是 keypoint head
        bbox_kpt_matrices = np.concatenate([bbox_matrices, kpt_matrices], axis=1)  # (B, 4+nc, N_total)
        return bbox_kpt_matrices  # (B, 4+1+17*3, N_total)

    else:
        raise ValueError(f"task must be 'detect' or 'pose', got {task}")

def decode_yolov8_11_detect_heads(
    heads, img_size, reg_max=16
):
    """
    YOLOv8/v11 bbox head decode, 回傳 bbox_all (B, 4+nc, N)
    """
    bins = np.arange(reg_max).reshape(1, 1, reg_max, 1, 1)
    if isinstance(img_size, int):
        img_size = (img_size, img_size)
    in_h, in_w = img_size

    bbox_matrices = []
    feature_shapes = []
    for feat in heads:
        bsz, fc, fh, fw = feat.shape
        nc = fc - reg_max * 4  # nc = classes-threshold (reg_max: 4*16 bins)

        # grid
        grid_x, grid_y = grid_xy_cached(fh, fw)  # (H, W)
        grid = np.stack((grid_x + 0.5, grid_y + 0.5), axis=-1)  # (H, W, 2), +0.5 表anchor中心點
        grid = grid[None, ...] # (1, H, W, 2)

        # stride: 每格對應的像素寬 / 高
        stride = np.array([in_w / fw, in_h / fh])

        # 處理 head_s8, head_s16, head_s32 (:64 -> 4*16 bins)
        distance = feat[:, :reg_max * 4, :, :].reshape(bsz, 4, reg_max, fh, fw) # (B, 4, 16, H, W)
        distance = _softmax(distance, axis=2) #(B, 4, 16, H, W) (同個方向機率總和為1)
        ltrb = (distance * bins).sum(axis=2) # (B, 4, H, W) (每個方向的距離，summarization over bins)
        d = np.transpose(ltrb, (0, 2, 3, 1)) # 把 ltrb 轉為 (B, H, W, 4)

        # 解碼 bbox
        x1y1 = (grid - d[..., 0:2]) * stride  # (B, H, W, 2) 左上
        x2y2 = (grid + d[..., 2:4]) * stride  # (B, H, W, 2) 右下
        xy = (x2y2 + x1y1) / 2  # (B, H, W, 2) 中心點
        wh = (x2y2 - x1y1)  # (B, H, W, 2) 寬高
        pred = np.concatenate((xy, wh), axis=-1)  # (B, H, W, 4)

        # cls_threshold -> reg_max * 4: (之後是各classes-threshold，要sigmoid)
        cls = _sigmoid(feat[:, reg_max * 4:]) # (B, nc, H, W)

        # flatten (H, W) → N , channel first (B, C, N)
        N_layer = fh * fw
        pred = pred.reshape(bsz, N_layer, 4).transpose(0, 2, 1)  # (B, 4, N)
        cls_flat = cls.reshape(bsz, nc, N_layer) # (B, nc, N)

        # pred_bbox_confidence shape = (B, C, N) = (B, 4+nc, N)
        pred_bbox_confidence = np.concatenate([pred, cls_flat], axis=1)  # (B, 4+nc, N)
        bbox_matrices.append(pred_bbox_confidence)
        feature_shapes.append((fh, fw)) # 收集 feature shape 
    
    bbox_result = np.concatenate(bbox_matrices, axis=2).astype(np.float32)  # (B, 4+nc, N_total)
    return bbox_result, feature_shapes

def decode_yolov8_11_pose_heads(
    head_kpt,
    img_size,
    feature_shapes
):
    head_kpt = head_kpt.reshape(1, 51, 8400)
    bsz, fc, _ = head_kpt.shape # (B, 51, 8400)
    kpt_matrices = []  # 收集 keypoint head 的結果
    ptr = 0
    if isinstance(img_size, int):
        img_size = (img_size, img_size)
    in_h, in_w = img_size
    for (fh, fw) in feature_shapes:
        kpt_num = fh * fw  # 每個 head 有多少個 keypoint

        # grid
        grid_x, grid_y = grid_xy_cached(fh, fw)  # (H, W)
        grid = np.stack((grid_x + 0.5, grid_y + 0.5), axis=0)  # (2, H, W), +0.5 表 anchor 中心點
        grid = grid[None, None, ...]  # (1, 1, 2, H, W)

        # stride: 每格對應的像素寬 / 高
        stride = np.array([in_w / fw, in_h / fh]).reshape(1, 1, 2, 1, 1)  # (1, 1, 2, 1, 1)

        # feat: 原本 (B, C, A) == (1, 51, 8400) -> (B, 17, 3, H, W)
        feat = head_kpt[:, :, ptr:ptr + kpt_num].reshape(bsz, 17, 3, fh, fw)
        ptr += kpt_num  # 更新下一個 head 的起始 index

        # 處理kpt
        kpt_xy =((feat[:, :, :2, :, :] * 2 - 0.5) + grid) * stride  # (B, 17, 2, H, W)
        kpt_v = _sigmoid(feat[:, :, 2])  # confidence

        # flatten (H, W) → N
        kpt_mat = np.concatenate((kpt_xy, kpt_v[:,:,None,:,:]), axis=2)  # (B, 17, 3, H, W)
        kpt_mat = kpt_mat.reshape(bsz, 51, -1) # (B, 51, N)
        kpt_matrices.append(kpt_mat)
    return np.concatenate(kpt_matrices, axis=-1).astype(np.float32) # (B, 51, N_total)