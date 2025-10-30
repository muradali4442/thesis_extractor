from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional, cast

import PyPDF2
import pandas as pd

# ---- Optional dependencies with safe typing ---------------------------------
# We avoid `import tabula` then assigning None (which confuses mypy by changing
# a Module into None). Instead, import to a private alias and expose a typed name.

try:
    import tabula as _tabula  # type: ignore
    tabula: Any = _tabula
except Exception:  # pragma: no cover
    tabula = None  # type: ignore[assignment]

try:
    from pdf2image import convert_from_path as _convert_from_path  # type: ignore
    # Callable[..., List[Any]] is sufficient for typing; PIL Image is optional in CI.
    convert_from_path: Optional[Callable[..., List[Any]]] = cast(
        Callable[..., List[Any]], _convert_from_path
    )
except Exception:  # pragma: no cover
    convert_from_path = None

try:
    import pytesseract as _pytesseract  # type: ignore
    pytesseract: Any = _pytesseract
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore[assignment]


# ---- Public API --------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract plain text from a PDF using PyPDF2."""
    pdf_path = Path(pdf_path)
    text_parts: List[str] = []
    with pdf_path.open("rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            try:
                text_parts.append(page.extract_text() or "")
            except Exception as e:  # pragma: no cover
                text_parts.append(f"\n[WARN] Failed to extract page {i}: {e}\n")
    return "\n".join(text_parts)


def extract_tables_from_pdf(pdf_path: str | Path, pages: str = "all") -> List[pd.DataFrame]:
    """Extract tables using tabula-py (requires Java)."""
    if tabula is None:
        raise RuntimeError("tabula-py is not installed. Install with `pip install tabula-py`.")
    pdf_path = Path(pdf_path)

    try:
        dfs_any = tabula.read_pdf(str(pdf_path), pages=pages, multiple_tables=True)
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"Tabula failed on {pdf_path}: {e}") from e

    # tabula.read_pdf can return a DataFrame or a List[DataFrame] depending on args.
    if isinstance(dfs_any, list):
        df_list: List[pd.DataFrame] = [df for df in dfs_any if isinstance(df, pd.DataFrame)]
    elif isinstance(dfs_any, pd.DataFrame):
        df_list = [dfs_any]
    else:
        df_list = []

    return df_list


def pdf_to_images(pdf_path: str | Path, dpi: int = 300) -> List[Any]:
    """Render PDF pages to PIL Images (requires Poppler for pdf2image)."""
    if convert_from_path is None:
        raise RuntimeError("pdf2image is not installed. Install with `pip install pdf2image`.")
    # mypy: after the None check, Optional is narrowed.
    return convert_from_path(str(pdf_path), dpi=dpi)  # type: ignore[misc]


def ocr_images(images: Iterable[Any], lang: str = "eng") -> str:
    """Run OCR on a sequence of PIL Images via pytesseract."""
    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed. Install with `pip install pytesseract`.")
    texts: List[str] = []
    for i, img in enumerate(images):
        try:
            texts.append(pytesseract.image_to_string(img, lang=lang))
        except Exception as e:  # pragma: no cover
            texts.append(f"\n[WARN] OCR failed on image {i}: {e}\n")
    return "\n".join(texts)


def save_tables_to_csv(tables: List[pd.DataFrame], out_csv: str | Path) -> None:
    """Save multiple tables to a single CSV with table index separation."""
    out_csv = Path(out_csv)
    parts: List[pd.DataFrame] = []
    for idx, df in enumerate(tables):
        dfc = df.copy()
        dfc.insert(0, "table_id", idx)
        parts.append(dfc)
    if parts:
        pd.concat(parts, ignore_index=True).to_csv(out_csv, index=False)
    else:
        pd.DataFrame(columns=["table_id"]).to_csv(out_csv, index=False)
