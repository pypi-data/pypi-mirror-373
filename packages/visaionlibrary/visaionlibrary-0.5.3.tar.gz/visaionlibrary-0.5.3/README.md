# visaionlibrary

## 如何打包
```
pip install --upgrade build
python -m build
```

## 如何安装
```
pip install \
-i https://pypi.tuna.tsinghua.edu.cn/simple \
-f https://download.openmmlab.com/mmcv/dist/cu117/torch1.13/index.html \
--extra-index-url https://download.pytorch.org/whl/cu117 \
visaionlibrary-0.0.1-py3-none-any.whl
```

## 项目结构
- configs: 符合mm系列的配置文件
- tools: 配合configs使用的训练, 评测, 导出模型的脚本
- templates: 为了适应visaion平台, 在configs的基础上修改的配置, 对应的训练, 评测, 导出模型的脚本在visaionlibrary.tools下
- visaionlibrary: 项目库
- test: 一些测试脚本