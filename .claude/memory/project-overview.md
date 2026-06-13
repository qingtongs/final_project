---
name: project-overview
description: Animal detection YOLO project — what it is, key metrics, requirements compliance
metadata:
  type: project
---

# Animal Detection and Counting — Deep Learning Final Project

YOLO11s-based system detecting and counting 20 animal categories. Input: single image → Output: `{"cat": 2, "duck": 1, "deer": 1}` dictionary.

**Final model**: `runs/detect/runs/detect/animal_dataset_6sp_20cls_finetune/weights/best.pt`
**Metrics**: Precision 0.963, Recall 0.977, mAP50 0.978, mAP50-95 0.940
**Validation score**: 90.94/100 (balanced suppression post-processing)

**20 categories**: cat, dog, horse, cow, sheep, goat, pig, rabbit, chicken, duck, goose, deer, monkey, fox, wolf, bear, tiger, lion, zebra, giraffe

**Training stages**: animal_dataset1 → animal_dataset_5sp_v1 (weak classes) → animal_dataset_6sp_v1 (continued). All stages preserved 20-class output head.

**Key scripts**: detect.py (single image), evaluate.py (batch→JSON), postprocess.py (duplicate suppression), annotate_val_set.py (visual output)

**Requirements status**: Fully meets Final_Project_task.pdf — 3-part structure (data, system, evaluation), correct dictionary format, animal-only whitelist, positive-count constraint, batch evaluation.

**Known issues**: duck↔goose confusion, fox/wolf/dog confusion, occlusion counting errors.
