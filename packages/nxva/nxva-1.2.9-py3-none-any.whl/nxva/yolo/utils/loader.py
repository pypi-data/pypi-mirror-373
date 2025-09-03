#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom PyTorch Model Serialization/Deserialization Tool

This module provides a custom model loading function that can work with custom pickle modules,
used for loading YOLOv5 and YOLOv11 models, and supports module path mapping.

Main Features:
- Support for custom pickle modules
- Automatic module path mapping handling
- Compatible with YOLOv5 and YOLOv11
- Provides detailed debug information

Usage Example:
    from serialization import custom_load, create_custom_pickle_module
    
    pickle_module = create_custom_pickle_module({"DetectV5": "Detect"})
    model = custom_load('model.pt', pickle_module=pickle_module)
"""

import io, os, glob, yaml, importlib, pickle
from pathlib import Path
from typing import Union


import cv2, torch, numpy as np

class CustomModelLoader:
    def __init__(self, path, model_version='yolov5', task='detect', map_location='cpu'):
        self.path = path
        self.map_location = map_location
        self.loaded_storages = {}
        self.pickle_load_args = {'encoding': 'utf-8'}

        # 自動取得 torch major.minor 版本，例如 '1.10'、'1.13'
        self.torch_verson = self._get_torch_version()

        # 替換模組映射
        self.replace = self._replace_module(model_version, task)

        # 取得 map_location 對應的 restore_location
        self.restore_location = self._get_restore_location(map_location, self.torch_verson)

    # ---------------- private helpers ------------------
    def _replace_module(self, version, task):
        if version == 'yolov5':
            if task == 'pose':
                replace = {'Detect': 'PoseV5', 'Model': 'PoseModel', 'Upsample': 'torch1_10_Upsample'}
            elif task == 'detect':
                replace = {'Detect': 'DetectV5', 'Model': 'DetectionModel', 'Upsample': 'torch1_10_Upsample'}
            elif task == 'segment':
                replace = {'Segment': 'SegmentV5', 'Detect': 'DetectV5'}
            elif task == 'classify':
                replace = {'Classify': 'ClassifyV5'}
            else:
                raise ValueError(f"Unsupported task: {task}")
        elif version in ['yolov5u', 'yolov8', 'yolo11']:
            if task == 'pose':
                replace = {'Pose': 'PoseV11', 'Detect': 'DetectV11'}
            elif task == 'detect':
                replace = {'Detect': 'DetectV11'}
            elif task == 'segment':
                replace = {'Segment': 'SegmentV11', 'Detect': 'DetectV11'}
            elif task == 'classify':
                replace = {'Classify': 'ClassifyV11'}
            else:
                raise ValueError(f"Unsupported task: {task}")
        else:
            raise ValueError(f"Unsupported version: {version}. Supported versions: yolov5, yolov5u, yolov8, yolo11")
        return replace

    def _get_classes_from_module(self, module_path):
        try:
            mod = importlib.import_module(module_path)
            return {cls.__name__: f"{cls.__module__}.{cls.__qualname__}" for cls in mod.__dict__.values() if isinstance(cls, type)}
        except ImportError:
            return {}

    def _open_file(self, name_or_buffer, mode='rb'):
        if isinstance(name_or_buffer, str):
            return open(name_or_buffer, mode)
        else:
            return name_or_buffer

    def _get_torch_version(self):
        full_version = torch.__version__
        return ".".join(full_version.split(".")[:2])

    def _get_restore_location(self, map_location, version='1.10'):
        _string_classes = (str, bytes)  # 這個是之前程式中用的 _string_classes 定義
        default_restore_location = torch.serialization.default_restore_location

        if version in ['1.10', '1.11']:
            if map_location is None:
                restore_location = default_restore_location
            elif isinstance(map_location, dict):
                def restore_location(storage, location):
                    location = map_location.get(location, location)
                    return default_restore_location(storage, location)
            elif isinstance(map_location, _string_classes):
                def restore_location(storage, location):
                    return default_restore_location(storage, map_location)
            elif isinstance(map_location, torch.device):
                def restore_location(storage, location):
                    return default_restore_location(storage, str(map_location))
            else:
                def restore_location(storage, location):
                    result = map_location(storage, location)
                    if result is None:
                        result = default_restore_location(storage, location)
                    return result
        else:
            if map_location is None:
                def restore_location(storage, location):
                    return storage
            elif isinstance(map_location, _string_classes):
                def restore_location(storage, location):
                    from packaging import version  # 必須有這行
                    target = str(map_location)
                    if target.startswith('cuda'):
                        device = torch.device(target)
                        if version.parse(torch.__version__) > version.parse("2.2.0"):
                            device = device.index
                        return storage.cuda(device)
                    return storage.cpu()
            elif isinstance(map_location, torch.device):
                def restore_location(storage, location):
                    if map_location.type == 'cuda':
                        return storage.cuda(map_location)
                    return storage.cpu()
            else:
                def restore_location(storage, location):
                    result = map_location(storage, location)
                    return result if result is not None else storage
        return restore_location

    # ---------------- version-specific tensor loading ----------------
    def _load_tensor_1_13(self, dtype, numel, key, location, opened_zipfile):
        name = f'data/{key}'
        storage = opened_zipfile.get_storage_from_record(name, numel, torch.UntypedStorage).storage().untyped()
        self.loaded_storages[key] = torch.storage.TypedStorage(
            wrap_storage=self.restore_location(storage, location),
            dtype=dtype
        )

    def _persistent_load_1_13(self, saved_id, opened_zipfile):
        assert isinstance(saved_id, tuple)
        typename = saved_id[0].decode('ascii') if isinstance(saved_id[0], bytes) else saved_id[0]
        storage_type, key, location, numel = saved_id[1:]

        dtype = torch.uint8 if storage_type is torch.UntypedStorage else storage_type.dtype
        if key not in self.loaded_storages:
            location = location.decode('ascii') if isinstance(location, bytes) else location
            nbytes = numel * torch._utils._element_size(dtype)
            self._load_tensor_1_13(dtype, nbytes, key, location, opened_zipfile)
        return self.loaded_storages[key]

    def _load_tensor_1_10(self, data_type, size, key, location, opened_zipfile):
        name = f'data/{key}'
        dtype = data_type(0).dtype
        storage = opened_zipfile.get_storage_from_record(name, size, dtype).storage()
        self.loaded_storages[key] = self.restore_location(storage, location)

    def _persistent_load_1_10(self, saved_id, opened_zipfile):
        assert isinstance(saved_id, tuple)
        typename = saved_id[0].decode('ascii') if isinstance(saved_id[0], bytes) else saved_id[0]
        data_type, key, location, size = saved_id[1:]
        if key not in self.loaded_storages:
            location = location.decode('ascii') if isinstance(location, bytes) else location
            self._load_tensor_1_10(data_type, size, key, location, opened_zipfile)
        return self.loaded_storages[key]

    # ---------------- main load method ------------------
    def load(self):
        with self._open_file(self.path, 'rb') as opened_file:
            opened_zipfile = torch._C.PyTorchFileReader(opened_file)
            modules_dict = {}
            modules_dict.update(self._get_classes_from_module("nxva.yolo.nn.modules"))
            modules_dict.update(self._get_classes_from_module("nxva.yolo.nn.models"))
            for k, v in self.replace.items():
                if v in modules_dict:
                    modules_dict[k] = modules_dict[v]

            class UnpicklerWrapper(pickle.Unpickler):
                def find_class(inner_self, mod_name, name):
                    if name in modules_dict:
                        target = modules_dict[name]
                        mod_name_new = '.'.join(target.split('.')[:-1])
                        name_new = target.split('.')[-1]
                        try:
                            return super(UnpicklerWrapper, inner_self).find_class(mod_name_new, name_new)
                        except Exception:
                            pass
                    return super(UnpicklerWrapper, inner_self).find_class(mod_name, name)

            if self.torch_verson in ['1.10', '1.11']:
                persistent_loader = lambda sid: self._persistent_load_1_10(sid, opened_zipfile)
            else:
                persistent_loader = lambda sid: self._persistent_load_1_13(sid, opened_zipfile)

            data_file = io.BytesIO(opened_zipfile.get_record('data.pkl'))
            unpickler = UnpicklerWrapper(data_file, **self.pickle_load_args) if self.torch_verson == '1.13' else UnpicklerWrapper(data_file)
            unpickler.persistent_load = persistent_loader

            ckpt = unpickler.load()
            torch._utils._validate_loaded_sparse_tensors()
            return ckpt


IMG_FORMATS = ("bmp", "dng", "jpeg", "jpg", "mpo", "png", "tif", "tiff", "webp", "pfm")  # 支援的圖片格式

class LoadImages:
    """只讀取圖片（支援 .txt 檔案或 list 路徑，不支援影片）"""

    def __init__(self, path):
        self.input_type = None
        self.numpy_images = None

        # 如果是 .txt 檔案
        if isinstance(path, str) and Path(path).suffix == ".txt":
            if not os.path.isfile(path):
                raise FileNotFoundError(f"檔案不存在: {path}")
            
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

            if not lines:
                raise ValueError(f"{path} 中沒有有效的路徑")

            self.input_type = "string_list"
            self.files = [p for p in lines if p.split(".")[-1].lower() in IMG_FORMATS]

        # 如果是 list
        elif isinstance(path, list):
            if len(path) == 0:
                raise ValueError("輸入 list 不可為空")

            first_element = path[0]
            if isinstance(first_element, str):
                self.input_type = "string_list"
                self.files = [p for p in path if p.split(".")[-1].lower() in IMG_FORMATS]

            elif isinstance(first_element, np.ndarray):
                self.input_type = "numpy_list"
                self.numpy_images = path
                self.files = [f"numpy_array_{i}" for i in range(len(path))]

            else:
                raise ValueError(f"不支援的 list 元素型別: {type(first_element)}")

        # 其他情況，當成單一路徑或目錄
        else:
            files = []
            for p in sorted(path) if isinstance(path, (list, tuple)) else [path]:
                p = str(Path(p).resolve())
                if "*" in p:
                    files.extend(sorted(glob.glob(p, recursive=True)))  # glob
                elif os.path.isdir(p):
                    files.extend(sorted(glob.glob(os.path.join(p, "*.*"))))  # 資料夾
                elif os.path.isfile(p):
                    files.append(p)  # 檔案
                else:
                    raise FileNotFoundError(f"{p} 不存在")

            self.files = [x for x in files if x.split(".")[-1].lower() in IMG_FORMATS]

        if not self.files and self.numpy_images is None:
            raise ValueError(f"沒有符合的圖片，支援格式: {IMG_FORMATS}")

        self.nf = len(self.files) if self.numpy_images is None else len(self.numpy_images)
        self.count = 0
        print(f"讀取到 {self.nf} 張圖片")

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        if self.count >= self.nf:
            raise StopIteration

        # numpy list
        if self.input_type == "numpy_list":
            im0 = self.numpy_images[self.count]
            self.count += 1
            return im0

        # string list / 單一路徑
        path = self.files[self.count]
        im0 = cv2.imread(path)
        if im0 is None:
            raise ValueError(f"無法讀取圖片: {path}")
        self.count += 1
        return im0

    def get_all_images(self):
        """一次回傳所有圖片 (list of np.ndarray)"""
        if self.input_type == "numpy_list":
            return self.numpy_images

        all_images = []
        for path in self.files:
            img = cv2.imread(path)
            if img is not None:
                all_images.append(img)
            else:
                print(f"⚠️ 無法讀取圖片: {path}")
        return all_images

    def __len__(self):
        return self.nf

def load_config(config: Union[str]) -> dict:
    """載入配置"""
    if isinstance(config, str) and config.endswith(('yaml', 'yml')):
        try:
            with open(config, 'r') as f:
                setting = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Error loading config: {e}")
    
    # 特殊處理：將 kpt_shape 從列表轉換為 tuple
    if 'kpt_shape' in setting and isinstance(setting['kpt_shape'], list):
        setting['kpt_shape'] = tuple(setting['kpt_shape'])
    return setting