import time, thop
from pathlib import Path

import torch
import torch.nn as nn

from .loader import CustomModelLoader


def model_info(model, verbose=False, imgsz=640):
    """
    Prints model summary including layers, parameters, gradients, and FLOPs; imgsz may be int or list.

    Example: img_size=640 or img_size=[640, 320]
    """
    n_p = sum(x.numel() for x in model.parameters())  # number parameters
    n_g = sum(x.numel() for x in model.parameters() if x.requires_grad)  # number gradients
    if verbose:
        print(f"{'layer':>5} {'name':>40} {'gradient':>9} {'parameters':>12} {'shape':>20} {'mu':>10} {'sigma':>10}")
        for i, (name, p) in enumerate(model.named_parameters()):
            name = name.replace("module_list.", "")
            print(
                "%5g %40s %9s %12g %20s %10.3g %10.3g"
                % (i, name, p.requires_grad, p.numel(), list(p.shape), p.mean(), p.std())
            )

    try:  # FLOPs
        p = next(model.parameters())
        stride = max(int(model.stride.max()), 32) if hasattr(model, "stride") else 32  # max stride
        im = torch.empty((1, p.shape[1], stride, stride), device=p.device)  # input image in BCHW format
        flops = thop.profile(deepcopy(model), inputs=(im,), verbose=False)[0] / 1e9 * 2  # stride GFLOPs
        imgsz = imgsz if isinstance(imgsz, list) else [imgsz, imgsz]  # expand if int/float
        fs = f", {flops * imgsz[0] / stride * imgsz[1] / stride:.1f} GFLOPs"  # 640x640 GFLOPs
    except Exception:
        fs = ""

    name = Path(model.yaml_file).stem.replace("yolov5", "YOLOv5") if hasattr(model, "yaml_file") else "Model"
    # logger.info(f"{name} summary: {len(list(model.modules()))} layers, {n_p} parameters, {n_g} gradients{fs}")

# can only decorate on instance method
def timer():
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]  # 確定其中之一是 `self`
            if hasattr(self, 'verbose') and self.verbose:
                torch.cuda.synchronize()
                start_time = time.time()
                result = func(*args, **kwargs)
                torch.cuda.synchronize()
                end_time = time.time()
                print(f"{func.__name__}: {(end_time - start_time)*1000:.1f} ms")
            else:
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


def fuse_conv_and_bn(conv, bn):
    """
    Fuses Conv2d and BatchNorm2d layers into a single Conv2d layer.

    See https://tehnokv.com/posts/fusing-batchnorm-and-conv/.
    """
    fusedconv = (
        nn.Conv2d(
            conv.in_channels,
            conv.out_channels,
            kernel_size=conv.kernel_size,
            stride=conv.stride,
            padding=conv.padding,
            dilation=conv.dilation,
            groups=conv.groups,
            bias=True,
        )
        .requires_grad_(False)
        .to(conv.weight.device)
    )

    # Prepare filters
    w_conv = conv.weight.clone().view(conv.out_channels, -1)
    w_bn = torch.diag(bn.weight.div(torch.sqrt(bn.eps + bn.running_var)))
    fusedconv.weight.copy_(torch.mm(w_bn, w_conv).view(fusedconv.weight.shape))

    # Prepare spatial bias
    b_conv = torch.zeros(conv.weight.size(0), device=conv.weight.device) if conv.bias is None else conv.bias
    b_bn = bn.bias - bn.weight.mul(bn.running_mean).div(torch.sqrt(bn.running_var + bn.eps))
    fusedconv.bias.copy_(torch.mm(w_bn, b_conv.reshape(-1, 1)).reshape(-1) + b_bn)

    return fusedconv


def attempt_load(weights, device=None, replace=None, task=None, version=None):
    """
    Loads and fuses an ensemble or single YOLOv5 model from weights, handling device placement and model adjustments.

    Example inputs: weights=[a,b,c] or a single model weights=[a] or weights=a.
    """
    if replace is None:
        ckpt = torch.load(weights, map_location=device)  # load
        return ckpt['model'].to(device).float().fuse().eval()  # FP32 model

    else:
        loader = CustomModelLoader(weights, model_version=version, task=task, map_location=device)
        ckpt = loader.load()
        return ckpt['model'].float().fuse().eval()  # FP32 model

def build_nms(nms_type):
    if nms_type == 'torch':
        import torchvision
        return torchvision.ops.nms
    elif nms_type == 'numpy':
        from .nms import nms_np_agnostic
        return nms_np_agnostic


class ExportWrapper(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model.eval()

    def forward(self, x):
        outputs = self.model(x)
        return outputs[0]  # 只回傳 detection tensor

