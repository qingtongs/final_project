"""Post-processing helpers for model detections."""

from __future__ import annotations

from math import hypot
from typing import Any


def _area(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def _iou(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    intersection = _area([ix1, iy1, ix2, iy2])
    union = _area(box_a) + _area(box_b) - intersection
    return intersection / union if union > 0 else 0.0


def _center_distance(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    acx = (ax1 + ax2) / 2.0
    acy = (ay1 + ay2) / 2.0
    bcx = (bx1 + bx2) / 2.0
    bcy = (by1 + by2) / 2.0
    return hypot(acx - bcx, acy - bcy)


def _diagonal(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return hypot(max(0.0, x2 - x1), max(0.0, y2 - y1))


def _similar_size(box_a: list[float], box_b: list[float], ratio: float) -> bool:
    area_a = _area(box_a)
    area_b = _area(box_b)
    if area_a <= 0 or area_b <= 0:
        return False
    smaller = min(area_a, area_b)
    larger = max(area_a, area_b)
    return smaller / larger >= ratio


def _same_class(det_a: dict[str, Any], det_b: dict[str, Any]) -> bool:
    name_a = det_a.get("mapped_name") or det_a.get("class_name")
    name_b = det_b.get("mapped_name") or det_b.get("class_name")
    return name_a == name_b


def suppress_close_detections(
    detections: list[dict[str, Any]],
    iou_threshold: float = 0.40,
    center_threshold: float = 0.30,
    size_ratio: float = 0.50,
    cross_class_iou_threshold: float = 0.62,
    cross_class_center_threshold: float = 0.18,
    cross_class_size_ratio: float = 0.70,
) -> list[dict[str, Any]]:
    """Keep the highest-confidence box when detections are likely duplicates."""
    kept: list[dict[str, Any]] = []
    sorted_detections = sorted(
        detections,
        key=lambda item: float(item.get("confidence", 0.0)),
        reverse=True,
    )

    for detection in sorted_detections:
        box = detection["bbox_xyxy"]
        duplicate = False
        for existing in kept:
            existing_box = existing["bbox_xyxy"]
            same_class = _same_class(detection, existing)
            overlap = _iou(box, existing_box)
            min_diag = min(_diagonal(box), _diagonal(existing_box))
            distance = _center_distance(box, existing_box)

            if same_class and overlap >= iou_threshold:
                duplicate = True
                break

            if (
                same_class
                and
                min_diag > 0
                and distance <= center_threshold * min_diag
                and _similar_size(box, existing_box, size_ratio)
            ):
                duplicate = True
                break

            if not same_class and overlap >= cross_class_iou_threshold:
                duplicate = True
                break

            if (
                not same_class
                and min_diag > 0
                and distance <= cross_class_center_threshold * min_diag
                and _similar_size(box, existing_box, cross_class_size_ratio)
            ):
                duplicate = True
                break

        if not duplicate:
            kept.append(detection)

    return sorted(kept, key=lambda item: item.get("source_index", 0))
