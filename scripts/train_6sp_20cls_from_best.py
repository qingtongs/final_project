"""Fine-tune the latest 20-class best model on animal_dataset_6sp_v1."""

from ultralytics import YOLO


def main() -> None:
    model = YOLO("runs/detect/runs/detect/animal_dataset_5sp_20cls_finetune/weights/best.pt")
    model.train(
        data="configs/animal_dataset_6sp_20cls.yaml",
        epochs=60,
        batch=8,
        imgsz=640,
        device=0,
        freeze=10,
        patience=15,
        save=True,
        save_period=10,
        plots=True,
        val=True,
        workers=0,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=8.0,
        translate=0.1,
        scale=0.4,
        flipud=0.05,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.05,
        close_mosaic=10,
        lr0=0.0005,
        lrf=0.01,
        warmup_epochs=3,
        weight_decay=0.0005,
        project="runs/detect",
        name="animal_dataset_6sp_20cls_finetune",
        exist_ok=True,
    )


if __name__ == "__main__":
    main()
