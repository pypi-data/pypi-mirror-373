import numpy as np
import atexit
import json
import logging
import multiprocessing.resource_tracker

from multiprocessing import shared_memory

class SHMHandler():
    def __init__(
        self,
        w,
        h,
        cameras_num,
        max_detection_num=10,
        shared_name="frames_results_shm",
        buffer_per_camera=2,
        feature_dim=0,
        namespace=None,
    ):
        """
        Shared memory handler for frames and bboxes

        Shared memory block layout:

        ---- all camera control block ----
        +---------------+----------------+
        | Control Block | Metadata Block |
        +---------------+----------------+
        ------- one camera one buffer block -------
        +--------------+--------------+------------+
        | Camera Block | Bboxes Block | ReID Block |
        +--------------+--------------+------------+

        Args:
            w: int
                frame width
            h: int
                frame height
            cameras_num: int
                camera number
            max_detection_num: int
                max detection number per frame
            shared_name: str
                shared memory name
            buffer_per_camera: int
                buffer number per camera
            namespace: str
                namespace for logger, default is None
                
        Attributes:
            width: int
                frame width
            height: int
                frame height
            cameras_num: int
                camera number
            max_rows: int
                max detection number per frame
            max_cols: int
                max columns of bboxes (x1, y1, x2, y2, score, class)
            bboxes_size: int
                size of bboxes shared memory block
            meta_size: int
                size of metadata shared memory block
            frame_size: int
                size of frames shared memory block
            slot_size: int
                size of each slot in shared memory block
            camera_block_size: int
                size of each camera's buffer in shared memory block
            control_bytes_per_camera: int
                control bytes per camera (16 bytes)
            control_block_size: int
                control block size in shared memory block
            total_size: int
                total size of shared memory block
            shared_name: str
                shared memory name
            shm: shared_memory.SharedMemory 
                shared memory object
        """
        self.logger            = logging.getLogger(namespace) if namespace else logging.getLogger()

        self.width             = w # width
        self.height            = h # height

        self.cameras_num       = cameras_num # camera數量

        # bboxes SharedMemory Block
        self.max_rows          = max_detection_num # 最大偵測數量
        self.max_cols          = 6 # bboxes.shape
        self.bboxes_size       = self.max_rows * self.max_cols * np.float32().nbytes
        
        # ReID SharedMemory Block
        self.feature_dim       = feature_dim # ReID特徵長度512
        self.reid_size         = self.max_rows * self.feature_dim * np.float32().nbytes
        
        # meta SharedMemory Block
        self.meta_size         = 1024

        # Frames SharedMemory Block
        self.frame_size        = h * w * 3 * np.dtype(np.uint8).itemsize

        # Control SharedMemory Block
        self.control_bytes     = 16
        self.control_size      = self.control_bytes

        # SharedMemory slot size
        self.slot_size         = self.frame_size + self.bboxes_size + self.reid_size
        
        # double buffer & Camera Block
        self.camera_block_size = buffer_per_camera * self.slot_size

        # Total shared memory size
        self.total_size        = self.control_size + self.meta_size + self.cameras_num * self.camera_block_size

        self.shared_name       = shared_name
        try:
            self.shm           = shared_memory.SharedMemory(name=self.shared_name)
            multiprocessing.resource_tracker.unregister('/' + self.shared_name, 'shared_memory')
        except FileNotFoundError:
            self.logger.error(f"Shared memory {self.shared_name} not found.")
            pass
        
    def build_shared_memory(self):
        """
        Create shared memory block
        """
        try:
            self.shm = shared_memory.SharedMemory(name=self.shared_name, create=True, size=self.total_size)
        except FileExistsError:
            shared_memory.SharedMemory(name=self.shared_name).close()
            shared_memory.SharedMemory(name=self.shared_name).unlink()
            self.shm = shared_memory.SharedMemory(create=True, size=self.total_size, name=self.shared_name)
            self.logger.info("Shared memory already exists. Close the old one and build the new one.")

        atexit.register(shared_memory.SharedMemory(name=self.shared_name).close)
        atexit.register(shared_memory.SharedMemory(name=self.shared_name).unlink)

    def get_control_block_offset(self):
        """
        Calculate the offset of the control block

        Returns:
            offset: int
                control_block的位移量
        """
        return 0
    
    def get_meta_block_offset(self):
        """
        Calculate the offset of the metadata block for a given camera ID

        Returns:
            offset: int
                metadata block的位移量
        """
        return self.control_size

    def get_slot_offset(self, cam_id, slot_idx):
        """
        計算 slot 的位移
        Args:
            cam_id: int 
                camera ID
            slot_idx: int 
                buffer index (0 or 1)
        Returns:
            offset: int n
                slot 的位移量
        """
        return self.control_size + self.meta_size + cam_id * self.camera_block_size + slot_idx * self.slot_size
    
    def read_control_info(self):
        """
        Read control information from the shared memory

        Args:
            cam_id: int 
                camera ID
        Returns:
            slot_idx: int 
                0 or 1 control double buffer
        """
        offset = self.get_control_block_offset()
        slot_idx = int.from_bytes(self.shm.buf[offset:offset+8], byteorder='little', signed=True)
        return slot_idx
    
    def read_meta_info(self):
        """
        Read metadata information from the shared memory

        Args:
            cam_id: int 
                camera ID
        Returns:
            meta_dict: dict
                metadata dictionary
        """
        offset = self.get_meta_block_offset()
        meta_bytes = bytes(self.shm.buf[offset:offset+self.meta_size])
        
        # 去除多餘 \x00
        meta_bytes = meta_bytes.rstrip(b'\x00')
        meta_str = meta_bytes.decode('utf-8', errors='ignore')

        if meta_str:
            try:
                meta_dict = json.loads(meta_str)
            except json.JSONDecodeError:
                start = meta_str.find('{')
                if start != -1:
                    try:
                        meta_dict = json.loads(meta_str[start:])
                    except json.JSONDecodeError:
                        meta_dict = {}
                else:
                    meta_dict = {}
        else:
            meta_dict = {}

        return meta_dict

    def write_control_info(self, slot_idx):
        """
        Write control information to the shared memory

        Args:
            cam_id: int 
                camera ID
            slot_idx: int 
                0 or 1 control double buffer
        """
        offset = self.get_control_block_offset()
        # slot_idx (int64)
        self.shm.buf[offset:offset+8] = slot_idx.to_bytes(8, 'little', signed=True)

    def write_meta_info(self, meta_str):
        """
        Write metadata information to the shared memory

        Args:
            cam_id: int 
                camera ID
            meta_str: str 
                metadata string
        """
        offset = self.get_meta_block_offset()
        meta_bytes = meta_str.encode('utf-8')

        # 寫metadata
        if len(meta_bytes) > self.meta_size:
            meta_bytes = meta_bytes[:self.meta_size]  # 截斷

        self.shm.buf[offset:offset+len(meta_bytes)] = meta_bytes

        # 若不足 self.meta_size，補 0
        remain = self.meta_size - len(meta_bytes)
        if remain > 0:
            self.shm.buf[offset+len(meta_bytes):offset+self.meta_size] = b'\x00' * remain
        
    def read_frame_and_bbox(self, cam_id):
        """
        1) 從 control block 讀出最新的 slot_idx
        2) 複製該 slot 裡的 frame + bbox + reid
        3) 回傳 (frame, meta_dict, frame_counter)

        Args:
            cam_id: int
                camera ID

        Returns:
            frame: np.ndarray
                frame
            bbox: np.ndarray
                bboxes shape=(max_rows, max_cols)
        """
        slot_idx = self.read_control_info()
        slot_offset = self.get_slot_offset(cam_id, slot_idx)

        # 讀取 frame
        np_frame_view = np.ndarray(
            shape=(self.height, self.width, 3),
            dtype=np.uint8,
            buffer=self.shm.buf,
            offset=slot_offset, # 起始位置
            )
        frame = np_frame_view.copy()  # 複製一份，以免被覆蓋

        bbox_offset = slot_offset + self.frame_size
        
        # 讀取 bboxes
        np_bbox_view = np.ndarray(
            shape=(self.max_rows, self.max_cols),
            dtype=np.float32,
            buffer=self.shm.buf,
            offset=bbox_offset, # 起始位置
            )
        
        # 去除全 0 的 bboxes
        bbox = np_bbox_view[~np.all(np_bbox_view == 0, axis=1)]

        # 讀取 ReID
        reid_offset = bbox_offset + self.bboxes_size

        np_reid_view = np.ndarray(
            shape=(self.max_rows, self.feature_dim),
            dtype=np.float32,
            buffer=self.shm.buf,
            offset=reid_offset, # 起始位置
        )

        # 去除全 0 的 ReID
        reid = np_reid_view[~np.all(np_reid_view == 0, axis=1)]

        return frame, bbox, reid
    
    def write_frame_and_bbox(self, cam_id, slot_idx, frame, bbox, reid):
        """
        Write frame and bbox to the shared memory
        1) 計算 slot 的位移量
        2) 寫影像
        3) 寫 bbox

        Args:
            cam_id: int 
                camera ID
            slot_idx: int 
                buffer index (0 or 1)
            frame: np.ndarray
                frame shape=(h, w, 3)
            bbox: np.ndarray
                bboxes shape=(max_rows, max_cols)
            meta_str: str 
                metadata
        """
        slot_offset = self.get_slot_offset(cam_id, slot_idx)

        # 寫影像
        np_frame_view = np.ndarray(
            shape=(self.height, self.width, 3),
            dtype=np.uint8,
            buffer=self.shm.buf,
            offset=slot_offset, # 起始位置
        )
        np_frame_view[:] = frame  # 複製進共享記憶體

        bbox_offset = slot_offset + self.frame_size

        # 寫bbox
        np_bbox_view = np.ndarray(
            shape=(self.max_rows, self.max_cols),
            dtype=np.float32,
            buffer=self.shm.buf,
            offset=bbox_offset, # 起始位置
            )
        
        # 補 0
        np_bbox_view[:] = 0
        rows = min(bbox.shape[0], self.max_rows)
        cols = min(bbox.shape[1], self.max_cols)
        # 寫入
        np_bbox_view[:rows, :cols] = bbox[:rows, :cols]

        # 寫 ReID
        reid_offset = bbox_offset + self.bboxes_size
        
        np_reid_view = np.ndarray(
            shape=(self.max_rows, self.feature_dim),
            dtype=np.float32,
            buffer=self.shm.buf,
            offset=reid_offset, # 起始位置
        )

        # 補 0
        np_reid_view[:] = 0
        reid_rows = min(reid.shape[0], self.max_rows)
        reid_cols = min(reid.shape[1], self.feature_dim)
        # 寫入
        np_reid_view[:reid_rows, :reid_cols] = reid[:reid_rows, :reid_cols]
