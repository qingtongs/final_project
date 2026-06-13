"""Convert animal_dataset_6sp_v1 LabelMe JSON labels to a 20-class YOLO dataset."""

from __future__ import annotations

import json
import random
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "datasets" / "animal_dataset_6sp_v1"
OUTPUT_DIR = PROJECT_ROOT / "dataset" / "animal_dataset_6sp_yolo_20cls"
CONFIG_PATH = PROJECT_ROOT / "configs" / "animal_dataset_6sp_20cls.yaml"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = [
    "cat", "dog", "horse", "cow", "sheep", "goat", "pig", "rabbit",
    "chicken", "duck", "goose", "deer", "monkey", "fox", "wolf",
    "bear", "tiger", "lion", "zebra", "giraffe",
]


def shape_to_yolo_line(shape: dict, image_width: int, image_height: int) -> str:
    label = int(str(shape["label"]))
    if label < 0 or label >= len(CLASS_NAMES):
        raise ValueError(f"Class id out of range: {label}")

    points = shape.get("points", [])
    if len(points) < 2:
        raise ValueError(f"Shape has fewer than 2 points: {shape}")

    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    x1 = max(0.0, min(xs))
    y1 = max(0.0, min(ys))
    x2 = min(float(image_width), max(xs))
    y2 = min(float(image_height), max(ys))
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"Invalid box for class {label}: {(x1, y1, x2, y2)}")

    x_center = ((x1 + x2) / 2) / image_width
    y_center = ((y1 + y2) / 2) / image_height
    box_width = (x2 - x1) / image_width
    box_height = (y2 - y1) / image_height
    return f"{label} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"


def write_yaml() -> None:
    names = "\n".join(f"  {idx}: {name}" for idx, name in enumerate(CLASS_NAMES))
    CONFIG_PATH.write_text(
        "\n".join([
            "# 20-class YOLO config generated from animal_dataset_6sp_v1",
            f"path: {OUTPUT_DIR.as_posix()}",
            "train: images/train",
            "val: images/val",
            "test: images/val",
            "",
            "nc: 20",
            "names:",
            names,
            "",
        ]),
        encoding="utf-8",
    )


def main() -> None:
    images = sorted(p for p in SOURCE_DIR.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        raise FileNotFoundError(f"No images found in {SOURCE_DIR}")

    missing = [p.name for p in images if not p.with_suffix(".json").exists()]
    if missing:
        raise FileNotFoundError(f"Missing JSON labels for: {missing[:10]}")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    shuffled = images[:]
    random.Random(42).shuffle(shuffled)
    val_stems = {p.stem for p in shuffled[:max(1, round(len(shuffled) * 0.2))]}

    split_counts = {"train": 0, "val": 0}
    object_counts = {"train": 0, "val": 0}
    class_counts: dict[str, int] = {}

    for image_path in images:
        split = "val" if image_path.stem in val_stems else "train"
        out_image_dir = OUTPUT_DIR / "images" / split
        out_label_dir = OUTPUT_DIR / "labels" / split
        out_image_dir.mkdir(parents=True, exist_ok=True)
        out_label_dir.mkdir(parents=True, exist_ok=True)

        data = json.loads(image_path.with_suffix(".json").read_text(encoding="utf-8"))
        width = int(data["imageWidth"])
        height = int(data["imageHeight"])
        lines = []
        for shape in data.get("shapes", []):
            label = str(shape.get("label"))
            lines.append(shape_to_yolo_line(shape, width, height))
            class_counts[label] = class_counts.get(label, 0) + 1

        shutil.copy2(image_path, out_image_dir / image_path.name)
        (out_label_dir / f"{image_path.stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        split_counts[split] += 1
        object_counts[split] += len(lines)

    write_yaml()
    print(f"YOLO dataset written to: {OUTPUT_DIR}")
    print(f"Config written to: {CONFIG_PATH}")
    print(f"Train images: {split_counts['train']}, objects: {object_counts['train']}")
    print(f"Val images: {split_counts['val']}, objects: {object_counts['val']}")
    print(f"Class counts: {dict(sorted(class_counts.items(), key=lambda kv: int(kv[0])))}")


if __name__ == "__main__":
    main()
