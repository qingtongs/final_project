"""Copy val_set images and draw detections with boxes, labels, and confidences."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import cv2
from ultralytics import YOLO

from postprocess import suppress_close_detections


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def find_images(image_dir: Path) -> list[Path]:
    return sorted(
        p for p in image_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def draw_label(image, text: str, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.7
    thickness = 2
    (text_w, text_h), baseline = cv2.getTextSize(text, font, scale, thickness)
    label_y1 = max(0, y1 - text_h - baseline - 6)
    label_y2 = label_y1 + text_h + baseline + 6
    cv2.rectangle(image, (x1, label_y1), (x1 + text_w + 8, label_y2), color, -1)
    cv2.putText(
        image,
        text,
        (x1 + 4, label_y2 - baseline - 3),
        font,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )


def color_for_class(class_id: int) -> tuple[int, int, int]:
    palette = [
        (56, 56, 255), (151, 157, 255), (31, 112, 255), (29, 178, 255),
        (49, 210, 207), (10, 249, 72), (23, 204, 146), (134, 219, 61),
        (52, 147, 26), (187, 212, 0), (168, 153, 44), (255, 194, 0),
        (147, 69, 52), (255, 115, 100), (236, 24, 0), (255, 56, 132),
        (133, 0, 82), (255, 56, 203), (200, 149, 255), (199, 55, 255),
    ]
    return palette[class_id % len(palette)]


def annotate(
    image_dir: Path,
    output_dir: Path,
    model_path: Path,
    conf: float,
    iou: float,
    imgsz: int,
    device: str,
) -> dict[str, list[dict]]:
    images = find_images(image_dir)
    if not images:
        raise FileNotFoundError(f"No images found in {image_dir}")

    copied_dir = output_dir / "images"
    annotated_dir = output_dir / "annotated"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    copied_dir.mkdir(parents=True)
    annotated_dir.mkdir(parents=True)

    model = YOLO(str(model_path))
    detections: dict[str, list[dict]] = {}

    for image_path in images:
        copied_path = copied_dir / image_path.name
        shutil.copy2(image_path, copied_path)

        image = cv2.imread(str(copied_path))
        if image is None:
            raise ValueError(f"Failed to read image: {copied_path}")

        result = model.predict(
            source=str(copied_path),
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            device=device,
            verbose=False,
        )[0]

        image_detections: list[dict] = []
        if result.boxes is not None:
            boxes = result.boxes
            raw_detections: list[dict] = []
            for source_index, box in enumerate(boxes):
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = str(model.names[class_id])
                x1, y1, x2, y2 = [int(round(v)) for v in box.xyxy[0].tolist()]
                raw_detections.append(
                    {
                        "source_index": source_index,
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox_xyxy": [x1, y1, x2, y2],
                    }
                )

            image_detections = suppress_close_detections(raw_detections)
            for detection in image_detections:
                class_id = detection["class_id"]
                confidence = detection["confidence"]
                class_name = detection["class_name"]
                x1, y1, x2, y2 = detection["bbox_xyxy"]
                color = color_for_class(class_id)
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
                draw_label(image, f"{class_name} {confidence:.2f}", x1, y1, color)

            image_detections = [
                {
                    "class_id": detection["class_id"],
                    "class_name": detection["class_name"],
                    "confidence": round(float(detection["confidence"]), 6),
                    "bbox_xyxy": detection["bbox_xyxy"],
                }
                for detection in image_detections
            ]

        annotated_path = annotated_dir / image_path.name
        cv2.imwrite(str(annotated_path), image)
        detections[image_path.stem] = image_detections
        print(f"{image_path.name}: {len(image_detections)} detections")

    (output_dir / "detections_with_boxes.json").write_text(
        json.dumps(detections, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return detections


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate val_set with detection boxes and confidences")
    parser.add_argument("--image-dir", type=Path, default=PROJECT_ROOT / "val_set")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "outputs" / "val_set_annotated")
    parser.add_argument("--model", type=Path, default=PROJECT_ROOT / "runs" / "detect" / "runs" / "detect" / "animal_dataset1" / "weights" / "best.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", type=str, default="0")
    args = parser.parse_args()

    annotate(
        image_dir=args.image_dir,
        output_dir=args.output_dir,
        model_path=args.model,
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz,
        device=args.device,
    )
    print(f"Annotated images saved to: {args.output_dir / 'annotated'}")
    print(f"Copied source images saved to: {args.output_dir / 'images'}")
    print(f"Detection JSON saved to: {args.output_dir / 'detections_with_boxes.json'}")


if __name__ == "__main__":
    main()
