# Animal Detection and Counting Project Documentation
# 动物检测与计数项目文档

## Project Goal / 项目目标

Build a YOLO-based animal detection and counting system. For each input image, the system outputs a JSON dictionary whose keys are supported animal categories and whose values are positive integer counts.

构建基于YOLO的动物检测与计数系统。对于每张输入图片，系统输出一个JSON字典，键为支持的动物类别，值为正整数计数。

## Supported Categories / 支持类别

cat, dog, horse, cow, sheep, goat, pig, rabbit, chicken, duck, goose, deer, monkey, fox, wolf, bear, tiger, lion, zebra, giraffe (20 classes / 20类)

## Runtime Environment / 运行环境

| Item / 项目 | Detail / 详情 |
|---|---|
| Project root / 项目根目录 | `E:\final_project\animal_detection_project` |
| Python environment / Python环境 | `.venv_cuda` |
| CUDA device / CUDA设备 | NVIDIA GeForce RTX 3070 Ti Laptop GPU |
| PyTorch version / PyTorch版本 | 2.5.1+cu121 |
| Key env vars / 关键环境变量 | `YOLO_CONFIG_DIR`, `TORCH_HOME` |

## Final Model / 最终模型

- **Model path / 模型路径**: `runs\detect\runs\detect\animal_dataset_6sp_20cls_finetune\weights\best.pt`
- **Base model / 基础模型**: YOLO11s (COCO pretrained / COCO预训练)
- **Dataset config / 数据集配置**: `configs\animal_dataset_6sp_20cls.yaml`

### Final Training Metrics / 最终训练指标

| Metric / 指标 | Value / 数值 |
|---|---|
| Precision / 精确率 | 0.963 |
| Recall / 召回率 | 0.977 |
| mAP50 | 0.978 |
| mAP50-95 | 0.940 |

## Training Stages / 训练阶段

| Stage / 阶段 | Data / 数据 | Purpose / 目的 |
|---|---|---|
| Stage 1 | animal_dataset1 | Train 20 animal classes / 训练20个动物类别 |
| Stage 2 | animal_dataset_5sp_v1 | Improve wolf/goose/horse/cow/monkey / 改善5个弱类别 |
| Stage 3 | animal_dataset_6sp_v1 | Continue optimization from best model / 从最佳模型继续优化 |

## Key Scripts / 关键脚本

| Script / 脚本 | Purpose / 作用 |
|---|---|
| `scripts\detect.py` | Single-image detection and counting / 单张图片检测与计数 |
| `scripts\evaluate.py` | Batch validation and JSON prediction export / 批量验证与JSON预测导出 |
| `scripts\annotate_val_set.py` | Copy validation images and draw boxes with class names and confidence / 复制验证集图片并绘制边界框 |
| `scripts\postprocess.py` | Balanced close-box duplicate suppression / 平衡式近距框重复抑制 |
| `scripts\train_6sp_20cls_from_best.py` | Final 20-class fine-tuning from previous best / 最终20类微调 |

## Post-Processing Rules / 后处理规则

1. **Same-class boxes / 同类别框**: Merge when IoU ≥ 0.40, or when centers are close (≤30% of min diagonal) with similar sizes (area ratio ≥ 0.50) / IoU≥0.40时合并，或中心距近（≤最小对角线的30%）且尺寸相似（面积比≥0.50）时合并
2. **Cross-class boxes / 跨类别框**: Merge under stricter conditions: IoU ≥ 0.62 or centers ≤18% of min diagonal with area ratio ≥ 0.70 / 更严格条件下合并：IoU≥0.62或中心距≤最小对角线的18%且面积比≥0.70
3. **Keep highest confidence / 保留最高置信度**: In all merge cases, the highest-confidence detection is retained / 所有合并情况下保留置信度最高的检测

## Validation Results / 验证结果

- **Average score / 平均分**: 90.94 / 100
- **Perfect images / 满分图片**: 9 / 15
- **Validation set / 验证集**: 15 images / 15张图片

## Final Deliverables / 最终交付物

| File / 文件 | Path / 路径 |
|---|---|
| Report (DOCX) / 报告 | `outputs\final_deliverables\animal_detection_project_report.docx` |
| Report (PDF) / 报告PDF | `outputs\final_deliverables\animal_detection_project_report.pdf` |
| Presentation (PPTX) / 演示文稿 | `outputs\final_deliverables\animal_detection_project_presentation.pptx` |
| Documentation / 文档 | `outputs\final_deliverables\project_documentation.md` |

## Reproduce Evaluation / 复现评估

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

## Known Issues / 已知问题

- Duck ↔ goose confusion / 鸭与鹅容易混淆
- Fox ↔ wolf ↔ dog confusion / 狐狸、狼、狗容易混淆
- Occlusion & tight grouping cause count errors / 遮挡和密集排列导致计数错误
- Synthetic scene generalization / 合成场景泛化能力

## Future Work / 后续工作

- Add more manually verified hard examples for weak classes / 增加弱类别的人工验证难例
- Per-class confidence threshold optimization / 逐类置信度阈值优化
- Test-time augmentation / 测试时增强
- Ensemble methods / 集成方法
