import torch.nn as nn
import torch
import cv2
import numpy as np
import torchvision.transforms as T
import onnxruntime as ort
from .models import build_model
from .reid_model_factory import load_pretrained_weights
from ..nxtrt import TRTInference

class ReIDDetectMultiBackend(nn.Module):
    # ReID models MultiBackend class for python inference on various backends
    def __init__(self, weights='osnet_x0_25_msmt17.pt', device=torch.device('cpu'), fp16=False, pretrained=True):
        super().__init__()
        self.model_name = (weights.split('/')[-1]).split('.')[0]
        model_type = (weights.split('/')[-1]).split('.')[-1]

        self.pt = False
        self.pth = False
        self.onnx = False
        self.engine = False
        # 根據model_type
        if model_type == 'pt':
            self.pt = True
        elif model_type == 'pth':
            self.pth = True
        elif model_type == 'onnx':
            self.onnx = True
        elif model_type == 'engine':
            self.engine = True
        else:
            pass
        # a = basename(w) #擷取weights 名稱
        self.fp16 = fp16

        # Build transform functions
        self.device = torch.device(device)

        # Build model
        if model_type in ['pt', 'pth']:
            self.model = build_model(
                self.model_name,
                num_classes=1,
                # pretrained=not (w and w.is_file()),
                pretrained=not(weights),
                use_gpu=device
            )
            load_pretrained_weights(self.model,weights)

            self.model.to(device).eval()
            self.model.half() if self.fp16 else  self.model.float()

        elif model_type == 'onnx':
            providers = ['CUDAExecutionProvider' if self.device.type == 'cuda' else 'CPUExecutionProvider']
            self.session = ort.InferenceSession(weights, providers=providers)

            # 取得 ONNX 輸入的名稱
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name

            print(f'Successfully loaded ONNX model from {weights}')

        elif model_type == 'engine':
            if "ir" in self.model_name:
                input_shape = [(1,3,112,112)]

            elif "osnet" in self.model_name:
                input_shape = [(1,3,256,128)]

            self.model = TRTInference(weights, input_shape=input_shape)
            print(f'Successfully loaded engine model from {weights}')

    def _preprocess(self, imgs):
        if isinstance(imgs, np.ndarray):
            imgs = [imgs]

        processed_imgs = []
        for img in imgs:
            # OpenCV 預設 BGR → 轉為 RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Resize 根據模式選擇
            if "osnet" in self.model_name:
                img = cv2.resize(img, (128, 256), interpolation=cv2.INTER_AREA)
                transform = T.Compose([
                    T.ToTensor(),
                    T.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
                ])
            elif "ir" in self.model_name:
                img = cv2.resize(img, (112, 112), interpolation=cv2.INTER_AREA)
                transform = T.Compose([
                    T.ToTensor(),
                    T.Normalize(mean=[0.5, 0.5, 0.5],
                                std=[0.5, 0.5, 0.5])
                ])
            else:
                raise ValueError(f"Unknown preprocess in {self.model_name}")

            img = transform(img).to(self.device)
            processed_imgs.append(img)

        return torch.stack(processed_imgs).to(self.device)
    
    def forward(self, im_batch):
        # preprocess batch
        im_batch = self._preprocess(im_batch)

        # batch to half
        if self.fp16 and im_batch.dtype != torch.float16:
           im_batch = im_batch.half()

        # batch processing
        features = []
        if self.pt:
            features = self.model(im_batch)
        elif self.pth:
            features = self.model(im_batch)
        elif self.onnx:  # ONNX Runtime
            im_batch = im_batch.cpu().numpy()  # torch to numpy
            features = self.session.run([self.output_name], {self.input_name: im_batch})[0]
        elif self.engine:  # TensorRT
            if isinstance(im_batch, torch.Tensor):
                im_batch = im_batch.detach().cpu().numpy()
            features = self.model.infer([im_batch])

        if isinstance(features, (list, tuple)):
            return self.from_numpy(features[0]) if len(features) == 1 else [self.from_numpy(x) for x in features]
        else:
            return self.from_numpy(features)

    def from_numpy(self, x):
        return torch.from_numpy(x).to(self.device) if isinstance(x, np.ndarray) else x

    def warmup(self):
        if not any([self.pt, self.pth, self.onnx, self.engine]):
            return
        if self.device.type == 'cpu':
            return

        # 根據模型類型與是否為 TensorRT engine，決定 shape
        shape_map = {
            "ir":     ((1, 3, 112, 112), (112, 112, 3)),
            "osnet":  ((1, 3, 256, 128), (256, 128, 3)),
        }

        for key, (engine_shape, default_shape) in shape_map.items():
            if key in self.model_name:
                shape = engine_shape if self.engine else default_shape
                break
                
            else:
                raise ValueError(f"Unknown model name: {self.model_name}")

        # 建立假資料並執行 warmup
        dummy_input = np.empty(shape, dtype=np.uint8)

        self.forward(dummy_input)
        print('Warm Up Successfully')