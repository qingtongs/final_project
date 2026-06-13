# Animal Detection and Counting Project

## 中文说明

### 1. 项目简介

本项目是 Deep Learning Final Project 的动物检测与计数系统。系统以单张图片作为输入，使用 YOLO11s 检测动物目标，经过类别白名单过滤、重复框抑制和计数后，输出符合要求的 JSON 字典：

```json
{
  "eval_000001": {
    "cat": 2,
    "duck": 1,
    "deer": 1
  }
}
```

最终系统支持 20 个动物类别，并可批量处理验证集或测试集图片。

### 2. 支持类别

```text
cat, dog, horse, cow, sheep, goat, pig, rabbit,
chicken, duck, goose, deer, monkey, fox, wolf,
bear, tiger, lion, zebra, giraffe
```

### 3. 文档与项目结构

```text
animal_detection_project/
  configs/                         数据集配置文件
  dataset/                         YOLO 训练数据
  datasets/                        原始/中间数据集与 LabelMe JSON 标注
  outputs/                         预测结果、标注图、日志和最终交付文件
    final_deliverables/            报告、PPT、PDF 和项目说明文档
  runs/                            YOLO 训练输出和模型权重
  scripts/                         数据处理、训练、推理、评估和文档生成脚本
  val_set/                         本地验证集图片
  .venv_cuda/                      CUDA Python 虚拟环境
  README.md                        中英双语项目说明
```

最终交付文件位于：

```text
outputs/final_deliverables/
  animal_detection_project_report.docx
  animal_detection_project_report.pdf
  animal_detection_project_presentation.pptx
  project_documentation.md
```

### 4. 运行环境

本项目后续默认使用 CUDA 环境运行。

```powershell
cd E:\final_project\animal_detection_project
$env:YOLO_CONFIG_DIR='E:\final_project\animal_detection_project\ultralytics_config'
$env:TORCH_HOME='E:\final_project\animal_detection_project\.torch'
.\.venv_cuda\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
```

已验证环境：

```text
Python virtual environment: .venv_cuda
PyTorch: 2.5.1+cu121
GPU: NVIDIA GeForce RTX 3070 Ti Laptop GPU
```

### 5. 最终模型

最终模型是在 20 类检测头上持续微调得到的，没有改成 5 类或 6 类小模型，因此仍可输出完整 20 类动物标签。

```text
runs/detect/runs/detect/animal_dataset_6sp_20cls_finetune/weights/best.pt
```

最终训练指标：

```text
Precision: 0.963
Recall:    0.977
mAP50:     0.978
mAP50-95:  0.940
```

### 6. 数据构建流程

本项目的数据处理按阶段推进：

1. 合并 `datasets/animal_dataset_xfz` 和 `datasets/animal_dataset_yzy`。
2. 将标签统一整理为 JSON / LabelMe 风格格式。
3. 构建 `animal_dataset1` 的 20 类 YOLO 数据集。
4. 使用 `animal_dataset_5sp_v1` 对狼、鹅、马、牛、猴等弱类别进行继续优化。
5. 使用 `animal_dataset_6sp_v1` 在上一版 best 模型基础上继续优化。
6. 保持最终模型为 20 类检测模型，避免丢失原始类别空间。

### 7. 常用脚本

| 脚本 | 作用 |
| --- | --- |
| `scripts/detect.py` | 单张图片检测与计数 |
| `scripts/evaluate.py` | 批量验证并导出 JSON |
| `scripts/annotate_val_set.py` | 复制验证集并绘制框、类别和置信度 |
| `scripts/postprocess.py` | 重复预测框抑制 |
| `scripts/merge_datasets_to_json.py` | 合并数据集并整理 JSON 标签 |
| `scripts/label_5sp_v1_labelme.py` | 自动生成 LabelMe 风格 JSON 标注 |
| `scripts/prepare_6sp_yolo_20cls.py` | 生成 6sp 的 20 类 YOLO 数据集 |
| `scripts/train_6sp_20cls_from_best.py` | 基于 best 模型继续微调 |

### 8. 批量验证

使用最终模型验证 `val_set`：

```powershell
cd E:\final_project\animal_detection_project
$env:YOLO_CONFIG_DIR='E:\final_project\animal_detection_project\ultralytics_config'
$env:TORCH_HOME='E:\final_project\animal_detection_project\.torch'
.\.venv_cuda\Scripts\python.exe scripts\evaluate.py `
  --image-dir val_set `
  --model runs\detect\runs\detect\animal_dataset_6sp_20cls_finetune\weights\best.pt `
  --output outputs\valset_predictions_6sp_20cls_finetuned_suppressed_balanced.json `
  --conf 0.25 --iou 0.45 --imgsz 640 --device 0
```

当前 balanced 后处理版本的本地验证平均分：

```text
90.94 / 100
```

### 9. 生成带框验证图

```powershell
.\.venv_cuda\Scripts\python.exe scripts\annotate_val_set.py `
  --image-dir val_set `
  --output-dir outputs\val_set_annotated_6sp_20cls_finetuned_suppressed_balanced `
  --model runs\detect\runs\detect\animal_dataset_6sp_20cls_finetune\weights\best.pt `
  --conf 0.25 --iou 0.45 --imgsz 640 --device 0
```

输出：

```text
outputs/val_set_annotated_6sp_20cls_finetuned_suppressed_balanced/annotated
outputs/val_set_annotated_6sp_20cls_finetuned_suppressed_balanced/detections_with_boxes.json
```

### 10. 后处理说明

YOLO 自带 NMS 后，项目额外增加了 `scripts/postprocess.py`：

- 同类别框：如果重叠较大，或中心接近且尺寸相近，只保留置信度最高的框。
- 不同类别框：仅在两个框很可能覆盖同一个目标时抑制低置信度框。
- 该逻辑同时用于 JSON 计数和验证图画框，保证显示结果与提交结果一致。

### 11. 已知问题与改进方向

- 鸭和鹅容易混淆。
- 狐、狼、狗在相似姿态或背景中仍可能混淆。
- 遮挡、多动物紧密排列时仍可能出现计数误差。
- 后续可增加人工核验的困难样本，并继续针对弱类别微调。

---

## English Version

### 1. Overview

This project is an animal detection and counting system for the Deep Learning Final Project. The system takes one image as input, detects animal instances with YOLO11s, filters unsupported classes, suppresses duplicate boxes, counts each animal category, and exports a clean JSON dictionary.

Example output:

```json
{
  "eval_000001": {
    "cat": 2,
    "duck": 1,
    "deer": 1
  }
}
```

The final system supports 20 animal categories and can process a validation or evaluation image folder in batch mode.

### 2. Supported Categories

```text
cat, dog, horse, cow, sheep, goat, pig, rabbit,
chicken, duck, goose, deer, monkey, fox, wolf,
bear, tiger, lion, zebra, giraffe
```

### 3. Documentation and Project Layout

```text
animal_detection_project/
  configs/                         Dataset configuration files
  dataset/                         YOLO-format training datasets
  datasets/                        Raw/intermediate datasets and LabelMe JSON labels
  outputs/                         Predictions, annotated images, logs, and deliverables
    final_deliverables/            Report, PDF, PPT, and project documentation
  runs/                            YOLO training runs and model weights
  scripts/                         Data processing, training, inference, evaluation, and document scripts
  val_set/                         Local validation images
  .venv_cuda/                      CUDA Python virtual environment
  README.md                        Bilingual project README
```

Final deliverables:

```text
outputs/final_deliverables/
  animal_detection_project_report.docx
  animal_detection_project_report.pdf
  animal_detection_project_presentation.pptx
  project_documentation.md
```

### 4. Runtime Environment

This project should be run with the CUDA environment by default.

```powershell
cd E:\final_project\animal_detection_project
$env:YOLO_CONFIG_DIR='E:\final_project\animal_detection_project\ultralytics_config'
$env:TORCH_HOME='E:\final_project\animal_detection_project\.torch'
.\.venv_cuda\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
```

Verified environment:

```text
Python virtual environment: .venv_cuda
PyTorch: 2.5.1+cu121
GPU: NVIDIA GeForce RTX 3070 Ti Laptop GPU
```

### 5. Final Model

The final model remains a 20-class detector. Fine-tuning on the 5sp and 6sp datasets did not reduce the output head to only 5 or 6 classes.

```text
runs/detect/runs/detect/animal_dataset_6sp_20cls_finetune/weights/best.pt
```

Final training metrics:

```text
Precision: 0.963
Recall:    0.977
mAP50:     0.978
mAP50-95:  0.940
```

### 6. Dataset Construction

The data pipeline was built in stages:

1. Merge `datasets/animal_dataset_xfz` and `datasets/animal_dataset_yzy`.
2. Normalize annotations into JSON / LabelMe-style formats.
3. Build the 20-class YOLO dataset from `animal_dataset1`.
4. Fine-tune weak categories with `animal_dataset_5sp_v1`.
5. Continue optimization with `animal_dataset_6sp_v1` from the previous best model.
6. Keep the final detector as a 20-class model to preserve the full evaluation vocabulary.

### 7. Main Scripts

| Script | Purpose |
| --- | --- |
| `scripts/detect.py` | Single-image detection and counting |
| `scripts/evaluate.py` | Batch evaluation and JSON export |
| `scripts/annotate_val_set.py` | Copy validation images and draw boxes, labels, and confidences |
| `scripts/postprocess.py` | Duplicate prediction suppression |
| `scripts/merge_datasets_to_json.py` | Merge datasets and normalize JSON labels |
| `scripts/label_5sp_v1_labelme.py` | Generate LabelMe-style JSON labels |
| `scripts/prepare_6sp_yolo_20cls.py` | Prepare the 6sp 20-class YOLO dataset |
| `scripts/train_6sp_20cls_from_best.py` | Continue fine-tuning from the best model |

### 8. Batch Validation

Run validation on `val_set` with the final model:

```powershell
cd E:\final_project\animal_detection_project
$env:YOLO_CONFIG_DIR='E:\final_project\animal_detection_project\ultralytics_config'
$env:TORCH_HOME='E:\final_project\animal_detection_project\.torch'
.\.venv_cuda\Scripts\python.exe scripts\evaluate.py `
  --image-dir val_set `
  --model runs\detect\runs\detect\animal_dataset_6sp_20cls_finetune\weights\best.pt `
  --output outputs\valset_predictions_6sp_20cls_finetuned_suppressed_balanced.json `
  --conf 0.25 --iou 0.45 --imgsz 640 --device 0
```

Current internal validation score with balanced post-processing:

```text
90.94 / 100
```

### 9. Annotated Validation Images

```powershell
.\.venv_cuda\Scripts\python.exe scripts\annotate_val_set.py `
  --image-dir val_set `
  --output-dir outputs\val_set_annotated_6sp_20cls_finetuned_suppressed_balanced `
  --model runs\detect\runs\detect\animal_dataset_6sp_20cls_finetune\weights\best.pt `
  --conf 0.25 --iou 0.45 --imgsz 640 --device 0
```

Outputs:

```text
outputs/val_set_annotated_6sp_20cls_finetuned_suppressed_balanced/annotated
outputs/val_set_annotated_6sp_20cls_finetuned_suppressed_balanced/detections_with_boxes.json
```

### 10. Post-processing

In addition to YOLO's built-in NMS, this project applies an extra duplicate-suppression layer in `scripts/postprocess.py`:

- Same-class boxes are merged when they overlap strongly or have close centers with similar sizes.
- Cross-class boxes are merged only when they are very likely to describe the same object.
- The same post-processing logic is used for JSON counting and annotated image drawing.

### 11. Known Limitations and Future Work

- Duck and goose are still easy to confuse.
- Fox, wolf, and dog may be confused under similar poses or backgrounds.
- Occlusion and tightly grouped animals may still cause counting errors.
- Future improvements should add more manually verified hard examples and continue targeted fine-tuning for weak categories.
