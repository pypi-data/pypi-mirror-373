from mmengine.registry import DATASETS, MODELS
from mmengine.runner import Runner
import visaionlibrary.datasets
import visaionlibrary.models.data_preprocessor



if __name__ == "__main__":
    data_root = "/root/data/road-crack"
    meta_info = dict(
        classes=['background', 'crack'],
        palette=[(0, 0, 0), (255, 0, 0)])
    
    data_pipeline = [
        dict(type='LoadImageFromFile', color_type="grayscale", imdecode_backend='cv2'),  # color_type 取值为 grayscale 或 color；imdecode_backend 取值为 'cv2', 'turbojpeg', 'pillow', 'tifffile'
        dict(type='LoadSegAnnotations', reduce_zero_label=False),
        dict(
            type='RandomRescale',
            base_scale_factor=1.0,
            random_scale_range=0.1,
            random_scale_prob=1.0),
        dict(
            type='SegRegionSampler',
            region_size=1024),
        dict(
            type='PackSegInputsVisaion',
            dual_mode=False,
            meta_keys=['img_path', 'seg_map_path', 'ori_shape', 'img_shape',
                        'pad_shape', 'scale_factor', 'flip', 'flip_direction',
                        'coord', 'sample_idx', 'dataset_metainfo'])
    ]
    
    dataset_cfg = dict(
        type='VisaionSegDataset',
        metainfo=meta_info,
        data_root=data_root,
        data_prefix=dict(),
        pipeline=data_pipeline)
    
    train_dataloader = dict(
        batch_size=4,
        num_workers=1,
        sampler=dict(
            type='InfiniteSamplerBatch',
            shuffle=True,
            neg_ratio=0.2,
            batch_size=4),
        batch_sampler=dict(type='BatchSamplerConstantOne', drop_last=False),
        dataset=dataset_cfg
    )
    
    # dataset = DATASETS.build(dataset_cfg)

    dataloader = Runner.build_dataloader(train_dataloader)

    data_preprocessor_cfg = dict(
        type='SegDataPreProcessor',
        mean=[103.53, 116.28, 123.675],
        std=[57.375, 57.12, 58.395],
        bgr_to_rgb=False,
        grayscale_to_color=True,
        pad_val=0,
        seg_pad_val=0,
        size_divisor=1,
        )
    
    data_preprocessor = MODELS.build(data_preprocessor_cfg)

    for batch in dataloader:
        batch = data_preprocessor(batch, training=True)