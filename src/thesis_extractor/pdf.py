from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Iterable
import io
import subprocess

import PyPDF2
import pandas as pd

try:
    import tabula  # type: ignore
except Exception:  # pragma: no cover
    tabula = None

try:
    from pdf2image import convert_from_path  # type: ignore
except Exception:  # pragma: no cover
    convert_from_path = None

try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract plain text from a PDF using PyPDF2.

    Args:
        pdf_path: Path to a PDF file.

    Returns:
        Concatenated text of all pages.
    """
    pdf_path = Path(pdf_path)
    text_parts: List[str] = []
    with pdf_path.open("rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            try:
                text_parts.append(page.extract_text() or "")
            except Exception as e:
                text_parts.append(f"\n[WARN] Failed to extract page {i}: {e}\n")
    return "\n".join(text_parts)


def extract_tables_from_pdf(pdf_path: str | Path, pages: str = "all") -> List[pd.DataFrame]:
    """Extract tables using tabula-py (requires Java).

    Args:
        pdf_path: PDF path.
        pages: Pages spec, e.g. "all", "1-3", "1,3,5".

    Returns:
        List of DataFrames, one per detected table.
    """
    if tabula is None:
        raise RuntimeError("tabula-py is not installed. Install with `pip install tabula-py`.")
    pdf_path = Path(pdf_path)
    try:
        dfs = tabula.read_pdf(str(pdf_path), pages=pages, multiple_tables=True)
        return dfs or []
    except Exception as e:
        raise RuntimeError(f"Tabula failed on {pdf_path}: {e}")


def pdf_to_images(pdf_path: str | Path, dpi: int = 300) -> List["Image.Image"]:
    """Render PDF pages to PIL Images (requires poppler for pdf2image)."""
    if convert_from_path is None:
        raise RuntimeError("pdf2image is not installed. Install with `pip install pdf2image`.")
    return convert_from_path(str(pdf_path), dpi=dpi)


def ocr_images(images: Iterable["Image.Image"], lang: str = "eng") -> str:
    """Run OCR on a sequence of PIL Images via pytesseract."""
    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed. Install with `pip install pytesseract`.")
    texts = []
    for i, img in enumerate(images):
        try:
            texts.append(pytesseract.image_to_string(img, lang=lang))
        except Exception as e:
            texts.append(f"\n[WARN] OCR failed on image {i}: {e}\n")
    return "\n".join(texts)


def save_tables_to_csv(tables: List[pd.DataFrame], out_csv: str | Path) -> None:
    """Save multiple tables to a single CSV with table index separation."""
    out_csv = Path(out_csv)
    # Concatenate with a marker column
    parts = []
    for idx, df in enumerate(tables):
        df = df.copy()
        df.insert(0, "table_id", idx)
        parts.append(df)
    if parts:
        pd.concat(parts, ignore_index=True).to_csv(out_csv, index=False)
    else:
        # Write empty CSV with headers
        pd.DataFrame(columns=["table_id"]).to_csv(out_csv, index=False)
