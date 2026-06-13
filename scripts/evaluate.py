"""
Batch evaluation script.
Processes all evaluation images and writes predictions to a JSON file.

Usage:
    python scripts/evaluate.py --image-dir <path_to_eval_images> --output predictions.json
    python scripts/evaluate.py --image-dir <path_to_eval_images> --output predictions.json --model runs/detect/train/weights/best.pt
"""

from ultralytics import YOLO
from pathlib import Path
from typing import Dict, List
import argparse
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detect import AnimalDetector, ANIMAL_CATEGORIES

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def find_images(image_dir: str) -> List[str]:
    """Find all image files in the directory."""
    image_dir = Path(image_dir)
    images = [
        p for p in image_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return [str(p) for p in sorted(images)]


def batch_evaluate(
    image_dir: str,
    model_path: str = "runs/detect/train/weights/best.pt",
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    imgsz: int = 640,
    device: str = "0",
    output_path: str = "predictions.json",
) -> Dict[str, Dict[str, int]]:
    """
    Run animal detection on all images in a directory and save predictions to JSON.

    Args:
        image_dir: Directory containing evaluation images
        model_path: Path to trained model weights
        conf_threshold: Confidence threshold
        iou_threshold: NMS IoU threshold
        imgsz: Inference image size
        device: Device for inference
        output_path: Path to save JSON predictions

    Returns:
        Dictionary mapping image filenames to prediction dictionaries
    """
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    detector = AnimalDetector(
        model_path=model_path,
        conf_threshold=conf_threshold,
        iou_threshold=iou_threshold,
        imgsz=imgsz,
        device=device,
    )

    images = find_images(image_dir)
    if not images:
        print(f"No images found in {image_dir}")
        return {}

    print(f"Found {len(images)} images in {image_dir}")

    predictions = {}
    for i, img_path in enumerate(images):
        img_name = Path(img_path).stem
        result = detector.detect_and_count(img_path)
        predictions[img_name] = result
        print(f"[{i+1}/{len(images)}] {img_name}: {result}")

    # Save predictions
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)

    print(f"\nPredictions saved to {output_path}")
    print(f"Total images processed: {len(predictions)}")

    return predictions


def main():
    parser = argparse.ArgumentParser(description="Batch Evaluation for Animal Detection")
    parser.add_argument("--image-dir", type=str, required=True,
                        help="Directory containing evaluation images")
    parser.add_argument("--model", type=str, default="runs/detect/train/weights/best.pt",
                        help="Path to model weights")
    parser.add_argument("--output", type=str, default="outputs/predictions.json",
                        help="Output JSON file path")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--device", type=str, default="0", help="Device")

    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    batch_evaluate(
        image_dir=args.image_dir,
        model_path=args.model,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
        imgsz=args.imgsz,
        device=args.device,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
