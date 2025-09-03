import os
from typing import List

import cv2
import torch
import numpy as np

class DatasetLoader:
    """
    通用YOLO格式資料集解析器，支援detect/segment/pose/classify四種任務，支援batch。
    只需要一個驗證集合的txt檔案，自動將images路徑轉換為labels路徑。
    """
    def __init__(self, val_txt_path: str, task: str, num_kpts: None, batch_size: int = 1, img_size: tuple = (320, 320)):
        assert val_txt_path.endswith('.txt'), 'val_txt_path must end with .txt'
        assert task in ['detect', 'segment', 'pose', 'classify'], 'task must be detect/segment/pose/classify'
        assert batch_size > 0, 'batch_size must be greater than 0'
        assert len(img_size) == 2, 'img_size must be a tuple of (width, height)'

        self.val_txt = self.read_lines(val_txt_path)
        self.task = task
        self.num_kpts = int(num_kpts[0]) if num_kpts else None
        self.batch_size = batch_size
        self.img_size = img_size

    def read_lines(self, txt_path: str) -> List[str]:
        """讀取txt檔案中的圖片路徑"""
        with open(txt_path, 'r') as f:
            return [line.strip() for line in f.readlines()]

    def get_label_path(self, img_path: str) -> str:
        """將圖片路徑轉換為對應的標籤路徑 (images -> labels, .jpg/.png -> .txt)"""
        # 將路徑中的 'images' 替換為 'labels'
        label_path = img_path.replace('/images/', '/labels/')
        # 將圖片副檔名替換為 .txt
        base_name = os.path.splitext(label_path)[0]
        return base_name + '.txt'

    def load_image(self, img_path: str) -> np.ndarray:
        """載入圖片並返回原始 numpy array"""
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Cannot load image: {img_path}")
        return img

    def load_yolo_label(self, label_path: str) -> np.ndarray:
        """載入YOLO格式的檢測標籤 (class_id, x_center, y_center, width, height)"""
        labels = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        labels.append([float(x) for x in parts])
        return np.array(labels, dtype=np.float32) if labels else np.zeros((0, 5), dtype=np.float32)

    def load_segmentation_label(self, label_path: str) -> np.ndarray:
        """載入分割標籤 (class_id, x_center, y_center, width, height, mask_points...)"""
        labels = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = float(parts[0])
                        bbox = [float(x) for x in parts[1:5]]
                        mask_points = [float(x) for x in parts[5:]]
                        # 使用 object 數組來存儲可變長度的 mask_points
                        labels.append([class_id] + bbox + mask_points)
        
        if labels:
            # 使用 object 數組來處理不同長度的 mask_points
            return np.array(labels, dtype=object)
        else:
            return np.zeros((0, 5), dtype=np.float32)

    def load_pose_label(self, label_path: str) -> np.ndarray:
        """載入姿態估計標籤 (class_id, x_center, y_center, width, height, keypoints...)"""
        labels = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5 + self.num_kpts * 3:
                        class_id = float(parts[0])
                        bbox = [float(x) for x in parts[1:5]]
                        kpts = [float(x) for x in parts[5:]]
                        labels.append([class_id] + bbox + kpts)
        return np.array(labels, dtype=np.float32) if labels else np.zeros((0, 5 + self.num_kpts * 3), dtype=np.float32)

    def load_classify_label(self, label_path: str) -> np.ndarray:
        """載入分類標籤 (單一class_id)"""
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                class_id = int(f.readline().strip())
            return np.array([class_id], dtype=np.int64)
        else:
            return np.array([0], dtype=np.int64)  # 預設class_id為0

    def __len__(self):
        return len(self.val_txt)

    def __getitem__(self, idx):
        """取得單個樣本"""
        val_img_path = self.val_txt[idx]
        gt_label_path = self.get_label_path(val_img_path)
        
        val_img = self.load_image(val_img_path)
        
        # 根據任務載入對應的標籤
        if self.task == 'detect':
            gt_label_tensor = self.load_yolo_label(gt_label_path)
        elif self.task == 'segment':
            gt_label_tensor = self.load_segmentation_label(gt_label_path)
        elif self.task == 'pose':
            gt_label_tensor = self.load_pose_label(gt_label_path)
        elif self.task == 'classify':
            gt_label_tensor = self.load_classify_label(gt_label_path)
        else:
            raise ValueError(f"Unknown task: {self.task}")
        
        return val_img, gt_label_tensor

    def __iter__(self):
        """批次迭代器"""
        n = len(self)
        for i in range(0, n, self.batch_size):
            batch_val_imgs = []
            batch_gt_labels = []
            
            for j in range(i, min(i + self.batch_size, n)):
                val_img, gt_label = self[j]
                batch_val_imgs.append(val_img)
                batch_gt_labels.append(gt_label)
            
            # 保持圖片為 list 格式: [cv2.imread, cv2.imread, ...]
            # batch_val_imgs = torch.stack(batch_val_imgs)  # 移除這行
            
            # 所有任務都進行對齊處理
            if self.batch_size > 1:
                batch_gt_labels = self._align_labels(batch_gt_labels)
            else:
                # batch_size = 1 時，直接轉換為 numpy array
                batch_gt_labels = np.array(batch_gt_labels)
            
            yield batch_val_imgs, batch_gt_labels

    def _align_labels(self, label_list: List[np.ndarray]) -> np.ndarray:
        """
        對齊不同長度的 label list，用於 batch_size > 1 的情況
        對於 detect/segment/pose 任務，每張圖的物件數量可能不同
        對於 classify 任務，每個樣本只有一個 class_id，需要對齊成 (batch_size, 1)
        """
        if not label_list:
            return np.array([])
        
        # classify 任務的特殊處理
        if self.task == 'classify':
            # classify 的每個 label 形狀是 (1,)，需要對齊成 (batch_size, 1)
            return np.array(label_list)
        
        # segment 任務的特殊處理 - 使用 object 數組
        if self.task == 'segment':
            # 對於分割任務，每個 label 是 object 數組，包含可變長度的 mask_points
            return np.array(label_list, dtype=object)
        
        # detect/pose 任務的處理
        # 找出最大的物件數量
        max_objects = max(label.shape[0] for label in label_list)
        
        if max_objects == 0:
            # 如果所有 label 都是空的，返回空的 batch array
            # 這裡需要確保 feature_dim 的正確性，對於空 array，其 shape[1] 可能為0
            # 假設至少有5個特徵 (class_id, bbox_xywh)
            feature_dim = label_list[0].shape[1] if label_list[0].shape[0] > 0 else (5 + self.num_kpts * 3 if self.task == 'pose' else (5 if self.task == 'detect' or self.task == 'segment' else 1))
            return np.zeros((len(label_list), 0, feature_dim), dtype=np.float32)
        
        # 獲取每個 label 的特徵維度
        feature_dim = label_list[0].shape[1]
        
        # 創建對齊後的 batch array
        aligned_labels = []
        for label in label_list:
            if label.shape[0] == 0:
                # 如果 label 是空的，用零填充
                padded = np.zeros((max_objects, feature_dim), dtype=np.float32)
            else:
                # 如果 label 不為空，進行填充
                if label.shape[0] < max_objects:
                    # 用零填充到最大長度
                    padding = np.zeros((max_objects - label.shape[0], feature_dim), dtype=np.float32)
                    padded = np.vstack([label, padding])
                else:
                    padded = label
            
            aligned_labels.append(padded)
        
        return np.array(aligned_labels)

# 使用範例：
# loader = DatasetLoader('val_imgs.txt', task='pose', num_kpts=17, batch_size=4, img_size=(320, 320))
# for val_imgs, gt_labels in loader:
#     print(len(val_imgs), gt_labels.shape)  # val_imgs: [cv2.imread, cv2.imread, ...], gt_labels: torch.Tensor
