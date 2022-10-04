# Dataset

此处为数据集堆放点, 以 `.TAR` 归档格式储存.

文件布局: 若干同目录单元, 一个单元由 `x.png` 和 `x.txt` 组成.

- `x` 可以为任何数字或者名称
- `png` 内是材质图片(32x)
- `txt`是该材质的英文名称.

文件命名格式: `dataset-IDENTIFIER-(block/item).tar`

# 从材质包生成名称

使用 [dataset-generator](../datagen.py)

```bash
python3 ./datagen.py some_path_to_resourcepack
```

将会输出到 `out` 目录下. 请自行打包