---
name: file-organization
description: Where project files live — deliverables path, scripts, cleanup status
metadata:
  type: project
---

# File Organization

## Final Deliverables
```
项目要求/报告/
├── animal_detection_project_presentation_en.pptx
├── animal_detection_project_presentation_zh.pptx
├── animal_detection_project_report.docx
├── animal_detection_project_report.pdf
├── project_documentation.md
└── src/
    ├── generate_ppt_en.py
    ├── generate_ppt_zh.py
    └── generate_report_zh.py
```

## Project Scripts (in `scripts/`)
- `detect.py` — single-image detection & counting
- `evaluate.py` — batch evaluation → JSON
- `postprocess.py` — duplicate suppression
- `annotate_val_set.py` — draw boxes on validation images
- `train_*.py` — training scripts for each stage
- `prepare_*.py` — dataset preparation

## Deleted / Migrated
- `outputs/final_deliverables/` — DELETED (old bilingual versions migrated to `项目要求/报告/`)
- Old generation scripts removed from `scripts/` — only kept in `项目要求/报告/src/`

## Key Paths
- Model: `runs/detect/runs/detect/animal_dataset_6sp_20cls_finetune/weights/best.pt`
- Config: `configs/animal_dataset_6sp_20cls.yaml`
- Val predictions: `outputs/valset_predictions_6sp_20cls_finetuned_suppressed_balanced.json`
- Annotated val: `outputs/val_set_annotated_6sp_20cls_finetuned_suppressed_balanced/`
