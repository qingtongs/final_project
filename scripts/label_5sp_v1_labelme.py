"""Auto-label animal_dataset_5sp_v1 images as LabelMe-style JSON files."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import cv2
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_DIR = PROJECT_ROOT / "datasets" / "animal_dataset_5sp_v1"
DEFAULT_MODEL = PROJECT_ROOT / "runs" / "detect" / "runs" / "detect" / "animal_dataset1" / "weights" / "best.pt"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def find_images(dataset_dir: Path) -> list[Path]:
    return sorted(
        p for p in dataset_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def rectangle_shape(label: str, x1: float, y1: float, x2: float, y2: float) -> dict[str, Any]:
    return {
        "label": str(label),
        "score": None,
        "points": [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
        "group_id": None,
        "description": "",
        "difficult": False,
        "shape_type": "rectangle",
        "flags": {},
        "attributes": {},
        "kie_linking": [],
    }


def labelme_data(image_path: Path, width: int, height: int, shapes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "version": "3.3.5",
        "flags": {},
        "shapes": shapes,
        "imagePath": image_path.name,
        "imageData": None,
        "imageHeight": height,
        "imageWidth": width,
    }


def color_for_class(class_id: int) -> tuple[int, int, int]:
    palette = [
        (56, 56, 255), (151, 157, 255), (31, 112, 255), (29, 178, 255),
        (49, 210, 207), (10, 249, 72), (23, 204, 146), (134, 219, 61),
        (52, 147, 26), (187, 212, 0), (168, 153, 44), (255, 194, 0),
        (147, 69, 52), (255, 115, 100), (236, 24, 0), (255, 56, 132),
        (133, 0, 82), (255, 56, 203), (200, 149, 255), (199, 55, 255),
    ]
    return palette[class_id % len(palette)]


def draw_label(image, text: str, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.65
    thickness = 2
    (text_w, text_h), baseline = cv2.getTextSize(text, font, scale, thickness)
    label_y1 = max(0, y1 - text_h - baseline - 6)
    label_y2 = label_y1 + text_h + baseline + 6
    cv2.rectangle(image, (x1, label_y1), (x1 + text_w + 8, label_y2), color, -1)
    cv2.putText(image, text, (x1 + 4, label_y2 - baseline - 3), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)


def write_preview(image_path: Path, preview_path: Path, detections: list[dict[str, Any]], names: dict[int, str]) -> None:
    image = cv2.imread(str(image_path))
    if image is None:
        return
    for detection in detections:
        class_id = int(detection["class_id"])
        confidence = float(detection["confidence"])
        x1, y1, x2, y2 = detection["bbox_xyxy"]
        color = color_for_class(class_id)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
        draw_label(image, f"{names[class_id]} {confidence:.2f}", x1, y1, color)
    cv2.imwrite(str(preview_path), image)


def auto_label(dataset_dir: Path, model_path: Path, conf: float, iou: float, imgsz: int, device: str) -> None:
    images = find_images(dataset_dir)
    if not images:
        raise FileNotFoundError(f"No images found in {dataset_dir}")

    preview_dir = dataset_dir / "_preview_boxes"
    if preview_dir.exists():
        shutil.rmtree(preview_dir)
    preview_dir.mkdir(parents=True)

    model = YOLO(str(model_path))
    summary: dict[str, Any] = {
        "model": str(model_path),
        "confidence_threshold": conf,
        "iou_threshold": iou,
        "images": {},
    }

    for image_path in images:
        result = model.predict(
            source=str(image_path),
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            device=device,
            verbose=False,
        )[0]

        height, width = result.orig_shape
        shapes: list[dict[str, Any]] = []
        detections: list[dict[str, Any]] = []

        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
                x1 = max(0.0, min(x1, width))
                y1 = max(0.0, min(y1, height))
                x2 = max(0.0, min(x2, width))
                y2 = max(0.0, min(y2, height))
                shapes.append(rectangle_shape(str(class_id), x1, y1, x2, y2))
                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": str(model.names[class_id]),
                        "confidence": round(confidence, 6),
                        "bbox_xyxy": [round(x1), round(y1), round(x2), round(y2)],
                    }
                )

        output_json = image_path.with_suffix(".json")
        output_json.write_text(
            json.dumps(labelme_data(image_path, width, height, shapes), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_preview(image_path, preview_dir / image_path.name, detections, model.names)
        summary["images"][image_path.name] = detections
        print(f"{image_path.name}: {len(shapes)} labels -> {output_json.name}")

    (dataset_dir / "_auto_label_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Preview images saved to: {preview_dir}")
    print(f"Summary saved to: {dataset_dir / '_auto_label_summary.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-label animal_dataset_5sp_v1 in xfz/LabelMe JSON format")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", type=str, default="0")
    args = parser.parse_args()

    auto_label(args.dataset_dir, args.model, args.conf, args.iou, args.imgsz, args.device)


if __name__ == "__main__":
    main()
