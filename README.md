# Thesis Extractor

Modular utilities for **PDF text & table extraction**, **OCR**, and a tiny **RAG demo** — refactored from a thesis notebook into a clean, testable Python package with a CLI.

[![Tests](https://img.shields.io/github/actions/workflow/status/yourname/thesis-extractor/ci.yml?branch=main)](https://github.com/yourname/thesis-extractor/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)](#)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **Why this exists**  
> Many thesis projects live in Jupyter notebooks. This repo shows how to turn a one-off notebook into a **reusable, config-driven package** with tests, a CLI, and CI — the kind of repo reviewers and hiring managers love to see.

---

## Features
- **PDF → text** via PyPDF2 with simple error handling
- **PDF → tables** via `tabula-py` (Java required)
- **OCR** using `pdf2image` + `pytesseract`
- **RAG demo** using Haystack BM25 + prompt LLM (opt‑in)
- **Evaluation helpers** (precision/recall/F1) and a minimal **visualization** module
- **CLI** powered by `click`, config-driven (YAML), no hardcoded paths
- **Tests + CI + pre-commit** (ruff, black-compatible, mypy-ready)

## Install
```bash
git clone https://github.com/yourname/thesis-extractor.git
cd thesis-extractor
pip install -e .
# optional but recommended
pip install -r dev-requirements.txt
pre-commit install
```

### Runtime dependencies
Core libs are specified in `pyproject.toml`. For OCR/table extraction you may need system deps:
- **tabula-py** → Java runtime
- **pdf2image** → Poppler (e.g., `apt install poppler-utils`)

## Quickstart
```bash
# Text extraction
thesis-extractor pdf extract --pdf paper1.pdf --out out/text.txt

# Table extraction
thesis-extractor pdf tables --pdf paper1.pdf --out out/tables.csv

# OCR (images + text)
thesis-extractor ocr images --pdf paper1.pdf --out out/images
thesis-extractor ocr text   --pdf paper1.pdf

# (Optional) RAG demo
export HF_TOKEN=...   # if your model requires it
thesis-extractor rag index --data out/text.txt
thesis-extractor rag ask --question "What does section 3 conclude?" --top-k 5

# Evaluation + viz
thesis-extractor eval run --pred predictions.csv --gold gold.csv --out out/metrics.csv
thesis-extractor viz metrics --csv out/metrics.csv
```

## Project layout
```
src/thesis_extractor/
  pdf.py         # text & table extraction, OCR helpers
  rag.py         # Haystack pipeline setup & querying (optional)
  eval.py        # evaluation utilities
  visualize.py   # plotting & word cloud
  cli.py         # CLI commands
tests/
.github/workflows/ci.yml  # CI (pytest, ruff, mypy)
configs/base.yaml         # defaults
```

## Configuration
Edit `configs/base.yaml` or pass flags on the CLI. Example:
```yaml
pdf:
  dpi: 300
ocr:
  lang: eng
rag:
  model: google/flan-t5-base
```

## Development
```bash
# lint
ruff check .
# type-check
mypy src
# tests
pytest -q
```

## Roadmap
- [ ] Persistable vector store + real indexing CLI
- [ ] More robust table detection strategies
- [ ] Richer evaluation metrics & reports
- [ ] Example dataset + demo notebook (Colab badge)
- [ ] Packaging to PyPI

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License
[MIT](LICENSE)

## Citation
If this work is useful in academic contexts, please cite:

```bibtex
@software{thesis_extractor_2025,
  author = {Your Name},
  title = {Thesis Extractor: Modular PDF/OCR/RAG Utilities},
  year = {2025},
  url = {https://github.com/yourname/thesis-extractor},
  version = {0.1.0}
}
```
