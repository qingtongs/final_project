"""
Quick validation script.
Test the system on a few images to check format and output correctness.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detect import AnimalDetector, ANIMAL_CATEGORIES


def validate_output(predictions: dict) -> bool:
    """
    Validate prediction output format.
    
    Rules:
    - Must be a valid dictionary
    - Keys must be animal category names
    - Values must be integers >= 1
    - No non-anal categories allowed
    - No count=0 entries
    """
    issues = []
    
    for key, value in predictions.items():
        # Check key is a string
        if not isinstance(key, str):
            issues.append(f"Key {key} is not a string")
            continue
        
        # Check key is a valid animal category
        if key not in ANIMAL_CATEGORIES:
            issues.append(f"Category '{key}' is not in the supported animal list")
        
        # Check value is an integer
        if not isinstance(value, int):
            issues.append(f"Count for '{key}' is not an integer: {value}")
        
        # Check value >= 1
        if isinstance(value, (int, float)) and value < 1:
            issues.append(f"Count for '{key}' is less than 1: {value}")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description="Quick Validation")
    parser.add_argument("--image", type=str, help="Single image to test")
    parser.add_argument("--image-dir", type=str, help="Directory of images to test")
    parser.add_argument("--model", type=str, default="runs/detect/train/weights/best.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--device", type=str, default="0")
    
    # Parse args manually to avoid conflict with sys.argv
    args = parser.parse_args()
    
    detector = AnimalDetector(
        model_path=args.model,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
        device=args.device,
    )
    
    if args.image:
        result = detector.detect_and_count(args.image)
        print(f"Image: {args.image}")
        print(f"Result: {json.dumps(result, indent=2)}")
        issues = validate_output(result)
        if issues:
            print(f"Validation issues: {issues}")
        else:
            print("✓ Output format is valid")
    
    elif args.image_dir:
        from pathlib import Path
        IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        images = []
        for ext in IMAGE_EXTS:
            images.extend(Path(args.image_dir).glob(f"*{ext}"))
        images = sorted(images)
        
        for img in images:
            result = detector.detect_and_count(str(img))
            issues = validate_output(result)
            status = "✓" if not issues else "✗"
            print(f"{status} {img.name}: {result}")
            if issues:
                print(f"  Issues: {issues}")
    else:
        print("Provide --image or --image-dir")


if __name__ == "__main__":
    import argparse
    main()
