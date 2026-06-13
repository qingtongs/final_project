"""
Animal detection and counting system.
Takes a single image as input, outputs a dictionary with animal categories and counts.
"""

from ultralytics import YOLO
from pathlib import Path
from typing import Dict
import argparse
import json
import os

from postprocess import suppress_close_detections

# Supported animal categories (must match evaluation exactly)
ANIMAL_CATEGORIES = {
    "cat", "dog", "horse", "cow", "sheep", "goat", "pig", "rabbit",
    "chicken", "duck", "goose", "deer", "monkey", "fox", "wolf",
    "bear", "tiger", "lion", "zebra", "giraffe"
}

# Mapping from COCO class names to our evaluation categories
# Some COCO names need to be mapped, others are direct matches
COCO_TO_EVAL = {
    "cat": "cat",
    "dog": "dog",
    "horse": "horse",
    "cow": "cow",
    "sheep": "sheep",
    "bear": "bear",
    "zebra": "zebra",
    "giraffe": "giraffe",
    "bird": None,       # Filter out - too generic
    "elephant": None,   # Not in evaluation categories
}


class AnimalDetector:
    """Animal detection and counting system based on YOLO11."""

    def __init__(
        self,
        model_path: str = "runs/detect/train/weights/best.pt",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        imgsz: int = 640,
        device: str = "0",
    ):
        """
        Initialize the detector.

        Args:
            model_path: Path to trained YOLO model weights
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
            imgsz: Inference image size
            device: Device for inference
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.imgsz = imgsz
        self.device = device

    def detect_and_count(self, image_path: str) -> Dict[str, int]:
        """
        Detect animals in an image and count each category.

        Args:
            image_path: Path to input image

        Returns:
            Dictionary mapping animal category names to counts.
            Example: {"cat": 2, "duck": 1, "deer": 1}
        """
        results = self.model.predict(
            source=image_path,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            imgsz=self.imgsz,
            device=self.device,
            verbose=False,
        )

        counts = {}
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            detections = []
            for source_index, box in enumerate(boxes):
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]

                # Map COCO name to evaluation category if needed
                mapped_name = COCO_TO_EVAL.get(class_name, class_name)

                # Only count supported animal categories
                if mapped_name and mapped_name in ANIMAL_CATEGORIES:
                    detections.append(
                        {
                            "source_index": source_index,
                            "class_id": cls_id,
                            "class_name": class_name,
                            "mapped_name": mapped_name,
                            "confidence": float(box.conf[0]),
                            "bbox_xyxy": [float(v) for v in box.xyxy[0].tolist()],
                        }
                    )

            for detection in suppress_close_detections(detections):
                mapped_name = detection["mapped_name"]
                counts[mapped_name] = counts.get(mapped_name, 0) + 1

        return counts

    def detect_single(self, image_path: str) -> Dict[str, int]:
        """Alias for detect_and_count for clarity."""
        return self.detect_and_count(image_path)


def main():
    parser = argparse.ArgumentParser(description="Animal Detection and Counting")
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--model", type=str, default="runs/detect/train/weights/best.pt",
                        help="Path to model weights")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--device", type=str, default="0", help="Device")

    args = parser.parse_args()
    detector = AnimalDetector(
        model_path=args.model,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
        imgsz=args.imgsz,
        device=args.device,
    )

    result = detector.detect_and_count(args.image)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
