import os
import shutil
from pathlib import Path

import ktc
import onnx
import numpy as np


def optimize_onnx_model(input_path, output_path=''):
    """
    Optimize the ONNX model to fit the toolchain and Kneron hardware specification.
    Args:
        input_path: Path to the input ONNX model.
        output_path: Path to save the optimized ONNX model. 
            If not provided, saves as "optimized.onnx" in the same directory as input_path.
    Returns:
        output_path: Path to the optimized ONNX model.
        optimized: The optimized ONNX model.
    """
    if not output_path:
        output_path = Path(input_path).parent / "optimized.onnx"

    optimized = ktc.onnx_optimizer.onnx2onnx_flow(
        onnx.load(input_path), 
        eliminate_tail=True
    )
    # import kneronnxopt
    # optimized = kneronnxopt.optimize(
    #     onnx.load(input_path),
    #     skip_fuse_qkv=True,
    # )
    onnx.save(optimized, output_path)
    print("[ONNX model optimized]")
    print("- output_path:", output_path)
    return output_path, optimized


def quantize_compile(
        onnx_model,
        input_images, 
        platform="720",
        model_id=40001,
        output_dir="/data1/kneron_flow"
    ):
    """
    Quantize and compile the model with Kneron toolchain flow.
    onnx -> bie
    bie  -> nef
    Args:
        onnx_model: ONNX model to be quantized and compiled.
        input_images: List of preprocessed images for quantization.
        platform: Target platform, e.g., "720".
        model_id: Unique identifier for the model.
        output_dir: Directory to save the output NEF file.
    Returns:
        bie_path: Path to the generated BIE file.
        nef_path: Path to the generated NEF file.
    """
    assert isinstance(onnx_model, onnx.ModelProto), "onnx_model must be an instance of onnx.ModelProto"
    assert isinstance(input_images, list), "input_images must be a list of preprocessed images"
    assert all(isinstance(img, np.ndarray) for img in input_images), "All items in input_images must be numpy arrays"

    orig_cwd = Path.cwd()

    # Create a ModelConfig object with the optimized ONNX model
    km = ktc.ModelConfig(
        id=model_id, 
        version="0001", 
        platform=platform, 
        onnx_model=onnx_model
    )

    input_mapping = {"images": input_images}  # input name must match the ONNX model input name

    # Output_dir defaults to "/data1/kneron_flow" and cannot be changed,
    # since it is used by the Kneron Flow to store intermediate files.
    bie_path = km.analysis(input_mapping)
    print("[Quantization completed]")
    print("- raw bie_path:", bie_path)

    nef_path = ktc.compile([km]) 
    print("[Compilation completed]")
    print("- raw nef_path:", nef_path)

    if output_dir != "/data1/kneron_flow":
        # since ktc operation changes the current working directory,
        # we need to change it back to the script directory
        os.chdir(orig_cwd)
        os.makedirs(output_dir, exist_ok=True)
        # Copy the BIE and NEF files to the specified output directory
        shutil.copy(bie_path, os.path.join(output_dir, Path(bie_path).name))
        shutil.copy(nef_path, os.path.join(output_dir, Path(nef_path).name))
        print(f"[Files copied to {output_dir}]")
    
    return bie_path, nef_path


def onnx_to_nef(
        onnx_path, 
        input_images, 
        platform="720",
        model_id=40001, 
        output_dir="/data1/kneron_flow"
    ):
    """
    Convert ONNX model to NEF format.
    Recommand to use different model_id for different models.
    Args:
        onnx_path: Path to the ONNX model file.
        input_images: List of preprocessed images for quantization.
        platform: Target platform, e.g., "720".
        model_id: Unique identifier for the model.
        output_dir: Directory to save the output NEF file.
    Returns:
        Boolean indicating success or failure.
    """
    try:
        _, opt_model = optimize_onnx_model(onnx_path)
        _, _ = quantize_compile(opt_model, input_images, platform, model_id, output_dir)
        return True
    except Exception as e:
        print(f"[Error in converting ONNX to NEF: {e}]")
        return False
    

def combine_nef_files(
        nef_paths, 
        output_path="./"
    ):
    """
    Combine multiple NEF files into one.
    Args:
        nef_paths: List of NEF file paths to combine.
        output_path: Folder path to save the combined NEF file.
    Returns:
        Combined NEF file path.
    """
    if not nef_paths:
        raise ValueError("No NEF paths provided for combination.")
    
    if not isinstance(nef_paths, list):
        nef_paths = [nef_paths]

    combined_nef = ktc.combine_nef(nef_paths, output_path)
    print(f"[Combined NEF file created at {output_path}]")
    return combined_nef