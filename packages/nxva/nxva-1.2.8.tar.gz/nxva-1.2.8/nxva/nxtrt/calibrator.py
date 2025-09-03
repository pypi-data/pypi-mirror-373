import pycuda.autoinit
import os
import cv2
import pycuda.driver as cuda
import numpy as np
import tensorrt as trt
from .data_process import DetectionDataProcess


class Calibrator(trt.IInt8EntropyCalibrator2):
    def __init__(self, calib_dir, input_shape, batch_size = 8, cache_file="calibration.cache"):
        """
        初始化 TensorRT 的 INT8 熵校準器（Entropy Calibrator），負責將校準圖片依 batch 提供給 TensorRT 做 INT8 量化。

        Args:
            calib_dir (str): 
                校準圖片所在的資料夾路徑，內部應包含 .jpg 或 .png 格式的圖片。
            input_shape (tuple): 
                模型的輸入 shape，格式為 (B, C, H, W)，其中 B 為 batch size（仍須單獨指定）。
            batch_size (int, optional): 
                每次校準處理的圖片數量（也就是一次傳給 TensorRT 幾張圖），預設為 8。
            cache_file (str, optional): 
                校準快取檔案的名稱，用於儲存或重複使用 TensorRT 的量化結果，預設為 'calibration.cache'。
        """
        super().__init__()
        self.cache_file = cache_file # 設定校準用的快取檔案名稱
        self.batch_size = batch_size # 每批處理的影像數量
        self.input_shape = input_shape # 模型輸入的形狀 (B, C, H, W)
        self.image_paths = [os.path.join(calib_dir, f) for f in os.listdir(calib_dir) if f.endswith(('.jpg', '.png'))] # 取得所有校準資料夾中符合 jpg 或 png 格式的影像檔案路徑
        self.current_index = 0 # 記錄當前讀取到第幾張圖片
        intbytes = int(self.batch_size * np.prod(self.input_shape[1:]) * np.float32().nbytes) # 計算一個 batch 的輸入張量總位元組大小 (float32 大小 × 通道 × 高 × 寬 × batch 數)
        self.device_input = cuda.mem_alloc(intbytes) # 在 GPU 中分配記憶體空間
        self.processor = DetectionDataProcess() # 自定義的影像處理類別（預處理

    def get_batch_size(self):
        return self.batch_size # 回傳 batch 大小
    
    def get_batch(self, names):
        try:
            if self.current_index + self.batch_size > len(self.image_paths): # 檢查是否還有足夠的圖片
                print("No more images for calibration.")
                return None

            batch = [] # 儲存處理後的圖片

            for i in range(self.batch_size): # 逐張處理一個 batch 的圖片
                img_path = self.image_paths[self.current_index + i] # 取得圖片路徑
                img = cv2.imread(img_path) # 使用 OpenCV 讀取圖片
                if img is None: # 若圖片讀取失敗，印出錯誤訊息
                    print(f"Failed to read image: {img_path}")
                    raise ValueError(f"Image {img_path} could not be read.")
                
                new_shape = self.input_shape[2:] # 提取 (height, width)
                img_process, _ = self.processor.preprocess(img, new_shape) # 呼叫預處理函式

                batch.append(img_process) # 加入 batch 列表
            
            if len(batch) == 0: # 如果這個 batch 裡沒有有效圖片
                print("No valid images in batch!")
                return None
            batch = np.stack(batch, axis=0) # 將多張圖堆疊成一個 numpy array
            batch = np.ascontiguousarray(batch, dtype=np.float32) # 確保記憶體連續，且轉成 float32
            cuda.memcpy_htod(self.device_input, batch) # 將資料從 host 傳輸到 GPU 裡
            self.current_index += self.batch_size # 更新目前圖片的 index
            print(f"Calibrated batch {self.current_index // self.batch_size}") # 印出目前校準到第幾批
            return [int(self.device_input)] # 回傳 GPU 上的資料指標

        except Exception as e:
            print(f"[ERROR] Exception caught in get_batch(): {type(e).__name__}: {e}") # 捕捉錯誤並顯示
            return None
        
    def read_calibration_cache(self): # 嘗試從本地讀取先前的校準快取
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as f:
                return f.read() # 回傳快取內容
        return None # 若無快取則回傳 None

    def write_calibration_cache(self, cache): # 將校準快取寫入檔案
        with open(self.cache_file, "wb") as f:
            f.write(cache) # 將快取寫入磁碟
        
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file) # 寫完後刪掉快取檔案，避免不同設備使用到相同快取