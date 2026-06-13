"""
Quick validation: Run YOLO11s pre-trained model on validation images.
Outputs predictions.json with animal category counts.

Usage:
    python quick_val.py
"""

import os
import sys
import json
from pathlib import Path

# ============ CONFIG ============
# Validation images directory (modify if needed)
VAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "val_set")
# Output file
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions.json")
# Model
MODEL_NAME = "yolo11s.pt"
# Confidence threshold
CONF = 0.25
# IOU threshold for NMS
IOU = 0.45
# Image size
IMGSZ = 640
# CUDA device
DEVICE = "0"
# ================================

# Supported animal categories (evaluation set)
ANIMAL_CATEGORIES = {
    "cat", "dog", "horse", "cow", "sheep", "goat", "pig", "rabbit",
    "chicken", "duck", "goose", "deer", "monkey", "fox", "wolf",
    "bear", "tiger", "lion", "zebra", "giraffe"
}

# COCO class name → evaluation category mapping
COCO_TO_EVAL = {
    "cat": "cat",
    "dog": "dog",
    "horse": "horse",
    "cow": "cow",
    "sheep": "sheep",
    "bear": "bear",
    "zebra": "zebra",
    "giraffe": "giraffe",
    "bird": None,       # Too generic, filter out
    "elephant": None,   # Not in eval categories
}


def main():
    # Check/install ultralytics
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ultralytics not installed. Installing...")
        os.system(f"{sys.executable} -m pip install ultralytics")
        from ultralytics import YOLO

    # Check validation directory
    val_path = Path(VAL_DIR)
    if not val_path.exists():
        print(f"ERROR: Validation directory not found: {VAL_DIR}")
        print("Please place validation images in the 'val_images' folder next to this script.")
        sys.exit(1)

    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    images = [
        p for p in val_path.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]
    images = sorted(images)

    if not images:
        print(f"ERROR: No images found in {VAL_DIR}")
        sys.exit(1)

    print(f"Found {len(images)} validation images")

    # Load model (auto-downloads if not present)
    print(f"Loading model: {MODEL_NAME}")
    model = YOLO(MODEL_NAME)
    print(f"Model classes: {model.names}")

    # Run inference on all images
    predictions = {}
    for i, img_path in enumerate(images):
        img_name = img_path.stem
        results = model.predict(
            source=str(img_path),
            conf=CONF,
            iou=IOU,
            imgsz=IMGSZ,
            device=DEVICE,
            verbose=False,
        )

        counts = {}
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0])
                conf_val = float(box.conf[0])
                class_name = model.names[cls_id]

                # Map COCO name to evaluation category
                mapped_name = COCO_TO_EVAL.get(class_name, class_name)

                # Only count supported animal categories
                if mapped_name and mapped_name in ANIMAL_CATEGORIES:
                    counts[mapped_name] = counts.get(mapped_name, 0) + 1

        predictions[img_name] = counts
        print(f"[{i+1}/{len(images)}] {img_name}: {counts}")

    # Save predictions
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)

    print(f"\nPredictions saved to: {OUTPUT_FILE}")
    print(f"Total images processed: {len(predictions)}")

    # Print summary
    print("\n" + "=" * 50)
    print("PREDICTION SUMMARY")
    print("=" * 50)
    for img_name, preds in predictions.items():
        if preds:
            items = ", ".join(f"{k}: {v}" for k, v in preds.items())
            print(f"  {img_name}: {{{items}}}")
        else:
            print(f"  {img_name}: {{}} (no animals detected)")


if __name__ == "__main__":
    main()
