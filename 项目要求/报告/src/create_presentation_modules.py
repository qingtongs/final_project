from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT_ROOT / "outputs" / "doc_ppt_work" / "presentations" / "animal-detection-final"
SLIDES_DIR = WORKSPACE / "slides"


SLIDE_SOURCE = r'''
let CTX;

const COLORS = {
  ink: "#172033",
  muted: "#5E6A7D",
  blue: "#245A9A",
  cyan: "#32A6B8",
  green: "#4B9B68",
  orange: "#E28A32",
  red: "#C94F4F",
  paper: "#F7F9FC",
  panel: "#FFFFFF",
  line: "#D8E2EF",
  dark: "#0E1A2B"
};

function shape(slide, geometry, left, top, width, height, fill = undefined, line = undefined) {
  return CTX.addShape(slide, {
    geometry,
    left, top, width, height,
    fill: fill || "#00000000",
    line: line ? { fill: line, width: 1 } : { fill: "#00000000", width: 0 }
  });
}

function text(slide, value, left, top, width, height, opts = {}) {
  return CTX.addText(slide, {
    text: value,
    left, top, width, height,
    fontSize: opts.size || 24,
    typeface: opts.font || "Arial",
    color: opts.color || COLORS.ink,
    bold: opts.bold || false,
    align: opts.align || "left",
    valign: opts.valign || "top",
    fill: opts.fill || "#00000000",
    line: { fill: "#00000000", width: 0 },
    insets: { left: 0, right: 0, top: 0, bottom: 0 }
  });
}

function kicker(slide, value, index = "01") {
  shape(slide, "rect", 64, 44, 16, 16, COLORS.cyan, COLORS.cyan).name = `kicker-${index}-marker`;
  const k = text(slide, value, 92, 36, 420, 30, { size: 13, bold: true, color: COLORS.blue });
  k.name = `kicker-${index}-label`;
}

function title(slide, value, subtitle = "") {
  text(slide, value, 64, 78, 860, 86, { size: 38, bold: true, color: COLORS.ink });
  if (subtitle) text(slide, subtitle, 66, 158, 800, 46, { size: 18, color: COLORS.muted });
}

function footer(slide, n) {
  shape(slide, "line", 64, 674, 1056, 0, undefined, COLORS.line);
  text(slide, "YOLO11s animal detection and counting | Deep Learning Final Project", 64, 684, 760, 20, { size: 10, color: COLORS.muted });
  text(slide, String(n).padStart(2, "0"), 1160, 684, 56, 20, { size: 11, bold: true, color: COLORS.blue, align: "right" });
}

function metric(slide, value, label, left, top, color = COLORS.blue) {
  shape(slide, "roundRect", left, top, 190, 110, COLORS.panel, COLORS.line);
  text(slide, value, left + 18, top + 18, 150, 38, { size: 30, bold: true, color });
  text(slide, label, left + 18, top + 62, 150, 34, { size: 14, color: COLORS.muted });
}

function bullet(slide, items, left, top, width, size = 19) {
  items.forEach((item, i) => {
    shape(slide, "ellipse", left, top + i * 42 + 10, 8, 8, COLORS.cyan, COLORS.cyan);
    text(slide, item, left + 22, top + i * 42, width - 22, 36, { size, color: COLORS.ink });
  });
}

function pipelineStep(slide, label, detail, left, top, color) {
  shape(slide, "roundRect", left, top, 185, 122, "#FFFFFF", COLORS.line);
  shape(slide, "rect", left, top, 185, 10, color, color);
  text(slide, label, left + 16, top + 22, 150, 28, { size: 19, bold: true, color: COLORS.ink });
  text(slide, detail, left + 16, top + 58, 148, 48, { size: 13, color: COLORS.muted });
}

function bar(slide, label, value, max, left, top, color) {
  text(slide, label, left, top, 220, 22, { size: 14, color: COLORS.ink });
  shape(slide, "rect", left + 230, top + 4, 430, 14, "#E8EEF6", "#E8EEF6");
  shape(slide, "rect", left + 230, top + 4, 430 * value / max, 14, color, color);
  text(slide, value.toFixed(2), left + 676, top - 1, 60, 22, { size: 13, bold: true, color });
}

export async function slide01(presentation, ctx) {
  CTX = ctx;
  const slide = presentation.slides.add();
  shape(slide, "rect", 0, 0, 1280, 720, COLORS.paper, COLORS.paper);
  shape(slide, "rect", 0, 0, 410, 720, COLORS.dark, COLORS.dark);
  text(slide, "Animal\nDetection\nand Counting", 64, 112, 300, 170, { size: 43, bold: true, color: "#FFFFFF" });
  text(slide, "YOLO11s + custom 20-class fine-tuning", 68, 304, 300, 54, { size: 18, color: "#BBD2F0" });
  metric(slide, "20", "animal categories", 510, 150, COLORS.blue);
  metric(slide, "0.978", "final mAP50", 735, 150, COLORS.green);
  metric(slide, "90.94", "validation score", 960, 150, COLORS.orange);
  text(slide, "Output contract", 510, 318, 220, 30, { size: 22, bold: true });
  text(slide, "{\"cat\": 2, \"duck\": 1, \"deer\": 1}", 510, 360, 570, 34, { size: 24, color: COLORS.blue });
  bullet(slide, [
    "One image in, one clean dictionary out",
    "Only supported animal categories are retained",
    "Counts are generated after detection filtering and duplicate suppression"
  ], 510, 430, 610, 18);
  footer(slide, 1);
  return slide;
}

export async function slide02(presentation, ctx) {
  CTX = ctx;
  const slide = presentation.slides.add();
  shape(slide, "rect", 0, 0, 1280, 720, COLORS.paper, COLORS.paper);
  kicker(slide, "TASK REQUIREMENTS", "02");
  title(slide, "The project is a structured detection-to-dictionary problem.", "The detector must satisfy both visual recognition and strict JSON formatting.");
  pipelineStep(slide, "Detect", "Find every animal instance and localize it with a box.", 90, 260, COLORS.blue);
  pipelineStep(slide, "Filter", "Keep only the 20 allowed animal categories.", 330, 260, COLORS.cyan);
  pipelineStep(slide, "Suppress", "Remove duplicate predictions before counting.", 570, 260, COLORS.orange);
  pipelineStep(slide, "Count", "Group remaining boxes by class label.", 810, 260, COLORS.green);
  pipelineStep(slide, "Export", "Write batch results as JSON dictionaries.", 1050, 260, COLORS.red);
  text(slide, "Scoring focus", 92, 466, 260, 28, { size: 23, bold: true });
  bullet(slide, [
    "Category recall: does every true species appear?",
    "Counting accuracy: is each class count correct?",
    "False positives: each extra wrong category costs 5 points"
  ], 92, 512, 980, 18);
  footer(slide, 2);
  return slide;
}

export async function slide03(presentation, ctx) {
  CTX = ctx;
  const slide = presentation.slides.add();
  shape(slide, "rect", 0, 0, 1280, 720, COLORS.paper, COLORS.paper);
  kicker(slide, "DATASET BUILD", "03");
  title(slide, "Training data was expanded in stages instead of replacing the class vocabulary.", "Every fine-tuning stage preserved the 20-class output head.");
  const rows = [
    ["Merge", "xfz + yzy", "convert labels to JSON"],
    ["Train", "animal_dataset1", "20-class YOLO baseline"],
    ["Improve", "animal_dataset_5sp_v1", "wolf / goose / horse / cow / monkey"],
    ["Continue", "animal_dataset_6sp_v1", "targeted optimization from best model"]
  ];
  rows.forEach((r, i) => {
    const top = 238 + i * 82;
    shape(slide, "roundRect", 92, top, 996, 58, "#FFFFFF", COLORS.line);
    text(slide, r[0], 118, top + 16, 120, 22, { size: 18, bold: true, color: COLORS.blue });
    text(slide, r[1], 270, top + 16, 260, 22, { size: 18, bold: true, color: COLORS.ink });
    text(slide, r[2], 560, top + 16, 460, 22, { size: 17, color: COLORS.muted });
  });
  text(slide, "Label format", 92, 592, 140, 24, { size: 20, bold: true });
  text(slide, "LabelMe-style JSON for annotation review; YOLO TXT after conversion for training.", 240, 594, 780, 24, { size: 17, color: COLORS.muted });
  footer(slide, 3);
  return slide;
}

export async function slide04(presentation, ctx) {
  CTX = ctx;
  const slide = presentation.slides.add();
  shape(slide, "rect", 0, 0, 1280, 720, COLORS.paper, COLORS.paper);
  kicker(slide, "MODEL PIPELINE", "04");
  title(slide, "The final system couples YOLO inference with task-specific post-processing.", "The post-processing layer is important because the grading object is a dictionary, not a box list.");
  pipelineStep(slide, "YOLO11s", "COCO-pretrained detector", 88, 250, COLORS.blue);
  pipelineStep(slide, "Fine-tune", "animal_dataset1 -> 5sp -> 6sp", 318, 250, COLORS.cyan);
  pipelineStep(slide, "Whitelist", "20 supported labels only", 548, 250, COLORS.green);
  pipelineStep(slide, "NMS+", "balanced close-box suppression", 778, 250, COLORS.orange);
  pipelineStep(slide, "JSON", "positive counts only", 1008, 250, COLORS.red);
  text(slide, "Training setup", 90, 470, 190, 28, { size: 22, bold: true });
  bullet(slide, [
    "CUDA environment on RTX 3070 Ti Laptop GPU",
    "imgsz=640, batch=8, freeze first 10 layers, patience=15",
    "Augmentations: HSV jitter, translation, scale, flip, mosaic, light mixup"
  ], 90, 516, 980, 18);
  footer(slide, 4);
  return slide;
}

export async function slide05(presentation, ctx) {
  CTX = ctx;
  const slide = presentation.slides.add();
  shape(slide, "rect", 0, 0, 1280, 720, COLORS.paper, COLORS.paper);
  kicker(slide, "TRAINING RESULT", "05");
  title(slide, "Final fine-tuning converged quickly and selected epoch 2 as best.", "Validation metrics remained high while later epochs showed no sustained improvement.");
  await CTX.addImage(slide, { path: "E:/final_project/animal_detection_project/runs/detect/runs/detect/animal_dataset_6sp_20cls_finetune/results.png", left: 70, top: 218, width: 690, height: 365, fit: "contain", alt: "Training curves" });
  metric(slide, "0.963", "precision", 820, 230, COLORS.blue);
  metric(slide, "0.977", "recall", 1030, 230, COLORS.green);
  metric(slide, "0.978", "mAP50", 820, 370, COLORS.orange);
  metric(slide, "0.940", "mAP50-95", 1030, 370, COLORS.red);
  text(slide, "Best checkpoint: runs/detect/runs/detect/animal_dataset_6sp_20cls_finetune/weights/best.pt", 822, 535, 340, 46, { size: 14, color: COLORS.muted });
  footer(slide, 5);
  return slide;
}

export async function slide06(presentation, ctx) {
  CTX = ctx;
  const slide = presentation.slides.add();
  shape(slide, "rect", 0, 0, 1280, 720, COLORS.paper, COLORS.paper);
  kicker(slide, "VALIDATION SCORE", "06");
  title(slide, "Balanced duplicate suppression produced a 90.94 average validation score.", "The remaining errors are concentrated in confusing bird and canine-like classes.");
  metric(slide, "90.94", "average score / 100", 82, 235, COLORS.orange);
  metric(slide, "9", "perfect images", 306, 235, COLORS.green);
  metric(slide, "15", "validation images", 530, 235, COLORS.blue);
  bar(slide, "eval_001384", 100, 100, 82, 420, COLORS.green);
  bar(slide, "eval_001391", 83.33, 100, 82, 462, COLORS.orange);
  bar(slide, "val_1", 75, 100, 82, 504, COLORS.orange);
  bar(slide, "val_2", 61.67, 100, 82, 546, COLORS.red);
  bar(slide, "val_9", 61.67, 100, 82, 588, COLORS.red);
  text(slide, "Main deductions", 880, 250, 220, 28, { size: 22, bold: true });
  bullet(slide, [
    "val_1: fox was missed",
    "val_2 / val_9: duck confused with goose",
    "eval_001402: extra horse category"
  ], 880, 302, 310, 17);
  footer(slide, 6);
  return slide;
}

export async function slide07(presentation, ctx) {
  CTX = ctx;
  const slide = presentation.slides.add();
  shape(slide, "rect", 0, 0, 1280, 720, COLORS.paper, COLORS.paper);
  kicker(slide, "VISUAL OUTPUT", "07");
  title(slide, "Validation images are copied and annotated with boxes and confidence scores.", "The same post-processing logic is used for both displayed boxes and JSON counts.");
  await CTX.addImage(slide, { path: "E:/final_project/animal_detection_project/outputs/val_set_annotated_6sp_20cls_finetuned_suppressed_balanced/annotated/eval_001384.png", left: 78, top: 215, width: 520, height: 390, fit: "contain", alt: "Annotated validation example" });
  text(slide, "Post-processing rule", 660, 228, 270, 28, { size: 22, bold: true });
  bullet(slide, [
    "Same-class boxes: merge when overlap or centers are close",
    "Cross-class boxes: merge only when they likely cover the same object",
    "Keep the highest-confidence detection"
  ], 660, 280, 470, 18);
  text(slide, "Output directory", 660, 500, 200, 24, { size: 18, bold: true, color: COLORS.blue });
  text(slide, "outputs/val_set_annotated_6sp_20cls_finetuned_suppressed_balanced", 660, 536, 470, 50, { size: 14, color: COLORS.muted });
  footer(slide, 7);
  return slide;
}

export async function slide08(presentation, ctx) {
  CTX = ctx;
  const slide = presentation.slides.add();
  shape(slide, "rect", 0, 0, 1280, 720, COLORS.dark, COLORS.dark);
  text(slide, "Conclusion", 72, 72, 500, 60, { size: 44, bold: true, color: "#FFFFFF" });
  text(slide, "The project delivers a reproducible YOLO-based animal counting system with data preparation, fine-tuning, validation scoring, JSON export, and visual annotation.", 76, 156, 960, 62, { size: 23, color: "#DCE8F8" });
  shape(slide, "roundRect", 76, 280, 330, 190, "#142A46", "#355B88");
  shape(slide, "roundRect", 474, 280, 330, 190, "#142A46", "#355B88");
  shape(slide, "roundRect", 872, 280, 330, 190, "#142A46", "#355B88");
  text(slide, "Strength", 106, 314, 200, 28, { size: 22, bold: true, color: "#FFFFFF" });
  text(slide, "High mAP and strong dictionary-format validation performance across most large and distinctive animal classes.", 106, 356, 260, 76, { size: 17, color: "#DCE8F8" });
  text(slide, "Limitation", 504, 314, 200, 28, { size: 22, bold: true, color: "#FFFFFF" });
  text(slide, "Duck/goose and fox/wolf/dog confusions remain the main source of lost points.", 504, 356, 260, 76, { size: 17, color: "#DCE8F8" });
  text(slide, "Next step", 902, 314, 200, 28, { size: 22, bold: true, color: "#FFFFFF" });
  text(slide, "Add more manually verified hard examples and continue targeted fine-tuning with stricter validation review.", 902, 356, 260, 76, { size: 17, color: "#DCE8F8" });
  text(slide, "Final deliverables: report, PPT, source code, and evaluation JSON.", 76, 612, 900, 26, { size: 18, color: "#BBD2F0" });
  return slide;
}
'''


def main() -> None:
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(1, 9):
        module_path = SLIDES_DIR / f"slide-{i:02d}.mjs"
        module_path.write_text(SLIDE_SOURCE, encoding="utf-8")
    print(SLIDES_DIR)


if __name__ == "__main__":
    main()
