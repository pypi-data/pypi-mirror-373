import pycuda.autoinit
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda

class TRTInference:
    def __init__(self, engine_path, input_shape):
        """
        初始化 TRTWrapper，載入 TensorRT Engine，並準備執行所需的 CUDA 資源與記憶體配置。

        Args:
            engine_path (str): 
                TensorRT engine 檔案的路徑（例如 'model.engine'）。
            input_shape (List[Tuple[int]]): 
                模型每個輸入的 shape 組成的列表，例如 [(1, 3, 640, 640)]。
                對於多輸入模型，這裡需要列出每個 input tensor 的 shape。
        """
        # 建立 TRT 的 logger，方便除錯
        self.TRT_LOGGER = trt.Logger()

        # 開啟 .engine檔案，並載入成 TRT runtime 的 engine
        with open(engine_path, "rb") as f:
            runtime = trt.Runtime(self.TRT_LOGGER)
            self.engine = runtime.deserialize_cuda_engine(f.read())

        # 建立執行 context，用來之後執行推論
        self.context = self.engine.create_execution_context()
        
        # 取得當前的 CUDA context(PyCUDA 管理用)
        self.cuda_context = cuda.Context.get_current()

        # 檢查 input_shape 是 list 且每個元素是 tuple（代表每個輸入的 shape）
        assert isinstance(input_shape, list), "input_shape should be list, e.g. [(B, C, H, W)]"
        assert all(isinstance(shape, tuple) for shape in input_shape), "input_shape should be list[tuple], e.g. [(B, C, H, W)]"
        self.input_shapes = input_shape

        self._bufs = {}        # name -> DeviceAllocation
        self._buf_bytes = {}   # name -> currently allocated size (bytes)

        # 把 engine 的所有 tensor（輸入和輸出）的名稱抓出來
        self.input_names = []
        self.output_names = []
        self.d_inputs = []
        self.d_outputs = []     # 儲存 GPU 記憶體位址
        self.output_shapes = [] # 儲存對應的 shape
        self.input_dtypes = []
        self.output_dtypes = []

        major_version, minor_version, *_ = map(int, trt.__version__.split('.'))
        self.check_version = (major_version, minor_version) >= (8, 5)
        if self.check_version:

            for idx in range(self.engine.num_io_tensors):

                name = self.engine.get_tensor_name(idx)
                mode = self.engine.get_tensor_mode(name)
                if mode == trt.TensorIOMode.INPUT:
                    self.input_dtypes.append(self.engine.get_tensor_dtype(name)) # 得到input_type
                    self.input_names.append(name)
                elif mode == trt.TensorIOMode.OUTPUT:
                    self.output_dtypes.append(self.engine.get_tensor_dtype(name)) # 得到output_type
                    self.output_names.append(name)

            # 檢查是否為 dynamic shape，只要輸入 tensor 的 shape 裡有 -1 就算是
            self.is_dynamic = any(-1 in self.engine.get_tensor_shape(name) for name in self.input_names)

            if not self.is_dynamic:

                # 根據輸入 shape 分配 GPU 記憶體空間
                for shape, dtype in zip(self.input_shapes, self.input_dtypes):  # input_shape 應為 List[Tuple]

                    if dtype == trt.DataType.HALF:
                        np_dtype = np.float16
                    elif dtype == trt.DataType.FLOAT:
                        np_dtype = np.float32
                    else:
                        raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                    self.d_inputs.append(cuda.mem_alloc(int(np.prod(shape)) * np.dtype(np_dtype).itemsize))

                # 綁定所有 output
                for name, dtype in zip(self.output_names, self.output_dtypes):  # 遍歷所有 tensors

                    if dtype == trt.DataType.HALF:
                        np_dtype = np.float16
                    elif dtype == trt.DataType.FLOAT:
                        np_dtype = np.float32
                    else:
                        raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                    shape = self.engine.get_tensor_shape(name) # 取得 shape
                    self.output_shapes.append(shape) # 加入對應 shape
                    self.d_outputs.append(cuda.mem_alloc(int(np.prod(shape)) * np.dtype(np_dtype).itemsize)) # 分配對應大小的記憶體

        else:
            self.input_bindings = []
            self.output_bindings = []

            for i in range(self.engine.num_bindings):
                name = self.engine.get_binding_name(i)
                if self.engine.binding_is_input(i):
                    self.input_dtypes.append(self.engine.get_binding_dtype(i)) # 得到input_type
                    self.input_bindings.append(i)
                    self.input_names.append(name)
                else:
                    self.output_dtypes.append(self.engine.get_binding_dtype(i)) # 得到output_type
                    self.output_bindings.append(i)
                    self.output_names.append(name)

            self.is_dynamic = any(-1 in self.engine.get_binding_shape(i) for i in self.input_bindings)
            
            if not self.is_dynamic:
                for shape, dtype in zip(self.input_shapes, self.input_dtypes):

                    if dtype == trt.DataType.HALF:
                        np_dtype = np.float16
                    elif dtype == trt.DataType.FLOAT:
                        np_dtype = np.float32
                    else:
                        raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                    self.d_inputs.append(cuda.mem_alloc(int(np.prod(shape)) * np.dtype(np_dtype).itemsize))
                for i, dtype in zip(self.output_bindings, self.output_dtypes):

                    if dtype == trt.DataType.HALF:
                        np_dtype = np.float16
                    elif dtype == trt.DataType.FLOAT:
                        np_dtype = np.float32
                    else:
                        raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")
                    
                    shape = self.engine.get_binding_shape(i)
                    self.output_shapes.append(shape)
                    self.d_outputs.append(cuda.mem_alloc(int(np.prod(shape)) * np.dtype(np_dtype).itemsize))

    def infer(self, input_array):
        """
        使用 TensorRT Engine 進行推論，根據是否為 dynamic shape 自動處理記憶體與 shape 設定。

        Args:
            input_array (List[np.ndarray]): 
                一個或多個輸入 tensor 的 numpy 陣列，需與初始化時給定的 input shape 對應，
                且格式為 float32。每個陣列 shape 應為 (B, C, H, W)。

        Returns:
            List[np.ndarray]: 
                模型的推論輸出，每個輸出為一個 numpy 陣列（如多頭輸出則為多個）。
        """
        # 進入 CUDA context，確保推論過程中使用正確的 context
        self.cuda_context.push()
        try:
            # 確保傳入的輸入資料是 list of numpy arrays
            assert isinstance(input_array, list), "input_array should be list, e.g. [(B, C, H, W)]"
            assert all(isinstance(arr, np.ndarray) for arr in input_array), "input_array should be list[np.ndarray]"
            
            # 初始化 bindings 陣列，TensorRT 會根據這個對應 input/output 記憶體位址
            # if self.check_version:
            #     bindings = [None] * self.engine.num_io_tensors
            # else:
            #     bindings = [None] * self.engine.num_bindings

            bindings = [0] * self.engine.num_bindings

            if self.is_dynamic:
                # 設定 input shape 並分配記憶體
                d_inputs = []
                d_outputs = []
                output_shapes = []
                
                if self.check_version:
                    
                    for name, arr, dtype in zip(self.input_names, input_array, self.input_dtypes):
                        bidx = self.engine.get_binding_index(name)

                        if dtype == trt.DataType.HALF:
                            np_dtype = np.float16
                        elif dtype == trt.DataType.FLOAT:
                            np_dtype = np.float32
                        else:
                            raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                        if arr.ndim == 3:
                            arr = np.expand_dims(arr, axis=0)  # (C,H,W) -> (1,C,H,W)

                        arr = arr.astype(np_dtype)
                        self.context.set_input_shape(name, arr.shape) # 設定實際的輸入 shape
                        arr = np.ascontiguousarray(arr) # 確保 float32 且記憶體連續

                        d_input = self._get_buf(name, arr.nbytes) # 先檢查input是否有更大記憶體需要配置

                        # d_input = cuda.mem_alloc(arr.nbytes) # 為這筆 input 分配 GPU 記憶體
                        cuda.memcpy_htod(d_input, arr) # 傳資料到 GPU
                        d_inputs.append(d_input)

                        bindings[bidx] = int(d_input)

                    # # 綁定 input 到正確的 index
                    # for name, d_input in zip(self.input_names, d_inputs):
                    #     for idx in range(self.engine.num_io_tensors):
                    #         if self.engine.get_tensor_name(idx) == name:
                    #             bindings[idx] = int(d_input)
                    #             break

                    # 根據實際 output shape 分配記憶體
                    for name, dtype in zip(self.output_names, self.output_dtypes):
                        bidx = self.engine.get_binding_index(name)

                        shape = self.context.get_tensor_shape(name)
                        output_shapes.append(shape)

                        if dtype == trt.DataType.HALF:
                            np_dtype = np.float16
                        elif dtype == trt.DataType.FLOAT:
                            np_dtype = np.float32
                        else:
                            raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                        nbytes = int(np.prod(shape)) * np.dtype(np_dtype).itemsize
                        d_output = self._get_buf(name, nbytes) # 先檢查output是否有更大記憶體需要配置

                        # d_output = cuda.mem_alloc(int(np.prod(shape)) * np.dtype(np_dtype).itemsize)  # float32: 4 bytes
                        d_outputs.append(d_output)

                        bindings[bidx] = int(d_output)

                    # # 綁定所有 output tensor 到對應的位置
                    # for name, d_output in zip(self.output_names, d_outputs):
                    #     for idx in range(self.engine.num_io_tensors):
                    #         if self.engine.get_tensor_name(idx) == name:
                    #             bindings[idx] = int(d_output)
                    #             break

                else:
                    for name, arr, i, dtype in zip(self.input_names, input_array, self.input_bindings, self.input_dtypes):

                        if dtype == trt.DataType.HALF:
                            np_dtype = np.float16
                        elif dtype == trt.DataType.FLOAT:
                            np_dtype = np.float32
                        else:
                            raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                        if arr.ndim == 3:
                            arr = np.expand_dims(arr, axis=0)  # (C,H,W) -> (1,C,H,W)

                        arr = arr.astype(np_dtype)
                        self.context.set_binding_shape(i, arr.shape) # 設定實際的輸入 shape
                        arr = np.ascontiguousarray(arr) # 確保 float32 且記憶體連續

                        d_input = self._get_buf(name, arr.nbytes)

                        # d_input = cuda.mem_alloc(arr.nbytes) # 為這筆 input 分配 GPU 記憶體
                        cuda.memcpy_htod(d_input, arr) # 傳資料到 GPU
                        d_inputs.append(d_input)
                        bindings[i] = int(d_input)

                    for name, i, dtype in zip(self.output_names, self.output_bindings, self.output_dtypes):
                        shape = self.context.get_binding_shape(i)
                        output_shapes.append(shape)

                        if dtype == trt.DataType.HALF:
                            np_dtype = np.float16
                        elif dtype == trt.DataType.FLOAT:
                            np_dtype = np.float32
                        else:
                            raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                        #d_output = cuda.mem_alloc(int(np.prod(shape)) * np.dtype(np_dtype).itemsize)

                        nbytes = int(np.prod(shape)) * np.dtype(np_dtype).itemsize
                        d_output = self._get_buf(name, nbytes)

                        d_outputs.append(d_output)
                        bindings[i] = d_output

                # 執行推論
                self.context.execute_v2(bindings)

                # 從 GPU 拷貝回 CPU
                output_arrays = []
                for shape, d_out, dtype in zip(output_shapes, d_outputs, self.output_dtypes):

                    if dtype == trt.DataType.HALF:
                        np_dtype = np.float16
                    elif dtype == trt.DataType.FLOAT:
                        np_dtype = np.float32
                    else:
                        raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                    out_array = np.empty(shape, dtype=np_dtype)
                    cuda.memcpy_dtoh(out_array, d_out)
                    output_arrays.append(out_array)
            
            else:

                if self.check_version:
                    # 設定 input shape
                    for name, arr in zip(self.input_names, input_array):
                        self.context.set_input_shape(name, arr.shape)
                    
                    for arr, d_input, shape, dtype in zip(input_array, self.d_inputs, self.input_shapes, self.input_dtypes):
                        if dtype == trt.DataType.HALF:
                            np_dtype = np.float16
                        elif dtype == trt.DataType.FLOAT:
                            np_dtype = np.float32
                        else:
                            raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                        if arr.ndim == 3:
                            arr = np.expand_dims(arr, axis=0)  # (C,H,W) -> (1,C,H,W)

                        arr = arr.astype(np_dtype)
                        arr = np.ascontiguousarray(arr)
                        cuda.memcpy_htod(d_input, arr)

                    # 綁定
                    for name, d_input in zip(self.input_names, self.d_inputs):
                        bidx = self.engine.get_binding_index(name)
                        bindings[bidx] = int(d_input)
                    for name, d_output in zip(self.output_names, self.d_outputs):
                        bidx = self.engine.get_binding_index(name)
                        bindings[bidx] = int(d_output)

                    # # 綁定 input 到正確的 index
                    # for name, d_input in zip(self.input_names, self.d_inputs):
                    #     for idx in range(self.engine.num_io_tensors):
                    #         if self.engine.get_tensor_name(idx) == name:
                    #             bindings[idx] = int(d_input)
                    #             break

                    # # 綁定所有 output tensor 到對應的位置
                    # for out_name, d_out in zip(self.output_names, self.d_outputs):
                    #     idx = None
                    #     for i in range(self.engine.num_io_tensors):
                    #         if self.engine.get_tensor_name(i) == out_name:
                    #             idx = i
                    #             break
                    #     assert idx is not None # 確保找到對應位置

                    #     bindings[idx] = int(d_out) # 將輸出記憶體綁定

                else:
                    for arr, d_input, i, dtype in zip(input_array, self.d_inputs, self.input_bindings, self.input_dtypes):
                        if dtype == trt.DataType.HALF:
                            np_dtype = np.float16
                        elif dtype == trt.DataType.FLOAT:
                            np_dtype = np.float32
                        else:
                            raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                        if arr.ndim == 3:
                            arr = np.expand_dims(arr, axis=0)  # (C,H,W) -> (1,C,H,W)

                        arr = arr.astype(np_dtype)
                        arr = np.ascontiguousarray(arr)

                        ok = self.context.set_binding_shape(i, arr.shape) # ← 關鍵

                        cuda.memcpy_htod(d_input, arr)
                        bindings[i] = int(d_input)

                    for d_output, i in zip(self.d_outputs, self.output_bindings):
                        bindings[i] = int(d_output)

                # 推論
                self.context.execute_v2(bindings)

                # 把輸出從 GPU 拷貝回 CPU（轉成 numpy 陣列）
                output_arrays = []
                for shape, d_out, dtype in zip(self.output_shapes, self.d_outputs, self.output_dtypes):
                    if dtype == trt.DataType.HALF:
                        np_dtype = np.float16
                    elif dtype == trt.DataType.FLOAT:
                        np_dtype = np.float32
                    else:
                        raise TypeError(f"Unsupported input dtype: {dtype}, only support float16 or float32")

                    out_array = np.empty(shape, dtype=np_dtype)
                    cuda.memcpy_dtoh(out_array, d_out) # GPU → CPU
                    output_arrays.append(out_array)

            return output_arrays

        finally:
            # pop 掉 CUDA context
            self.cuda_context.pop()

    def _get_buf(self, name, nbytes):
        cur = self._buf_bytes.get(name, 0)
        if cur < nbytes:
            # 釋放舊的，避免靠 GC 延後釋放造成峰值
            old = self._bufs.get(name)
            if old is not None:
                try:
                    old.free()
                except Exception:
                    pass
            self._bufs[name] = cuda.mem_alloc(nbytes)
            self._buf_bytes[name] = nbytes
        return self._bufs[name]