import cv2
import numpy as np
import time

class BaseDataProcess:
    def preprocess(self):
        raise NotImplementedError("prepocess function should be overwrited if not used ultralytics detect")
    
    def postprocess(self):
        raise NotImplementedError("postprocess function should be overwrited if not used ultralytics detect")

class DetectionDataProcess(BaseDataProcess):
    def preprocess(self, img, new_shape):
        """
        對輸入圖片做 resize 並保持長寬比，補齊邊界至指定大小，轉為 (1, 3, H, W) 格式並正規化。

        Args:
            img (np.ndarray): 原始圖片，格式為 HWC（Height, Width, Channels），BGR 色彩順序。
            new_shape (tuple): 模型輸入的目標尺寸 (height, width)。

        Returns:
            tuple:
                img (np.ndarray): 預處理後的圖片，格式為 (1, 3, H, W)，float32，數值在 0~1。
                ratio_pad (tuple): ((r, r), (dw, dh))，r 為縮放比例，dw/dh 為 padding 值。
        """
        new_shape = new_shape
        color = (114, 114, 114)
        shape = img.shape[:2]
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        r = min(r, 1.0)
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        dw /= 2
        dh /= 2
        if shape[::-1] != new_unpad:
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
        img = img[:, :, ::-1]
        img = img.transpose(2, 0, 1)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        img = np.ascontiguousarray(img, dtype=np.float32)

        return img, ((r, r), (dw, dh))

    def _xywh2xyxy(self, x):
        """
        將 bbox 從 (x_center, y_center, w, h) 轉為 (x1, y1, x2, y2) 格式。

        Args:
            x (np.ndarray): 輸入的 bounding boxes，shape 為 (N, 4)。

        Returns:
            y (np.ndarray): 轉換後的 bounding boxes，shape 為 (N, 4)。
        """
        y = np.empty_like(x)  # faster than clone/copy
        xy = x[..., :2]  # centers
        wh = x[..., 2:] / 2  # half width-height
        y[..., :2] = xy - wh  # top left xy
        y[..., 2:] = xy + wh  # bottom right xy
        return y

    def _nms_numpy_boxes(self, boxes, scores, iou_threshold=0.5):
        """
        用 NumPy 改寫的 NMS 演算法。

        Args:
            boxes (np.ndarray): 所有預測框，shape 為 (N, 4)，格式為 [x1, y1, x2, y2]。
            scores (np.ndarray): 每個 box 的置信度分數，shape 為 (N,)。
            iou_threshold (float): IoU 閾值，重疊高於此值的 box 會被抑制，預設 0.5。

        Returns:
            List[int]: 保留下來的 box 索引。
        """
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            if order.size == 1:
                break

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h

            iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)

            inds = np.where(iou <= iou_threshold)[0]
            order = order[inds + 1]

        return keep

    def _non_max_suppression(self,
        prediction,
        conf_thres=0.25,
        iou_thres=0.45,
        classes=None,
        agnostic=False,
        multi_label=False,
        labels=(),
        max_det=300,
        nc=0,  # number of classes (optional)
        max_time_img=0.05,
        max_nms=30000,
        max_wh=7680,
        in_place=True,
        rotated=False,
    ):
        """
        執行 Non-Maximum Suppression（NMS）來過濾重疊的 bbox，可支援 multi-label、class-agnostic 等功能。

        Args:
            prediction (np.ndarray): 模型原始輸出，shape 為 (batch, num_classes + 4 + num_masks, num_boxes)。
            conf_thres (float): 置信度門檻，低於此值的框會被捨棄。
            iou_thres (float): NMS 的 IoU 閾值。
            classes (List[int] or None): 若設定，僅保留這些類別的偵測。
            agnostic (bool): 若為 True，則不考慮類別進行 NMS（所有框視為同類）。
            multi_label (bool): 若為 True，支援一個框有多個類別。
            labels (List[List]): 每張圖片的預設標籤框，可用於自動標註。
            max_det (int): NMS 後最多保留多少個框。
            nc (int): 類別數。預設為 0，會從輸出自動推論。
            max_time_img (float): 每張圖片處理時間上限（秒）。
            max_nms (int): 最多傳入 NMS 的框數上限。
            max_wh (int): 最大圖片尺寸（用於類別偏移處理）。
            in_place (bool): 是否在原始 prediction 上直接修改。
            rotated (bool): 是否處理旋轉框（OBB）。

        Returns:
            List[np.ndarray]: 每張圖片的 NMS 結果，每項 shape 為 (n, 6+mask)，欄位為 (x1, y1, x2, y2, conf, class_id[, mask...])。
        """


        bs = prediction.shape[0]  # batch size (BCN, i.e. 1,84,6300)
        nc = nc or (prediction.shape[1] - 4)  # number of classes
        nm = prediction.shape[1] - nc - 4  # number of masks
        mi = 4 + nc  # mask start index
        xc = prediction[:, 4:mi].max(axis=1) > conf_thres  # candidates

        # Settings
        time_limit = 2.0 + max_time_img * bs  # seconds to quit after
        multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)

        prediction = prediction.transpose(0, 2, 1)  # shape(1,84,6300) to shape(1,6300,84)
        if not rotated:
            if in_place:
                prediction[..., :4] = self._xywh2xyxy(prediction[..., :4])  # xywh to xyxy
            else:
                prediction = np.concatenate((self._xywh2xyxy(prediction[..., :4]), prediction[..., 4:]), axis=-1)  # xywh to xyxy

        t = time.time()
        output = [np.zeros((0, 6 + nm))] * bs
        for xi, x in enumerate(prediction):  # image index, image inference
            x = x[xc[xi]]  # confidence

            # Cat apriori labels if autolabelling
            if labels and len(labels[xi]) and not rotated:
                lb = labels[xi]
                v = np.zeros((len(lb), nc + nm + 4), device=x.device)
                v[:, :4] = self._xywh2xyxy(lb[:, 1:5])  # box
                v[range(len(lb)), lb[:, 0].long() + 4] = 1.0  # cls
                x = np.concatenate((x, v), axis=0)

            # If none remain process next image
            if not x.shape[0]:
                continue

            box = x[:, :4]           
            cls = x[:, 4:4 + nc]     
            mask = x[:, 4 + nc:] if nm > 0 else np.zeros((x.shape[0], 0))    # 剩下的是 mask（如果有）

            if multi_label:
                i, j = np.where(cls > conf_thres)
                x = np.concatenate((box[i], x[i, 4 + j, None], j[:, None].float(), mask[i]), axis=1)
            else:  # best class only
                conf = np.max(cls, axis=1)
                j = np.argmax(cls, axis=1)
                x = np.concatenate((box, conf[:, None], j[:, None].astype(np.float32), mask), axis=1)[conf > conf_thres]

            # Filter by class
            if classes is not None:
                x = x[(x[:, 5:6] == classes).any(1)]

            # Check shape
            n = x.shape[0]  # number of boxes
            if not n:  # no boxes
                continue
            if n > max_nms:  # excess boxes
                x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence and remove excess boxes

            # Batched NMS
            c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
            scores = x[:, 4]  # scores
            # if rotated:
            #     boxes = np.concatenate((x[:, :2] + c, x[:, 2:4], x[:, -1:]), axis=-1)  # xywhr
            #     i = self._nms_rotated(boxes, scores, iou_thres)
            # else:
            boxes = x[:, :4] + c  # boxes (offset by class)
            i = self._nms_numpy_boxes(boxes, scores, iou_thres)  # NMS
            
            i = i[:max_det]  # limit detections

            output[xi] = x[i]
            if (time.time() - t) > time_limit:
                break  # time limit exceeded

        return output
    
    def _clip_boxes(self, boxes, shape):
        """
        Takes a list of bounding boxes and a shape (height, width) and clips the bounding boxes to the shape.

        Args:
            boxes (torch.Tensor | numpy.ndarray): The bounding boxes to clip.
            shape (tuple): The shape of the image.

        Returns:
            (numpy.ndarray): The clipped boxes.
        """
        boxes[..., [0, 2]] = boxes[..., [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[..., [1, 3]] = boxes[..., [1, 3]].clip(0, shape[0])  # y1, y2

        return boxes
    
    def scale_boxes(self, img1_shape, boxes, img0_shape, ratio_pad=None, padding=True, xywh=False):
        """
        Rescale bounding boxes from img1_shape to img0_shape.

        Args:
            img1_shape (tuple): The shape of the image that the bounding boxes are for, in the format of (height, width).
            boxes (torch.Tensor): The bounding boxes of the objects in the image, in the format of (x1, y1, x2, y2).
            img0_shape (tuple): The shape of the target image, in the format of (height, width).
            ratio_pad (tuple): A tuple of (ratio, pad) for scaling the boxes. If not provided, the ratio and pad will be
                calculated based on the size difference between the two images.
            padding (bool): If True, assuming the boxes is based on image augmented by yolo style. If False then do regular
                rescaling.
            xywh (bool): The box format is xywh or not.

        Returns:
            numpy.ndarray: The scaled bounding boxes, in the format of (x1, y1, x2, y2).
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
        return self._clip_boxes(boxes, img0_shape)

    def postprocess(self, model, output, img, new_shape, conf_thres=0.6, iou_thres=0.5):
        """
        將模型原始輸出進行 NMS 並還原為原始圖片尺度下的結果。

        Args:
            model: 包含 output_names 的模型物件，用來對應輸出名稱。
            output (List[np.ndarray]): TensorRT 推論的原始輸出。
            img (np.ndarray): 原始輸入圖片（未經預處理），格式為 HWC BGR。
            new_shape (tuple): 模型的輸入尺寸 (height, width)。
            conf_thres (float): 置信度門檻，預設 0.6。
            iou_thres (float): IoU 閾值，預設 0.5。

        Returns:
            Tuple:
                scaled_boxes (np.ndarray): 還原為原始圖片尺寸的邊框，shape 為 (n, 4)。
                confs (np.ndarray): 每個偵測框的置信度，shape 為 (n,)。
                class_ids (np.ndarray): 每個偵測框的類別索引，shape 為 (n,)。
        """
        
        output_main = None
        for name, out in zip(model.output_names, output):
            if name == 'output0':
                output_main = out
                break

        detections = self._non_max_suppression(output_main, conf_thres=conf_thres, iou_thres=iou_thres)

        if detections is not None and len(detections):
            det = detections[0]
            boxes = det[:, :4]
            confs = det[:, 4]
            class_ids = det[:, 5]
        
        else:
            boxes = np.zeros((0, 4))
            confs = np.zeros((0,))
            class_ids = np.zeros((0,))
            return boxes, confs, class_ids

        img0_shape = img.shape[:2]
        _, ratio_pad = self.preprocess(img, new_shape)
        img1_shape = new_shape

        scaled_boxes = self.scale_boxes(
            img1_shape=img1_shape,    # TRT 輸入圖片尺寸
            boxes=boxes,  # 要轉換的 bbox
            img0_shape=img0_shape,      # 原始圖片尺寸
            ratio_pad=(ratio_pad),  # Ultralytics 的 ratio_pad 格式
            padding=True
        )

        return scaled_boxes, confs, class_ids

    def _np_box_iou(self, box1, box2):
        """
        使用 NumPy 計算兩組框之間的 IoU。

        Args:
            box1 (np.ndarray): 第一組 box，shape 為 (N, 4)。
            box2 (np.ndarray): 第二組 box，shape 為 (M, 4)。

        Returns:
            np.ndarray: IoU 矩陣，shape 為 (N, M)。
        """
        area1 = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])  # (N,)
        area2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])  # (M,)

        inter_x1 = np.maximum(box1[:, None, 0], box2[:, 0])
        inter_y1 = np.maximum(box1[:, None, 1], box2[:, 1])
        inter_x2 = np.minimum(box1[:, None, 2], box2[:, 2])
        inter_y2 = np.minimum(box1[:, None, 3], box2[:, 3])

        inter_w = np.clip(inter_x2 - inter_x1, a_min=0, a_max=None)
        inter_h = np.clip(inter_y2 - inter_y1, a_min=0, a_max=None)
        inter_area = inter_w * inter_h

        union = area1[:, None] + area2 - inter_area
        return inter_area / (union + 1e-6)

    def compute_tp_for_map(self, labels_boxes, labels_class_ids, pred_scaled_boxes, pred_confs, pred_class_ids):
        """
        根據預測與標註框，計算多個 IoU 門檻下的 true positive，用於後續計算 mAP。

        Args:
            labels_boxes (np.ndarray): 標註框，shape 為 (n_labels, 4)。
            labels_class_ids (np.ndarray): 標註類別 ID，shape 為 (n_labels,)。
            pred_scaled_boxes (np.ndarray): 模型預測框（已還原至原圖比例），shape 為 (n_preds, 4)。
            pred_confs (np.ndarray): 模型預測置信度，shape 為 (n_preds,)。
            pred_class_ids (np.ndarray): 模型預測類別 ID，shape 為 (n_preds,)。

        Returns:
            Tuple:
                tp (np.ndarray): true positive 標記矩陣，shape 為 (n_preds, 10)，對應 IoU 門檻 0.5~0.95。
                confs (np.ndarray): 每個預測的 confidence 分數，shape 為 (n_preds,)。
                pred_classes (np.ndarray): 預測類別 ID，shape 為 (n_preds,)。
                target_classes (np.ndarray): 標註類別 ID，shape 為 (n_labels,)。
        """

        preds = np.concatenate([pred_scaled_boxes, pred_confs[:, None], pred_class_ids[:, None]], axis=1)

        ious = self._np_box_iou(pred_scaled_boxes, labels_boxes)
        pred_classes = preds[:, 5].astype(int)
        target_classes = labels_class_ids.astype(int)

        iou_thresholds = np.linspace(0.5, 0.95, 10)
        n_preds = len(preds)
        tp = np.zeros((n_preds, len(iou_thresholds)), dtype=bool)

        for i, thresh in enumerate(iou_thresholds):
            iou_max = ious.max(axis=1)
            iou_idx = ious.argmax(axis=1)
            matched_gt_classes = target_classes[iou_idx]
            correct = (iou_max > thresh) & (pred_classes == matched_gt_classes)
            tp[:, i] = correct

        return tp, preds[:, 4], pred_classes, target_classes