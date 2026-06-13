"""Merge xfz and yzy animal datasets into one LabelMe-style JSON dataset."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "datasets"
XFZ_DIR = DATASETS_DIR / "animal_dataset_xfz"
YZY_DIR = DATASETS_DIR / "animal_dataset_yzy"
OUTPUT_DIR = DATASETS_DIR / "animal_dataset_merged_json"


def image_size(image_path: Path) -> tuple[int, int]:
    with Image.open(image_path) as image:
        return image.size


def labelme_json(
    *,
    image_name: str,
    width: int,
    height: int,
    shapes: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "version": "3.3.5",
        "flags": {},
        "shapes": shapes,
        "imagePath": f"../images/{image_name}",
        "imageData": None,
        "imageHeight": height,
        "imageWidth": width,
    }


def rectangle_shape(label: str, x1: float, y1: float, x2: float, y2: float) -> dict[str, Any]:
    x1, x2 = sorted((max(0.0, x1), max(0.0, x2)))
    y1, y2 = sorted((max(0.0, y1), max(0.0, y2)))
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


def normalize_xfz_shapes(source_json: Path) -> list[dict[str, Any]]:
    data = json.loads(source_json.read_text(encoding="utf-8"))
    shapes: list[dict[str, Any]] = []
    for shape in data.get("shapes", []):
        points = shape.get("points", [])
        if len(points) < 2:
            continue
        xs = [float(point[0]) for point in points]
        ys = [float(point[1]) for point in points]
        shapes.append(rectangle_shape(str(shape.get("label", "")), min(xs), min(ys), max(xs), max(ys)))
    return shapes


def convert_yolo_txt(source_txt: Path, width: int, height: int) -> list[dict[str, Any]]:
    shapes: list[dict[str, Any]] = []
    for line_no, line in enumerate(source_txt.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f"{source_txt}:{line_no} expected 5 YOLO fields, got {len(parts)}")
        label, cx, cy, box_w, box_h = parts
        cx_f = float(cx) * width
        cy_f = float(cy) * height
        box_w_f = float(box_w) * width
        box_h_f = float(box_h) * height
        x1 = cx_f - box_w_f / 2
        y1 = cy_f - box_h_f / 2
        x2 = cx_f + box_w_f / 2
        y2 = cy_f + box_h_f / 2
        shapes.append(rectangle_shape(label, x1, y1, x2, y2))
    return shapes


def copy_image(source: Path, output_images_dir: Path) -> Path:
    target = output_images_dir / source.name
    if target.exists():
        raise FileExistsError(f"Duplicate output image name: {target.name}")
    shutil.copy2(source, target)
    return target


def write_label(target_json: Path, data: dict[str, Any]) -> None:
    target_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    output_images_dir = OUTPUT_DIR / "images"
    output_labels_dir = OUTPUT_DIR / "labels"

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    output_images_dir.mkdir(parents=True, exist_ok=True)
    output_labels_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, Any]] = []

    for image_path in sorted(XFZ_DIR.glob("*.jpg")):
        source_json = image_path.with_suffix(".json")
        if not source_json.exists():
            raise FileNotFoundError(f"Missing label for {image_path}")
        copied_image = copy_image(image_path, output_images_dir)
        width, height = image_size(copied_image)
        shapes = normalize_xfz_shapes(source_json)
        write_label(
            output_labels_dir / f"{copied_image.stem}.json",
            labelme_json(image_name=copied_image.name, width=width, height=height, shapes=shapes),
        )
        manifest.append({"image": f"images/{copied_image.name}", "label": f"labels/{copied_image.stem}.json", "source": "animal_dataset_xfz", "objects": len(shapes)})

    for image_path in sorted((YZY_DIR / "images").glob("*.jpg")):
        source_txt = YZY_DIR / "yzy_labels" / f"{image_path.stem}.txt"
        if not source_txt.exists():
            raise FileNotFoundError(f"Missing label for {image_path}")
        copied_image = copy_image(image_path, output_images_dir)
        width, height = image_size(copied_image)
        shapes = convert_yolo_txt(source_txt, width, height)
        write_label(
            output_labels_dir / f"{copied_image.stem}.json",
            labelme_json(image_name=copied_image.name, width=width, height=height, shapes=shapes),
        )
        manifest.append({"image": f"images/{copied_image.name}", "label": f"labels/{copied_image.stem}.json", "source": "animal_dataset_yzy", "objects": len(shapes)})

    summary = {
        "dataset": "animal_dataset_merged_json",
        "total_images": len(manifest),
        "total_labels": len(manifest),
        "sources": {
            "animal_dataset_xfz": sum(1 for item in manifest if item["source"] == "animal_dataset_xfz"),
            "animal_dataset_yzy": sum(1 for item in manifest if item["source"] == "animal_dataset_yzy"),
        },
        "items": manifest,
    }
    write_label(OUTPUT_DIR / "manifest.json", summary)

    print(f"Merged dataset written to: {OUTPUT_DIR}")
    print(f"Images: {len(list(output_images_dir.glob('*.jpg')))}")
    print(f"JSON labels: {len(list(output_labels_dir.glob('*.json')))}")


if __name__ == "__main__":
    main()
