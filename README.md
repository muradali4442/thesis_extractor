# Thesis Extractor - Biomedical PDF/Text–Table RAG

A small, practical toolkit for **PDF text & table extraction**, **OCR** and a simple **RAG** pipeline. It’s based on my master’s thesis and focuses on using both **text and tables** to answer **competency questions (CQs)** in the biomedical domain.

[![Tests](https://img.shields.io/github/actions/workflow/status/muradali4442/thesis_extractor/ci.yml?branch=main)](https://github.com/muradali4442/thesis_extractor/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)](#)

---

## What it does (short)
- Extract **text** from PDFs with `PyPDF2`.
- Extract **tables** with `tabula-py` (Java required).
- Optional **OCR** for scanned PDFs with `pdf2image` + `pytesseract` (Poppler required).
- **Merge text + tables** into Markdown for LLM-ready context.
- **RAG demo**: BM25 retrieval (Haystack) + an LLM (tested with **Mixtral‑8x7B** via Hugging Face).
- Small **evaluation** helpers and a simple **metrics plot**.
- **CLI** for all tasks; **config** via YAML.

Read the full abstract in **[docs/ABSTRACT.md](docs/ABSTRACT.md)**.

---

## Install
```bash
git clone https://github.com/muradali4442/thesis_extractor.git
cd thesis_extractor
pip install -e .
# optional (dev tools)
pip install -r dev-requirements.txt
pre-commit install
```

### System deps
- `tabula-py` → Java runtime
- `pdf2image` → Poppler (`apt install poppler-utils` or `brew install poppler`)

---

## Quickstart
```bash
# 1) Extract from a PDF
thesis-extractor pdf extract --pdf data/paper.pdf --out out/text.txt
thesis-extractor pdf tables  --pdf data/paper.pdf --out out/tables.csv

# 2) Merge text + tables to one file (for RAG)
thesis-extractor data merge --text out/text.txt --tables out/tables.csv --out out/merged.md

# 3) Ask a question with BM25 + LLM (Mixtral via HF Inference)
export HF_TOKEN=...  # or pass --api-key
thesis-extractor rag ask   --data out/merged.md   --question "Which clinical outcomes improved and under what conditions?"   --model mistralai/Mixtral-8x7B-Instruct-v0.1   --top-k 5
```

---

## Config (example)
Edit `configs/base.yaml` or pass flags:
```yaml
pdf:
  dpi: 300
ocr:
  lang: eng
rag:
  model: mistralai/Mixtral-8x7B-Instruct-v0.1
```
> You can also override on the CLI for one‑off runs.

---

## Project layout
```
src/thesis_extractor/
  pdf.py         # text & table extraction, OCR helpers
  preprocess.py  # merge text + tables -> Markdown
  rag.py         # Haystack BM25 + LLM (Mixtral via HF)
  eval.py        # baseline metrics
  visualize.py   # simple plotting
  cli.py         # CLI commands
configs/
tests/
.github/workflows/ci.yml
```

---

## Notes
- The pipeline is **domain‑agnostic**; I used biomedical papers (IEEE, CEUR‑WS Vol‑3880 & Vol‑3578), but you can point it at any PDFs.
- To use Mixtral or another LLM on Hugging Face, set `HF_TOKEN` or pass `--api-key`. A custom endpoint can be passed via `--api-base-url`.

---

## License
[MIT](LICENSE)

## Citation
```bibtex
@software{thesis_extractor_2025,
  author  = {Your Name},
  title   = {Thesis Extractor — Biomedical PDF/Text–Table RAG},
  year    = {2025},
  url     = {https://github.com/muradali4442/thesis_extractor},
  version = {0.1.0}
}
```
