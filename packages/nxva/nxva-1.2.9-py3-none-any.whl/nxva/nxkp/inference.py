import time, math
from collections import deque
from dataclasses import dataclass
from typing import Tuple, Dict, Iterable, Deque, Optional

import kp
import numpy as np

from .device import KneronDevice
from .decode_head import decode_yolo_head


class InferenceError(RuntimeError):
    """Raised when any step of the inference pipeline fails."""


@dataclass
class ModelMeta:
    """
    Metadata for a model loaded from NEF.
    Attributes:
        model_id: Unique identifier for the model.
        c: Number of channels in the input tensor.
        h: Height of the input tensor.
        w: Width of the input tensor.
        radix: Radix used for quantization.
        scale: Scale factor used for quantization.
    """
    model_id: int
    c: int
    h: int
    w: int
    radix: int
    scale: float


class InferenceSession:
    """
    Hight-level wrapper that completes a **single‑model** inference workflow on a Kneron USB dongle.
    The class encapsulates the boilerplate steps shown in *plus_python* docs:

    1. Connect to the device and (if necessary) load firmware
    2. Load NEF model
    3. Rearrange layout (4W4C8B) and quantize with radix/scale
    4. Call *generic_data_inference_send / receive*

    Attributes:
        dev: KneronDevice instance, must be connected before use.
        max_inflight: Maximum number of inflight inference requests.
        _model_desc: Loaded model descriptor, if any.
        _models: Dictionary mapping model IDs to ModelMeta instances.
        _inflight: Current number of inflight requests.
        _send_ts: Timestamps of sent requests, used for latency measurement.
        _seq_queue: Sequence numbers of sent requests, used for matching responses.
        _seq_counter: Monotonic sequence number for requests, wraps around at 2^31.
        _model_queue: Queue to match which model the output belongs to.
        _shape_queue: Queue to match original image shape for post-processing.
    """

    #: KL520 / KL720 both support 4W4C8B
    _INPUT_LAYOUT = kp.ModelTensorDataLayout.KP_MODEL_TENSOR_DATA_LAYOUT_4W4C8B
    _WIDTH_ALIGN_BASE = 16
    _CHANNEL_ALIGN_BASE = 4

    def __init__(
        self,
        device: KneronDevice,
        nef_path: str,
        version = 'yolo11',
        task = 'detect',
        max_inflight: int = 2,
    ) -> None:
        self.dev = device
        # self.decode_head = decode_yolo_head
        self.version = version
        self.task = task

        # check the device is connected
        if self.dev.device_group is None:
            self.dev.connect()

        # load model
        if nef_path is not None:
            # self._model_desc = kp.core.load_model_from_file(self.dev.device_group, str(nef_path))
            self.dev.load_model_from_file(str(nef_path))
            self._model_desc = self.dev.model_nef_descriptor
        # else:
        #     # assume already loaded by caller
        #     infos = kp.core.get_system_info(self.dev.device_group)
        #     if not infos or infos[0].number_of_models == 0:
        #         raise InferenceError("No model loaded and nef_path not given")
        #     self._model_desc = None  # we don't actually need it later

        # ------------ collect meta of every model ------------
        self._models: Dict[int, ModelMeta] = {}
        for m in self._model_desc.models:
            node = m.input_nodes[0]
            if node.data_layout != self._INPUT_LAYOUT:
                raise InferenceError(f"Model {m.id} layout {node.data_layout} not 4W4C8B")
            qp = node.quantization_parameters.v1.quantized_fixed_point_descriptor_list[0]
            c, h, w = node.tensor_shape_info.v1.shape_npu[1:]
            self._models[m.id] = ModelMeta(
                model_id=m.id,
                c=c,
                h=h,
                w=w,
                radix=qp.radix,
                scale=qp.scale.value,
            )

        if not self._models:
            raise InferenceError("No model found in NEF")
        
        self.default_model_id = next(iter(self._models))

        # pipeline control
        self.max_inflight = max(max_inflight, 1)
        self._inflight: int = 0     # the number of images sent but not yet received
        self._seq_counter: int = 0  # monotonic inference_number
        self._seq_queue: Deque[int] = deque()
        self._send_ts: Deque[float] = deque()
        self._model_queue: Deque[int] = deque()  # to match which model the output belongs to
        self._shape_queue: Deque[Tuple[int, int]] = deque()  # to match original image shape


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _prepare_npu_buffer(self, float_chw: np.ndarray, meta:ModelMeta) -> bytes:
        """
        quantize → 4W4C8B re‑layout → bytes to NPU
        float_chw: (C, H, W) float32 0‑1
        """
        # 1. quantize (radix, scale)
        data = float_chw * (2 ** meta.radix * meta.scale)
        data = np.clip(np.round(data), -128, 127).astype(np.int8)

        # 2. CHW -> HWC
        data = data.transpose(1, 2, 0)  # (H,W,C)

        # 3. 4W4C8B relayout (KL520/KL720 hardware requirement)
        width_align = self._WIDTH_ALIGN_BASE * math.ceil(meta.w / self._WIDTH_ALIGN_BASE)
        ch_block_num = math.ceil(meta.c / self._CHANNEL_ALIGN_BASE)

        re_layout = np.zeros(
            (
                meta.h,
                ch_block_num,
                width_align,
                self._CHANNEL_ALIGN_BASE,
            ),
            dtype=np.int8,
        )

        ch_offset = 0
        for b in range(ch_block_num):
            end = min(ch_offset + self._CHANNEL_ALIGN_BASE, meta.c)
            re_layout[:meta.h, b, :meta.w, :(end - ch_offset)] = data[:, :, ch_offset:end]
            ch_offset += self._CHANNEL_ALIGN_BASE

        return re_layout.tobytes()
    
    def _send_to_npu(self, npu_buffer: bytes, model_id: int) -> None:
        """
        Send a single image to the NPU for inference.
        npu_buffer: image data processed by _prepare_npu_buffer()
        """
        seq = self._seq_counter
        self._seq_counter = (self._seq_counter + 1) & 0x7FFF_FFFF  # wrap around
        desc = kp.GenericDataInferenceDescriptor(
            model_id=model_id,
            inference_number=seq,
            input_node_data_list=[kp.GenericInputNodeData(buffer=npu_buffer)],
        )

        try:
            kp.inference.generic_data_inference_send(
                device_group=self.dev.device_group, 
                generic_inference_input_descriptor=desc
            )
        except kp.ApiKPException as e:
            print(f"Error during inference: {e}")

        self._inflight += 1
        self._send_ts.append(time.time())
        self._seq_queue.append(seq)
        self._model_queue.append(model_id)

    def _recv_from_npu(self):
        try:
            raw = kp.inference.generic_data_inference_receive(
                device_group=self.dev.device_group
            )
        except kp.ApiKPException as e:
            print(f"Error during inference: {e}")

        latency = time.time() - self._send_ts.popleft()
        expected_seq = self._seq_queue.popleft()
        model_id = self._model_queue.popleft()
        orig_shape = self._shape_queue.popleft()

        if raw.header.inference_number != expected_seq:
            raise InferenceError(
                f"inference_number mismatch (expect {expected_seq} got {raw.header.inference_number})"
            )
        
        outputs = [
            kp.inference.generic_inference_retrieve_float_node(
                node_idx=idx,
                generic_raw_result=raw,
                channels_ordering=kp.ChannelOrdering.KP_CHANNEL_ORDERING_CHW,
            ).ndarray
            for idx in range(raw.header.num_output_node)
        ]
        self._inflight -= 1
        return model_id, outputs, latency, orig_shape

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def send(self, image: np.ndarray, model_id: Optional[int] = None):
        """
        Asynchronously send a single image for inference.
        Receive one when inflight queue is full.
        """
        model_id = model_id or self.default_model_id
        if model_id not in self._models:
            raise InferenceError(f"model_id {model_id} not in NEF")
        meta = self._models[model_id]
        npu_buf = self._prepare_npu_buffer(image, meta)
        if self._inflight >= self.max_inflight:
            self.recv()
        self._shape_queue.append(image.shape[:2])  # store original shape for postprocessing
        self._send_to_npu(npu_buf, model_id)

    def recv(self, block: bool = True):
        """
        Asynchronously receive inference result.

        Args:
            block: 
                If True, will block until a result is available.
                If False and no result is available, will return None.
        """
        if self._inflight == 0:
            if block:
                raise InferenceError("recv() called with empty inflight queue")
            return None
        model_id, outputs, _, orig_shape = self._recv_from_npu()
        return outputs
    
    def infer(self, image: np.ndarray, model_id: Optional[int] = None):
        """Synchronized inference for a single image."""
        meta = self._models[model_id]
        self.send(image, model_id)
        return self.recv()
        
    def stream(self, images: Iterable[np.ndarray], model_id: Optional[int] = None):
        """Generator that yields inference results for a stream of images."""
        for img in images:
            self.send(img, model_id)
            # receive one result if inflight queue is full
            if self._inflight >= self.max_inflight:
                yield self.recv()
        # receive remaining results
        while self._inflight:
            yield self.recv()

    # ------------------------------------------------------------------
    # Context manager sugar: ensure proper cleanup
    # ------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # Cleanup to avoid resource leaks
        while self._inflight:
            try:
                self.recv()
            except Exception:
                break