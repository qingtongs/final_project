"""
Data preparation utilities.
- Convert datasets from various formats to YOLO format
- Split dataset into train/val/test
- Data augmentation helpers
"""

import os
import shutil
import random
from pathlib import Path
from typing import List, Tuple
import argparse


def split_dataset(
    source_images: str,
    source_labels: str,
    output_dir: str = "dataset",
    train_ratio: float = 0.8,
    val_ratio: float = 0.15,
    test_ratio: float = 0.05,
    seed: int = 42,
):
    """
    Split images and labels into train/val/test directories in YOLO format.

    Args:
        source_images: Directory containing all images
        source_labels: Directory containing all YOLO-format label files
        output_dir: Output root directory
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        seed: Random seed for reproducibility
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Ratios must sum to 1.0"

    random.seed(seed)

    # Find all image files
    img_dir = Path(source_images)
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    images = []
    for ext in IMAGE_EXTS:
        images.extend(img_dir.glob(f"*{ext}"))
        images.extend(img_dir.glob(f"*{ext.upper()}"))
    images = sorted(images)

    print(f"Found {len(images)} images")

    # Shuffle
    random.shuffle(images)

    # Split
    n = len(images)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    train_imgs = images[:n_train]
    val_imgs = images[n_train:n_train + n_val]
    test_imgs = images[n_train + n_val:]

    splits = {
        "train": train_imgs,
        "val": val_imgs,
        "test": test_imgs,
    }

    label_dir = Path(source_labels)

    for split_name, split_imgs in splits.items():
        # Create directories
        img_out = Path(output_dir) / "images" / split_name
        lbl_out = Path(output_dir) / "labels" / split_name
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)

        for img_path in split_imgs:
            # Copy image
            shutil.copy2(img_path, img_out / img_path.name)

            # Copy corresponding label
            label_name = img_path.stem + ".txt"
            label_path = label_dir / label_name
            if label_path.exists():
                shutil.copy2(label_path, lbl_out / label_name)
            else:
                print(f"Warning: No label file for {img_path.name}")

        print(f"{split_name}: {len(split_imgs)} images")

    print(f"Dataset split complete. Output: {output_dir}")


def verify_dataset(dataset_yaml: str = "configs/animal_dataset.yaml"):
    """Verify dataset integrity: check images and labels match."""
    from ultralytics.data.utils import check_dataset
    import yaml

    with open(dataset_yaml) as f:
        cfg = yaml.safe_load(f)

    for split in ["train", "val"]:
        img_dir = Path(cfg[split])
        lbl_dir = img_dir.parent.parent / "labels" / split

        if not img_dir.exists():
            print(f"Warning: {split} image dir not found: {img_dir}")
            continue

        images = list(img_dir.glob("*"))
        labels = list(lbl_dir.glob("*.txt")) if lbl_dir.exists() else []

        img_stems = {p.stem for p in images}
        lbl_stems = {p.stem for p in labels}

        missing_labels = img_stems - lbl_stems
        missing_images = lbl_stems - img_stems

        print(f"\n{split} set: {len(images)} images, {len(labels)} labels")
        if missing_labels:
            print(f"  Images without labels: {len(missing_labels)}")
        if missing_images:
            print(f"  Labels without images: {len(missing_images)}")
        if not missing_labels and not missing_images:
            print(f"  ✓ All images and labels match!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset Preparation")
    parser.add_argument("--source-images", type=str, help="Source image directory")
    parser.add_argument("--source-labels", type=str, help="Source label directory")
    parser.add_argument("--output", type=str, default="dataset", help="Output directory")
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.05)
    parser.add_argument("--verify", action="store_true", help="Only verify dataset")

    args = parser.parse_args()

    if args.verify:
        verify_dataset()
    elif args.source_images and args.source_labels:
        split_dataset(
            args.source_images, args.source_labels,
            args.output, args.train_ratio, args.val_ratio, args.test_ratio
        )
    else:
        print("Provide --source-images and --source-labels, or use --verify")
