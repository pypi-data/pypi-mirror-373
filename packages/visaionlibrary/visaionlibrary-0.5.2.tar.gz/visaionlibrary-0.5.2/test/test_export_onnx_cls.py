import torch
import onnx
import onnxsim
import argparse
import json
from visaionlibrary.utils import ResnetOnnxWrapper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="/root/data/visaion/visaionlib/configs/resnet_34_cls.py")
    parser.add_argument("--checkpoint", type=str, default="/root/data/visaion/visaionlib/work_dirs/resnet_34_cls/epoch_300.pth")
    parser.add_argument("--device", type=str, default="cpu")

    args = parser.parse_args()
    config = args.config
    checkpoint = args.checkpoint
    device = args.device
    print(f"config: {config}, checkpoint: {checkpoint}, device: {device}")
    
    wrapper = ResnetOnnxWrapper(config, checkpoint, device)
    x = torch.randint(0, 255, (1, 3, 224, 224))
    x = x.to(torch.float32)

    # 推理一次
    wrapper(x)

    # 导出onnx
    torch.onnx.export(
        wrapper,
        x,
        "resnet_34_cls.onnx",
        input_names=["input"],
        opset_version=11,
        do_constant_folding=True,
    )

    # 优化onnx
    model_opt, check_ok = onnxsim.simplify("resnet_34_cls.onnx")
    if check_ok:
        onnx.save(model_opt, "resnet_34_cls_opt.onnx")

    # 添加metadata
    onnx_model = onnx.load("resnet_34_cls_opt.onnx")
    metadata_props = {
        "task_type": "cls",
        "model_name": "resnet",
        "version": "0.4.x",
        "classes": {"0": "plastic", "1": "glass"},
    }
    onnx_info = json.dumps(metadata_props).encode('utf-8').decode('unicode_escape')
    meta = onnx_model.metadata_props.add()
    meta.key, meta.value = "metainfo", str(onnx_info)
    onnx.save(onnx_model, "resnet_34_cls_opt_metadata.onnx")
    print("done")
