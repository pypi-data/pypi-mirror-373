import torch
import onnx
import onnxsim
import argparse
import json
from visaionlibrary.utils import Yolov5InsOnnxWrapper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="/root/data/visaion/visaionlib/configs/yolov5s_ins_seg_all_in_one_visaion.py")
    parser.add_argument("--checkpoint", type=str, default="/root/data/visaion/visaionlib/work_dirs/yolov5s_ins_seg_all_in_one_visaion/epoch_300.pth")
    parser.add_argument("--device", type=str, default="cpu")

    args = parser.parse_args()
    config = args.config
    checkpoint = args.checkpoint
    device = args.device
    print(f"config: {config}, checkpoint: {checkpoint}, device: {device}")
    
    wrapper = Yolov5InsOnnxWrapper(config, checkpoint, device)
    x = torch.randint(0, 255, (1, 3, 640, 640))
    x = x.to(torch.float32)

    # 推理一次
    wrapper(x)

    # 导出onnx
    torch.onnx.export(
        wrapper,
        x,
        "yolov5s_ins_seg_all_in_one_visaion.onnx",
        input_names=["input"],
        opset_version=11,
        do_constant_folding=True,
    )

    # 优化onnx
    model_opt, check_ok = onnxsim.simplify("yolov5s_ins_seg_all_in_one_visaion.onnx")
    if check_ok:
        onnx.save(model_opt, "yolov5s_ins_seg_all_in_one_visaion_opt.onnx")

    # 添加metadata
    onnx_model = onnx.load("yolov5s_ins_seg_all_in_one_visaion_opt.onnx")
    metadata_props = {
        "task_type": "ins",
        "model_name": "yolov5",
        "version": "0.4.x",
        "classes": {"0": "ballon"},
    }
    onnx_info = json.dumps(metadata_props).encode('utf-8').decode('unicode_escape')
    meta = onnx_model.metadata_props.add()
    meta.key, meta.value = "metainfo", str(onnx_info)
    onnx.save(onnx_model, "yolov5s_ins_seg_all_in_one_visaion_opt_metadata.onnx")
    print("done")
