# Artixel

A rough implementation of generating pixel arts.

# Prerequisites

## DataSet

解压 `./dataset/%any%.tar` 并且分到 `train` 和 `test` 中.

(训练) 使用 `pip3 install --user ./requirements.txt` 安装所有所需依赖.

(贡献数据集) 使用 `pip3 install --user json5` 即可

关于贡献数据集, 参见 [DataSet](./dataset/README.md)

## Train

准备好环境 (CUDA, OpenCV etc) 后直接运行 `python3 train.py`

