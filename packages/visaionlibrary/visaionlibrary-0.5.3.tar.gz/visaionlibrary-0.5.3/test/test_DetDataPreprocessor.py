from mmengine.registry import DATASETS, MODELS
from mmengine.runner import Runner
import visaionlibrary.datasets
import visaionlibrary.models.data_preprocessor



if __name__ == "__main__":
    data_root = "/root/data/balloon"
    meta_info = dict(
        classes=['balloon'],
        palette=[(255, 0, 0)])
    
    data_pipeline = [
        dict(type='LoadImageFromFile', color_type="color", imdecode_backend='cv2'),  # color_type 取值为 grayscale 或 color；imdecode_backend 取值为 'cv2', 'turbojpeg', 'pillow', 'tifffile'
        dict(
            type='LoadAnnotations',
            _scope_="mmdet",
            poly2mask=False,
            with_bbox=True,
            with_mask=True),
        dict(
            type='CachedMosaic',
            _scope_="mmdet",
            img_scale=(640, 640),
            max_cached_images=20,
            pad_val=114.0,
            random_pop=False,
        ),
        dict(
            type='RandomResize',
            _scope_="mmdet",
            keep_ratio=True,
            ratio_range=(0.5, 2.0),
            scale=(1280, 1280),
        ),
        dict(type='RandomCrop', crop_size=(640, 640), _scope_="mmdet"),
        dict(type='YOLOXHSVRandomAug', _scope_="mmdet"),
        dict(prob=0.5, type='RandomFlip', _scope_="mmdet"),
        dict(type='Pad', pad_val=dict(img=(114, 114, 114)), size=(640, 640), _scope_="mmdet"),
        dict(
            type='CachedMixUp',
            _scope_="mmdet",
            img_scale=(640, 640),
            max_cached_images=10,
            pad_val=(114, 114, 114),
            prob=0.5,
            random_pop=False,
            ratio_range=(1.0, 1.0),
        ),
        dict(type='FilterAnnotations', min_gt_bbox_wh=(1, 1), _scope_="mmdet"),
        dict(type='PackDetInputs', _scope_="mmdet"),
    ]
    
    dataset_cfg = dict(
        type='VisaionInsDataset',
        metainfo=meta_info,
        data_root=data_root,
        data_prefix=dict(img=""),
        pipeline=data_pipeline)
    
    train_dataloader = dict(
        batch_size=4,
        num_workers=1,
        sampler=dict(
            type='VisaionInfiniteSampler',
            shuffle=True,
            bg_ratio=0.2,
            batch_size=4),
        dataset=dataset_cfg
    )
    
    # dataset = DATASETS.build(dataset_cfg)

    dataloader = Runner.build_dataloader(train_dataloader)

    data_preprocessor_cfg = dict(
        type='DetDataPreprocessor',
        _scope_="mmengine",
        mean=[103.53, 116.28, 123.675],
        std=[57.375, 57.12, 58.395],
        bgr_to_rgb=False,
        grayscale_to_color=True,
        pad_value=0,
        pad_mask=False,
        mask_pad_value=0,
        pad_seg=False,
        seg_pad_value=0,
        pad_size_divisor=1,
        )
    
    data_preprocessor = MODELS.build(data_preprocessor_cfg)

    for batch in dataloader:
        batch = data_preprocessor(batch, training=True)