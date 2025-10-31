from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd


def _df_to_markdown(df: pd.DataFrame, max_rows: int = 50, max_cols: int = 20) -> str:
    """Serialize a DataFrame to a compact GitHub-flavored Markdown table."""
    df = df.copy()

    # Trim overly wide/long tables to keep contexts LLM-friendly
    if df.shape[1] > max_cols:
        df = df.iloc[:, :max_cols]
    if df.shape[0] > max_rows:
        df = df.iloc[:max_rows, :]

    # Ensure string columns
    df = df.applymap(lambda x: "" if pd.isna(x) else str(x))

    # Build Markdown
    headers = " | ".join(df.columns.astype(str).tolist())
    sep = " | ".join(["---"] * len(df.columns))
    rows = [" | ".join(row) for row in df.values.tolist()]
    table_md = "\n".join([f"| {headers} |", f"| {sep} |"] + [f"| {r} |" for r in rows])
    return table_md


def merge_text_and_tables(
    text_path: str | Path,
    tables_csv_path: Optional[str | Path],
    out_path: Optional[str | Path] = None,
    title: str = "Merged Corpus",
) -> str:
    """
    Merge plain text (from PDF) and extracted tables (CSV with 'table_id') into a single Markdown corpus.
    Each table is represented as a Markdown table with an anchor and lightweight metadata.
    """
    text_path = Path(text_path)
    text = text_path.read_text(encoding="utf-8")

    parts: List[str] = [f"# {title}", "\n## TEXT\n", text.strip()]

    if tables_csv_path:
        csvp = Path(tables_csv_path)
        if csvp.exists() and csvp.stat().st_size > 0:
            df = pd.read_csv(csvp)
            # Expect a 'table_id' column; if missing, fabricate sequential IDs.
            if "table_id" not in df.columns:
                df.insert(0, "table_id", 0)

            # Split back into individual tables by table_id
            for tid, tdf in df.groupby("table_id"):
                # Drop helper col before markdown
                tdf = tdf.drop(columns=[c for c in ["table_id"] if c in tdf.columns])
                parts.append(f"\n## TABLE {tid}\n")
                parts.append(_df_to_markdown(tdf))
        else:
            parts.append("\n> _No tables CSV provided or file is empty._\n")

    merged = "\n".join(parts).strip()

    if out_path:
        op = Path(out_path)
        op.parent.mkdir(parents=True, exist_ok=True)
        op.write_text(merged, encoding="utf-8")

    return merged
