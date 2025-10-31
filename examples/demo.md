# Thesis Extractor — Minimal Demo

This demo shows the end‑to‑end flow on a **small example**. You can either use a real PDF
(Option A) or create toy inputs without a PDF (Option B).

> Requires the package installed in editable mode: `pip install -e .`

---

## Option A — With a real PDF

```bash
# 1) Extract text & tables from your PDF
thesis-extractor pdf extract --pdf data/paper.pdf --out out/text.txt
thesis-extractor pdf tables  --pdf data/paper.pdf --out out/tables.csv

# 2) Merge text + tables into one Markdown file (LLM-friendly)
thesis-extractor data merge --text out/text.txt --tables out/tables.csv --out out/merged.md

# 3) Ask a competency question (CQ) using BM25 + LLM
export HF_TOKEN=...  # or pass --api-key
thesis-extractor rag ask   --data out/merged.md   --question "Which datasets and clinical outcomes are reported? Cite tables."   --model mistralai/Mixtral-8x7B-Instruct-v0.1   --top-k 5
```

---

## Option B — No PDF (toy inputs)

```bash
# 0) Prepare toy inputs
mkdir -p out
printf "Hello world. This is a tiny test document.\nIt mentions AUC in the results." > out/text.txt
python - <<'PY'
import pandas as pd
df = pd.DataFrame({"table_id":[0,0], "Metric":["AUC","Accuracy"], "Value":[0.91,0.87]})
df.to_csv("out/tables.csv", index=False)
PY

# 1) Merge text + tables
thesis-extractor data merge --text out/text.txt --tables out/tables.csv --out out/merged.md

# 2) Ask a question
export HF_TOKEN=...  # or pass --api-key
thesis-extractor rag ask   --data out/merged.md   --question "What metrics are reported and their values? Cite tables."   --model mistralai/Mixtral-8x7B-Instruct-v0.1   --top-k 5
```

---

### Expected output (example)

A short, grounded answer referencing the table, e.g.:

> The study reports **AUC = 0.91** and **Accuracy = 0.87** (see **TABLE 0**).

*(Exact wording may differ by model/provider.)*
