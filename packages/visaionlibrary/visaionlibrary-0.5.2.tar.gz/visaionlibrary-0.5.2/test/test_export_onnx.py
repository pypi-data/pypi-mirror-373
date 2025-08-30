import torch
import onnx
import onnxsim
import argparse
import json
from visaionlibrary.utils import YoloOnnxWrapper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="/root/data/visaion/visaionlib/configs/mmyolo/yolov8/yolov8_s_fast_1xb12-40e_cat.py")
    parser.add_argument("--checkpoint", type=str, default="/root/data/visaion/visaionlib/work_dirs/yolov8_s_fast_1xb12-40e_cat/epoch_40.pth")
    parser.add_argument("--device", type=str, default="cpu")

    args = parser.parse_args()
    config = args.config
    checkpoint = args.checkpoint
    device = args.device
    print(f"config: {config}, checkpoint: {checkpoint}, device: {device}")
    
    wrapper = YoloOnnxWrapper(config, checkpoint, device)
    x = torch.randint(0, 255, (1, 3, 640, 640))
    x = x.to(torch.float32)

    # 推理一次
    wrapper(x)

    # 导出onnx
    torch.onnx.export(
        wrapper,
        x,
        "yolov8_s_fast_1xb12-40e_cat.onnx",
        input_names=["input"],
        opset_version=11,
        do_constant_folding=True,
    )

    # 优化onnx
    model_opt, check_ok = onnxsim.simplify("yolov8_s_fast_1xb12-40e_cat.onnx")
    if check_ok:
        onnx.save(model_opt, "yolov8_s_fast_1xb12-40e_cat_opt.onnx")

    # 添加metadata
    onnx_model = onnx.load("yolov8_s_fast_1xb12-40e_cat_opt.onnx")
    metadata_props = {
        "task_type": "det",
        "model_name": "yolov8",
        "version": "0.4.x",
        "classes": {"0": "cat"},
    }
    onnx_info = json.dumps(metadata_props).encode('utf-8').decode('unicode_escape')
    meta = onnx_model.metadata_props.add()
    meta.key, meta.value = "metainfo", str(onnx_info)
    onnx.save(onnx_model, "yolov8_s_fast_1xb12-40e_cat_opt_metadata.onnx")
    print("done")
