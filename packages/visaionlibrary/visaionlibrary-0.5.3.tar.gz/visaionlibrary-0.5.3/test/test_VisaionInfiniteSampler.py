from mmengine.registry import DATASETS, MODELS
from mmengine.runner import Runner
import visaionlibrary
import visaionlibrary.datasets
import visaionlibrary.models.data_preprocessor
import visaionlibrary.datasets.samplers
from mmengine.dist import get_dist_info, init_dist
import os


if __name__ == "__main__":
    init_dist("pytorch")
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
        batch_size=8,
        num_workers=2,
        sampler=dict(
            type='VisaionInfiniteSampler',
            shuffle=True,
            bg_ratio=0.2,
            batch_size=8,
            seed=1024),
        dataset=dataset_cfg
    )
    

    dataloader = Runner.build_dataloader(train_dataloader)

    rank, world_size = get_dist_info()
    for batch in dataloader:
        # print current process id
        print(f"process id: {os.getpid()}, world_size: {world_size}, process rank {rank} ,batch sample idx:{[sample.metainfo['sample_idx'] for sample in batch['data_samples']]}")