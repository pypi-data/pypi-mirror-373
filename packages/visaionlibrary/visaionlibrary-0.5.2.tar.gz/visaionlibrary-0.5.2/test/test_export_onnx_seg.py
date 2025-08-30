import torch
import onnx
import onnxsim
import argparse
import json
from visaionlibrary.utils import SegOnnxWrapper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="/root/data/visaion/visaionlib/configs/regnet_800mf-2x.py")
    parser.add_argument("--checkpoint", type=str, default="/root/data/visaion/visaionlib/work_dirs/regnet_800mf-2x/checkpoint_004000.pth")
    parser.add_argument("--device", type=str, default="cpu")

    args = parser.parse_args()
    config = args.config
    checkpoint = args.checkpoint
    device = args.device
    print(f"config: {config}, checkpoint: {checkpoint}, device: {device}")
    
    wrapper = SegOnnxWrapper(config, checkpoint, device)
    x = torch.randint(0, 255, (1, 3, 128, 128))
    x = x.to(torch.float32)

    # 推理一次
    wrapper(x)

    # 导出onnx
    torch.onnx.export(
        wrapper,
        x,
        "seg_model.onnx",
        input_names=["input"],
        opset_version=11,
        do_constant_folding=True,
    )

    # 优化onnx
    model_opt, check_ok = onnxsim.simplify("seg_model.onnx")
    if check_ok:
        onnx.save(model_opt, "seg_model_opt.onnx")

    # 添加metadata
    onnx_model = onnx.load("seg_model_opt.onnx")
    metadata_props = {
        "task_type": "seg",
        "model_name": "unet",
        "version": "0.4.x",
        "classes": {"0": "background", "1": "ng1", "2": "ng2"},
    }
    onnx_info = json.dumps(metadata_props).encode('utf-8').decode('unicode_escape')
    meta = onnx_model.metadata_props.add()
    meta.key, meta.value = "metainfo", str(onnx_info)
    onnx.save(onnx_model, "seg_model_opt_metadata.onnx")
    print("done")
