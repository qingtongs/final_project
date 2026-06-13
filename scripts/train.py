"""
Train YOLO11 model for animal detection and counting.
Fine-tune from COCO pre-trained weights.
"""

from ultralytics import YOLO
import argparse
import os


def train(
    model_size: str = "s",
    data_config: str = "configs/animal_dataset.yaml",
    epochs: int = 100,
    batch_size: int = 16,
    imgsz: int = 640,
    device: str = "0",
    resume: bool = False,
    freeze: int = 10,
):
    """
    Train / fine-tune YOLO11 on the animal dataset.

    Args:
        model_size: YOLO11 model variant (n, s, m, l, x)
        data_config: Path to dataset YAML config
        epochs: Number of training epochs
        batch_size: Batch size (reduce if OOM)
        imgsz: Input image size
        device: CUDA device id or 'cpu'
        resume: Resume from last checkpoint
        freeze: Number of backbone layers to freeze (10 = fine-tune mid-to-late layers)
    """
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    if resume:
        model = YOLO("runs/detect/train/weights/last.pt")
    else:
        # Load COCO pre-trained YOLO11 model
        model_name = f"yolo11{model_size}.pt"
        print(f"Loading pre-trained model: {model_name}")
        model = YOLO(model_name)

    print(f"Training on dataset: {data_config}")
    print(f"Epochs: {epochs}, Batch: {batch_size}, Image size: {imgsz}")
    print(f"Device: {device}, Freeze backbone layers: {freeze}")

    results = model.train(
        data=data_config,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=device,
        freeze=freeze,          # Freeze first N backbone layers for transfer learning
        patience=30,            # Early stopping patience
        save=True,
        save_period=10,         # Save checkpoint every 10 epochs
        plots=True,
        val=True,
        # Augmentation (tuned for animal detection)
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
        close_mosaic=10,        # Disable mosaic in last 10 epochs
        # Optimizer
        lr0=0.001,
        lrf=0.01,
        warmup_epochs=3,
        weight_decay=0.0005,
        project="runs/detect",
        name="train",
    )

    print("\nTraining complete!")
    print(f"Best model saved to: runs/detect/train/weights/best.pt")
    print(f"Last model saved to: runs/detect/train/weights/last.pt")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLO11 for Animal Detection")
    parser.add_argument("--model-size", type=str, default="s", choices=["n", "s", "m", "l", "x"],
                        help="YOLO11 model variant")
    parser.add_argument("--data", type=str, default="configs/animal_dataset.yaml",
                        help="Path to dataset config YAML")
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--device", type=str, default="0", help="Device (0, 1, ... or cpu)")
    parser.add_argument("--resume", action="store_true", help="Resume training")
    parser.add_argument("--freeze", type=int, default=10, help="Freeze first N backbone layers")

    args = parser.parse_args()
    train(
        model_size=args.model_size,
        data_config=args.data,
        epochs=args.epochs,
        batch_size=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        resume=args.resume,
        freeze=args.freeze,
    )
