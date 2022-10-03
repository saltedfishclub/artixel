# Dataset

此处为数据集堆放点, 以 `.TAR` 归档格式储存.

文件布局: 若干同目录单元, 一个单元由 `x.png` 和 `x.txt` 组成, `x` 可以为任何数字或者名称, `png` 内是材质图片(32x), `txt` 是该材质的英文名称.

文件命名格式: `dataset-IDENTIFIER-block/item.tar`

# 从材质包生成名称

使用 [dataset-generator](../dataset-generator)

> **Warning**  
> 还没写完, bug 多

将材质包物品内容解压到 `resource/minecraft` 下,并且提供 `en_us.json` 作为翻译文件.

```bash
java -jar ./dataset-generator.jar en_us.json ./out
```
