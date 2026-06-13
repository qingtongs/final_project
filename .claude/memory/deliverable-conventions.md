---
name: deliverable-conventions
description: PPT and report format rules — single-language only, output locations, generation scripts
metadata:
  type: feedback
---

# Deliverable Format Conventions

**CRITICAL**: PPT and report must be SINGLE-LANGUAGE only. Do NOT generate bilingual mixed-content slides or paragraphs.

- **PPT**: Separate English-only (`_en.pptx`) and Chinese-only (`_zh.pptx`) versions. No mixed EN/ZH on same slide.
- **Report**: Chinese-only (`.docx` + `.pdf`). Follows `项目要求/报告模板.docx` format. Sections: 一、引言 through 六、结论.

**Output location**: `项目要求/报告/`
**Generation scripts**: `项目要求/报告/src/` — `generate_ppt_en.py`, `generate_ppt_zh.py`, `generate_report_zh.py`

**How to apply**: When asked to regenerate deliverables, run the scripts in `项目要求/报告/src/`. Never create bilingual mixed versions again. The old `outputs/final_deliverables/` has been deleted — all final files live under `项目要求/报告/`.

**Why**: User explicitly rejected bilingual mixed format ("不要双语的版本", "ppt的要求是单独全英文或者单独中文"). Course is Chinese, template is Chinese, so report defaults to Chinese; PPT provided in both languages as separate files.
