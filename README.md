# Thesis Extractor, Biomedical PDF/Text–Table RAG Pipeline

Modular utilities for **PDF text & table extraction**, **OCR** and a compact **RAG demo** - refactored from a master’s thesis into a clean, testable Python package with a CLI. The thesis investigates how to better leverage **non-textual modalities (tables/figures)** alongside text to answer **competency questions (CQs)** in the biomedical domain using **LLMs** and **BM25** retrieval.

[![Tests](https://img.shields.io/github/actions/workflow/status/<yourname>/thesis_extractor/ci.yml?branch=main)](https://github.com/<yourname>/thesis_extractor/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)](#)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **What this is**  
> A research-driven, **config-first** package that turns a thesis notebook into a reusable toolchain for **biomedical PDF parsing** (text + tables), **OCR** and a **RAG** workflow (BM25 + LLM). It’s engineered for reproducibility (CLI, tests, CI) and readability for reviewers, hiring managers and admissions committees.

---

## Abstract (short)
Biomedical literature is growing rapidly and mixes **text, tables and figures**, making retrieval and synthesis challenging. This project examines the limitations of standard **RAG** systems that underuse non-textual modalities and proposes a modular pipeline that extracts **text and tabular data** from research PDFs, indexes them with **BM25** and synthesizes answers to **competency questions** using an **LLM (Mixtral-8x7B)**.

The corpus includes open-source papers from **IEEE** and **CEUR-WS** (AI for Healthcare 2024, Vol-3880; HC@AIxIA 2023, Vol-3578). The approach emphasizes **reproducibility** via open-source tools, public datasets and transparent configuration. Although focused on biomedicine, the design is **domain-agnostic** and applicable to areas like biodiversity, climate science and computational linguistics.

Evaluation considers **faithfulness**, **answer relevance**, **contextual relevance** and **groundedness**, comparing generated answers with expert-validated references. Results show improved integration of diverse sources and effective responses to complex biomedical questions.

> Read the full abstract in **[docs/ABSTRACT.md](docs/ABSTRACT.md)**.

---

## Features
- **PDF → text** via `PyPDF2` with simple error handling
- **PDF → tables** via `tabula-py` (Java required), CSV output with `table_id` markers
- **OCR** using `pdf2image` + `pytesseract` (Poppler required)
- **RAG demo** using Haystack **BM25** + prompt LLM (tested with Mixtral-8x7B; pluggable)
- **Evaluation helpers** (baseline precision/recall/F1) with hooks to align with thesis metrics
- **Visualization** utilities (quick metrics plot, word cloud)
- **CLI** powered by `click`, config-driven (YAML), no hardcoded paths
- **Tests + CI + pre-commit** (ruff, mypy-ready, black-compatible)

---

## Install
```bash
git clone https://github.com/<yourname>/thesis_extractor.git
cd thesis_extractor
pip install -e .
# optional but recommended
pip install -r dev-requirements.txt
pre-commit install
```

### Runtime dependencies
Core libs are specified in `pyproject.toml`. For OCR/table extraction you may need system deps:
- **tabula-py** → Java runtime
- **pdf2image** → Poppler (e.g., `apt install poppler-utils`, `brew install poppler`)

---

## Quickstart
```bash
# Text extraction
thesis-extractor pdf extract --pdf data/paper.pdf --out out/text.txt

# Table extraction
thesis-extractor pdf tables  --pdf data/paper.pdf --out out/tables.csv

# OCR (images + text)
thesis-extractor ocr images  --pdf data/paper.pdf --out out/images
thesis-extractor ocr text    --pdf data/paper.pdf

# (Optional) RAG demo — index text and ask a competency question (CQ)
export HF_TOKEN=...   # if your model/host requires it
thesis-extractor rag index --data out/text.txt
thesis-extractor rag ask --question "Which clinical outcomes improved and under what conditions?" --top-k 5

# Evaluation + viz (baseline)
thesis-extractor eval run --pred predictions.csv --gold gold.csv --out out/metrics.csv
thesis-extractor viz metrics --csv out/metrics.csv
```

---

## Project layout
```
src/thesis_extractor/
  pdf.py         # text & table extraction, OCR helpers
  rag.py         # Haystack BM25 + prompt LLM wiring (optional)
  eval.py        # baseline evaluation utilities
  visualize.py   # plotting & word cloud
  cli.py         # CLI commands
tests/
.github/workflows/ci.yml  # CI (pytest, ruff, mypy)
configs/base.yaml         # defaults
```

---

## Configuration
Edit `configs/base.yaml` or pass flags on the CLI. Example:
```yaml
pdf:
  dpi: 300
ocr:
  lang: eng
rag:
  model: mixtral-8x7b   # or any supported model/endpoint
```
You can also override any setting with CLI flags for one-off runs.

---

## Dataset & scope (as used in the thesis)
- Open-source biomedical articles from **IEEE**
- **CEUR-WS Vol-3880** — *Artificial Intelligence for Healthcare 2024*
- **CEUR-WS Vol-3578** — *HC@AIxIA 2023: AI for Healthcare*

> The pipeline is **domain-agnostic**. Swap in other corpora (e.g., climate or biodiversity) by changing inputs/configs; no code changes required.

---

## Method overview
1. **Ingestion & Extraction** — PDF → text (`PyPDF2`), PDF → tables (`tabula-py`), optional OCR for scans (`pdf2image` + `pytesseract`)
2. **Indexing** — chunking and **BM25** retrieval (Haystack `InMemoryDocumentStore`)
3. **Synthesis** — prompt **LLM** (e.g., Mixtral-8x7B) over retrieved contexts
4. **Evaluation** — baseline quantitative metrics + thesis-style criteria (faithfulness, answer relevance, contextual relevance, groundedness) against expert-validated references

---

## Development
```bash
# lint
ruff check .
# type-check
mypy src
# tests
pytest -q
```

---

## Roadmap
- [ ] Persistable document store + real indexing/serving lifecycle
- [ ] More robust table detection & figure/caption handling
- [ ] Richer metrics & reporting aligned with faithfulness/groundedness
- [ ] Example dataset + demo notebook (Colab badge)
- [ ] Packaging to PyPI

---

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## License
[MIT](LICENSE)

---

## Citation
If this work is useful in academic contexts, please cite:

```bibtex
@software{thesis_extractor_2025,
  author = {<Your Name>},
  title  = {Thesis Extractor: Biomedical PDF/Text–Table RAG Pipeline},
  year   = {2025},
  url    = {https://github.com/<yourname>/thesis_extractor},
  version= {0.1.0}
}
```
