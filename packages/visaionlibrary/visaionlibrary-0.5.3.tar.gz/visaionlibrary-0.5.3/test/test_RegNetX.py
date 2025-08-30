from visaionlibrary.models.seg.regnet import RegNetVisaion
import torch

model = RegNetVisaion(
    arch="regnetx_12gf",
    in_channels=3,
    stem_channels=32,
    base_channels=32,
    strides=(2, 2, 2, 2),
    dilations=(1, 1, 1, 1),
    out_indices=(0, 1, 2, 3),
    out_stem=True,
    style="pytorch",
    deep_stem=False,
)

model.eval()

input = torch.randn(1, 3, 224, 224)

outputs = model(input)

print([output.shape[1] for output in outputs])
