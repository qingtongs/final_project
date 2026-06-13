# Animal Detection and Counting Project Documentation

## Project Goal

Build a YOLO-based animal detection and counting system. For each input image, the system outputs a JSON dictionary whose keys are supported animal categories and whose values are positive integer counts.

## Supported Categories

cat, dog, horse, cow, sheep, goat, pig, rabbit, chicken, duck, goose, deer, monkey, fox, wolf, bear, tiger, lion, zebra, giraffe

## Runtime Environment

- Project root: `E:\final_project\animal_detection_project`
- Python environment: `.venv_cuda`
- CUDA device used: NVIDIA GeForce RTX 3070 Ti Laptop GPU
- Key environment variables:
  - `YOLO_CONFIG_DIR=E:\final_project\animal_detection_project\ultralytics_config`
  - `TORCH_HOME=E:\final_project\animal_detection_project\.torch`

## Final Model

- Model path: `runs\detect\runs\detect\animal_dataset_6sp_20cls_finetune\weights\best.pt`
- Base model: YOLO11s
- Final fine-tuning dataset config: `configs\animal_dataset_6sp_20cls.yaml`
- Final training metrics:
  - Precision: 0.963
  - Recall: 0.977
  - mAP50: 0.978
  - mAP50-95: 0.940

## Key Scripts

- `scripts\detect.py`: single-image detection and counting
- `scripts\evaluate.py`: batch validation and JSON prediction export
- `scripts\annotate_val_set.py`: copy validation images and draw boxes with class names and confidence scores
- `scripts\postprocess.py`: balanced close-box duplicate suppression
- `scripts\train_6sp_20cls_from_best.py`: final 20-class fine-tuning from the previous best model

## Final Validation Outputs

- Prediction JSON: `outputs\valset_predictions_6sp_20cls_finetuned_suppressed_balanced.json`
- Annotated validation images: `outputs\val_set_annotated_6sp_20cls_finetuned_suppressed_balanced\annotated`
- Detection details: `outputs\val_set_annotated_6sp_20cls_finetuned_suppressed_balanced\detections_with_boxes.json`
- Internal validation score: 90.94 / 100

## Reproduce Evaluation

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

## Final Deliverables

- Report DOCX: `outputs\final_deliverables\animal_detection_project_report.docx`
- Report PDF: `outputs\final_deliverables\animal_detection_project_report.pdf`
- Presentation PPTX: `outputs\final_deliverables\animal_detection_project_presentation.pptx`
