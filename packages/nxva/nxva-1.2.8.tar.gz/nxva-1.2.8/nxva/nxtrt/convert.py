import torch
import tensorrt as trt
import os
import onnx
import onnxslim
from .calibrator import Calibrator

class Convert:
    """將pytorch模型轉成trt"""

    @staticmethod
    def torch_to_onnx(model, input_shape, onnx_output_path='model.onnx', input_names=["images"], output_names=["output0"], slim=True, opset_version=14, dynamic=False, dtype=torch.float32):
        """  
        將 PyTorch 模型轉換為 ONNX 格式，支援靜態或動態輸入大小，並可進行簡化（slim）處理。     
        Args:
            model (torch.nn.Module): 
                要轉換的 PyTorch 模型。
            input_shape (tuple): 
                模型輸入的大小，例如 (1, 3, 640, 640)。
            onnx_output_path (str, optional): 
                輸出的 ONNX 檔名，預設為 'model.onnx'。
            input_names (list of str, optional): 
                ONNX 輸入節點的名稱，預設為 ["images"]。
            output_names (list of str, optional): 
                ONNX 輸出節點的名稱，預設為 ["output0"]。
            opset_version (int, optional): 
                ONNX opset 版本，預設為 14。
            dynamic (bool, optional): 
                是否啟用動態輸入（支援不同尺寸圖片），預設為 False。
            dtype (torch.dtype, optional): 
                模型輸入的資料型別，預設為 torch.float32。
        """
        model.eval()
        for layer in model.parameters():
            device = layer.device
            break
        dummy_input = torch.zeros(*input_shape, dtype=dtype).to(device)

        major, minor, *_ = map(int, trt.__version__.split('.'))
        if (major, minor) < (8, 5):
            opset_version = 12
        else:
            opset_version = opset_version

        if dynamic:
            # dynamic_axes = {"images": {0: "batch", 2: "height", 3: "width"}}
            dynamic_axes = {"images": {0: "batch"}}
            # dynamic_axes["output0"] = {0: "batch", 2: "anchors"}
            dynamic_axes["output0"] = {0: "batch"}

        else:
            dynamic_axes = None

        torch.onnx.export(
            model,
            dummy_input,
            onnx_output_path,
            input_names=input_names,
            output_names=output_names,
            do_constant_folding=True,
            opset_version=opset_version,
            dynamic_axes=dynamic_axes
        )

        print("ONNX export completed.")

        model_onnx = onnx.load(onnx_output_path)
        
        if slim:
            model_onnx = onnxslim.slim(model_onnx)
            print("ONNX_slim export completed.")

        onnx.save(model_onnx, onnx_output_path)

        

    @staticmethod
    def onnx_to_engine(input_path, input_shape, dynamic_batch=16, dynamic=False, type = 'fp16', calibration_data_dir=None):
        """
        將 ONNX 模型轉換為 TensorRT Engine 檔（.engine），支援 FP16、INT8 精度與動態輸入大小。

        Args:
            input_path (str): 
                要轉換的 ONNX 模型路徑，例如 'model.onnx'。
            input_shape (tuple): 
                模型的輸入形狀，例如 (1, 3, 640, 640)，作為 TensorRT 最常見的輸入大小(opt shape)。
            dynamic_batch:
                設定dynamic 最大的batch_size
            dynamic (bool, optional): 
                是否啟用 dynamic shape 支援（例如支援不同解析度或 batch size），預設為 False。
            type (str, optional): 
                精度模式，可選 'fp16' 或 'int8'，預設為 'fp16'。
            calibration_data_dir (str, optional): 
                若使用 INT8 模式時，需提供的校準圖片資料夾路徑。
        """
        base, _ = os.path.splitext(input_path)
        output_path = base + '.engine'

        TRT_LOGGER = trt.Logger(trt.Logger.INFO) # 建立 TensorRT 記錄器，設定為顯示 info 訊息
        builder = trt.Builder(TRT_LOGGER) # 建立 TensorRT engine builder
        network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)) # 建立網路，讓 TensorRT 能正確讀 ONNX 的 batch 大小
        parser = trt.OnnxParser(network, TRT_LOGGER) # 建立 ONNX 解析器 

        with open(input_path, 'rb') as f: # 讀取 ONNX 檔案
            success = parser.parse(f.read()) # 使用 parser 將 ONNX 模型轉換為 TensorRT 的網路定義

        config = builder.create_builder_config() # 建立 BuilderConfig，用於設定精度、記憶體限制等

        is_trt10 = int(trt.__version__.split(".")[0]) >= 10 # 檢查 TensorRT 是否為 v10 或以上
        if is_trt10:
            config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30) # v10 用 set_memory_pool_limit 設定 1GB 工作空間
        else:
            config.max_workspace_size = 1 << 30 # v10 以下版本使用 max_workspace_size 設定記憶體上限

        inputs = [network.get_input(i) for i in range(network.num_inputs)] # 取得模型的所有輸入
        if dynamic:
            profile = builder.create_optimization_profile()
            # min_shape = (1, input_shape[1], 32, 32)  # 設定輸入最小可以接受的尺寸
            min_shape = (1, input_shape[1], input_shape[2], input_shape[3])
            max_shape = (dynamic_batch, input_shape[1], input_shape[2], input_shape[3])  # 設定輸入最大可以接受的尺寸
            for inp in inputs:
                profile.set_shape(inp.name, min=min_shape, opt=input_shape, max=max_shape) # 對每個輸入設定這個範圍，opt: 最常見的輸入（TensorRT 會用這個做最佳化）
            config.add_optimization_profile(profile) # 把建立的 profile 加到 TensorRT 的 config 中，啟用 dynamic shape 支援

        config.profiling_verbosity = trt.ProfilingVerbosity.DETAILED

        if type == 'fp16':
            
            config.set_flag(trt.BuilderFlag.FP16) # 設定為 FP16 精度
            
        elif type == 'int8':

            config.set_flag(trt.BuilderFlag.INT8) # 設定為 INT8 精度

            if dynamic:
                config.set_calibration_profile(profile)  # 指定用哪組 shape 做校準

            calibrator = Calibrator(calibration_data_dir, input_shape) # 建立校準器物件
            config.int8_calibrator = calibrator # 設定到 config 上

        if is_trt10:
            engine = builder.build_serialized_network(network, config) # v10 使用新的 API：直接回傳序列化後的 engine
        else:
            engine = builder.build_engine(network, config) # v10 以下使用 build_engine，再手動序列化

        if engine is None:
            print("Failed to create the engine")
        else:
            with open(output_path, "wb") as f: # 寫入 engine 到磁碟
                if is_trt10:
                    f.write(engine) # v10 已序列化，直接寫入
                else:
                    f.write(engine.serialize()) # v10 以下需要先序列化再寫入

            
            print("Engine saved successfully!")

    @staticmethod
    def torch_to_engine(
        model, 
        input_shape, 
        dynamic_batch=16, 
        onnx_output_path='model.onnx', 
        input_names=["images"], 
        output_names=["output0"], 
        slim=True,
        opset_version=14, 
        dynamic=False, 
        dtype=torch.float32, 
        type='fp16', 
        calibration_image_dir=None
        ):
        """
        將 PyTorch 模型轉換為 TensorRT Engine(.engine 檔)，中途自動轉換為 ONNX 格式，可選擇是否啟用 dynamic shape 與精度設定。

        Args:
            model (torch.nn.Module): 
                要轉換的 PyTorch 模型(需為 eval 模式，建議已載入權重)。
            input_shape (tuple): 
                模型輸入的大小，例如 (1, 3, 640, 640)，會用來建立 dummy input。
            dynamic_batch (int, optional): 
                當 dynamic=True 時，設定 dynamic profile 的最大 batch size，預設為 16。
            onnx_output_path (str, optional): 
                中繼輸出的 ONNX 檔案路徑，預設為 'model.onnx'。
            input_names (list, optional): 
                ONNX 輸出時指定的 input tensor 名稱，預設為 ["images"]。
            output_names (list, optional): 
                ONNX 輸出時指定的 output tensor 名稱，預設為 ["output0"]。
            opset_version (int, optional): 
                ONNX opset 版本，影響 ONNX 模型內使用的 operator 格式，預設為 14。
                建議根據 TensorRT 支援度進行選擇。
            dynamic (bool, optional): 
                是否啟用 dynamic shape(可接受不同輸入尺寸)，預設為 False。
            dtype (torch.dtype, optional): 
                用於建立 dummy input 的 tensor dtype，預設為 torch.float32。
            type (str, optional): 
                TensorRT 精度設定，可選 'fp16' 或 'int8'，預設為 'fp16'。
            calibration_image_dir (str, optional): 
                若使用 INT8 模式，需提供校準圖片資料夾路徑，否則可設為 None。
        """
        Convert.torch_to_onnx(
            model, 
            input_shape, 
            onnx_output_path=onnx_output_path, 
            dynamic=dynamic,
            dtype=dtype,
            opset_version=opset_version,
            input_names=input_names, 
            output_names=output_names, 
            slim=slim
        )
        
        Convert.onnx_to_engine(
            onnx_output_path, 
            input_shape, 
            dynamic_batch=dynamic_batch, 
            dynamic=dynamic, 
            type=type, 
            calibration_data_dir=calibration_image_dir
        )
