# Code Structure

This repository keeps the project code small and reproducible. Large runtime folders, raw datasets, caches, and intermediate training checkpoints are intentionally excluded from Git.

## Main Entry Points

- `scripts/detect.py`: single-image inference and animal counting.
- `scripts/evaluate.py`: batch inference for a folder of images and JSON export.
- `scripts/annotate_val_set.py`: copies validation images and draws bounding boxes, labels, and confidence scores.
- `scripts/postprocess.py`: duplicate-box suppression shared by counting and visualization.
- `run_val.bat`: Windows CUDA validation entry point using the final 20-class best model.

## Dataset Scripts

- `scripts/merge_datasets_to_json.py`: merges source datasets and normalizes labels.
- `scripts/label_5sp_v1_labelme.py`: creates LabelMe-style auto-label JSON files and preview images.
- `scripts/prepare_animal_dataset1_yolo.py`: prepares `animal_dataset1` as a YOLO dataset.
- `scripts/prepare_5sp_yolo_20cls.py`: prepares `animal_dataset_5sp_v1` while preserving the 20-class label map.
- `scripts/prepare_6sp_yolo_20cls.py`: prepares `animal_dataset_6sp_v1` while preserving the 20-class label map.

## Training Scripts

- `scripts/train_animal_dataset1.py`: trains the first 20-class custom model.
- `scripts/train_5sp_20cls_from_best.py`: fine-tunes the 20-class model on the 5sp dataset.
- `scripts/train_6sp_20cls_from_best.py`: final fine-tuning stage from the previous best model.
- `scripts/train.py`: generic training script retained for experiments.

## Documentation Scripts

- `scripts/create_project_report.py`: regenerates the Word report from the provided course template.
- `scripts/create_presentation_modules.py`: regenerates the editable PPTX slide modules used for the presentation.

## Committed Binary Artifacts

The repository should include only final, submission-relevant binaries:

- `outputs/final_deliverables/animal_detection_project_report.docx`
- `outputs/final_deliverables/animal_detection_project_report.pdf`
- `outputs/final_deliverables/animal_detection_project_presentation.pptx`
- `runs/detect/runs/detect/animal_dataset_6sp_20cls_finetune/weights/best.pt`

Intermediate datasets and checkpoints are excluded to keep the GitHub repository practical.
