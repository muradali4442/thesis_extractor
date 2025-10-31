import pytest
from pathlib import Path

# Skip if pandas isn't available locally
pytest.importorskip("pandas")

import pandas as pd
from thesis_extractor.preprocess import merge_text_and_tables


def test_merge_smoke(tmp_path: Path):
    text_path = tmp_path / "text.txt"
    text_path.write_text("Hello world. This is a tiny test document.", encoding="utf-8")

    df = pd.DataFrame({
        "table_id": [0, 0],
        "Metric": ["AUC", "Accuracy"],
        "Value": [0.91, 0.87],
    })
    tables_csv = tmp_path / "tables.csv"
    df.to_csv(tables_csv, index=False)

    out_path = tmp_path / "merged.md"
    merged = merge_text_and_tables(text_path, tables_csv, out_path=out_path, title="Merged PDF Text + Tables")

    assert "## TEXT" in merged
    assert "## TABLE 0" in merged
    assert "| Metric | Value |" in merged  # markdown header
    assert out_path.exists() and out_path.stat().st_size > 0
