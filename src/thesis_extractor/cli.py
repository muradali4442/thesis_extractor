from __future__ import annotations

from pathlib import Path
import click
from . import pdf as pdfmod
from . import rag as ragmod
from . import eval as evalmod
from . import visualize as vizmod
from .preprocess import merge_text_and_tables


@click.group()
def main():
    """Thesis Extractor CLI."""


# ---------------- PDF ----------------
@main.group()
def pdf():
    """PDF utilities."""


@pdf.command("extract")
@click.option("--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", "out_path", type=click.Path(dir_okay=False), required=True)
def pdf_extract(pdf_path: str, out_path: str):
    text = pdfmod.extract_text_from_pdf(pdf_path)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(text, encoding="utf-8")
    click.echo(f"Wrote text to {out_path}")


@pdf.command("tables")
@click.option("--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", "out_csv", type=click.Path(dir_okay=False), required=True)
def pdf_tables(pdf_path: str, out_csv: str):
    tables = pdfmod.extract_tables_from_pdf(pdf_path)
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    pdfmod.save_tables_to_csv(tables, out_csv)
    click.echo(f"Wrote tables to {out_csv}")


# ---------------- DATA (merge) ----------------
@main.group()
def data():
    """Data preparation utilities."""


@data.command("merge")
@click.option("--text", "text_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--tables", "tables_csv", type=click.Path(exists=True, dir_okay=False), required=False)
@click.option("--out", "out_path", type=click.Path(dir_okay=False), required=True)
def data_merge(text_path: str, tables_csv: str | None, out_path: str):
    merged = merge_text_and_tables(text_path, tables_csv, out_path=out_path, title="Merged PDF Text + Tables")
    click.echo(f"Wrote merged corpus to {out_path} ({len(merged)} chars)")


# ---------------- OCR ----------------
@main.group()
def ocr():
    """OCR utilities."""


@ocr.command("images")
@click.option("--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", "out_dir", type=click.Path(file_okay=False), required=True)
def ocr_images(pdf_path: str, out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    images = pdfmod.pdf_to_images(pdf_path)
    for i, img in enumerate(images):
        img.save(Path(out_dir) / f"page_{i+1:03d}.png")
    click.echo(f"Saved {len(images)} images to {out_dir}")


@ocr.command("text")
@click.option("--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False), required=True)
def ocr_text(pdf_path: str):
    images = pdfmod.pdf_to_images(pdf_path)
    text = pdfmod.ocr_images(images)
    click.echo(text)


# ---------------- RAG ----------------
@main.group()
def rag():
    """RAG pipeline (Haystack BM25 + LLM)."""


@rag.command("index")
@click.option("--data", "data_path", type=click.Path(exists=True), required=True, help="Merged text file (Markdown).")
@click.option("--split-length", default=256, show_default=True)
@click.option("--split-overlap", default=32, show_default=True)
def rag_index(data_path: str, split_length: int, split_overlap: int):
    store = ragmod.build_document_store()
    text = Path(data_path).read_text(encoding="utf-8")
    ragmod.index_texts(store, [text], split_length=split_length, split_overlap=split_overlap)
    click.echo("Indexed merged corpus into in-memory BM25 store. (Note: not persisted.)")


@rag.command("ask")
@click.option("--question", required=True)
@click.option("--top-k", default=5, show_default=True)
@click.option("--model", default="mistralai/Mixtral-8x7B-Instruct-v0.1", show_default=True)
@click.option("--api-base-url", default=None, help="Optional: custom HF endpoint base URL.")
@click.option("--api-key", default=None, help="Optional: override HF token; else uses HF_TOKEN/HF_API_TOKEN env vars.")
@click.option("--data", "data_path", type=click.Path(exists=True), required=True, help="Merged text file to index on the fly.")
@click.option("--split-length", default=256, show_default=True)
@click.option("--split-overlap", default=32, show_default=True)
def rag_ask(
    question: str,
    top_k: int,
    model: str,
    api_base_url: str | None,
    api_key: str | None,
    data_path: str,
    split_length: int,
    split_overlap: int,
):
    # Build fresh store per run (simple & stateless for CI/demo)
    store = ragmod.build_document_store()
    text = Path(data_path).read_text(encoding="utf-8")
    ragmod.index_texts(store, [text], split_length=split_length, split_overlap=split_overlap)
    pipe = ragmod.build_qa_pipeline(store, model=model, api_base_url=api_base_url, api_key=api_key)
    ans, ctx = ragmod.ask(pipe, question, top_k=top_k)
    click.echo(ans)


# ---------------- EVAL ----------------
@main.group()
def eval():
    """Evaluation utilities."""


@eval.command("run")
@click.option("--pred", "pred_csv", type=click.Path(exists=True), required=True)
@click.option("--gold", "gold_csv", type=click.Path(exists=True), required=True)
@click.option("--out", "out_csv", type=click.Path(dir_okay=False), required=True)
def eval_run(pred_csv: str, gold_csv: str, out_csv: str):
    df = evalmod.evaluate_csv(pred_csv, gold_csv, out_csv)
    click.echo(df.to_string(index=False))


# ---------------- VIZ ----------------
@main.group()
def viz():
    """Visualization helpers."""


@viz.command("metrics")
@click.option("--csv", "csv_path", type=click.Path(exists=True), required=True)
def viz_metrics(csv_path: str):
    vizmod.plot_metrics(csv_path)
