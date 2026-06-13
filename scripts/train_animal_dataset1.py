"""Train YOLO11s on dataset/animal_dataset1_yolo using CUDA."""

from ultralytics import YOLO


def main() -> None:
    model = YOLO("yolo11s.pt")
    model.train(
        data="configs/animal_dataset1.yaml",
        epochs=100,
        batch=8,
        imgsz=640,
        device=0,
        freeze=10,
        patience=30,
        save=True,
        save_period=10,
        plots=True,
        val=True,
        workers=0,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        flipud=0.1,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        close_mosaic=10,
        lr0=0.001,
        lrf=0.01,
        warmup_epochs=3,
        weight_decay=0.0005,
        project="runs/detect",
        name="animal_dataset1",
        exist_ok=True,
    )


if __name__ == "__main__":
    main()
