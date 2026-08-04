---
title: "Ubuntu 22.04安装MMSegmentation完整记录与踩坑总结"

date: 2026-08-04

draft: false

author:
  - Yalun

tags:
  - MMSegmentation
  - OpenMMLab
  - PyTorch
  - CUDA
  - Conda
---

最近在 Ubuntu 22.04 环境下配置 MMSegmentation，并使用 NVIDIA RTX 4090 进行训练。

整个过程中主要遇到了：

- PyTorch 与 CUDA 版本匹配问题
- MMCV版本兼容问题
- mmcv._ext 编译问题
- mmengine版本导致resume卡死问题
- 训练权重保存问题

这里记录完整安装流程以及遇到的问题，希望可以帮助后续需要配置 MMSegmentation 的朋友。

---

# 一、创建 Conda 环境

首先创建 Python 环境：

```bash
conda create --name openmmlab python=3.8 -y

conda activate openmmlab
````

---

# 二、安装 PyTorch

## 1. CUDA版本选择

由于服务器显卡为 RTX 4090，因此 CUDA Toolkit 版本不能过低。

RTX 4090 使用 Ada Lovelace 架构，需要 CUDA 对其提供支持。

CUDA Toolkit 下载地址：

[CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)

需要注意：

> 系统 CUDA Toolkit 与 Conda 环境中的 CUDA Runtime 并不是完全等价。

我的理解：

* 系统 CUDA Toolkit 主要负责 CUDA Extension 编译
* PyTorch 环境中的 CUDA Runtime 负责运行时调用

因此，对于需要编译 CUDA 算子的 OpenMMLab 项目，需要保证：

```
GPU Driver
      ↓
CUDA Toolkit
      ↓
PyTorch CUDA Runtime
      ↓
MMCV CUDA Extension
```

之间相互兼容。

---

## 2. 安装 PyTorch

推荐安装较稳定版本：

### Conda安装

```bash
conda install pytorch==1.13.0 \
torchvision==0.14.0 \
torchaudio==0.13.0 \
pytorch-cuda=11.7 \
-c pytorch \
-c nvidia
```

### Pip安装

```bash
pip install torch==1.13.0+cu117 \
torchvision==0.14.0+cu117 \
torchaudio==0.13.0 \
--extra-index-url https://download.pytorch.org/whl/cu117
```

---

# 三、安装 OpenMMLab 依赖

MMSegmentation 1.x 版本基于：

```
MMEngine
      |
MMCV
      |
MMSegmentation
```

因此需要先安装 MMCV。

---

## 使用 MIM安装 MMCV

安装 openmim：

```bash
pip install -U openmim
```

安装 mmengine：

```bash
mim install mmengine
```

安装 MMCV：

```bash
mim install "mmcv>=2.0.0"
```

---

# 四、安装 MMSegmentation

## 方法1：源码安装（推荐）

如果需要修改代码或者进行模型开发：

```bash
git clone -b main https://github.com/open-mmlab/mmsegmentation.git

cd mmsegmentation

pip install -v -e .
```

参数说明：

```
-v
```

表示输出详细安装信息。

```
-e
```

表示 editable 模式安装。

修改源码后无需重新安装。

---

## 方法2：pip安装

如果只是作为第三方库使用：

```bash
pip install "mmsegmentation>=1.0.0"
```

---

# 五、测试安装是否成功

## 下载配置文件和权重

执行：

```bash
mim download mmsegmentation \
--config pspnet_r50-d8_4xb2-40k-cityscapes-512x1024 \
--dest .
```

下载完成后会得到：

```
pspnet_r50-d8_4xb2-40k-cityscapes-512x1024.py

pspnet_r50-d8_512x1024_40k_cityscapes_xxxxx.pth
```

---

## 推理测试

运行：

```bash
python demo/image_demo.py \
demo/demo.png \
configs/pspnet/pspnet_r50-d8_4xb2-40k_cityscapes-512x1024.py \
pspnet_r50-d8_512x1024_40k_cityscapes_xxxxx.pth \
--device cuda:0 \
--out-file result.jpg
```

如果运行成功，会生成：

```
result.jpg
```

其中包含预测分割结果。

---

# 六、常见报错及解决方法

# 1. MMCV版本不兼容

## 错误信息

```text
AssertionError:

MMCV==2.2.0 is used but incompatible.

Please install mmcv>=2.0.0rc4.
```

---

## 原因

MMSegmentation 对 MMCV 版本存在严格要求。

例如：

```
MMSegmentation
        |
        |
      MMCV
```

版本不匹配会导致初始化失败。

---

## 解决方法

方法1：

```bash
pip install mmcv-lite==2.0.0rc4
```

如果仍然失败：

方法2：

```bash
mim install mmcv==2.1.0
```

重新运行测试代码即可。

---

# 2. ModuleNotFoundError: No module named 'mmcv._ext'

## 错误信息

```text
ModuleNotFoundError:

No module named 'mmcv._ext'
```

---

## 原因分析

这个问题通常表示：

当前安装的是：

```
mmcv-lite
```

而不是：

```
mmcv-full
```

或者 MMCV CUDA Extension 没有正确编译。

---

## 解决方法

重新安装：

```bash
mim install mmcv==2.1.0
```

确认：

```bash
python -c "import mmcv;print(mmcv.__version__)"
```

```
2.1.0
```

即可。

---

